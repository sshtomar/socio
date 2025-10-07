"""
Session manager for maintaining conversation state
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class ConversationTurn:
    """Single turn in a conversation"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)


@dataclass
class SessionState:
    """State for a single session"""
    session_id: str
    notebook_id: str
    conversation_history: List[ConversationTurn] = field(default_factory=list)
    notebook_variables: Dict[str, str] = field(default_factory=dict)
    last_activity: datetime = field(default_factory=datetime.now)

    def add_turn(self, role: str, content: str, metadata: Dict = None):
        """Add a conversation turn"""
        turn = ConversationTurn(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.conversation_history.append(turn)
        self.last_activity = datetime.now()

    def get_history_for_agent(self, max_turns: int = 10) -> List[Dict]:
        """Get conversation history formatted for agent"""
        # Get recent turns
        recent = self.conversation_history[-max_turns:]

        # Format for Claude API
        return [
            {"role": turn.role, "content": turn.content}
            for turn in recent
        ]

    def update_variables(self, variables: Dict[str, str]):
        """Update tracked notebook variables"""
        self.notebook_variables.update(variables)
        self.last_activity = datetime.now()


class SessionManager:
    """Manages conversation sessions and state"""

    def __init__(self, max_sessions: int = 1000):
        self.sessions: Dict[str, SessionState] = {}
        self.max_sessions = max_sessions

    def get_or_create_session(
        self,
        session_id: str,
        notebook_id: str
    ) -> SessionState:
        """Get existing session or create new one"""
        if session_id not in self.sessions:
            # Clean up old sessions if needed
            if len(self.sessions) >= self.max_sessions:
                self._cleanup_old_sessions()

            self.sessions[session_id] = SessionState(
                session_id=session_id,
                notebook_id=notebook_id
            )

        return self.sessions[session_id]

    def add_user_message(self, session_id: str, message: str):
        """Add user message to session"""
        if session_id in self.sessions:
            self.sessions[session_id].add_turn("user", message)

    def add_assistant_message(
        self,
        session_id: str,
        message: str,
        metadata: Dict = None
    ):
        """Add assistant message to session"""
        if session_id in self.sessions:
            self.sessions[session_id].add_turn(
                "assistant",
                message,
                metadata=metadata
            )

    def update_notebook_state(
        self,
        session_id: str,
        variables: Dict[str, str]
    ):
        """Update notebook variable state"""
        if session_id in self.sessions:
            self.sessions[session_id].update_variables(variables)

    def get_conversation_context(
        self,
        session_id: str,
        max_turns: int = 10
    ) -> List[Dict]:
        """Get conversation history for agent"""
        if session_id in self.sessions:
            return self.sessions[session_id].get_history_for_agent(max_turns)
        return []

    def clear_session(self, session_id: str):
        """Clear a specific session"""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def _cleanup_old_sessions(self, max_age_hours: int = 24):
        """Remove old inactive sessions"""
        now = datetime.now()
        to_remove = []

        for session_id, session in self.sessions.items():
            age = (now - session.last_activity).total_seconds() / 3600
            if age > max_age_hours:
                to_remove.append(session_id)

        for session_id in to_remove:
            del self.sessions[session_id]

    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get session information"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            return {
                "session_id": session.session_id,
                "notebook_id": session.notebook_id,
                "turn_count": len(session.conversation_history),
                "last_activity": session.last_activity.isoformat(),
                "variables": list(session.notebook_variables.keys())
            }
        return None


# Global session manager instance
_session_manager = None


def get_session_manager() -> SessionManager:
    """Get global session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
