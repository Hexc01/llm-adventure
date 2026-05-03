import json
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY", "sk-4jhwfa2S8ka97pGZ41KDMw2m2Giq3ddaRcnJ19LHgXv91MWl"),
    base_url=os.environ.get("OPENAI_BASE_URL", "https://api.bltcy.ai/v1"),
)

MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")

SYSTEM_PROMPT = """你是一个文字冒险游戏的主持人（DM）。玩家会输入行动，你需要：

1. 描述场景和结果（生动有趣，2-4句话）
2. 给出2-4个可选行动
3. 如果有状态变化（受伤、获得物品等），在state_change中反映

你必须严格按照以下JSON格式回复，不要输出任何其他内容：

{
  "narrative": "场景描述文字",
  "choices": ["行动1", "行动2", "行动3"],
  "state_change": {
    "hp": 100,
    "location": "当前位置",
    "add_items": ["物品名"],
    "remove_items": ["物品名"],
    "story_node": "当前剧情节点"
  }
}

游戏规则：
- 世界观：暗黑奇幻中世纪，有魔法、怪物、地下城
- 玩家初始在一座被诅咒的小镇边缘
- hp为0时游戏结束
- 保持故事连贯性，记住之前的对话
- 每次回复的narrative要生动有画面感
- choices要有意义，引导玩家探索不同方向"""


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
        max_tokens=512,
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
        }
