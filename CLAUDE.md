# 暗黑传说 | Dark Legend - LLM 文字冒险游戏

## 项目概述
LLM 驱动的暗黑奇幻文字冒险游戏。玩家输入自由行动，LLM 充当地下城主（DM）生成叙事和选项。

## 技术栈
- **后端**: Python FastAPI + OpenAI SDK（兼容格式）
- **前端**: Vue 3 + Pinia + Vite
- **LLM**: LongCat-Flash-Lite（美团），配置在 `backend/.env`

## 项目结构
```
backend/
├── main.py         # FastAPI 路由（5个端点）
├── game.py         # 游戏逻辑：战斗、NPC、任务推进
├── llm.py          # LLM 客户端 + 系统提示词
├── dice.py         # D20 骰子系统 + 战斗解析
├── models.py       # Pydantic 数据模型
└── .env            # LLM API 配置（gitignored）

frontend/src/
├── App.vue                    # 根组件
├── stores/game.js             # Pinia 状态管理
├── api/game.js                # API 调用层
└── components/
    ├── StatusBar.vue           # HP + 位置 + 任务状态
    ├── ChatWindow.vue          # 对话消息流
    ├── ChoicePanel.vue         # 选项 + 自定义输入 + 游戏结束面板
    ├── CombatPanel.vue         # 战斗界面（敌人信息 + 6种战术）
    ├── QuestTracker.vue        # 主线任务进度条
    └── Inventory.vue           # 物品栏
```

## 核心游戏系统

### 战斗系统 (dice.py)
- D20 骰子，难度等级 1-20
- 6种战术：攻击(+0)、全力一击(-3,1.8x)、防御反击(+5,0.6x)、魔法(-2,1.5x)、闪避(+4,0.3x受伤)、逃跑(+6)
- 有效掷骰 = 骰子 + 战术修正 >= 敌人难度 = 成功

### NPC 系统
- LLM 生成 NPC 信息（名字、性格、提示）
- NPC 提供关于宝藏、boss弱点、游戏技巧的线索

### 主线任务 (7阶段)
undiscovered → rumor → clues → lair → boss → treasure → escape/victory
- 小镇隐藏远古宝藏，被暗影龙守护
- 击败boss拿到宝藏逃离小镇 = 胜利
- HP=0 = 游戏结束（可重启或返回主界面）

## API 端点
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/game/new` | POST | 创建新游戏 |
| `/api/game/action` | POST | 普通行走动/探索 |
| `/api/game/combat` | POST | 战斗行动（掷骰子） |
| `/api/game/npc` | POST | NPC对话 |
| `/api/game/state` | GET | 获取当前状态 |

## LLM 配置
通过环境变量配置（`backend/.env`）：
```
OPENAI_API_KEY=你的key
OPENAI_BASE_URL=https://api.longcat.chat/openai
LLM_MODEL=LongCat-Flash-Lite
```
使用 OpenAI 兼容格式，可随时换其他提供商。

## 运行方式
```bash
# 后端
cd backend && pip install -r requirements.txt && uvicorn main:app --reload --port 8000

# 前端
cd frontend && npm install && npm run dev
```
前端 vite.config.js 代理 /api → localhost:8000

## 关键设计决策
- LLM 负责叙事和触发遭遇，后端代码负责骰子/战斗/任务的确定性逻辑
- LLM 返回 `encounter` 字段触发战斗或NPC，返回 `state_change.quest_progress` 推进任务
- 游戏状态纯内存存储，重启丢失
