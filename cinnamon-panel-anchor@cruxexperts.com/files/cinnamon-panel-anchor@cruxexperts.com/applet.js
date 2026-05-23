const Applet = imports.ui.applet;
const PopupMenu = imports.ui.popupMenu;
const Main = imports.ui.main;
const Mainloop = imports.mainloop;
const Settings = imports.ui.settings;
const Util = imports.misc.util;
const GLib = imports.gi.GLib;
const St = imports.gi.St;

const UUID = "cinnamon-panel-anchor@cruxexperts.com";
const VERSION = "0.2.2";
const PROJECT_URL = "https://github.com/CruxExperts/cinnamon-panel-anchor";
const APPLET_PATH = imports.ui.appletManager.appletMeta[UUID].path;
const AppletManager = imports.ui.appletManager;
const ICONS = {
    ok: APPLET_PATH + "/icons/panel-anchor-ok.svg",
    attention: APPLET_PATH + "/icons/panel-anchor-attention.svg",
    error: APPLET_PATH + "/icons/panel-anchor-error.svg",
    working: APPLET_PATH + "/icons/panel-anchor-working.svg",
    brand: APPLET_PATH + "/icons/anchor-icon.svg"
};

function backendCommand() {
    let launcher = APPLET_PATH + "/cinnamon-panel-anchor-backend";
    if (GLib.file_test(launcher, GLib.FileTest.IS_EXECUTABLE))
        return launcher;
    return "cinnamon-panel-anchor";
}

function runBackend(args, callback) {
    let argv = [backendCommand()].concat(args);
    try {
        Util.spawn_async(argv, (output) => {
            try {
                callback(JSON.parse(output));
            } catch (e) {
                callback({
                    ok: false,
                    severity: "error",
                    summary: "Backend returned invalid JSON",
                    monitors: [],
                    panels: [],
                    anchors: [],
                    pending_decision: null,
                    plan: null,
                    messages: [],
                    error: String(e),
                    error_details: { type: "InvalidJSON", message: String(e) },
                    version: VERSION,
                    log_path: null
                });
            }
        });
    } catch (e) {
        callback({
            ok: false,
            severity: "error",
            summary: "Backend unavailable",
            monitors: [],
            panels: [],
            anchors: [],
            pending_decision: null,
            plan: null,
            messages: [],
            error: String(e),
            error_details: { type: "BackendUnavailable", message: String(e) },
            version: VERSION,
            log_path: null
        });
    }
}

function logAppletEvent(event, outcome, message, context) {
    runBackend([
        "log-event",
        "--json",
        "--component", "applet",
        "--event", event,
        "--outcome", outcome || "ok",
        "--message", message || "",
        "--context", JSON.stringify(context || {})
    ], () => {});
}

function runningInstanceCount(logger) {
    try {
        if (AppletManager.getRunningInstancesForUuid)
            return AppletManager.getRunningInstancesForUuid(UUID).length;
    } catch (e) {
        logger("duplicate-check-failed", "warning", String(e), {});
    }
    return 0;
}

function actorMatchesUuid(actor) {
    let delegate = actor ? actor._delegate : null;
    return !!(delegate && (delegate.uuid === UUID || delegate._uuid === UUID || (delegate.metadata && delegate.metadata.uuid === UUID)));
}

class CinnamonPanelAnchorApplet extends Applet.TextIconApplet {
    constructor(metadata, orientation, panelHeight, instanceId) {
        super(orientation, panelHeight, instanceId);
        this.refreshInterval = 30;
        this.showNotifications = true;
        this.restoreAutomatically = false;
        this.debugLogging = true;
        this._refreshTimer = 0;
        this._lastNotificationKey = null;
        this._inFlight = {};
        this._stoppedForSession = false;
        this.setAllowedLayout(Applet.AllowedLayout.BOTH);
        this._setAppletIcon("brand");
        this.set_applet_label("");
        this.set_applet_tooltip("Cinnamon Panel Anchor\n" + PROJECT_URL);
        this._applet_context_menu.addAction("Open Applet Settings", () => this.configureApplet());
        this._applet_context_menu.addAction("Quit for Session", () => this._quitForSession());
        this._applet_context_menu.addAction("Disable Applet", () => this._disableApplet());

        this.menuManager = new PopupMenu.PopupMenuManager(this);
        this.menu = new Applet.AppletPopupMenu(this, orientation);
        this.menuManager.addMenu(this.menu);
        this.settings = new Settings.AppletSettings(this, metadata.uuid, instanceId);
        this.settings.bind("refresh-interval", "refreshInterval", () => this._restartTimer());
        this.settings.bind("show-notifications", "showNotifications", null);
        this.settings.bind("restore-automatically", "restoreAutomatically", null);
        this.settings.bind("debug-logging", "debugLogging", null);
        this._guardDuplicateInstance();
        this._buildMenu(null);
        this.refresh();
        this._restartTimer();
    }

