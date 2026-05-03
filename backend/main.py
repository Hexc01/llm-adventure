from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import GameAction
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

    # 生成初始场景
    result = await llm.chat([], "玩家刚刚来到被诅咒的小镇边缘，开始了冒险。请描述初始场景。")

    session.history.append({"role": "assistant", "content": result["narrative"]})
    game.apply_state_change(session, result.get("state_change", {}))

    return {
        "session_id": session.id,
        "narrative": result["narrative"],
        "choices": result.get("choices", []),
        "state": session.state.model_dump(),
    }


@app.post("/api/game/action")
async def game_action(session_id: str, body: GameAction):
    """处理玩家行动"""
    session = game.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")

    if session.state.hp <= 0:
        raise HTTPException(status_code=400, detail="Game over")

    # 构建提示
    prompt = game.build_action_prompt(session.state, body.action)
    session.history.append({"role": "user", "content": prompt})

    # 调用 LLM
    result = await llm.chat(session.history, prompt)

    # 更新状态
    session.history.append({"role": "assistant", "content": result["narrative"]})
    game.apply_state_change(session, result.get("state_change", {}))

    return {
        "narrative": result["narrative"],
        "choices": result.get("choices", []),
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
