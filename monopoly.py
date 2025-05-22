import os
import json
import random
from . import constants
from loguru import logger
from typing import Dict, List, Optional


class MonopolySystem:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.properties_file = os.path.join(data_dir, "properties.json")

        # 初始化地图和事件数据
        self._init_properties()

        # 加载数据
        self.map_data = constants.MONOPOLY_MAP
        self.events_data = constants.RANDOM_EVENTS
        self.properties_data = self._load_json(self.properties_file)

    def _init_properties(self):
        """初始化地产数据"""
        if not os.path.exists(self.properties_file):
            self._save_json(self.properties_file, {})

    def _load_json(self, file_path: str) -> dict:
        """加载JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载{file_path}失败: {e}")
            return {}

    def _save_json(self, file_path: str, data: dict):
        """保存JSON文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存{file_path}失败: {e}")

    def roll_dice(self) -> int:
        """掷骰子"""
        return random.randint(1, 6)

    def get_block_info(self, position: int) -> dict:
        """获取指定位置的地块信息"""
        position = position % self.map_data["total_blocks"]
        return self.map_data["blocks"].get(str(position), self.map_data["default_block"])

    def get_property_owner(self, position: int) -> Optional[str]:
        """获取地块所有者"""
        return self.properties_data.get(str(position))

    def buy_property(self, position: int, player_id: str, price: int) -> bool:
        """购买地块"""
        if str(position) in self.properties_data:
            return False

        self.properties_data[str(position)] = {
            "owner": player_id,
            "level": 1,
            "price": price
        }
        self._save_json(self.properties_file, self.properties_data)
        return True

    def calculate_property_price(self, position: int) -> int:
        """计算地块价格"""
        block = self.get_block_info(position)
        base_price = 1000

        # 根据距离起点的远近调整价格
        distance_factor = 1 + (position % 10) * 0.2

        # 计算最终价格
        final_price = int(base_price * constants.BASE_PRICE_OF_THE_AREA[block["region"]] * distance_factor)
        return final_price

    def calculate_rent(self, position: int) -> int:
        """计算租金"""
        property_data = self.properties_data.get(str(position))
        if not property_data:
            return 0

        block = self.get_block_info(position)
        base_rent = property_data["price"] * 0.2

        # 计算最终租金
        final_rent = int(base_rent * constants.RENT_MULTIPLIER_OF_THE_AREA[block["region"]] * property_data["level"] * 2)
        return final_rent

    def calculate_price(self, rent, level, multiplier=2):
        """
        根据租金（rent）和等级（level）计算价值（price）的函数。

        Args:
            rent (float): 地块的租金。
            level (int): 地块的等级（≥ 0）。
            multiplier (float): 等级对价值的影响倍数（默认为 1）。

        Returns:
            float: 计算得到的地块价值（price）。
        """
        if rent < 0 or level < 0:
            raise ValueError("rent 和 level 必须是非负数")
        if multiplier <= 0:
            raise ValueError("multiplier 必须是正数")

        # 核心计算公式
        price = rent * (1 + level * multiplier)
        return price

    def get_property_info(self, position: int) -> dict:
        """获取地产详细信息"""
        property_data = self.properties_data.get(str(position))
        if not property_data:
            return None
        # 计算租金
        rent = self.calculate_rent(position)

        # 计算地产价值
        price = self.calculate_price(rent, property_data["level"])

        block = self.get_block_info(position)
        return {
            "name": block["name"],
            "type": block["type"],
            "region": block["region"],
            "level": property_data["level"],
            "price": price,
            "rent": rent,
            "owner": property_data["owner"]
        }

    def trigger_random_event(self) -> dict:
        """触发随机事件"""
        event_type = random.choice(["good_events", "bad_events"])
        events = self.events_data[event_type]
        return random.choice(events)

    def upgrade_property(self, position: int) -> bool:
        """升级地产"""
        if str(position) not in self.properties_data:
            return False

        property_data = self.properties_data[str(position)]
        if property_data["level"] >= 3:  # 最高3级
            return False

        property_data["level"] += 1
        self._save_json(self.properties_file, self.properties_data)
        return True

    def get_player_properties(self, player_id: str) -> List[int]:
        """获取玩家的所有地产"""
        return [
            int(pos) for pos, data in self.properties_data.items()
            if data["owner"] == player_id
        ]

    def update_property_owner(self, position: int, new_owner: str) -> bool:
        """直接修改地产的所有者，不影响其它逻辑

        Args:
            position (int): 地块位置
            new_owner (str): 新的所有者ID

        Returns:
            bool: 如果修改成功返回True，否则返回False（例如地产不存在）
        """
        pos_key = str(position)
        if pos_key not in self.properties_data:
            return False

        self.properties_data[pos_key]["owner"] = new_owner
        self._save_json(self.properties_file, self.properties_data)
        return True