    _logAppletEvent(event, outcome, message, context) {
        if (!this.debugLogging)
            return;
        logAppletEvent(event, outcome, message, context);
    }

    _guardDuplicateInstance() {
        let count = runningInstanceCount((event, outcome, message, context) => this._logAppletEvent(event, outcome, message, context));
        if (count > 1) {
            this._stoppedForSession = true;
            this.actor.hide();
            this._logAppletEvent("duplicate-instance-hidden", "skipped", "duplicate Cinnamon applet instance hidden", {
                instanceId: this.instance_id,
                runningInstances: count
            });
        }
        this._pruneDuplicateActors();
    }

    _pruneDuplicateActors() {
        try {
            let containers = [Main.panel, Main.panelManager];
            containers.forEach((container) => {
                if (!container || !container.actor || !container.actor.get_children)
                    return;
                let seen = false;
                container.actor.get_children().forEach((actor) => {
                    if (!actorMatchesUuid(actor))
                        return;
                    if (!seen) {
                        seen = true;
                        return;
                    }
                    actor.hide();
                    this._logAppletEvent("duplicate-actor-pruned", "ok", "stale duplicate actor hidden", {});
                });
            });
        } catch (e) {
            this._logAppletEvent("duplicate-cleanup-failed", "warning", String(e), {});
        }
    }

    _buildMenu(payload) {
        this.menu.removeAll();
        this.menu.addMenuItem(this._textRow(payload ? (payload.summary || "Status unavailable") : "Loading panel anchor status...", this._healthText(payload), "panel-anchor-dashboard"));
        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());

        if (payload && payload.pending_decision) {
            this.menu.addAction("Keep This Layout", () => this._runAction("keep-current", ["capture", "--json"]));
            this.menu.addAction("Restore Saved Layout", () => this._runAction("restore", ["restore", "--json"]));
        } else {
            this.menu.addAction("Save Current Layout", () => this._runAction("capture", ["capture", "--json"]));
            if (payload && (payload.anchors || []).length > 0)
                this.menu.addAction("Restore Saved Layout", () => this._runAction("restore", ["restore", "--json"]));
        }

        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
        this.menu.addAction("Refresh Status", () => this.refresh());
        this.menu.addAction("Open Display Settings", () => Util.spawn(["cinnamon-settings", "display"]));
        this.menu.addAction("Copy Diagnostics", () => this._copyDiagnostics());
        this.menu.addAction("Open Applet Settings", () => this.configureApplet());

