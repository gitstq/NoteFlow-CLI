"""
NoteFlow-CLI Storage Module
Handles persistent storage of notes, categories, and tags using JSON files.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from noteflow.models import Category, Note, Tag


class Storage:
    """
    JSON-based storage backend for NoteFlow.
    
    Provides zero-dependency persistent storage using standard library JSON.
    All data is stored locally in a .noteflow directory.
    """
    
    DEFAULT_STORAGE_DIR = ".noteflow"
    NOTES_FILE = "notes.json"
    CATEGORIES_FILE = "categories.json"
    TAGS_FILE = "tags.json"
    CONFIG_FILE = "config.json"
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize storage.
        
        Args:
            base_path: Base directory for storage. Defaults to current directory.
        """
        self.base_path = Path(base_path or os.getcwd())
        self.storage_dir = self.base_path / self.DEFAULT_STORAGE_DIR
        self._ensure_storage_dir()
        self._initialize_files()
    
    def _ensure_storage_dir(self) -> None:
        """Create storage directory if it doesn't exist."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def _initialize_files(self) -> None:
        """Initialize storage files if they don't exist."""
        for filename in [self.NOTES_FILE, self.CATEGORIES_FILE, self.TAGS_FILE]:
            filepath = self.storage_dir / filename
            if not filepath.exists():
                self._write_json(filepath, [])
        
        config_path = self.storage_dir / self.CONFIG_FILE
        if not config_path.exists():
            self._write_json(config_path, {
                "version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "default_category": None,
                "auto_save": True,
                "git_integration": True
            })
    
    def _read_json(self, filepath: Path) -> Any:
        """Read JSON file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return [] if filepath.stem != "config" else {}
    
    def _write_json(self, filepath: Path, data: Any) -> None:
        """Write JSON file with pretty formatting."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    # ==================== Notes Operations ====================
    
    def save_note(self, note: Note) -> None:
        """Save a note to storage."""
        notes = self.get_all_notes()
        
        # Update existing note or add new one
        existing_index = next(
            (i for i, n in enumerate(notes) if n.id == note.id), None
        )
        
        if existing_index is not None:
            notes[existing_index] = note
        else:
            notes.append(note)
        
        self._write_json(
            self.storage_dir / self.NOTES_FILE,
            [n.to_dict() for n in notes]
        )
    
    def get_note(self, note_id: str) -> Optional[Note]:
        """Get a note by ID."""
        notes = self.get_all_notes()
        return next((n for n in notes if n.id == note_id), None)
    
    def get_all_notes(self) -> List[Note]:
        """Get all notes."""
        data = self._read_json(self.storage_dir / self.NOTES_FILE)
        return [Note.from_dict(n) for n in data]
    
    def delete_note(self, note_id: str) -> bool:
        """Delete a note by ID."""
        notes = self.get_all_notes()
        filtered_notes = [n for n in notes if n.id != note_id]
        
        if len(filtered_notes) < len(notes):
            self._write_json(
                self.storage_dir / self.NOTES_FILE,
                [n.to_dict() for n in filtered_notes]
            )
            return True
        return False
    
    def get_notes_by_category(self, category_id: str) -> List[Note]:
        """Get all notes in a category."""
        return [n for n in self.get_all_notes() if n.category_id == category_id]
    
    def get_notes_by_tag(self, tag: str) -> List[Note]:
        """Get all notes with a specific tag."""
        return [n for n in self.get_all_notes() if tag in n.tags]
    
    def get_pinned_notes(self) -> List[Note]:
        """Get all pinned notes."""
        return [n for n in self.get_all_notes() if n.is_pinned]
    
    def get_recent_notes(self, limit: int = 10) -> List[Note]:
        """Get most recently updated notes."""
        notes = self.get_all_notes()
        return sorted(notes, key=lambda n: n.updated_at, reverse=True)[:limit]
    
    # ==================== Categories Operations ====================
    
    def save_category(self, category: Category) -> None:
        """Save a category to storage."""
        categories = self.get_all_categories()
        
        existing_index = next(
            (i for i, c in enumerate(categories) if c.id == category.id), None
        )
        
        if existing_index is not None:
            categories[existing_index] = category
        else:
            categories.append(category)
        
        self._write_json(
            self.storage_dir / self.CATEGORIES_FILE,
            [c.to_dict() for c in categories]
        )
    
    def get_category(self, category_id: str) -> Optional[Category]:
        """Get a category by ID."""
        categories = self.get_all_categories()
        return next((c for c in categories if c.id == category_id), None)
    
    def get_all_categories(self) -> List[Category]:
        """Get all categories."""
        data = self._read_json(self.storage_dir / self.CATEGORIES_FILE)
        return [Category.from_dict(c) for c in data]
    
    def delete_category(self, category_id: str) -> bool:
        """Delete a category by ID."""
        categories = self.get_all_categories()
        filtered = [c for c in categories if c.id != category_id]
        
        if len(filtered) < len(categories):
            self._write_json(
                self.storage_dir / self.CATEGORIES_FILE,
                [c.to_dict() for c in filtered]
            )
            return True
        return False
    
    # ==================== Tags Operations ====================
    
    def save_tag(self, tag: Tag) -> None:
        """Save a tag to storage."""
        tags = self.get_all_tags()
        
        if not any(t.name == tag.name for t in tags):
            tags.append(tag)
            self._write_json(
                self.storage_dir / self.TAGS_FILE,
                [t.to_dict() for t in tags]
            )
    
    def get_all_tags(self) -> List[Tag]:
        """Get all tags."""
        data = self._read_json(self.storage_dir / self.TAGS_FILE)
        return [Tag.from_dict(t) for t in data]
    
    def delete_tag(self, tag_name: str) -> bool:
        """Delete a tag by name."""
        tags = self.get_all_tags()
        filtered = [t for t in tags if t.name != tag_name]
        
        if len(filtered) < len(tags):
            self._write_json(
                self.storage_dir / self.TAGS_FILE,
                [t.to_dict() for t in filtered]
            )
            return True
        return False
    
    # ==================== Config Operations ====================
    
    def get_config(self) -> Dict[str, Any]:
        """Get configuration."""
        return self._read_json(self.storage_dir / self.CONFIG_FILE)
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """Update configuration."""
        current = self.get_config()
        current.update(config)
        self._write_json(self.storage_dir / self.CONFIG_FILE, current)
    
    # ==================== Export Operations ====================
    
    def export_to_markdown(self, output_dir: str) -> int:
        """
        Export all notes to Markdown files.
        
        Returns:
            Number of notes exported.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        notes = self.get_all_notes()
        for note in notes:
            filename = f"{note.id}_{note.title[:30].replace(' ', '_')}.md"
            filepath = output_path / filename
            
            frontmatter = f"""---
