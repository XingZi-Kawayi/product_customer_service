import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory.memory_manager import MemoryManager

print("=" * 60)
print("Memory Function Test")
print("=" * 60)

print("\n1. Creating memory manager...")
memory = MemoryManager(session_id="test_session")
print(f"   [OK] Memory manager created, session ID: {memory.session_id}")

print("\n2. Adding test conversations...")
memory.add_user_message("Hello")
memory.add_ai_message("Hello! I'm the customer service of Zhisaotong. How can I help you?")
memory.add_user_message("How to charge my robot?")
memory.add_ai_message("Please put the robot back to the charging base.")
print("   [OK] Test conversations added")

print("\n3. Viewing history...")
history = memory.get_history_messages()
for msg in history:
    role = "User" if msg["role"] == "user" else "Assistant"
    print(f"   {role}: {msg['content']}")

print("\n4. Getting LangChain messages...")
lc_messages = memory.get_langchain_messages(system_prompt="You are a helpful assistant")
print(f"   [OK] Got {len(lc_messages)} messages")

print("\n5. Listing all sessions...")
sessions = MemoryManager.list_sessions()
print(f"   [OK] Found {len(sessions)} sessions: {sessions}")

print("\n6. Clearing history...")
memory.clear_history()
print("   [OK] History cleared")

print("\n7. Deleting test session...")
MemoryManager.delete_session("test_session")
print("   [OK] Test session deleted")

print("\n" + "=" * 60)
print("[OK] All tests passed! Memory function works.")
print("=" * 60)
