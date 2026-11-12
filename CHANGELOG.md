# Changelog

## Version 1, draft 2

Package `videomd` 1.1.0.

- **Smaller required core.** A card needs `videomd`, `name`, `description`, `source`, `shots` and `lang`. `made_mix` is optional; in shot files only `shot`, `time` and `tokens` are required, and `inferred` is optional.
- **Identity.** `source.sha256` (hash of the whole file) and `source.url`. `source` needs `duration` and at least one of `file` or `url`.
- **`name`** is lowercase letters, digits and hyphens, at most 64 characters. **`description`** may be up to 1024 characters and should say what the video is about before how it was made.
- **The map is a `videomd-map` block**, `path | tokens | about`, instead of a Markdown table. Paths may be directories or glob patterns. Every topic file must be in the map.
- **Timeline keys renamed**: `say` → `story`, `cam` → `camera`, `over` → `overlay`, `real~` → `material~`. `made~` no longer carries an id in parentheses: timeline values are prose, ids live in shot files.
- **New conformance rules**: every shot file has a timeline line, and its file name matches its `shot`.
- `frames` may use names other than `sheet`, `first`, `last`.
- New guides: [docs/integrate.md](docs/integrate.md) and [docs/authoring.md](docs/authoring.md).

## Version 1, draft 1

Package `videomd` 1.0.0. First published version.
