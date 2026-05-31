"""
NoteFlow-CLI Data Models
Core data structures for notes, categories, and tags.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class NoteStatus(str, Enum):
    """Note status enumeration."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"


class NotePriority(str, Enum):
    """Note priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Tag:
    """Tag model for note categorization."""
    name: str
    color: str = "#3498db"
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tag to dictionary."""
        return {
            "name": self.name,
            "color": self.color,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tag":
        """Create tag from dictionary."""
        return cls(
            name=data["name"],
            color=data.get("color", "#3498db"),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now()
        )


@dataclass
class Category:
    """Category model for note organization."""
    id: str = field(default_factory=lambda: str(uuid4())[:8])
    name: str = ""
    description: str = ""
    parent_id: Optional[str] = None
    icon: str = "📁"
    color: str = "#2ecc71"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert category to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "parent_id": self.parent_id,
            "icon": self.icon,
            "color": self.color,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Category":
        """Create category from dictionary."""
        return cls(
            id=data.get("id", str(uuid4())[:8]),
            name=data.get("name", ""),
            description=data.get("description", ""),
            parent_id=data.get("parent_id"),
            icon=data.get("icon", "📁"),
            color=data.get("color", "#2ecc71"),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now()
        )


@dataclass
class Note:
    """Note model - core data structure for notes."""
    id: str = field(default_factory=lambda: str(uuid4())[:12])
    title: str = ""
    content: str = ""
    category_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    status: NoteStatus = NoteStatus.DRAFT
    priority: NotePriority = NotePriority.MEDIUM
    is_pinned: bool = False
    is_encrypted: bool = False
    git_commit: Optional[str] = None
    git_branch: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert note to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category_id": self.category_id,
            "tags": self.tags,
            "status": self.status.value,
            "priority": self.priority.value,
            "is_pinned": self.is_pinned,
            "is_encrypted": self.is_encrypted,
            "git_commit": self.git_commit,
            "git_branch": self.git_branch,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Note":
        """Create note from dictionary."""
        return cls(
            id=data.get("id", str(uuid4())[:12]),
            title=data.get("title", ""),
            content=data.get("content", ""),
            category_id=data.get("category_id"),
            tags=data.get("tags", []),
            status=NoteStatus(data.get("status", "draft")),
            priority=NotePriority(data.get("priority", "medium")),
            is_pinned=data.get("is_pinned", False),
            is_encrypted=data.get("is_encrypted", False),
            git_commit=data.get("git_commit"),
            git_branch=data.get("git_branch"),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now()
        )
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the note."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the note."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now()
    
    def update_content(self, content: str) -> None:
        """Update note content."""
        self.content = content
        self.updated_at = datetime.now()
    
    def archive(self) -> None:
        """Archive the note."""
        self.status = NoteStatus.ARCHIVED
        self.updated_at = datetime.now()
    
    def restore(self) -> None:
        """Restore archived note."""
        self.status = NoteStatus.DRAFT
        self.updated_at = datetime.now()
    
    def pin(self) -> None:
        """Pin the note."""
        self.is_pinned = True
        self.updated_at = datetime.now()
    
    def unpin(self) -> None:
        """Unpin the note."""
        self.is_pinned = False
        self.updated_at = datetime.now()
    
    @property
    def word_count(self) -> int:
        """Get word count of note content."""
        return len(self.content.split())
    
    @property
    def char_count(self) -> int:
        """Get character count of note content."""
        return len(self.content)
    
    @property
    def preview(self) -> str:
        """Get a preview of the note content."""
        preview_text = self.content[:100]
        if len(self.content) > 100:
            preview_text += "..."
        return preview_text.replace("\n", " ")
    
    def __str__(self) -> str:
        """String representation of note."""
        status_icon = {
            NoteStatus.DRAFT: "📝",
            NoteStatus.PUBLISHED: "✅",
            NoteStatus.ARCHIVED: "📦",
            NoteStatus.DELETED: "🗑️"
        }
        pin_icon = "📌 " if self.is_pinned else ""
        return f"{pin_icon}{status_icon[self.status]} [{self.id}] {self.title}"
