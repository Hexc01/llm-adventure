from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import GameAction, CombatAction, NPCState
import game
import llm

app = FastAPI(title="LLM Adventure")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/game/new")
async def new_game():
    """创建新游戏"""
    session = game.create_session()

    # 生成初始场景，提示LLM设置任务和位置
    init_prompt = (
        "玩家刚刚来到被诅咒的小镇边缘，开始了冒险。"
        "请描述初始场景，注意在state_change中设置location为具体位置名称，"
        "并将quest_progress设置为rumor（让玩家听到关于宝藏的传闻）。"
        "在encounter中设置一个友善的NPC（比如酒馆老板或守卫），告诉玩家关于小镇诅咒和隐藏宝藏的信息。"
    )
    result = await llm.chat([], init_prompt)

    session.history.append({"role": "assistant", "content": result["narrative"]})
    game.apply_state_change(session, result.get("state_change", {}))

    # 处理初始遭遇
    encounter_result = game.start_encounter(session, result.get("encounter", {"type": "none"}))

    return {
        "session_id": session.id,
        "narrative": result["narrative"],
        "choices": result.get("choices", []),
        "state": session.state.model_dump(),
        "encounter": encounter_result,
    }


@app.post("/api/game/action")
async def game_action(session_id: str, body: GameAction):
    """处理玩家行动"""
    session = game.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")

    state = session.state

    if state.game_over:
        raise HTTPException(status_code=400, detail="Game over")

    # 如果正在战斗中，不允许普通行动
    if state.combat.active:
        raise HTTPException(status_code=400, detail="正在战斗中，请使用战斗行动")

    # 如果正在NPC对话中
    if state.npc.active:
        prompt = f"玩家对NPC说：\"{body.action}\""
        session.history.append({"role": "user", "content": prompt})
        result = await llm.chat_npc(session.history, prompt)
        session.history.append({"role": "assistant", "content": result["narrative"]})

        # 检查是否结束对话
        farewell_keywords = ["告别", "离开", "再见", "走"]
        if any(kw in body.action for kw in farewell_keywords):
            session.state.npc = NPCState()

        return {
            "narrative": result["narrative"],
            "choices": result.get("choices", ["继续探索"]),
            "state": session.state.model_dump(),
            "encounter": {"type": "none"},
        }

    # 普通行动
    prompt = game.build_action_prompt(state, body.action)
    session.history.append({"role": "user", "content": prompt})

    # 调用 LLM
    result = await llm.chat(session.history, prompt)

    # 更新状态
    session.history.append({"role": "assistant", "content": result["narrative"]})
    game.apply_state_change(session, result.get("state_change", {}))

    # 处理遭遇
    encounter_result = game.start_encounter(session, result.get("encounter", {"type": "none"}))

    return {
        "narrative": result["narrative"],
        "choices": result.get("choices", []),
        "state": session.state.model_dump(),
        "encounter": encounter_result,
    }


@app.post("/api/game/combat")
async def game_combat(session_id: str, body: CombatAction):
    """处理战斗行动"""
    session = game.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")

    if session.state.game_over:
        raise HTTPException(status_code=400, detail="Game over")

    if not session.state.combat.active:
        raise HTTPException(status_code=400, detail="当前没有战斗")

    # 解析战斗行动（掷骰子）
    combat_result = game.resolve_combat_action(session, body.tactic)

    # 让LLM描述战斗场景
    tactic_name = game.TACTIC_NAMES.get(body.tactic, body.tactic)
    prompt = llm.COMBAT_PROMPT.format(
        enemy_name=session.state.combat.enemy.name if session.state.combat.active else combat_result.get("enemy_defeated", "敌人"),
        enemy_description=session.state.combat.enemy.description if session.state.combat.active else "",
        enemy_hp=combat_result.get("enemy_hp", 0),
        enemy_max_hp=combat_result.get("enemy_hp", 0),
        difficulty=session.state.combat.enemy.difficulty if session.state.combat.active else 0,
        player_hp=combat_result.get("player_hp", session.state.hp),
        player_max_hp=session.state.max_hp,
        round_num=session.state.combat.round_num if session.state.combat.active else 0,
        tactic_description=tactic_name,
        combat_result=combat_result["description"],
    )

    session.history.append({"role": "user", "content": f"[战斗] {tactic_name}"})
    llm_result = await llm.chat_combat(session.history, prompt)
    session.history.append({"role": "assistant", "content": llm_result["narrative"]})

    # 如果战斗结束，处理战后状态
    if combat_result.get("combat_ended"):
        if combat_result.get("result") == "victory":
            enemy_name = combat_result.get("enemy_defeated", "敌人")
            session.state.inventory.append(f"{enemy_name}的战利品")
            if combat_result.get("enemy_defeated") and session.state.combat.enemy.enemy_type == "boss":
                game.advance_quest(session, "boss", f"击败了{enemy_name}！")

    return {
        "narrative": llm_result["narrative"],
        "choices": llm_result.get("choices", ["攻击", "全力一击", "防御反击", "魔法攻击", "闪避", "逃跑"]),
        "state": session.state.model_dump(),
        "combat_result": combat_result,
    }


@app.post("/api/game/npc")
async def game_npc_action(session_id: str, body: GameAction):
    """处理NPC对话行动"""
    session = game.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")

    if not session.state.npc.active:
        raise HTTPException(status_code=400, detail="当前没有NPC对话")

    npc = session.state.npc.npc
    hints_text = "\n".join(f"- {h}" for h in npc.hints) if npc.hints else "- （没有特别的信息）"

    prompt = llm.NPC_PROMPT.format(
        npc_name=npc.name,
        npc_personality=npc.personality,
        hints_text=hints_text,
        player_action=body.action,
    )

    session.history.append({"role": "user", "content": f"[对话] {body.action}"})
    result = await llm.chat_npc(session.history, prompt)
    session.history.append({"role": "assistant", "content": result["narrative"]})

    # 检查是否结束对话
    farewell_keywords = ["告别", "离开", "再见", "走"]
    if any(kw in body.action for kw in farewell_keywords):
        session.state.npc = game.NPCState()

    return {
        "narrative": result["narrative"],
        "choices": result.get("choices", ["继续询问", "告别离开"]),
        "state": session.state.model_dump(),
    }


@app.get("/api/game/state")
async def get_state(session_id: str):
    """获取游戏状态"""
    session = game.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")
    return {
        "state": session.state.model_dump(),
        "history_len": len(session.history),
    }
