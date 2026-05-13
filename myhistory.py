import os
import argparse
import sys
import subprocess
import sqlite3
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich import box

def get_history_from_sqlite(db_path):
    if not os.path.exists(db_path):
        return []
    
    items = []
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()
        # xonsh_history schema: inp, rtn, tsb, tse, sessionid, out, info, frequency, cwd
        cursor.execute("SELECT inp, tsb, cwd, rtn FROM xonsh_history ORDER BY tsb DESC")
        for row in cursor.fetchall():
            items.append({
                'inp': row[0],
                'ts': row[1],
                'cwd': row[2],
                'rtn': row[3]
            })
        conn.close()
    except Exception as e:
        # Fallback for errors
        return []
    return items

def get_history_items(history_file=None):
    if not history_file:
        # Default xonsh sqlite path on macOS
        history_file = os.path.expanduser("~/.local/share/xonsh/xonsh-history.sqlite")
    
    items = get_history_from_sqlite(history_file)
    return items

def format_ts(ts):
    try:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
    except:
        return str(ts)

def copy_to_clipboard(text):
    try:
        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
        process.communicate(input=text.encode('utf-8'))
    except Exception as e:
        print(f"Error copying to clipboard: {e}")

def main():
    parser = argparse.ArgumentParser(description="Search xonsh history and copy to clipboard.")
    parser.add_argument('search_terms', nargs='*', help="Words to search in history")
    parser.add_argument('--history-file', '-f', help="Path to xonsh-history.sqlite file")
    
    args = parser.parse_args()
    
    search_query = " ".join(args.search_terms).lower() if args.search_terms else ""

    all_items = get_history_items(args.history_file)
    
    # Mock data if no history found (for development/testing)
    if not all_items:
        all_items = [
            {'inp': 'jrnl-cli sum-up-tasks --help', 'ts': 1770977055.385808, 'rtn': 0, 'frequency': 1, 'cwd': '/Users/edo/tmp/tmp_20260213_1039_tasks_outputs'},
            {'inp': 'ls -la', 'ts': 1770977100.0, 'rtn': 0, 'frequency': 1, 'cwd': '/Users/edo/git/my/myhistory'},
            {'inp': 'git status', 'ts': 1770977200.0, 'rtn': 0, 'frequency': 1, 'cwd': '/Users/edo/git/my/myhistory'},
            {'inp': 'python3 myhistory.py test', 'ts': 1770977300.0, 'rtn': 0, 'frequency': 1, 'cwd': '/Users/edo/git/my/myhistory'},
        ]
    
    filtered_items = []
    for item in all_items:
        if search_query in item.get('inp', '').lower():
            filtered_items.append(item)

    if not filtered_items:
        print(f"No history items found matching: {search_query}")
        return

    # Interactive selection using Rich
    console = Console(highlight=False)
    selected_index = 0
    
    import tty
    import termios

    def get_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == '\x1b': # ESC
                ch = sys.stdin.read(2)
                return ch
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def generate_table(selected_idx):
        table = Table(box=box.SIMPLE, expand=True, show_header=True, header_style="bold magenta")
        table.add_column("TS", width=16, no_wrap=True, overflow="ellipsis")
        table.add_column("Command", overflow="ellipsis", no_wrap=True)

        # Show a window of items if there are many
        max_rows = console.height - 5
        start_idx = max(0, selected_idx - max_rows // 2)
        end_idx = min(len(filtered_items), start_idx + max_rows)
        
        for i in range(start_idx, end_idx):
            item = filtered_items[i]
            style = "reverse" if i == selected_idx else ""
            table.add_row(
                format_ts(item.get('ts')),
                item.get('inp', ''),
                style=style
            )
        return table

    with Live(generate_table(selected_index), console=console, screen=False, auto_refresh=False, vertical_overflow="crop") as live:
        while True:
            live.update(generate_table(selected_index), refresh=True)
            key = get_key()
            
            if key == '[A': # Up
                selected_index = max(0, selected_index - 1)
            elif key == '[B': # Down
                selected_index = min(len(filtered_items) - 1, selected_index + 1)
            elif key in ('\r', '\n'): # Enter
                selected_command = filtered_items[selected_index].get('inp', '')
                copy_to_clipboard(selected_command)
                break
            elif key in ('q', '\x03'): # q or Ctrl-C
                break

if __name__ == "__main__":
    main()