        if (payload) {
            this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
            this.menu.addMenuItem(this._textRow(this._statusDetail(payload), this._diagnosticText(payload), "panel-anchor-dashboard"));
        }

        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
        this.menu.addMenuItem(this._textRow(PROJECT_URL, "", "panel-anchor-muted"));
    }

    on_applet_clicked() {
        if (this._stoppedForSession)
            return;
        this.menu.toggle();
        this.refresh();
    }

    _setState(payload) {
        let icon = "ok";
        if (!payload.ok || payload.severity === "error")
            icon = "error";
        else if (payload.pending_decision || payload.severity === "attention")
            icon = "attention";
        else if (payload.plan && payload.plan.changed)
            icon = "working";
        this._setAppletIcon(icon);
    }

    _setAppletIcon(state) {
        this.set_applet_icon_path(ICONS[state] || ICONS.brand);
    }

    _textRow(primary, secondary, styleClass) {
        let item = new PopupMenu.PopupBaseMenuItem({ reactive: false, can_focus: false });
        let box = new St.BoxLayout({ vertical: true, style_class: styleClass || "" });
        let primaryLabel = new St.Label({ text: primary || "" });
        box.add_actor(primaryLabel);
        if (secondary) {
            let secondaryLabel = new St.Label({ text: secondary, style_class: "panel-anchor-muted" });
            box.add_actor(secondaryLabel);
        }
        item.addActor(box);
        return item;
    }

    _healthText(payload) {
        if (!payload)
            return "";
        if (payload.pending_decision)
            return "Choose whether to keep the current panel layout or restore the saved one.";
        if (!payload.ok)
            return payload.error || "Backend status needs attention.";
        if (payload.plan && payload.plan.changed)
            return "Saved layout is ready to restore.";
        return "Panel layout is protected.";
    }

    _countText(count, singular, plural) {
        return String(count) + " " + (count === 1 ? singular : plural);
    }

    _statusDetail(payload) {
        let anchors = (payload.anchors || []).length;
        let monitors = (payload.monitors || []).length;
        let panels = (payload.panels || []).length;
        let parts = [
            this._countText(anchors, "saved layout", "saved layouts"),
            this._countText(monitors, "monitor", "monitors"),
            this._countText(panels, "panel", "panels")
        ];
        if (payload.pending_decision)
            parts.push("1 pending decision");
        return parts.join(" | ");
    }

    _diagnosticText(payload) {
        if (payload.error)
            return payload.error;
        if (payload.messages && payload.messages.length > 0)
            return payload.messages.slice(0, 2).join(" | ");
        return "No backend errors reported";
    }

    _render(payload) {
        this._setState(payload);
        this._buildMenu(payload);
        if (payload.pending_decision) {
            this._notify("Panel move decision needed", "Open the applet to keep the move or restore saved anchors.");
        } else if (!payload.ok) {
            this._notify("Cinnamon Panel Anchor needs attention", payload.error || payload.summary);
        } else if (this.restoreAutomatically && payload.plan && payload.plan.changed) {
            this._runAction("restore-auto", ["restore", "--json"]);
        }
    }

    _notify(title, body) {
        let key = title + ":" + body;
        if (this.showNotifications && Main.messageTray && key !== this._lastNotificationKey) {
            this._lastNotificationKey = key;
            Main.notify(title, body);
        } else if (key === this._lastNotificationKey) {
            this._logAppletEvent("notification-deduped", "skipped", title, { body: body });
        }
    }

    refresh() {
        if (this._stoppedForSession)
            return;
        runBackend(["status", "--json"], (payload) => this._render(payload));
    }

    _restartTimer() {
        if (this._refreshTimer) {
            Mainloop.source_remove(this._refreshTimer);
            this._refreshTimer = 0;
        }
        let interval = Math.max(10, Number(this.refreshInterval) || 30);
        this._refreshTimer = Mainloop.timeout_add_seconds(interval, () => {
            this.refresh();
            return true;
        });
    }

    _runAction(key, args) {
        if (this._inFlight[key]) {
            this._logAppletEvent("action-skipped-in-flight", "skipped", key, { args: args });
            return;
        }
        this._inFlight[key] = true;
        this._logAppletEvent("action-started", "started", key, { args: args });
        this._setAppletIcon("working");
        runBackend(args, (payload) => {
            this._inFlight[key] = false;
            this._render(payload);
            this._logAppletEvent("action-finished", payload.ok ? "ok" : "failed", key, { args: args, error: payload.error || null });
            if (!payload.ok)
                this._notify("Cinnamon Panel Anchor action failed", payload.error || payload.summary);
        });
    }

    _copyDiagnostics() {
        if (this._inFlight["diagnostics"]) {
            this._logAppletEvent("action-skipped-in-flight", "skipped", "diagnostics", {});
            return;
        }
        this._inFlight["diagnostics"] = true;
        runBackend(["diagnose", "--json"], (payload) => {
            this._inFlight["diagnostics"] = false;
            St.Clipboard.get_default().set_text(St.ClipboardType.CLIPBOARD, JSON.stringify(payload, null, 2));
            this._render(payload);
            this._logAppletEvent("diagnostics-copied", payload.ok ? "ok" : "failed", "diagnostics copied", { error: payload.error || null });
        });
    }

    _quitForSession() {
        this._stoppedForSession = true;
        if (this.menu)
            this.menu.close();
        if (this.actor)
            this.actor.hide();
        this._stopTimer();
        this._logAppletEvent("quit-for-session", "ok", "applet hidden for current Cinnamon session", {});
    }

    _disableApplet() {
        runBackend(["disable-applet", "--json"], (payload) => {
            this._logAppletEvent("disable-applet", payload.ok ? "ok" : "failed", "persistent disable requested", {
                error: payload.error || null
            });
            if (payload.ok)
                this._quitForSession();
            else
                this._notify("Cinnamon Panel Anchor action failed", payload.error || payload.summary);
        });
    }

    _stopTimer() {
        if (this._refreshTimer) {
            Mainloop.source_remove(this._refreshTimer);
            this._refreshTimer = 0;
        }
    }

    on_applet_removed_from_panel() {
        this._stopTimer();
        if (this.settings)
            this.settings.finalize();
    }
}

function main(metadata, orientation, panelHeight, instanceId) {
    return new CinnamonPanelAnchorApplet(metadata, orientation, panelHeight, instanceId);
}
