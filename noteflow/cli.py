#!/usr/bin/env python3
"""
NoteFlow-CLI - Command Line Interface
Main entry point for the NoteFlow CLI application.
"""

import argparse
import sys
from datetime import datetime
from typing import List, Optional

from noteflow import __version__
from noteflow.core import NoteFlow
from noteflow.models import NotePriority, NoteStatus


def print_success(msg: str) -> None:
    """Print success message."""
    print(f"\033[92m✓\033[0m {msg}")


def print_error(msg: str) -> None:
    """Print error message."""
    print(f"\033[91m✗\033[0m {msg}", file=sys.stderr)


def print_info(msg: str) -> None:
    """Print info message."""
    print(f"\033[94mℹ\033[0m {msg}")


def print_note(note, show_content: bool = False) -> None:
    """Print note details."""
    status_icons = {
        NoteStatus.DRAFT: "📝",
        NoteStatus.PUBLISHED: "✅",
        NoteStatus.ARCHIVED: "📦",
        NoteStatus.DELETED: "🗑️"
    }
    priority_colors = {
        NotePriority.LOW: "\033[90m",
        NotePriority.MEDIUM: "\033[94m",
        NotePriority.HIGH: "\033[93m",
        NotePriority.CRITICAL: "\033[91m"
    }
    
    icon = status_icons.get(note.status, "📝")
    pin = "📌 " if note.is_pinned else ""
    priority = f"{priority_colors.get(note.priority, '')}[{note.priority.value.upper()}]\033[0m "
    
    print(f"\n{pin}{icon} \033[1m{note.title}\033[0m")
    print(f"   ID: {note.id}")
    print(f"   Status: {note.status.value} | Priority: {note.priority.value}")
    print(f"   Tags: {', '.join(note.tags) if note.tags else 'None'}")
    print(f"   Created: {note.created_at.strftime('%Y-%m-%d %H:%M')}")
    print(f"   Updated: {note.updated_at.strftime('%Y-%m-%d %H:%M')}")
    
    if note.git_branch:
        print(f"   Git: {note.git_branch}" + (f" @ {note.git_commit}" if note.git_commit else ""))
    
    if show_content and note.content:
        print(f"\n   {note.content}\n")
    else:
        print(f"   Preview: {note.preview}")


def cmd_new(args: argparse.Namespace) -> int:
    """Create a new note."""
    nf = NoteFlow()
    
    # Read content from stdin or argument
    content = args.content or ""
    if args.stdin:
        content = sys.stdin.read()
    elif args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            print_error(f"File not found: {args.file}")
            return 1
    
    # Parse tags
    tags = args.tags.split(",") if args.tags else []
    
    # Parse status
    status = NoteStatus.DRAFT
    if args.published:
        status = NoteStatus.PUBLISHED
    
    # Parse priority
    priority = NotePriority.MEDIUM
    if args.priority:
        priority = NotePriority(args.priority.lower())
    
    note = nf.create_note(
        title=args.title,
        content=content,
        tags=tags,
        status=status,
        priority=priority,
        category_id=args.category
    )
    
    print_success(f"Created note: {note.id}")
    print_note(note)
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    """List notes."""
    nf = NoteFlow()
    
    # Parse filters
    status = NoteStatus(args.status) if args.status else None
    tags = args.tags.split(",") if args.tags else []
    
    notes = nf.list_notes(
        status=status,
        category_id=args.category,
        tags=tags,
        pinned_only=args.pinned,
        limit=args.limit
    )
    
    if not notes:
        print_info("No notes found.")
        return 0
    
    print(f"\n\033[1mNotes ({len(notes)}):\033[0m\n")
    
    for note in notes:
        print(f"  {note}")
    
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    """Show note details."""
    nf = NoteFlow()
    
    note = nf.get_note(args.note_id)
    if not note:
        print_error(f"Note not found: {args.note_id}")
        return 1
    
    print_note(note, show_content=not args.brief)
    return 0


