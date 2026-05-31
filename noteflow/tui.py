"""
NoteFlow-CLI TUI Dashboard
Terminal User Interface for interactive note management.
"""

import os
import sys
from typing import List, Optional

# Minimal TUI implementation without external dependencies
# Uses ANSI escape codes for terminal control

class Colors:
    """ANSI color codes."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"


class TUIDashboard:
    """
    Terminal User Interface Dashboard for NoteFlow.
    
    A lightweight, zero-dependency TUI using only ANSI escape codes.
    """
    
    def __init__(self, noteflow):
        """
        Initialize TUI Dashboard.
        
        Args:
            noteflow: NoteFlow instance.
        """
        self.nf = noteflow
        self.selected_index = 0
        self.notes: List = []
        self.mode = "list"  # list, search, view
        self.search_query = ""
        self.message = ""
        self.running = True
    
    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def move_cursor(self, row: int, col: int) -> None:
        """Move cursor to specified position."""
        print(f"\033[{row};{col}H", end="")
    
    def hide_cursor(self) -> None:
        """Hide the cursor."""
        print("\033[?25l", end="")
    
    def show_cursor(self) -> None:
        """Show the cursor."""
        print("\033[?25h", end="")
    
    def draw_header(self) -> None:
        """Draw the header."""
        print(f"{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}")
        print("  🧠 NoteFlow-CLI Dashboard".ljust(os.get_terminal_size().columns))
        print(f"{Colors.RESET}")
    
    def draw_footer(self) -> None:
        """Draw the footer with keyboard shortcuts."""
        cols = os.get_terminal_size().columns
        print(f"{Colors.BG_BLACK}{Colors.WHITE}")
        shortcuts = " [q]Quit [n]New [s]Search [Enter]View [/]Search [r]Refresh [?]Help "
        print(shortcuts.ljust(cols))
        print(f"{Colors.RESET}")
    
    def draw_notes_list(self) -> None:
        """Draw the list of notes."""
        self.notes = self.nf.list_notes(limit=20)
        
        print(f"\n{Colors.BOLD}  Notes ({len(self.notes)}):{Colors.RESET}\n")
        
        if not self.notes:
            print(f"  {Colors.DIM}No notes found. Press 'n' to create one.{Colors.RESET}")
            return
        
        for i, note in enumerate(self.notes):
            if i == self.selected_index:
                print(f"{Colors.BG_BLUE}{Colors.WHITE}  → {note}{Colors.RESET}")
            else:
                print(f"    {note}")
    
    def draw_search_mode(self) -> None:
        """Draw search interface."""
        print(f"\n{Colors.BOLD}  Search:{Colors.RESET} ", end="")
        print(f"{Colors.CYAN}{self.search_query}█{Colors.RESET}")
        
        if self.search_query:
            results = self.nf.search(self.search_query, limit=10)
            if results:
                print(f"\n  {Colors.DIM}Results:{Colors.RESET}\n")
                for i, result in enumerate(results):
                    note = result.note
                    if i == self.selected_index:
                        print(f"{Colors.BG_BLUE}{Colors.WHITE}  → {note}{Colors.RESET}")
                    else:
                        print(f"    {note}")
            else:
                print(f"\n  {Colors.DIM}No results found.{Colors.RESET}")
    
    def draw_note_view(self, note) -> None:
        """Draw detailed note view."""
        print(f"\n{Colors.BOLD}{Colors.CYAN}  {note.title}{Colors.RESET}")
        print(f"  {Colors.DIM}{'─' * 50}{Colors.RESET}")
        print(f"  ID: {note.id}")
        print(f"  Status: {note.status.value} | Priority: {note.priority.value}")
        print(f"  Tags: {', '.join(note.tags) if note.tags else 'None'}")
        print(f"  Created: {note.created_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"  Updated: {note.updated_at.strftime('%Y-%m-%d %H:%M')}")
        
        if note.git_branch:
            print(f"  Git: {note.git_branch}" + (f" @ {note.git_commit}" if note.git_commit else ""))
        
        print(f"\n  {Colors.DIM}Content:{Colors.RESET}")
        print(f"  {note.content}\n")
        
        print(f"  {Colors.DIM}[e]Edit [d]Delete [p]Pin [a]Archive [Esc]Back{Colors.RESET}")
    
    def draw_help(self) -> None:
        """Draw help screen."""
        print(f"\n{Colors.BOLD}  Keyboard Shortcuts:{Colors.RESET}\n")
        shortcuts = [
            ("n", "Create new note"),
            ("s", "Search notes"),
            ("/", "Quick search"),
            ("Enter", "View selected note"),
            ("↑/k", "Move up"),
            ("↓/j", "Move down"),
            ("p", "Pin/Unpin note"),
            ("a", "Archive note"),
            ("d", "Delete note"),
            ("r", "Refresh list"),
            ("q", "Quit"),
            ("?", "Show this help"),
        ]
        
        for key, desc in shortcuts:
            print(f"    {Colors.CYAN}{key.ljust(10)}{Colors.RESET} {desc}")
        
        print(f"\n  {Colors.DIM}Press any key to close...{Colors.RESET}")
    
    def draw_message(self) -> None:
        """Draw status message."""
        if self.message:
            print(f"\n  {Colors.GREEN}{self.message}{Colors.RESET}")
            self.message = ""
    
    def render(self) -> None:
        """Render the full TUI."""
        self.clear_screen()
        self.draw_header()
        
        if self.mode == "list":
            self.draw_notes_list()
        elif self.mode == "search":
            self.draw_search_mode()
        elif self.mode == "view" and self.notes:
            self.draw_note_view(self.notes[self.selected_index])
        elif self.mode == "help":
            self.draw_help()
        
        self.draw_message()
        self.draw_footer()
    
    def handle_input(self, key: str) -> None:
        """Handle keyboard input."""
        if self.mode == "list":
            if key == "q":
                self.running = False
            elif key == "n":
                self.create_note_interactive()
            elif key == "s" or key == "/":
                self.mode = "search"
                self.search_query = ""
                self.selected_index = 0
            elif key == "r":
                self.message = "Refreshed!"
            elif key == "?":
                self.mode = "help"
            elif key in ("UP", "k"):
                self.selected_index = max(0, self.selected_index - 1)
            elif key in ("DOWN", "j"):
                self.selected_index = min(len(self.notes) - 1, self.selected_index + 1)
            elif key == "ENTER":
                if self.notes:
                    self.mode = "view"
        
        elif self.mode == "search":
            if key == "ESC":
                self.mode = "list"
                self.selected_index = 0
            elif key == "ENTER":
                if self.notes:
                    self.mode = "view"
            elif key in ("UP", "k"):
                self.selected_index = max(0, self.selected_index - 1)
            elif key in ("DOWN", "j"):
                self.selected_index = min(len(self.notes) - 1, self.selected_index + 1)
            elif key == "BACKSPACE":
                self.search_query = self.search_query[:-1]
            elif len(key) == 1:
                self.search_query += key
        
        elif self.mode == "view":
            if key == "ESC" or key == "q":
                self.mode = "list"
            elif key == "e":
                self.edit_note_interactive()
            elif key == "d":
                self.delete_note_interactive()
            elif key == "p":
                self.toggle_pin()
            elif key == "a":
                self.archive_note()
        
        elif self.mode == "help":
            self.mode = "list"
    
    def create_note_interactive(self) -> None:
        """Interactive note creation."""
        self.show_cursor()
        print(f"\n  {Colors.BOLD}Create New Note{Colors.RESET}")
        
        title = input("  Title: ")
        if not title:
            self.message = "Cancelled."
            self.hide_cursor()
            return
        
        print("  Content (Ctrl+D to finish):")
        lines = []
        try:
            while True:
                line = input("  ")
                lines.append(line)
        except EOFError:
            pass
        
        content = "\n".join(lines)
        tags_input = input("  Tags (comma-separated): ")
        tags = [t.strip() for t in tags_input.split(",") if t.strip()]
        
        note = self.nf.create_note(title=title, content=content, tags=tags)
        self.message = f"Created note: {note.id}"
        self.hide_cursor()
    
    def edit_note_interactive(self) -> None:
        """Interactive note editing."""
        if not self.notes:
            return
        
        note = self.notes[self.selected_index]
        self.show_cursor()
        
        print(f"\n  {Colors.BOLD}Edit Note: {note.id}{Colors.RESET}")
        
        new_title = input(f"  Title [{note.title}]: ")
        if new_title:
            note.title = new_title
        
        print(f"  Content (current: {note.preview})")
        new_content = input("  New content: ")
        if new_content:
            note.content = new_content
        
        tags_input = input(f"  Tags [{', '.join(note.tags)}]: ")
        if tags_input:
            note.tags = [t.strip() for t in tags_input.split(",") if t.strip()]
        
        self.nf.update_note(note.id, title=note.title, content=note.content, tags=note.tags)
        self.message = "Note updated!"
        self.hide_cursor()
    
    def delete_note_interactive(self) -> None:
        """Interactive note deletion."""
        if not self.notes:
            return
        
        note = self.notes[self.selected_index]
        self.show_cursor()
        
        confirm = input(f"\n  Delete '{note.title}'? [y/N]: ")
        if confirm.lower() == "y":
            self.nf.delete_note(note.id)
            self.message = "Note deleted!"
            self.mode = "list"
            self.selected_index = max(0, self.selected_index - 1)
        
        self.hide_cursor()
    
    def toggle_pin(self) -> None:
        """Toggle pin status of selected note."""
        if not self.notes:
            return
        
        note = self.notes[self.selected_index]
        if note.is_pinned:
            self.nf.unpin_note(note.id)
            self.message = "Note unpinned!"
        else:
            self.nf.pin_note(note.id)
            self.message = "Note pinned!"
    
    def archive_note(self) -> None:
        """Archive selected note."""
        if not self.notes:
            return
        
        note = self.notes[self.selected_index]
        self.nf.archive_note(note.id)
        self.message = "Note archived!"
        self.mode = "list"
    
    def run(self) -> None:
        """Run the TUI dashboard."""
        self.hide_cursor()
        
        try:
            # Set terminal to raw mode for single keypress
            import tty
            import termios
            old_settings = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
            
            while self.running:
                self.render()
                
                # Read single keypress
                key = sys.stdin.read(1)
                
                # Handle special keys
                if key == "\x1b":  # Escape sequence
                    next1 = sys.stdin.read(1)
                    if next1 == "[":
                        next2 = sys.stdin.read(1)
                        if next2 == "A":
                            key = "UP"
                        elif next2 == "B":
                            key = "DOWN"
                    else:
                        key = "ESC"
                elif key == "\r" or key == "\n":
                    key = "ENTER"
                elif key == "\x7f" or key == "\x08":
                    key = "BACKSPACE"
                elif key == "\x04":  # Ctrl+D
                    key = "q"
                
                self.handle_input(key)
            
            # Restore terminal settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        
        except ImportError:
            # Fallback for Windows
            import msvcrt
            while self.running:
                self.render()
                key = msvcrt.getch()
                if key == b"\x1b":
                    key = "ESC"
                elif key == b"\r":
                    key = "ENTER"
                elif key == b"\x08":
                    key = "BACKSPACE"
                else:
                    key = key.decode("utf-8", errors="ignore")
                self.handle_input(key)
        
        finally:
            self.show_cursor()
            self.clear_screen()
            print(f"{Colors.GREEN}Thanks for using NoteFlow! 👋{Colors.RESET}\n")


def run_dashboard(noteflow) -> None:
    """
    Run the TUI dashboard.
    
    Args:
        noteflow: NoteFlow instance.
    """
    dashboard = TUIDashboard(noteflow)
    dashboard.run()
