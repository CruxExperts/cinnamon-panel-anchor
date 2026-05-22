# UI Design Patterns

This page preserves the UI direction for the Cinnamon Panel Anchor applet redesign. It is a design reference for future applet work, not a user-facing workflow guide.

## Current Problem

The current popup behaves like a flat command menu. It exposes several actions at the same level, uses command names that are easy to misread without context, and shows state mostly as raw counts or backend text. Some actions are only valid in specific states, but the menu does not explain why. The icon choices also mix generic status symbols with the product metaphor, which makes the panel state harder to scan.

## Chosen Direction

Use a guided status popup. The first visible content should explain the current anchor state, then offer the one best next action for that state. Secondary actions remain available, but grouped below the primary action so the user does not have to interpret a command list while troubleshooting a panel placement issue.

The visual metaphor is a panel-anchor glyph: a small panel edge joined to an anchor point. Use that metaphor for applet identity and for custom state icons only when standard symbolic icons cannot express the state clearly.

Invalid actions should stay visible but disabled. A disabled restore action with a short reason is clearer than hiding restore when no anchors exist, because it teaches what must happen next.

## Interaction Patterns

- Show one clear status header: protected, working, needs attention, or error.
- Present one primary next action based on the current state.
- Group secondary actions after the primary action: refresh, capture, restore, keep current move, display settings, diagnostics, and applet settings.
- Add short action hints where command names need context.
- Keep invalid actions visible and disable them with a reason.
- Prefer direct state text over raw backend terms in the popup. Raw details belong in diagnostics.

## Icon Rules

- Use simple symbolic icons for popup actions and panel state.
- Prefer recognizable Cinnamon, XApp, GNOME, or freedesktop-style glyphs before creating custom artwork.
- Use the custom panel-anchor glyph for applet identity and anchor-specific states that theme icons cannot communicate.
- Keep custom symbolic icons monochrome, simple, and legible at panel size.
- Do not rely on an icon alone when the command is not widely recognized.

## Notification Rules

- Notifications are attention-only: restored drift, missing connector fallback, manual-move decision needed, or backend failure.
- Deduplicate repeated notifications so the same state does not keep interrupting the user.
- Keep notifications user-disableable through applet settings.
- Never make a notification the only source of state. The popup must independently show the same actionable condition.
- Notification actions, if added later, must mirror actions available from the popup.

## Cinnamon Implementation Notes

- Build popup rows with Cinnamon menu primitives such as `PopupBaseMenuItem` and `PopupIconMenuItem` when custom row layout or action icons are needed.
- Use `setSensitive()` for invalid-but-visible actions.
- Store user-facing preferences in `settings-schema.json`.
- Bind applet settings with `Settings.AppletSettings`.
- Use `set_applet_icon_symbolic_path()` for custom symbolic state icons when theme icons are insufficient.
- Keep the applet as the resident UI/controller. The CLI remains backend, installer, diagnostics, and packaging support tooling.

## Source References

- [GNOME HIG: UI Icons](https://developer.gnome.org/hig/guidelines/ui-icons.html)
- [GNOME HIG: Buttons](https://developer.gnome.org/hig/patterns/controls/buttons.html)
- [GNOME HIG: Notifications](https://developer.gnome.org/hig/patterns/feedback/notifications.html)
- [Linux Mint Cinnamon tutorials: Applet, desklet and extension settings](https://projects.linuxmint.com/reference/git/cinnamon-tutorials/xlet-settings.html)
- [Linux Mint Cinnamon tutorials: Writing applets](https://projects.linuxmint.com/reference/git/cinnamon-tutorials/write-applet.html)