def cmd_edit(args: argparse.Namespace) -> int:
    """Edit a note."""
    nf = NoteFlow()
    
    note = nf.get_note(args.note_id)
    if not note:
        print_error(f"Note not found: {args.note_id}")
        return 1
    
    updates = {}
    
    if args.title:
        updates["title"] = args.title
    if args.content:
        updates["content"] = args.content
    if args.tags:
        updates["tags"] = args.tags.split(",")
    if args.status:
        updates["status"] = NoteStatus(args.status.lower())
    if args.priority:
        updates["priority"] = NotePriority(args.priority.lower())
    if args.category is not None:
        updates["category_id"] = args.category
    
    if not updates:
        print_error("No updates specified.")
        return 1
    
    note = nf.update_note(args.note_id, **updates)
    print_success(f"Updated note: {note.id}")
    print_note(note)
    return 0


def cmd_delete(args: argparse.Namespace) -> int:
    """Delete a note."""
    nf = NoteFlow()
    
    if not args.force:
        note = nf.get_note(args.note_id)
        if not note:
            print_error(f"Note not found: {args.note_id}")
            return 1
        
        print_note(note)
        confirm = input("\nDelete this note? [y/N]: ")
        if confirm.lower() != "y":
            print_info("Cancelled.")
            return 0
    
    if nf.delete_note(args.note_id):
        print_success(f"Deleted note: {args.note_id}")
        return 0
    else:
        print_error(f"Failed to delete note: {args.note_id}")
        return 1


def cmd_search(args: argparse.Namespace) -> int:
    """Search notes."""
    nf = NoteFlow()
    
    tags = args.tags.split(",") if args.tags else []
    status = NoteStatus(args.status) if args.status else None
    
    results = nf.search(
        query=args.query,
        status=status,
        tags=tags,
        category_id=args.category,
        limit=args.limit
    )
    
    if not results:
        print_info("No matching notes found.")
        return 0
    
    print(f"\n\033[1mSearch Results ({len(results)}):\033[0m\n")
    
    for result in results:
        note = result.note
        score = f" [{result.score:.2f}]" if result.score > 0 else ""
        print(f"  {note}{score}")
        
        if result.highlights.get("content"):
            for highlight in result.highlights["content"][:2]:
                print(f"    → {highlight}")
    
    return 0


def cmd_pin(args: argparse.Namespace) -> int:
    """Pin or unpin a note."""
    nf = NoteFlow()
    
    if args.unpin:
        note = nf.unpin_note(args.note_id)
        if note:
            print_success(f"Unpinned note: {note.id}")
            return 0
    else:
        note = nf.pin_note(args.note_id)
        if note:
            print_success(f"Pinned note: {note.id}")
            return 0
    
    print_error(f"Note not found: {args.note_id}")
    return 1


def cmd_archive(args: argparse.Namespace) -> int:
    """Archive or restore a note."""
    nf = NoteFlow()
    
    if args.restore:
        note = nf.restore_note(args.note_id)
        if note:
            print_success(f"Restored note: {note.id}")
            return 0
    else:
        note = nf.archive_note(args.note_id)
        if note:
            print_success(f"Archived note: {note.id}")
            return 0
    
    print_error(f"Note not found: {args.note_id}")
    return 1


def cmd_category(args: argparse.Namespace) -> int:
    """Manage categories."""
    nf = NoteFlow()
    
    if args.list:
        categories = nf.list_categories()
        if not categories:
            print_info("No categories found.")
            return 0
        
        print("\n\033[1mCategories:\033[0m\n")
        for cat in categories:
            notes_count = len(nf.storage.get_notes_by_category(cat.id))
            print(f"  {cat.icon} {cat.name} ({notes_count} notes)")
        return 0
    
    if args.create:
        category = nf.create_category(
            name=args.create,
            description=args.description or "",
            icon=args.icon or "📁"
        )
        print_success(f"Created category: {category.id} - {category.name}")
        return 0
    
    if args.delete:
        if nf.delete_category(args.delete):
            print_success(f"Deleted category: {args.delete}")
            return 0
        else:
            print_error(f"Category not found: {args.delete}")
            return 1
    
    print_error("Specify --list, --create, or --delete")
    return 1


