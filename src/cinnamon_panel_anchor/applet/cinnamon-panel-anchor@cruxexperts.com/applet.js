const Applet = imports.ui.applet;
const PopupMenu = imports.ui.popupMenu;
const Main = imports.ui.main;
const Mainloop = imports.mainloop;
const Settings = imports.ui.settings;
const Util = imports.misc.util;
const GLib = imports.gi.GLib;
const St = imports.gi.St;

const UUID = "cinnamon-panel-anchor@cruxexperts.com";
const APPLET_PATH = imports.ui.appletManager.appletMeta[UUID].path;

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
                    error: String(e)
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
            error: String(e)
        });
    }
}

class CinnamonPanelAnchorApplet extends Applet.TextIconApplet {
    constructor(metadata, orientation, panelHeight, instanceId) {
        super(orientation, panelHeight, instanceId);
        this.refreshInterval = 30;
        this.showNotifications = true;
        this._refreshTimer = 0;
        this._lastNotificationKey = null;
        this.setAllowedLayout(Applet.AllowedLayout.BOTH);
        this.set_applet_icon_symbolic_name("anchor");
        this.set_applet_label("");
        this.set_applet_tooltip("Cinnamon Panel Anchor");
        this._applet_context_menu.addAction("Open Applet Settings", () => this.configureApplet());

        this.menuManager = new PopupMenu.PopupMenuManager(this);
        this.menu = new Applet.AppletPopupMenu(this, orientation);
        this.menuManager.addMenu(this.menu);
        this._statusItems = [];
        this.settings = new Settings.AppletSettings(this, metadata.uuid, instanceId);
        this.settings.bind("refresh-interval", "refreshInterval", () => this._restartTimer());
        this.settings.bind("show-notifications", "showNotifications", null);
        this._buildMenu();
        this.refresh();
        this._restartTimer();
    }

    _buildMenu() {
        this.menu.removeAll();
        this._summary = new PopupMenu.PopupMenuItem("Loading panel anchor status...", { reactive: false });
        this.menu.addMenuItem(this._summary);
        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());

        this._statusBox = new PopupMenu.PopupMenuSection();
        this.menu.addMenuItem(this._statusBox);

        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
        this.menu.addAction("Refresh", () => this.refresh());
        this.menu.addAction("Capture Current Layout", () => this._runAction(["capture", "--json"]));
        this.menu.addAction("Restore Saved Anchors", () => this._runAction(["restore", "--json"]));
        this.menu.addAction("Keep Current Move", () => this._runAction(["capture", "--json"]));
        this.menu.addAction("Open Cinnamon Display Settings", () => Util.spawn(["cinnamon-settings", "display"]));
        this.menu.addAction("Copy Diagnostics", () => this._copyDiagnostics());
        this.menu.addAction("Open Applet Settings", () => this.configureApplet());
    }

    on_applet_clicked() {
        this.menu.toggle();
        this.refresh();
    }

    _setState(payload) {
        let icon = "emblem-ok-symbolic";
        if (!payload.ok || payload.severity === "error")
            icon = "dialog-error-symbolic";
        else if (payload.pending_decision || payload.severity === "attention")
            icon = "dialog-warning-symbolic";
        else if (payload.plan && payload.plan.changed)
            icon = "view-refresh-symbolic";
        this.set_applet_icon_symbolic_name(icon);
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
        this._statusLine("Diagnostics", payload.error || "No backend errors reported");
        if (payload.messages) {
            payload.messages.slice(0, 4).forEach((message) => this._statusLine("Message", message));
        }
        if (payload.pending_decision) {
            this._notify("Panel move decision needed", "Open the applet to keep the move or restore saved anchors.");
        } else if (!payload.ok) {
            this._notify("Cinnamon Panel Anchor needs attention", payload.error || payload.summary);
        }
    }

    _notify(title, body) {
        let key = title + ":" + body;
        if (this.showNotifications && Main.messageTray && key !== this._lastNotificationKey) {
            this._lastNotificationKey = key;
            Main.notify(title, body);
        }
    }

    refresh() {
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

    _runAction(args) {
        this.set_applet_icon_symbolic_name("view-refresh-symbolic");
        runBackend(args, (payload) => {
            this._render(payload);
            if (!payload.ok)
                this._notify("Cinnamon Panel Anchor action failed", payload.error || payload.summary);
        });
    }

    _copyDiagnostics() {
        runBackend(["diagnose", "--json"], (payload) => {
            St.Clipboard.get_default().set_text(St.ClipboardType.CLIPBOARD, JSON.stringify(payload, null, 2));
            this._render(payload);
        });
    }

    on_applet_removed_from_panel() {
        if (this._refreshTimer) {
            Mainloop.source_remove(this._refreshTimer);
            this._refreshTimer = 0;
        }
        if (this.settings)
            this.settings.finalize();
    }
}

function main(metadata, orientation, panelHeight, instanceId) {
    return new CinnamonPanelAnchorApplet(metadata, orientation, panelHeight, instanceId);
}
