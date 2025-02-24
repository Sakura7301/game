import time


# 获取加成信息函数
def get_multiple(property, multiple):
    """获取对应属性的数值，并增强鲁棒性"""
    # 检查 multiple 是否为字典
    if not isinstance(multiple, dict):
        raise ValueError("参数 multiple 必须为字典类型")

    default_value = 1
    default_str = ""
    symbol_type = {
        'attack': '⚔️',
        'defense': '🛡️',
        'max_hp': '💖',
        'exp': '📚',
        'gold': '🪙',
    }

    # 利用 get 方法获取数据，防止 KeyError
    data = multiple.get(property)
    if isinstance(data, dict):
        expire_time = data.get('time')
        bonus_value = data.get('value')
        # 确保 expire_time 和 bonus_value 均为数值类型
        if isinstance(expire_time, (int, float)) and isinstance(bonus_value, (int, float)):
            if expire_time > time.time():
                default_str = f"{symbol_type[property]}{bonus_value:.0%}"
                default_value = bonus_value + 1

    return default_value, default_str