id: {note.id}
title: {note.title}
tags: {', '.join(note.tags)}
status: {note.status.value}
priority: {note.priority.value}
created: {note.created_at.isoformat()}
updated: {note.updated_at.isoformat()}
---

"""
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(frontmatter + note.content)
        
        return len(notes)
    
    def export_to_json(self, output_file: str) -> int:
        """
        Export all data to a single JSON file.
        
        Returns:
            Number of notes exported.
        """
        notes = self.get_all_notes()
        categories = self.get_all_categories()
        tags = self.get_all_tags()
        
        export_data = {
            "version": "1.0.0",
            "exported_at": datetime.now().isoformat(),
            "notes": [n.to_dict() for n in notes],
            "categories": [c.to_dict() for c in categories],
            "tags": [t.to_dict() for t in tags]
        }
        
        self._write_json(Path(output_file), export_data)
        return len(notes)
    
    def import_from_json(self, input_file: str) -> int:
        """
        Import data from a JSON file.
        
        Returns:
            Number of notes imported.
        """
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Import notes
        for note_data in data.get("notes", []):
            note = Note.from_dict(note_data)
            self.save_note(note)
        
        # Import categories
        for cat_data in data.get("categories", []):
            category = Category.from_dict(cat_data)
            self.save_category(category)
        
        # Import tags
        for tag_data in data.get("tags", []):
            tag = Tag.from_dict(tag_data)
            self.save_tag(tag)
        
        return len(data.get("notes", []))
    
    # ==================== Statistics ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        notes = self.get_all_notes()
        categories = self.get_all_categories()
        tags = self.get_all_tags()
        
        status_counts = {}
        for note in notes:
            status = note.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_notes": len(notes),
            "total_categories": len(categories),
            "total_tags": len(tags),
            "pinned_notes": len([n for n in notes if n.is_pinned]),
            "status_distribution": status_counts,
            "total_words": sum(n.word_count for n in notes),
            "total_chars": sum(n.char_count for n in notes)
        }