def cmd_tag(args: argparse.Namespace) -> int:
    """Manage tags."""
    nf = NoteFlow()
    
    if args.list:
        tags = nf.list_tags()
        if not tags:
            print_info("No tags found.")
            return 0
        
        print("\n\033[1mTags:\033[0m\n")
        for tag in tags:
            notes_count = len(nf.storage.get_notes_by_tag(tag.name))
            print(f"  #{tag.name} ({notes_count} notes)")
        return 0
    
    if args.delete:
        if nf.delete_tag(args.delete):
            print_success(f"Deleted tag: #{args.delete}")
            return 0
        else:
            print_error(f"Tag not found: #{args.delete}")
            return 1
    
    print_error("Specify --list or --delete")
    return 1


def cmd_export(args: argparse.Namespace) -> int:
    """Export notes."""
    nf = NoteFlow()
    
    if args.format == "json":
        count = nf.export_json(args.output)
        print_success(f"Exported {count} notes to {args.output}")
    else:
        count = nf.export_markdown(args.output)
        print_success(f"Exported {count} notes to {args.output}/")
    
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    """Import notes."""
    nf = NoteFlow()
    
    count = nf.import_json(args.file)
    print_success(f"Imported {count} notes from {args.file}")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    """Show statistics."""
    nf = NoteFlow()
    stats = nf.get_stats()
    
    print("\n\033[1m📊 NoteFlow Statistics\033[0m\n")
    print(f"  Total Notes: {stats['total_notes']}")
    print(f"  Total Categories: {stats['total_categories']}")
    print(f"  Total Tags: {stats['total_tags']}")
    print(f"  Pinned Notes: {stats['pinned_notes']}")
    print(f"  Total Words: {stats['total_words']:,}")
    print(f"  Total Characters: {stats['total_chars']:,}")
    print(f"\n  Status Distribution:")
    for status, count in stats['status_distribution'].items():
        print(f"    • {status}: {count}")
    print(f"\n  Storage: {stats['storage_path']}")
    
    return 0


def cmd_quick(args: argparse.Namespace) -> int:
    """Create a quick note."""
    nf = NoteFlow()
    
    content = args.content or sys.stdin.read()
    tags = args.tags.split(",") if args.tags else []
    
    note = nf.quick_note(content, tags)
    print_success(f"Created quick note: {note.id}")
    print_note(note)
    return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="noteflow",
        description="🧠 NoteFlow-CLI - Lightweight Terminal Intelligent Note & Knowledge Management Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  noteflow new "My Note" -c "Note content here"
  noteflow list --status draft
  noteflow search "important" --tags work,urgent
  noteflow show abc123
  noteflow quick "Quick thought to save"
