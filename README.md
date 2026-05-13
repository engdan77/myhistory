# myhistory

`myhistory` is a small CLI tool designed for `xonsh` shell users to quickly search through their command history, select a command using an interactive interface, and copy it directly to the macOS clipboard.

## Features

- **Direct SQLite Access**: Reads `xonsh` history directly from the `xonsh-history.sqlite` database, making it fast and independent of a running `xonsh` session.
- **Interactive Search**: Filter your history by providing search terms.
- **Rich UI**: Uses the `rich` library to provide a clean, selectable list of commands with timestamps.
- **macOS Integration**: Automatically copies the selected command to the clipboard using `pbcopy`.
- **Automatic Truncation**: Handles long commands gracefully by truncating them with an ellipsis to fit your terminal width.

## Installation

This tool requires Python 3.14 or later and the `rich` library.

If you are using `uv`:

```bash
uv tool install .
```

Or using `pip`:

```bash
pip install .
```

## Usage

Simply run `myhistory` followed by any keywords you want to search for:

```bash
myhistory git commit
```

If no search terms are provided, it will show the most recent history items.

### Arguments

- `search_terms`: Optional words to filter the history.
- `-f`, `--history-file`: Manually specify the path to the `xonsh-history.sqlite` file. By default, it looks in `~/.local/share/xonsh/xonsh-history.sqlite`.

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Up Arrow` | Move selection up |
| `Down Arrow` | Move selection down |
| `Enter` | Copy selected command to clipboard and exit |
| `q` or `Ctrl+C` | Exit without copying |

## Requirements

- macOS (for `pbcopy` support)
- `xonsh` (as the source of history)
- `rich` library
