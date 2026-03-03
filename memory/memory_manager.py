import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from utils.path_tool import get_abs_path


class MemoryManager:
    def __init__(self, session_id: str = "default", max_history: int = 20):
        self.session_id = session_id
        self.max_history = max_history
        self.history: List[Dict[str, Any]] = []
        self.memory_dir = get_abs_path("./memory")
        self._ensure_memory_dir()
        self._load_history()

    def _ensure_memory_dir(self):
        if not os.path.exists(self.memory_dir):
            os.makedirs(self.memory_dir)

    def _get_history_file_path(self) -> str:
        return os.path.join(self.memory_dir, f"{self.session_id}.json")

    def _load_history(self):
        file_path = self._get_history_file_path()
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = data.get("history", [])
            except Exception:
                self.history = []

    def _save_history(self):
        file_path = self._get_history_file_path()
        data = {
            "session_id": self.session_id,
            "updated_at": datetime.now().isoformat(),
            "history": self.history
        }
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")

    def add_message(self, role: str, content: str):
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-self.max_history * 2:]
        
        self._save_history()

    def add_user_message(self, content: str):
        self.add_message("user", content)

    def add_ai_message(self, content: str):
        self.add_message("assistant", content)

    def get_history_messages(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        if limit is None:
            limit = self.max_history
        return self.history[-limit * 2:]

    def get_langchain_messages(self, system_prompt: Optional[str] = None, limit: Optional[int] = None) -> List:
        messages = []
        
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        
        history = self.get_history_messages(limit)
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        return messages

    def clear_history(self):
        self.history = []
        self._save_history()

    def get_history_summary(self) -> str:
        if not self.history:
            return "暂无对话历史"
        
        summary = [f"对话历史（共 {len(self.history)} 条）："]
        for i, msg in enumerate(self.history[-10:], 1):
            role = "用户" if msg["role"] == "user" else "助手"
            content = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
            summary.append(f"{i}. {role}: {content}")
        
        return "\n".join(summary)

    @staticmethod
    def list_sessions() -> List[str]:
        memory_dir = get_abs_path("./memory")
        if not os.path.exists(memory_dir):
            return []
        
        sessions = []
        for filename in os.listdir(memory_dir):
            if filename.endswith(".json"):
                sessions.append(filename.replace(".json", ""))
        
        return sorted(sessions)

    @staticmethod
    def delete_session(session_id: str) -> bool:
        memory_dir = get_abs_path("./memory")
        file_path = os.path.join(memory_dir, f"{session_id}.json")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception:
                return False
        return False
