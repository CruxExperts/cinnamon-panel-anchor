from __future__ import annotations


def ask_keep_or_restore(message: str) -> str | None:
    try:
        import gi  # type: ignore

        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk  # type: ignore
    except (ImportError, ValueError):
        return None

    dialog = Gtk.MessageDialog(
        message_type=Gtk.MessageType.QUESTION,
        buttons=Gtk.ButtonsType.NONE,
        text=message,
    )
    dialog.add_button("Keep", 1)
    dialog.add_button("Restore", 2)
    try:
        response = dialog.run()
    finally:
        dialog.destroy()
    if response == 1:
        return "keep"
    if response == 2:
        return "restore"
    return None
