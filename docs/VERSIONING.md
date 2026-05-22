# Versioning

`VERSION` is the source of truth. For v0.2.1, the synchronized surfaces are:

- `pyproject.toml`
- `src/cinnamon_panel_anchor/_version.txt`
- Cinnamon applet `metadata.json`
- checked-in Spices `info.json` and nested applet metadata

Check synchronization with:

```sh
uv run python tools/version_sync.py --check
```

Apply version updates with:

```sh
uv run python tools/version_sync.py --write
```
