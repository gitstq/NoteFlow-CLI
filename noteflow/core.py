"""
NoteFlow-CLI Core Module
Main NoteFlow class that orchestrates all functionality.
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from noteflow.models import Category, Note, NotePriority, NoteStatus, Tag
from noteflow.search import SearchEngine, SearchResult
from noteflow.storage import Storage


class NoteFlow:
    """
    Main NoteFlow application class.
    
    Provides a unified interface for note management with:
    - CRUD operations for notes, categories, and tags
    - Full-text search with TF-IDF
    - Git integration
    - Import/Export capabilities
    - Statistics and analytics
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize NoteFlow.
        
        Args:
            base_path: Base directory for storage. Defaults to current directory.
        """
        self.storage = Storage(base_path)
        self.search_engine = SearchEngine()
        self._git_info: Optional[Dict[str, str]] = None
        
        # Index existing notes
        self._rebuild_index()
    
    def _rebuild_index(self) -> None:
        """Rebuild search index from stored notes."""
        notes = self.storage.get_all_notes()
        self.search_engine.index_notes(notes)
    
    # ==================== Git Integration ====================
    
    def _get_git_info(self) -> Dict[str, str]:
        """Get current git branch and commit info."""
        if self._git_info is not None:
            return self._git_info
        
        info = {"branch": None, "commit": None}
        
        try:
            # Get current branch
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.storage.base_path
            )
            if result.returncode == 0:
                info["branch"] = result.stdout.strip()
            
            # Get current commit
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.storage.base_path
            )
            if result.returncode == 0:
                info["commit"] = result.stdout.strip()
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        
        self._git_info = info
        return info
    
    # ==================== Note Operations ====================
    
    def create_note(
        self,
        title: str,
        content: str = "",
        category_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        status: NoteStatus = NoteStatus.DRAFT,
        priority: NotePriority = NotePriority.MEDIUM,
        link_git: bool = True
    ) -> Note:
        """
        Create a new note.
        
        Args:
            title: Note title.
            content: Note content (Markdown supported).
            category_id: Optional category ID.
            tags: Optional list of tags.
            status: Note status.
            priority: Note priority.
            link_git: Whether to link current git branch/commit.
            
        Returns:
            Created Note object.
        """
        note = Note(
            title=title,
            content=content,
            category_id=category_id,
            tags=tags or [],
            status=status,
            priority=priority
        )
        
        # Link git info if enabled
        if link_git:
            git_info = self._get_git_info()
            note.git_branch = git_info.get("branch")
            note.git_commit = git_info.get("commit")
        
        # Save to storage
        self.storage.save_note(note)
        
        # Update search index
        self.search_engine.index_note(note)
        
        # Update tags
        for tag_name in note.tags:
            self.create_tag(tag_name)
        
        return note
    
    def get_note(self, note_id: str) -> Optional[Note]:
        """
        Get a note by ID.
        
        Args:
            note_id: Note ID.
            
        Returns:
            Note object or None if not found.
        """
        return self.storage.get_note(note_id)
    
    def update_note(
        self,
        note_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        category_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        status: Optional[NoteStatus] = None,
        priority: Optional[NotePriority] = None
    ) -> Optional[Note]:
        """
        Update an existing note.
        
        Args:
            note_id: Note ID to update.
            title: New title (optional).
            content: New content (optional).
            category_id: New category ID (optional).
            tags: New tags list (optional).
            status: New status (optional).
            priority: New priority (optional).
            
        Returns:
            Updated Note object or None if not found.
        """
        note = self.storage.get_note(note_id)
        if not note:
            return None
        
        if title is not None:
            note.title = title
        if content is not None:
            note.update_content(content)
        if category_id is not None:
            note.category_id = category_id
        if tags is not None:
            note.tags = tags
        if status is not None:
            note.status = status
        if priority is not None:
            note.priority = priority
        
        note.updated_at = datetime.now()
        
        # Save and reindex
        self.storage.save_note(note)
        self.search_engine.remove_note(note_id)
        self.search_engine.index_note(note)
        
        return note
    
    def delete_note(self, note_id: str) -> bool:
        """
        Delete a note.
        
        Args:
            note_id: Note ID to delete.
            
        Returns:
            True if deleted, False if not found.
        """
        result = self.storage.delete_note(note_id)
        if result:
            self.search_engine.remove_note(note_id)
        return result
    
    def archive_note(self, note_id: str) -> Optional[Note]:
        """Archive a note."""
        return self.update_note(note_id, status=NoteStatus.ARCHIVED)
    
    def restore_note(self, note_id: str) -> Optional[Note]:
        """Restore an archived note."""
        return self.update_note(note_id, status=NoteStatus.DRAFT)
    
    def pin_note(self, note_id: str) -> Optional[Note]:
        """Pin a note."""
        note = self.storage.get_note(note_id)
        if note:
            note.pin()
            self.storage.save_note(note)
        return note
    
    def unpin_note(self, note_id: str) -> Optional[Note]:
        """Unpin a note."""
        note = self.storage.get_note(note_id)
        if note:
            note.unpin()
            self.storage.save_note(note)
        return note
    
    def list_notes(
        self,
        status: Optional[NoteStatus] = None,
        category_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        pinned_only: bool = False,
        limit: int = 50
    ) -> List[Note]:
        """
        List notes with optional filters.
        
        Args:
            status: Filter by status.
            category_id: Filter by category.
            tags: Filter by tags.
            pinned_only: Only return pinned notes.
            limit: Maximum number of notes.
            
        Returns:
            List of Note objects.
        """
        notes = self.storage.get_all_notes()
        
        if status:
            notes = [n for n in notes if n.status == status]
        if category_id:
            notes = [n for n in notes if n.category_id == category_id]
        if tags:
            notes = [n for n in notes if all(t in n.tags for t in tags)]
        if pinned_only:
            notes = [n for n in notes if n.is_pinned]
        
        # Sort by pinned first, then by updated_at
        notes.sort(key=lambda n: (not n.is_pinned, n.updated_at), reverse=True)
        
        return notes[:limit]
    
    def get_recent_notes(self, limit: int = 10) -> List[Note]:
        """Get recently updated notes."""
        return self.storage.get_recent_notes(limit)
    
    # ==================== Category Operations ====================
    
    def create_category(
        self,
        name: str,
        description: str = "",
        parent_id: Optional[str] = None,
        icon: str = "📁",
        color: str = "#2ecc71"
    ) -> Category:
        """Create a new category."""
        category = Category(
            name=name,
            description=description,
            parent_id=parent_id,
            icon=icon,
            color=color
        )
        self.storage.save_category(category)
        return category
    
    def get_category(self, category_id: str) -> Optional[Category]:
        """Get a category by ID."""
        return self.storage.get_category(category_id)
    
    def list_categories(self) -> List[Category]:
        """List all categories."""
        return self.storage.get_all_categories()
    
    def delete_category(self, category_id: str) -> bool:
        """Delete a category."""
        return self.storage.delete_category(category_id)
    
    # ==================== Tag Operations ====================
    
    def create_tag(self, name: str, color: str = "#3498db") -> Tag:
        """Create a new tag."""
        tag = Tag(name=name, color=color)
        self.storage.save_tag(tag)
        return tag
    
    def list_tags(self) -> List[Tag]:
        """List all tags."""
        return self.storage.get_all_tags()
    
    def delete_tag(self, name: str) -> bool:
        """Delete a tag."""
        return self.storage.delete_tag(name)
    
    # ==================== Search Operations ====================
    
    def search(
        self,
        query: str,
        status: Optional[NoteStatus] = None,
        tags: Optional[List[str]] = None,
        category_id: Optional[str] = None,
        limit: int = 50
    ) -> List[SearchResult]:
        """
        Search notes.
        
        Args:
            query: Search query.
            status: Filter by status.
            tags: Filter by tags.
            category_id: Filter by category.
            limit: Maximum results.
            
        Returns:
            List of SearchResult objects.
        """
        return self.search_engine.search(
            query=query,
            status=status,
            tags=tags,
            category_id=category_id,
            limit=limit
        )
    
    def search_suggest(self, prefix: str) -> List[str]:
        """Get search suggestions for a prefix."""
        return self.search_engine.suggest(prefix)
    
    def get_related_notes(self, note_id: str, limit: int = 5) -> List[SearchResult]:
        """Get notes related to a specific note."""
        return self.search_engine.get_related_notes(note_id, limit)
    
    # ==================== Import/Export Operations ====================
    
    def export_markdown(self, output_dir: str) -> int:
        """Export all notes to Markdown files."""
        return self.storage.export_to_markdown(output_dir)
    
    def export_json(self, output_file: str) -> int:
        """Export all data to JSON."""
        return self.storage.export_to_json(output_file)
    
    def import_json(self, input_file: str) -> int:
        """Import data from JSON."""
        count = self.storage.import_from_json(input_file)
        self._rebuild_index()
        return count
    
    # ==================== Statistics ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get application statistics."""
        storage_stats = self.storage.get_stats()
        search_stats = self.search_engine.get_stats()
        
        return {
            **storage_stats,
            **search_stats,
            "storage_path": str(self.storage.storage_dir)
        }
    
    # ==================== Quick Note ====================
    
    def quick_note(self, content: str, tags: Optional[List[str]] = None) -> Note:
        """
        Create a quick note with auto-generated title.
        
        Args:
            content: Note content.
            tags: Optional tags.
            
        Returns:
            Created Note object.
        """
        # Generate title from first line
        lines = content.strip().split("\n")
        title = lines[0][:50] if lines else "Quick Note"
        
        return self.create_note(
            title=title,
            content=content,
            tags=tags,
            status=NoteStatus.DRAFT
        )
    
    # ==================== Batch Operations ====================
    
    def batch_tag(self, note_ids: List[str], tags: List[str]) -> int:
        """Add tags to multiple notes."""
        count = 0
        for note_id in note_ids:
            note = self.storage.get_note(note_id)
            if note:
                for tag in tags:
                    note.add_tag(tag)
                self.storage.save_note(note)
                count += 1
        return count
    
    def batch_archive(self, note_ids: List[str]) -> int:
        """Archive multiple notes."""
        count = 0
        for note_id in note_ids:
            if self.archive_note(note_id):
                count += 1
        return count
    
    def batch_delete(self, note_ids: List[str]) -> int:
        """Delete multiple notes."""
        count = 0
        for note_id in note_ids:
            if self.delete_note(note_id):
                count += 1
        return count