"""
    )
    
    parser.add_argument("--version", "-v", action="version", version=f"%(prog)s {__version__}")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # new command
    p_new = subparsers.add_parser("new", aliases=["create"], help="Create a new note")
    p_new.add_argument("title", help="Note title")
    p_new.add_argument("--content", "-c", help="Note content")
    p_new.add_argument("--file", "-f", help="Read content from file")
    p_new.add_argument("--stdin", action="store_true", help="Read content from stdin")
    p_new.add_argument("--tags", "-t", help="Comma-separated tags")
    p_new.add_argument("--category", "-C", help="Category ID")
    p_new.add_argument("--published", "-p", action="store_true", help="Mark as published")
    p_new.add_argument("--priority", choices=["low", "medium", "high", "critical"], help="Priority level")
    p_new.set_defaults(func=cmd_new)
    
    # list command
    p_list = subparsers.add_parser("list", aliases=["ls"], help="List notes")
    p_list.add_argument("--status", "-s", choices=["draft", "published", "archived"], help="Filter by status")
    p_list.add_argument("--tags", "-t", help="Filter by tags (comma-separated)")
    p_list.add_argument("--category", "-C", help="Filter by category")
    p_list.add_argument("--pinned", action="store_true", help="Show only pinned notes")
    p_list.add_argument("--limit", "-n", type=int, default=50, help="Maximum notes to show")
    p_list.set_defaults(func=cmd_list)
    
    # show command
    p_show = subparsers.add_parser("show", help="Show note details")
    p_show.add_argument("note_id", help="Note ID")
    p_show.add_argument("--brief", "-b", action="store_true", help="Brief output")
    p_show.set_defaults(func=cmd_show)
    
    # edit command
    p_edit = subparsers.add_parser("edit", help="Edit a note")
    p_edit.add_argument("note_id", help="Note ID")
    p_edit.add_argument("--title", "-t", help="New title")
    p_edit.add_argument("--content", "-c", help="New content")
    p_edit.add_argument("--tags", help="New tags (comma-separated)")
    p_edit.add_argument("--status", choices=["draft", "published", "archived"], help="New status")
    p_edit.add_argument("--priority", choices=["low", "medium", "high", "critical"], help="New priority")
    p_edit.add_argument("--category", "-C", help="New category ID")
    p_edit.set_defaults(func=cmd_edit)
    
    # delete command
    p_delete = subparsers.add_parser("delete", aliases=["rm"], help="Delete a note")
    p_delete.add_argument("note_id", help="Note ID")
    p_delete.add_argument("--force", "-f", action="store_true", help="Skip confirmation")
    p_delete.set_defaults(func=cmd_delete)
    
    # search command
    p_search = subparsers.add_parser("search", help="Search notes")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--tags", "-t", help="Filter by tags (comma-separated)")
    p_search.add_argument("--status", "-s", choices=["draft", "published", "archived"], help="Filter by status")
    p_search.add_argument("--category", "-C", help="Filter by category")
    p_search.add_argument("--limit", "-n", type=int, default=50, help="Maximum results")
    p_search.set_defaults(func=cmd_search)
    
    # pin command
    p_pin = subparsers.add_parser("pin", help="Pin or unpin a note")
    p_pin.add_argument("note_id", help="Note ID")
    p_pin.add_argument("--unpin", action="store_true", help="Unpin the note")
    p_pin.set_defaults(func=cmd_pin)
    
    # archive command
    p_archive = subparsers.add_parser("archive", help="Archive or restore a note")
    p_archive.add_argument("note_id", help="Note ID")
    p_archive.add_argument("--restore", action="store_true", help="Restore archived note")
    p_archive.set_defaults(func=cmd_archive)
    
    # category command
    p_cat = subparsers.add_parser("category", aliases=["cat"], help="Manage categories")
    p_cat.add_argument("--list", "-l", action="store_true", help="List categories")
    p_cat.add_argument("--create", "-c", metavar="NAME", help="Create a category")
    p_cat.add_argument("--delete", "-d", metavar="ID", help="Delete a category")
    p_cat.add_argument("--description", help="Category description")
    p_cat.add_argument("--icon", help="Category icon")
    p_cat.set_defaults(func=cmd_category)
    
    # tag command
    p_tag = subparsers.add_parser("tag", help="Manage tags")
    p_tag.add_argument("--list", "-l", action="store_true", help="List tags")
    p_tag.add_argument("--delete", "-d", metavar="NAME", help="Delete a tag")
    p_tag.set_defaults(func=cmd_tag)
    
    # export command
    p_export = subparsers.add_parser("export", help="Export notes")
    p_export.add_argument("output", help="Output file or directory")
    p_export.add_argument("--format", "-f", choices=["json", "markdown"], default="json", help="Export format")
    p_export.set_defaults(func=cmd_export)
    
    # import command
    p_import = subparsers.add_parser("import", help="Import notes")
    p_import.add_argument("file", help="JSON file to import")
    p_import.set_defaults(func=cmd_import)
    
    # stats command
    p_stats = subparsers.add_parser("stats", help="Show statistics")
    p_stats.set_defaults(func=cmd_stats)
    
    # quick command
    p_quick = subparsers.add_parser("quick", help="Create a quick note")
    p_quick.add_argument("content", nargs="?", help="Note content")
    p_quick.add_argument("--tags", "-t", help="Comma-separated tags")
    p_quick.set_defaults(func=cmd_quick)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
