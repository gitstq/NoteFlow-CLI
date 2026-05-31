"""
NoteFlow-CLI - Lightweight Terminal Intelligent Note & Knowledge Management Engine
轻量级终端智能笔记与知识管理引擎

A zero-dependency, privacy-first note management system for developers.
"""

__version__ = "1.0.0"
__author__ = "NoteFlow Team"
__license__ = "MIT"

from noteflow.core import NoteFlow
from noteflow.models import Note, Category, Tag
from noteflow.storage import Storage
from noteflow.search import SearchEngine

__all__ = [
    "NoteFlow",
    "Note",
    "Category", 
    "Tag",
    "Storage",
    "SearchEngine",
    "__version__",
]
