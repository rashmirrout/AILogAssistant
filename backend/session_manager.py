"""
Session manager for handling chat history persistence.
"""

import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from backend.file_manager import FileManager
from backend.models import ChatMessage

class SessionManager:
    """Manages chat sessions and history."""
    
    def __init__(self):
        self.file_manager = FileManager()
    
    def append_chat(
        self,
        issue_id: str,
        role: str,
        message: str,
        references: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Append a message to chat history.
        
        Args:
            issue_id: Issue ID
            role: Message role ('user' or 'assistant')
            message: Message content
            references: Optional list of references
            metadata: Optional metadata
        """
        if not self.file_manager.issue_exists(issue_id):
            raise FileNotFoundError(f"Issue {issue_id} does not exist")
        
        chat_message = ChatMessage(
            timestamp=datetime.now().isoformat(),
            role=role,
            message=message,
            references=references,
            metadata=metadata
        )
        
        chat_history_path = self.file_manager.get_chat_history_path(issue_id)
        
        # Append to JSONL file
        with open(chat_history_path, 'a', encoding='utf-8') as f:
            f.write(chat_message.json() + '\n')
    
    def load_history(self, issue_id: str, limit: Optional[int] = None) -> List[ChatMessage]:
        """
        Load chat history for an issue.
        
        Args:
            issue_id: Issue ID
            limit: Optional limit on number of recent messages to return
            
        Returns:
            List of chat messages (oldest first)
        """
        if not self.file_manager.issue_exists(issue_id):
            raise FileNotFoundError(f"Issue {issue_id} does not exist")
        
        chat_history_path = self.file_manager.get_chat_history_path(issue_id)
        
        if not chat_history_path.exists():
            return []
        
        messages = []
        with open(chat_history_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    message_data = json.loads(line)
                    messages.append(ChatMessage(**message_data))
        
        # Apply limit if specified (return most recent)
        if limit is not None and len(messages) > limit:
            messages = messages[-limit:]
        
        return messages
    
    def clear_history(self, issue_id: str):
        """
        Clear chat history for an issue.
        
        Args:
            issue_id: Issue ID
        """
        if not self.file_manager.issue_exists(issue_id):
            raise FileNotFoundError(f"Issue {issue_id} does not exist")
        
        chat_history_path = self.file_manager.get_chat_history_path(issue_id)
        
        # Clear file by truncating
        chat_history_path.write_text('', encoding='utf-8')
    
    def get_conversation_summary(self, issue_id: str) -> Dict[str, Any]:
        """
        Get summary statistics for a conversation.
        
        Args:
            issue_id: Issue ID
            
        Returns:
            Dict with summary statistics
        """
        messages = self.load_history(issue_id)
        
        user_messages = [m for m in messages if m.role == 'user']
        assistant_messages = [m for m in messages if m.role == 'assistant']
        
        return {
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "first_message": messages[0].timestamp if messages else None,
            "last_message": messages[-1].timestamp if messages else None
        }
    
    def export_history(self, issue_id: str, format: str = 'json') -> str:
        """
        Export chat history in specified format.
        
        Args:
            issue_id: Issue ID
            format: Export format ('json' or 'markdown')
            
        Returns:
            Formatted history string
        """
        messages = self.load_history(issue_id)
        
        if format == 'json':
            return json.dumps([m.dict() for m in messages], indent=2)
        
        elif format == 'markdown':
            lines = [f"# Chat History - Issue {issue_id}\n"]
            
            for msg in messages:
                role_display = "**User**" if msg.role == "user" else "**Assistant**"
                lines.append(f"\n## {role_display} ({msg.timestamp})\n")
                lines.append(f"{msg.message}\n")
                
                if msg.references:
                    lines.append("\n*References:*\n")
                    for ref in msg.references:
                        lines.append(f"- {ref}\n")
            
            return ''.join(lines)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
