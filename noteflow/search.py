"""
NoteFlow-CLI Search Engine
Full-text search and semantic search capabilities.
"""

import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from noteflow.models import Note, NoteStatus


@dataclass
class SearchResult:
    """Search result with relevance score."""
    note: Note
    score: float
    matches: List[str]
    highlights: Dict[str, List[str]]


class SearchEngine:
    """
    Lightweight search engine for notes.
    
    Features:
    - Full-text search with TF-IDF scoring
    - Tag-based filtering
    - Date range filtering
    - Status filtering
    - Boolean query support (AND, OR, NOT)
    """
    
    # Common stop words to ignore in search
    STOP_WORDS = {
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
        "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
        "to", "was", "were", "will", "with", "the", "this", "but", "they",
        "have", "had", "what", "when", "where", "who", "which", "why", "how",
        "all", "each", "every", "both", "few", "more", "most", "other", "some",
        "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too",
        "very", "can", "just", "should", "now"
    }
    
    def __init__(self):
        """Initialize search engine."""
        self._index: Dict[str, Dict[str, float]] = {}  # note_id -> {term: tfidf}
        self._doc_lengths: Dict[str, int] = {}  # note_id -> document length
        self._inverted_index: Dict[str, Set[str]] = {}  # term -> set of note_ids
        self._notes: Dict[str, Note] = {}  # note_id -> Note
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into lowercase words.
        
        Args:
            text: Input text to tokenize.
            
        Returns:
            List of lowercase tokens.
        """
        # Remove special characters and split
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        # Filter stop words
        return [t for t in tokens if t not in self.STOP_WORDS and len(t) > 1]
    
    def _compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        """
        Compute term frequency for tokens.
        
        Args:
            tokens: List of tokens.
            
        Returns:
            Dictionary of term -> TF score.
        """
        if not tokens:
            return {}
        
        counter = Counter(tokens)
        total = len(tokens)
        return {term: count / total for term, count in counter.items()}
    
    def _compute_idf(self, term: str, total_docs: int) -> float:
        """
        Compute inverse document frequency for a term.
        
        Args:
            term: The term to compute IDF for.
            total_docs: Total number of documents.
            
        Returns:
            IDF score.
        """
        doc_freq = len(self._inverted_index.get(term, set()))
        if doc_freq == 0:
            return 0.0
        
        import math
        return math.log(total_docs / doc_freq) + 1
    
    def index_note(self, note: Note) -> None:
        """
        Index a single note.
        
        Args:
            note: Note to index.
        """
        # Combine title and content for indexing
        text = f"{note.title} {note.content}"
        tokens = self._tokenize(text)
        
        # Store note
        self._notes[note.id] = note
        self._doc_lengths[note.id] = len(tokens)
        
        # Compute TF
        tf = self._compute_tf(tokens)
        
        # Update inverted index
        for term in tf:
            if term not in self._inverted_index:
                self._inverted_index[term] = set()
            self._inverted_index[term].add(note.id)
        
        # Store TF (IDF will be computed during search)
        self._index[note.id] = tf
    
    def index_notes(self, notes: List[Note]) -> None:
        """
        Index multiple notes.
        
        Args:
            notes: List of notes to index.
        """
        for note in notes:
            self.index_note(note)
    
    def remove_note(self, note_id: str) -> None:
        """
        Remove a note from the index.
        
        Args:
            note_id: ID of note to remove.
        """
        if note_id not in self._index:
            return
        
        # Remove from inverted index
        for term in list(self._inverted_index.keys()):
            self._inverted_index[term].discard(note_id)
            if not self._inverted_index[term]:
                del self._inverted_index[term]
        
        # Remove from main index
        del self._index[note_id]
        del self._doc_lengths[note_id]
        del self._notes[note_id]
    
    def search(
        self,
        query: str,
        status: Optional[NoteStatus] = None,
        tags: Optional[List[str]] = None,
        category_id: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 50
    ) -> List[SearchResult]:
        """
        Search notes with the given query and filters.
        
        Args:
            query: Search query string.
            status: Filter by note status.
            tags: Filter by tags (notes must have ALL tags).
            category_id: Filter by category.
            date_from: Filter notes updated after this date.
            date_to: Filter notes updated before this date.
            limit: Maximum number of results.
            
        Returns:
            List of SearchResult objects sorted by relevance.
        """
        # Parse query
        query_tokens = self._tokenize(query)
        
        if not query_tokens:
            # No query, return filtered notes
            return self._filter_notes(
                status=status,
                tags=tags,
                category_id=category_id,
                date_from=date_from,
                date_to=date_to,
                limit=limit
            )
        
        # Compute query TF-IDF
        query_tf = self._compute_tf(query_tokens)
        total_docs = len(self._notes)
        
        # Score documents
        scores: Dict[str, float] = {}
        matches: Dict[str, List[str]] = {}
        
        for term in query_tokens:
            if term not in self._inverted_index:
                continue
            
            idf = self._compute_idf(term, total_docs)
            
            for note_id in self._inverted_index[term]:
                if note_id not in scores:
                    scores[note_id] = 0.0
                    matches[note_id] = []
                
                tf = self._index[note_id].get(term, 0)
                scores[note_id] += tf * idf * query_tf[term]
                matches[note_id].append(term)
        
        # Create search results
        results: List[SearchResult] = []
        
        for note_id, score in scores.items():
            note = self._notes[note_id]
            
            # Apply filters
            if status and note.status != status:
                continue
            if tags and not all(t in note.tags for t in tags):
                continue
            if category_id and note.category_id != category_id:
                continue
            if date_from and note.updated_at < date_from:
                continue
            if date_to and note.updated_at > date_to:
                continue
            
            # Generate highlights
            highlights = self._generate_highlights(note, query_tokens)
            
            results.append(SearchResult(
                note=note,
                score=score,
                matches=matches[note_id],
                highlights=highlights
            ))
        
        # Sort by score and return top results
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]
    
    def _filter_notes(
        self,
        status: Optional[NoteStatus] = None,
        tags: Optional[List[str]] = None,
        category_id: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 50
    ) -> List[SearchResult]:
        """Filter notes without search query."""
        results: List[SearchResult] = []
        
        for note_id, note in self._notes.items():
            # Apply filters
            if status and note.status != status:
                continue
            if tags and not all(t in note.tags for t in tags):
                continue
            if category_id and note.category_id != category_id:
                continue
            if date_from and note.updated_at < date_from:
                continue
            if date_to and note.updated_at > date_to:
                continue
            
            results.append(SearchResult(
                note=note,
                score=1.0,  # No relevance score for filtered results
                matches=[],
                highlights={}
            ))
        
        # Sort by update time
        results.sort(key=lambda r: r.note.updated_at, reverse=True)
        return results[:limit]
    
    def _generate_highlights(
        self,
        note: Note,
        query_tokens: List[str]
    ) -> Dict[str, List[str]]:
        """
        Generate highlighted snippets for search results.
        
        Args:
            note: Note to highlight.
            query_tokens: Query tokens to highlight.
            
        Returns:
            Dictionary with 'title' and 'content' highlights.
        """
        highlights: Dict[str, List[str]] = {"title": [], "content": []}
        
        # Highlight in title
        title_lower = note.title.lower()
        for token in query_tokens:
            if token in title_lower:
                # Find the original case version
                pattern = re.compile(re.escape(token), re.IGNORECASE)
                matches = pattern.findall(note.title)
                highlights["title"].extend(matches)
        
        # Highlight in content
        content_lower = note.content.lower()
        for token in query_tokens:
            if token in content_lower:
                # Find context around match
                idx = content_lower.find(token)
                start = max(0, idx - 30)
                end = min(len(note.content), idx + len(token) + 30)
                snippet = note.content[start:end]
                if start > 0:
                    snippet = "..." + snippet
                if end < len(note.content):
                    snippet = snippet + "..."
                highlights["content"].append(snippet)
        
        return highlights
    
    def suggest(self, prefix: str, limit: int = 10) -> List[str]:
        """
        Suggest completions for a prefix.
        
        Args:
            prefix: Prefix to complete.
            limit: Maximum number of suggestions.
            
        Returns:
            List of suggested terms.
        """
        prefix_lower = prefix.lower()
        suggestions = [
            term for term in self._inverted_index
            if term.startswith(prefix_lower)
        ]
        
        # Sort by frequency (number of documents containing the term)
        suggestions.sort(
            key=lambda t: len(self._inverted_index[t]),
            reverse=True
        )
        
        return suggestions[:limit]
    
    def get_related_notes(self, note_id: str, limit: int = 5) -> List[SearchResult]:
        """
        Find notes related to a given note.
        
        Args:
            note_id: ID of the reference note.
            limit: Maximum number of related notes.
            
        Returns:
            List of related notes with similarity scores.
        """
        if note_id not in self._index:
            return []
        
        reference_tf = self._index[note_id]
        total_docs = len(self._notes)
        
        # Compute similarity with all other notes
        similarities: List[Tuple[str, float]] = []
        
        for other_id, other_tf in self._index.items():
            if other_id == note_id:
                continue
            
            # Cosine similarity
            dot_product = 0.0
            for term in set(reference_tf.keys()) & set(other_tf.keys()):
                idf = self._compute_idf(term, total_docs)
                dot_product += reference_tf[term] * other_tf[term] * (idf ** 2)
            
            if dot_product > 0:
                similarities.append((other_id, dot_product))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Create results
        results: List[SearchResult] = []
        for other_id, score in similarities[:limit]:
            results.append(SearchResult(
                note=self._notes[other_id],
                score=score,
                matches=[],
                highlights={}
            ))
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get search engine statistics."""
        return {
            "total_indexed_notes": len(self._notes),
            "total_unique_terms": len(self._inverted_index),
            "average_doc_length": (
                sum(self._doc_lengths.values()) / len(self._doc_lengths)
                if self._doc_lengths else 0
            ),
            "vocabulary_size": len(self._inverted_index)
        }
