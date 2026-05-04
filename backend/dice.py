import random


def roll(sides: int = 20) -> int:
    """掷骰子，返回1到sides之间的随机数"""
    return random.randint(1, sides)


def roll_multiple(count: int, sides: int = 6) -> list[int]:
    """掷多个骰子"""
    return [random.randint(1, sides) for _ in range(count)]


def resolve_combat(enemy_difficulty: int, tactic: str, player_hp: int) -> dict:
    """
    解析战斗结果

    参数:
        enemy_difficulty: 敌人难度等级 (1-20)，越高越难
        tactic: 玩家选择的战术
        player_hp: 玩家当前HP

    返回:
        包含 dice_roll, success, damage, hp_change, description 的字典
    """
    dice = roll(20)

    # 战术修正
    tactic_modifiers = {
        "attack": {"mod": 0, "desc": "普通攻击", "risk": "normal"},
        "heavy_attack": {"mod": -3, "desc": "全力一击", "risk": "high"},
        "defend": {"mod": 5, "desc": "防御反击", "risk": "low"},
        "magic": {"mod": -2, "desc": "魔法攻击", "risk": "high"},
        "dodge": {"mod": 4, "desc": "闪避", "risk": "low"},
        "flee": {"mod": 6, "desc": "逃跑", "risk": "low"},
    }

    tactic_info = tactic_modifiers.get(tactic, {"mod": 0, "desc": tactic, "risk": "normal"})
    effective_roll = dice + tactic_info["mod"]

    # 判定成功：有效掷骰 >= 敌人难度
    success = effective_roll >= enemy_difficulty

    # 计算伤害
    if tactic == "flee":
        if success:
            return {
                "dice_roll": dice,
                "effective_roll": effective_roll,
                "tactic": tactic_info["desc"],
                "success": True,
                "damage": 0,
                "hp_change": 0,
                "escaped": True,
                "description": f"你掷出了 {dice}（修正后 {effective_roll}），成功逃离了战斗！",
            }
        else:
            damage = random.randint(8, 15)
            return {
                "dice_roll": dice,
                "effective_roll": effective_roll,
                "tactic": tactic_info["desc"],
                "success": False,
                "damage": 0,
                "hp_change": -damage,
                "escaped": False,
                "description": f"你掷出了 {dice}（修正后 {effective_roll}），逃跑失败！敌人追上来对你造成了 {damage} 点伤害。",
            }

    if success:
        # 成功：对敌人造成伤害
        base_damage = random.randint(10, 20)
        if tactic == "heavy_attack":
            base_damage = int(base_damage * 1.8)
        elif tactic == "magic":
            base_damage = int(base_damage * 1.5)
        elif tactic == "defend":
            base_damage = int(base_damage * 0.6)

        return {
            "dice_roll": dice,
            "effective_roll": effective_roll,
            "tactic": tactic_info["desc"],
            "success": True,
            "damage": base_damage,
            "hp_change": 0,
            "escaped": False,
            "description": f"你掷出了 {dice}（修正后 {effective_roll}），{tactic_info['desc']}命中！造成了 {base_damage} 点伤害。",
        }
    else:
        # 失败：受到敌人伤害
        base_damage = random.randint(8, 18)
        if tactic == "defend":
            base_damage = int(base_damage * 0.4)
        elif tactic == "dodge":
            base_damage = int(base_damage * 0.3)
        elif tactic == "heavy_attack":
            base_damage = int(base_damage * 1.3)

        return {
            "dice_roll": dice,
            "effective_roll": effective_roll,
            "tactic": tactic_info["desc"],
            "success": False,
            "damage": 0,
            "hp_change": -base_damage,
            "escaped": False,
            "description": f"你掷出了 {dice}（修正后 {effective_roll}），{tactic_info['desc']}失败！敌人反击造成了 {base_damage} 点伤害。",
        }
