"""
Tests for NoteFlow-CLI
Unit tests for core functionality.
"""

import json
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from noteflow.core import NoteFlow
from noteflow.models import Category, Note, NotePriority, NoteStatus, Tag
from noteflow.search import SearchEngine
from noteflow.storage import Storage


class TestModels(unittest.TestCase):
    """Test data models."""
    
    def test_note_creation(self):
        """Test note creation."""
        note = Note(
            title="Test Note",
            content="This is a test note",
            tags=["test", "example"]
        )
        
        self.assertEqual(note.title, "Test Note")
        self.assertEqual(note.content, "This is a test note")
        self.assertEqual(note.tags, ["test", "example"])
        self.assertEqual(note.status, NoteStatus.DRAFT)
        self.assertIsNotNone(note.id)
    
    def test_note_to_dict(self):
        """Test note serialization."""
        note = Note(title="Test", content="Content")
        data = note.to_dict()
        
        self.assertIn("id", data)
        self.assertIn("title", data)
        self.assertEqual(data["title"], "Test")
    
    def test_note_from_dict(self):
        """Test note deserialization."""
        data = {
            "id": "abc123",
            "title": "Test",
            "content": "Content",
            "tags": ["a", "b"],
            "status": "published",
            "priority": "high",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        note = Note.from_dict(data)
        self.assertEqual(note.id, "abc123")
        self.assertEqual(note.title, "Test")
        self.assertEqual(note.status, NoteStatus.PUBLISHED)
        self.assertEqual(note.priority, NotePriority.HIGH)
    
    def test_note_word_count(self):
        """Test word count."""
        note = Note(content="One two three four five")
        self.assertEqual(note.word_count, 5)
    
    def test_note_preview(self):
        """Test preview generation."""
        note = Note(content="A" * 150)
        preview = note.preview
        self.assertTrue(len(preview) <= 103)  # 100 + "..."
        self.assertTrue(preview.endswith("..."))
    
    def test_category_creation(self):
        """Test category creation."""
        cat = Category(name="Work", icon="💼")
        self.assertEqual(cat.name, "Work")
        self.assertEqual(cat.icon, "💼")
    
    def test_tag_creation(self):
        """Test tag creation."""
        tag = Tag(name="important", color="#ff0000")
        self.assertEqual(tag.name, "important")
        self.assertEqual(tag.color, "#ff0000")


class TestStorage(unittest.TestCase):
    """Test storage operations."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = Storage(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_save_and_get_note(self):
        """Test saving and retrieving notes."""
        note = Note(title="Test", content="Content")
        self.storage.save_note(note)
        
        retrieved = self.storage.get_note(note.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.title, "Test")
    
    def test_get_all_notes(self):
        """Test getting all notes."""
        note1 = Note(title="Note 1")
        note2 = Note(title="Note 2")
        
        self.storage.save_note(note1)
        self.storage.save_note(note2)
        
        notes = self.storage.get_all_notes()
        self.assertEqual(len(notes), 2)
    
    def test_delete_note(self):
        """Test deleting notes."""
        note = Note(title="To Delete")
        self.storage.save_note(note)
        
        result = self.storage.delete_note(note.id)
        self.assertTrue(result)
        
        retrieved = self.storage.get_note(note.id)
        self.assertIsNone(retrieved)
    
    def test_category_operations(self):
        """Test category operations."""
        cat = Category(name="Test Category")
        self.storage.save_category(cat)
        
        retrieved = self.storage.get_category(cat.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Test Category")
    
    def test_export_json(self):
        """Test JSON export."""
        note = Note(title="Export Test")
        self.storage.save_note(note)
        
        export_path = os.path.join(self.temp_dir, "export.json")
        count = self.storage.export_to_json(export_path)
        
        self.assertEqual(count, 1)
        self.assertTrue(os.path.exists(export_path))
    
    def test_stats(self):
        """Test statistics."""
        note1 = Note(title="Note 1", content="Content 1")
        note2 = Note(title="Note 2", content="Content 2")
        
        self.storage.save_note(note1)
        self.storage.save_note(note2)
        
        stats = self.storage.get_stats()
        self.assertEqual(stats["total_notes"], 2)


class TestSearchEngine(unittest.TestCase):
    """Test search engine."""
    
    def setUp(self):
        """Set up test environment."""
        self.engine = SearchEngine()
        
        self.notes = [
            Note(id="1", title="Python Programming", content="Learn Python basics"),
            Note(id="2", title="JavaScript Guide", content="JavaScript fundamentals"),
            Note(id="3", title="Python Advanced", content="Advanced Python topics"),
        ]
        
        self.engine.index_notes(self.notes)
    
    def test_search_basic(self):
        """Test basic search."""
        results = self.engine.search("Python")
        self.assertEqual(len(results), 2)
    
    def test_search_scoring(self):
        """Test search result scoring."""
        results = self.engine.search("Python")
        
        # Results should be sorted by score
        if len(results) > 1:
            self.assertGreaterEqual(results[0].score, results[1].score)
    
    def test_search_no_results(self):
        """Test search with no results."""
        results = self.engine.search("xyznonexistent")
        self.assertEqual(len(results), 0)
    
    def test_search_suggest(self):
        """Test search suggestions."""
        suggestions = self.engine.suggest("Py")
        self.assertTrue(any("python" in s.lower() for s in suggestions))
    
    def test_remove_note(self):
        """Test removing note from index."""
        self.engine.remove_note("1")
        results = self.engine.search("Python")
        self.assertEqual(len(results), 1)


class TestNoteFlow(unittest.TestCase):
    """Test main NoteFlow class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.nf = NoteFlow(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_note(self):
        """Test note creation."""
        note = self.nf.create_note(
            title="Test Note",
            content="Test content",
            tags=["test"]
        )
        
        self.assertIsNotNone(note.id)
        self.assertEqual(note.title, "Test Note")
    
    def test_get_note(self):
        """Test retrieving notes."""
        created = self.nf.create_note(title="Test")
        retrieved = self.nf.get_note(created.id)
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, created.id)
    
    def test_update_note(self):
        """Test updating notes."""
        note = self.nf.create_note(title="Original")
        updated = self.nf.update_note(note.id, title="Updated")
        
        self.assertEqual(updated.title, "Updated")
    
    def test_delete_note(self):
        """Test deleting notes."""
        note = self.nf.create_note(title="To Delete")
        result = self.nf.delete_note(note.id)
        
        self.assertTrue(result)
        self.assertIsNone(self.nf.get_note(note.id))
    
    def test_search_notes(self):
        """Test searching notes."""
        self.nf.create_note(title="Python", content="Python content")
        self.nf.create_note(title="JavaScript", content="JS content")
        
        results = self.nf.search("Python")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].note.title, "Python")
    
    def test_pin_note(self):
        """Test pinning notes."""
        note = self.nf.create_note(title="Test")
        self.nf.pin_note(note.id)
        
        retrieved = self.nf.get_note(note.id)
        self.assertTrue(retrieved.is_pinned)
    
    def test_archive_note(self):
        """Test archiving notes."""
        note = self.nf.create_note(title="Test")
        self.nf.archive_note(note.id)
        
        retrieved = self.nf.get_note(note.id)
        self.assertEqual(retrieved.status, NoteStatus.ARCHIVED)
    
    def test_quick_note(self):
        """Test quick note creation."""
        note = self.nf.quick_note("Quick thought here")
        
        self.assertIsNotNone(note.id)
        self.assertIn("Quick", note.title)
    
    def test_category_management(self):
        """Test category management."""
        cat = self.nf.create_category(name="Work")
        
        self.assertIsNotNone(cat.id)
        self.assertEqual(len(self.nf.list_categories()), 1)
    
    def test_stats(self):
        """Test statistics."""
        self.nf.create_note(title="Note 1")
        self.nf.create_note(title="Note 2")
        
        stats = self.nf.get_stats()
        self.assertEqual(stats["total_notes"], 2)


if __name__ == "__main__":
    unittest.main()
