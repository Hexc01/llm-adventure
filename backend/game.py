import uuid
from models import (
    GameState, GameSession, Enemy, CombatState, CombatAction,
    NPCInfo, NPCState, QuestState,
)
import dice


# 内存存储游戏会话
sessions: dict[str, GameSession] = {}

# 战术描述映射
TACTIC_NAMES = {
    "attack": "普通攻击",
    "heavy_attack": "全力一击",
    "defend": "防御反击",
    "magic": "魔法攻击",
    "dodge": "闪避",
    "flee": "逃跑",
}


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

    # 任务进度
    if "quest_progress" in state_change:
        advance_quest(session, state_change["quest_progress"], state_change.get("quest_event", ""))

    # 检查游戏结束
    if state.hp <= 0:
        state.game_over = True


def advance_quest(session: GameSession, progress: str, event: str = ""):
    """推进主线任务"""
    quest = session.state.quest
    stage_order = ["undiscovered", "rumor", "clues", "lair", "boss", "treasure", "escape"]

    if progress == "victory" or progress == "escape":
        quest.stage = "victory"
        session.state.victory = True
        session.state.game_over = True
        return

    # 只能推进，不能后退
    if progress in stage_order:
        current_idx = stage_order.index(quest.stage) if quest.stage in stage_order else 0
        new_idx = stage_order.index(progress)
        if new_idx > current_idx:
            quest.stage = progress

    if event:
        quest.description = event

    if progress == "rumor":
        quest.description = "你听说小镇深处隐藏着一个远古宝藏……"
    elif progress == "clues":
        quest.description = "你正在寻找宝藏的线索"
    elif progress == "lair":
        quest.description = "你找到了暗影龙的巢穴！"
    elif progress == "boss":
        quest.boss_defeated = True
        quest.description = "暗影龙已被击败！快去拿宝藏！"
    elif progress == "treasure":
        quest.has_treasure = True
        quest.description = "你获得了远古宝藏！现在必须逃离小镇！"


def start_encounter(session: GameSession, encounter: dict) -> dict:
    """处理遭遇（战斗或NPC）"""
    encounter_type = encounter.get("type", "none")

    if encounter_type == "combat":
        enemy_data = encounter.get("enemy", {})
        enemy = Enemy(
            name=enemy_data.get("name", "未知生物"),
            description=enemy_data.get("description", "一只危险的生物"),
            difficulty=enemy_data.get("difficulty", 10),
            hp=enemy_data.get("hp", 30),
            max_hp=enemy_data.get("hp", 30),
            enemy_type=enemy_data.get("enemy_type", "monster"),
        )
        session.state.combat = CombatState(
            active=True,
            enemy=enemy,
            round_num=1,
            log=[f"遭遇了 {enemy.name}！"],
        )
        return {
            "type": "combat",
            "enemy": enemy.model_dump(),
            "combat_active": True,
        }

    elif encounter_type == "npc":
        npc_data = encounter.get("npc", {})
        npc = NPCInfo(
            name=npc_data.get("name", "神秘人"),
            personality=npc_data.get("personality", "友善的"),
            hints=npc_data.get("hints", []),
        )
        session.state.npc = NPCState(
            active=True,
            npc=npc,
            dialogue=[],
        )
        return {
            "type": "npc",
            "npc": npc.model_dump(),
            "npc_active": True,
        }

    return {"type": "none"}


def resolve_combat_action(session: GameSession, tactic: str) -> dict:
    """解析战斗行动"""
    combat = session.state.combat
    if not combat.active:
        return {"error": "当前没有战斗"}

    enemy = combat.enemy
    player_hp = session.state.hp

    # 掷骰子解析战斗
    result = dice.resolve_combat(enemy.difficulty, tactic, player_hp)

    combat.round_num += 1
    combat.log.append(result["description"])

    response = {
        "dice_roll": result["dice_roll"],
        "effective_roll": result["effective_roll"],
        "tactic": TACTIC_NAMES.get(tactic, tactic),
        "success": result["success"],
        "damage": result.get("damage", 0),
        "hp_change": result.get("hp_change", 0),
        "description": result["description"],
        "enemy_hp": enemy.hp,
        "player_hp": player_hp,
        "escaped": result.get("escaped", False),
    }

    if result.get("escaped"):
        # 逃跑成功
        combat.active = False
        session.state.combat = CombatState()
        response["combat_ended"] = True
        response["result"] = "escaped"
        return response

    if result["success"]:
        # 对敌人造成伤害
        enemy.hp = max(0, enemy.hp - result["damage"])
        response["enemy_hp"] = enemy.hp

        if enemy.hp <= 0:
            # 敌人被击败
            combat.active = False
            response["combat_ended"] = True
            response["result"] = "victory"
            response["enemy_defeated"] = enemy.name

            # 如果是boss，推进任务
            if enemy.enemy_type == "boss":
                advance_quest(session, "boss", f"击败了{enemy.name}！")

            session.state.combat = CombatState()
            return response
    else:
        # 玩家受伤
        new_hp = max(0, player_hp + result["hp_change"])
        session.state.hp = new_hp
        response["player_hp"] = new_hp

        if new_hp <= 0:
            session.state.game_over = True
            combat.active = False
            response["combat_ended"] = True
            response["result"] = "defeat"
            return response

    response["result"] = "ongoing"
    return response


def build_action_prompt(state: GameState, action: str) -> str:
    """构建带状态信息的玩家行动提示"""
    status_info = f"[HP: {state.hp}/{state.max_hp}]"
    if state.inventory:
        status_info += f" [物品: {', '.join(state.inventory)}]"
    status_info += f" [位置: {state.location}]"

    # 任务信息
    if state.quest.stage != "undiscovered":
        status_info += f" [任务: {state.quest.title} - {state.quest.description}]"

    return f"{status_info}\n玩家行动: {action}"
