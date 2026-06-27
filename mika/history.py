"""Conversation history persistence for mika CLI."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from mika.config import get_history_dir


def _history_path(session_id: str) -> Path:
    return get_history_dir() / f"{session_id}.json"


def create_session(title: Optional[str] = None) -> str:
    """Create a new chat session and return its ID."""
    session_id = uuid.uuid4().hex[:12]
    data = {
        "id": session_id,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "title": title or "Untitled chat",
        "messages": [],
    }
    save_session(session_id, data)
    return session_id


def save_session(session_id: str, data: Dict) -> None:
    """Persist a session to disk."""
    path = _history_path(session_id)
    data["updated_at"] = datetime.utcnow().isoformat()
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_session(session_id: str) -> Optional[Dict]:
    """Load a session by ID."""
    path = _history_path(session_id)
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def list_sessions(limit: int = 20) -> List[Dict]:
    """Return recent sessions sorted by updated_at descending."""
    sessions = []
    for path in get_history_dir().glob("*.json"):
        session = load_session(path.stem)
        if session:
            sessions.append(session)
    sessions.sort(key=lambda s: s.get("updated_at", ""), reverse=True)
    return sessions[:limit]


def add_message(session_id: str, role: str, content: str) -> None:
    """Append a message to a session."""
    session = load_session(session_id)
    if session is None:
        session = {
            "id": session_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "title": content[:40] if role == "user" else "Untitled chat",
            "messages": [],
        }
    session["messages"].append({"role": role, "content": content})
    if role == "user" and session.get("title") == "Untitled chat":
        session["title"] = content[:50]
    save_session(session_id, session)


def delete_session(session_id: str) -> bool:
    """Delete a session file."""
    path = _history_path(session_id)
    if path.exists():
        path.unlink()
        return True
    return False
