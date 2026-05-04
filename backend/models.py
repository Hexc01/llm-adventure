from pydantic import BaseModel, Field


class Enemy(BaseModel):
    """敌人信息"""
    name: str = "未知生物"
    description: str = ""
    difficulty: int = 10  # 难度等级 1-20
    hp: int = 30
    max_hp: int = 30
    enemy_type: str = "monster"  # monster, boss, undead, beast


class CombatState(BaseModel):
    """战斗状态"""
    active: bool = False
    enemy: Enemy = Field(default_factory=Enemy)
    round_num: int = 0
    log: list[str] = []


class NPCInfo(BaseModel):
    """NPC信息"""
    name: str = ""
    personality: str = ""
    hints: list[str] = []


class NPCState(BaseModel):
    """NPC对话状态"""
    active: bool = False
    npc: NPCInfo = Field(default_factory=NPCInfo)
    dialogue: list[str] = []


class QuestState(BaseModel):
    """主线任务状态"""
    stage: str = "undiscovered"  # undiscovered, rumor, clues, lair, boss, treasure, victory
    title: str = "诅咒小镇的秘密"
    description: str = ""
    clues_found: list[str] = []
    has_treasure: bool = False
    boss_defeated: bool = False


class GameState(BaseModel):
    hp: int = 100
    max_hp: int = 100
    location: str = "unknown"
    inventory: list[str] = []
    story_node: str = "start"
    combat: CombatState = Field(default_factory=CombatState)
    npc: NPCState = Field(default_factory=NPCState)
    quest: QuestState = Field(default_factory=QuestState)
    game_over: bool = False
    victory: bool = False


class GameAction(BaseModel):
    action: str


class CombatAction(BaseModel):
    tactic: str  # attack, heavy_attack, defend, magic, dodge, flee


class LLMResponse(BaseModel):
    narrative: str
    choices: list[str] = []
    state_change: dict = {}


class GameSession(BaseModel):
    id: str
    state: GameState
    history: list[dict] = []
