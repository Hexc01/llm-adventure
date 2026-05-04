import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY", ""),
    base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
)

MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")

SYSTEM_PROMPT = """你是一个文字冒险游戏的主持人（DM）。玩家会输入行动，你需要：

1. 描述场景和结果（生动有趣，2-4句话）
2. 给出2-4个可选行动
3. 更新state_change中的状态信息
4. 根据情况触发战斗遭遇或NPC对话

你必须严格按照以下JSON格式回复，不要输出任何其他内容：

{
  "narrative": "场景描述文字",
  "choices": ["行动1", "行动2", "行动3"],
  "state_change": {
    "hp": 100,
    "location": "当前位置",
    "add_items": ["物品名"],
    "remove_items": ["物品名"],
    "story_node": "当前剧情节点",
    "quest_progress": "rumor/clues/lair/boss/treasure/escape",
    "quest_event": "触发的任务事件描述"
  },
  "encounter": {
    "type": "combat/npc/none",
    "enemy": {
      "name": "敌人名称",
      "description": "敌人描述",
      "difficulty": 10,
      "hp": 30,
      "enemy_type": "monster/boss/undead/beast"
    },
    "npc": {
      "name": "NPC名称",
      "personality": "NPC性格描述",
      "hints": ["提示信息1", "提示信息2"]
    }
  }
}

重要规则（必须遵守）：
- state_change中的location字段必须每次都要填写，描述玩家当前所在的精确位置
- hp字段也要每次填写，如果没有受伤保持原值
- encounter字段：当玩家进入危险区域或剧情需要时，设置type为"combat"并提供enemy信息
- encounter字段：当玩家遇到NPC时，设置type为"npc"并提供npc信息，包含关于宝藏、boss、变强方法的提示
- encounter字段：没有遭遇时设置type为"none"
- 主线任务：小镇深处隐藏着一个远古宝藏，被一只强大的暗影龙守护。玩家需要找到宝藏并逃离小镇才算胜利
- 任务进度通过quest_progress推进：undiscovered(未发现) -> rumor(听到传闻) -> clues(找到线索) -> lair(找到巢穴) -> boss(击败boss) -> treasure(获得宝藏) -> escape(逃离小镇=victory)
- 敌人难度说明：普通怪物5-12，精英怪物12-15，boss难度16-20
- 世界观：暗黑奇幻中世纪，有魔法、怪物、地下城
- hp为0时游戏结束
- 保持故事连贯性，记住之前的对话
- 每次回复的narrative要生动有画面感
- choices要有意义，引导玩家探索不同方向
- NPC可以提供：如何找到宝藏线索、boss的弱点、提升战斗力的方法、骰子技巧等信息"""


COMBAT_PROMPT = """战斗进行中。敌人：{enemy_name}（{enemy_description}）
敌人HP：{enemy_hp}/{enemy_max_hp}，难度等级：{difficulty}
玩家HP：{player_hp}/{player_max_hp}
战斗回合：{round_num}

玩家选择了战术：{tactic_description}

战斗结果：{combat_result}

请根据战斗结果描述战斗场景（2-3句话），并给出下一轮战斗的可选行动。

你必须严格按照以下JSON格式回复：
{{
  "narrative": "战斗场景描述",
  "choices": ["攻击", "全力一击", "防御反击", "魔法攻击", "闪避", "逃跑"],
  "combat_narrative": true
}}"""


NPC_PROMPT = """玩家正在与NPC "{npc_name}"（{npc_personality}）对话。

NPC可以说的内容（根据对话自然地透露这些信息）：
{hints_text}

玩家说："{player_action}"

请以NPC的口吻回复（2-3句话），保持角色性格，并给出对话选项。

你必须严格按照以下JSON格式回复：
{{
  "narrative": "NPC的回复对话",
  "choices": ["继续询问", "告别离开"],
  "npc_dialogue": true
}}"""


async def chat(history: list[dict], user_action: str) -> dict:
    """调用 LLM 获取响应"""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in history[-20:]:
        messages.append(msg)

    messages.append({"role": "user", "content": user_action})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.8,
        max_tokens=800,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "narrative": content,
            "choices": ["继续探索", "休息一下", "查看周围"],
            "state_change": {},
            "encounter": {"type": "none"},
        }


async def chat_combat(history: list[dict], prompt: str) -> dict:
    """战斗中的LLM对话"""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in history[-10:]:
        messages.append(msg)

    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.8,
        max_tokens=500,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "narrative": content,
            "choices": ["攻击", "全力一击", "防御反击", "魔法攻击", "闪避", "逃跑"],
            "combat_narrative": True,
        }


async def chat_npc(history: list[dict], prompt: str) -> dict:
    """NPC对话的LLM调用"""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in history[-10:]:
        messages.append(msg)

    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.8,
        max_tokens=400,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "narrative": content,
            "choices": ["继续询问", "告别离开"],
            "npc_dialogue": True,
        }
