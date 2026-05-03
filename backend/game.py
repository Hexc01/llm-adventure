import uuid
from models import GameState, GameSession

# 内存存储游戏会话
sessions: dict[str, GameSession] = {}


def create_session() -> GameSession:
    """创建新游戏会话"""
    session_id = str(uuid.uuid4())[:8]
    session = GameSession(
        id=session_id,
        state=GameState(),
        history=[],
    )
    sessions[session_id] = session
    return session


def get_session(session_id: str) -> GameSession | None:
    """获取游戏会话"""
    return sessions.get(session_id)


def apply_state_change(session: GameSession, state_change: dict):
    """应用状态变更"""
    if not state_change:
        return

    state = session.state

    if "hp" in state_change:
        state.hp = max(0, min(state.max_hp, state_change["hp"]))
    if "location" in state_change:
        state.location = state_change["location"]
    if "add_items" in state_change:
        for item in state_change["add_items"]:
            if item not in state.inventory:
                state.inventory.append(item)
    if "remove_items" in state_change:
        for item in state_change["remove_items"]:
            if item in state.inventory:
                state.inventory.remove(item)
    if "story_node" in state_change:
        state.story_node = state_change["story_node"]


def build_action_prompt(state: GameState, action: str) -> str:
    """构建带状态信息的玩家行动提示"""
    status_info = f"[HP: {state.hp}/{state.max_hp}]"
    if state.inventory:
        status_info += f" [物品: {', '.join(state.inventory)}]"
    status_info += f" [位置: {state.location}]"

    return f"{status_info}\n玩家行动: {action}"
