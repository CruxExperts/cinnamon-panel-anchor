const Applet = imports.ui.applet;
const PopupMenu = imports.ui.popupMenu;
const Main = imports.ui.main;
const Mainloop = imports.mainloop;
const Settings = imports.ui.settings;
const Util = imports.misc.util;
const GLib = imports.gi.GLib;
const St = imports.gi.St;

const UUID = "cinnamon-panel-anchor@cruxexperts.com";
const VERSION = "0.2.1";
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
        this.legacyAutostartWatcher = false;
        this.debugLogging = true;
        this._refreshTimer = 0;
        this._lastNotificationKey = null;
        this._inFlight = {};
        this._stoppedForSession = false;
        this.setAllowedLayout(Applet.AllowedLayout.BOTH);
        this._setAppletIcon("brand");
        this.set_applet_label("");
        this.set_applet_tooltip("Cinnamon Panel Anchor " + VERSION);
        this._applet_context_menu.addAction("Open Applet Settings", () => this.configureApplet());

        this.menuManager = new PopupMenu.PopupMenuManager(this);
        this.menu = new Applet.AppletPopupMenu(this, orientation);
        this.menuManager.addMenu(this.menu);
        this._statusItems = [];
        this.settings = new Settings.AppletSettings(this, metadata.uuid, instanceId);
        this.settings.bind("refresh-interval", "refreshInterval", () => this._restartTimer());
        this.settings.bind("show-notifications", "showNotifications", null);
        this.settings.bind("restore-automatically", "restoreAutomatically", null);
        this.settings.bind("legacy-autostart-watcher", "legacyAutostartWatcher", () => this._applyLegacyAutostartSetting());
        this.settings.bind("debug-logging", "debugLogging", null);
        this._guardDuplicateInstance();
        this._buildMenu();
        this.refresh();
        this._refreshAutostartStatus();
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

    _buildMenu() {
        this.menu.removeAll();
        this._summary = new PopupMenu.PopupMenuItem("Loading panel anchor status...", { reactive: false });
        this.menu.addMenuItem(this._summary);
        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());

        this._statusBox = new PopupMenu.PopupMenuSection();
        this.menu.addMenuItem(this._statusBox);

        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
        this._version = new PopupMenu.PopupMenuItem("Version " + VERSION, { reactive: false });
        this.menu.addMenuItem(this._version);
        this._autostart = new PopupMenu.PopupMenuItem("Legacy autostart watcher: checking...", { reactive: false });
        this.menu.addMenuItem(this._autostart);
        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
        this.menu.addAction("Refresh", () => this.refresh());
        this.menu.addAction("Capture Current Layout", () => this._runAction("capture", ["capture", "--json"]));
        this.menu.addAction("Restore Saved Anchors", () => this._runAction("restore", ["restore", "--json"]));
        this.menu.addAction("Keep Current Move", () => this._runAction("keep-current", ["capture", "--json"]));
        this.menu.addAction("Open Cinnamon Display Settings", () => Util.spawn(["cinnamon-settings", "display"]));
        this.menu.addAction("Copy Diagnostics", () => this._copyDiagnostics());
        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
        this.menu.addAction("Quit for Session", () => this._quitForSession());
        this.menu.addAction("Disable Applet", () => this._disableApplet());
        this.menu.addAction("Open Applet Settings", () => this.configureApplet());
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

    _statusLine(label, value) {
        let item = new PopupMenu.PopupMenuItem(label + ": " + value, { reactive: false });
        this._statusBox.addMenuItem(item);
    }

    _render(payload) {
        this._setState(payload);
        this._summary.label.text = payload.summary || "Status unavailable";
        this._statusBox.removeAll();
        this._statusLine("Health", payload.ok ? "Protected" : "Needs attention");
        this._statusLine("Saved anchors", String((payload.anchors || []).length));
        this._statusLine("Current monitors", String((payload.monitors || []).length));
        this._statusLine("Current panel entries", String((payload.panels || []).length));
        this._statusLine("Pending decisions", payload.pending_decision ? "1" : "0");
        this._statusLine("Version", payload.version || VERSION);
        this._statusLine("Diagnostics", payload.error || "No backend errors reported");
        if (payload.messages) {
            payload.messages.slice(0, 4).forEach((message) => this._statusLine("Message", message));
        }
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
        this._refreshAutostartStatus();
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

    _refreshAutostartStatus() {
        runBackend(["autostart-status", "--json"], (payload) => {
            if (this._autostart)
                this._autostart.label.text = "Legacy autostart watcher: " + (payload.installed ? "on" : "off");
        });
    }

    _applyLegacyAutostartSetting() {
        let args = this.legacyAutostartWatcher ? ["install-autostart", "--json"] : ["uninstall-autostart", "--json"];
        runBackend(args, (payload) => {
            this._refreshAutostartStatus();
            this._logAppletEvent("legacy-autostart-toggle", payload.ok ? "ok" : "failed", this.legacyAutostartWatcher ? "on" : "off", {
                error: payload.error || null
            });
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
