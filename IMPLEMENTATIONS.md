# Implementations

Tools that write or read VIDEO.md packages. To add yours, open a pull request with a line in the right table; a tool that writes packages should pass `videomd check` on its output.

## Producers (write packages)

| Tool | Notes |
|---|---|
| [rea-video](https://github.com/JuneYaooo/rea-video) | Shot-level breakdown: production method per shot, real material, sound, packaging, remake plan. `rea-video decompose` writes a package; `rea-video videomd DIR --check` checks one. |

## Consumers (read packages)

| Tool | Notes |
|---|---|
| [videomd](src/videomd/) (this repository) | Reference reader and validator: `videomd check`, `videomd read`. |
