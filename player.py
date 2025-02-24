import csv
import json
import time
import logging
from .utils import get_multiple
from . import constants
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class Player:
    game = None
    """玩家类,用于管理玩家属性和状态"""
    def __init__(self, data: Dict[str, Any]):
        if not isinstance(data, dict):
            raise TypeError("data must be a dictionary")
        self.data = data

    @classmethod
    def set_game_handle(self, game):
        # 检查是否已经初始化
        if self.game is None:
            self.game = game

    @classmethod
    def get_game_handle(self):
        # 提供访问共享数据的方法
        return self.game

    @property
    def user_id(self) -> str:
        try:
            return str(self.data.get('user_id', ''))
        except Exception as e:
            logging.error(f"获取 user_id 时出错: {e}")
            return ''

    @property
    def nickname(self) -> str:
        try:
            return self.data.get('nickname', '')
        except Exception as e:
            logging.error(f"获取 nickname 时出错: {e}")
            return ''

    @property
    def gold(self) -> int:
        try:
            return int(self.data.get('gold', 0))
        except (ValueError, TypeError) as e:
            logging.error(f"解析 gold 时出错: {e}，返回默认值 0")
            return 0

    @gold.setter
    def gold(self, value: int):
        try:
            self.data['gold'] = str(int(value))
        except (ValueError, TypeError) as e:
            logging.error(f"设置 gold 时出错: {e}，不更新该值")

    @property
    def level(self) -> int:
        try:
            return int(self.data.get('level', 1))
        except (ValueError, TypeError) as e:
            logging.error(f"解析 level 时出错: {e}，返回默认值 1")
            return 1

    @level.setter
    def level(self, value: int):
        try:
            self.data['level'] = str(int(value))
        except (ValueError, TypeError) as e:
            logging.error(f"设置 level 时出错: {e}，不更新该值")

    @property
    def sign_in_timestamp(self) -> int:
        try:
            return int(self.data.get('sign_in_timestamp', 1))
        except (ValueError, TypeError) as e:
            logging.error(f"解析 sign_in_timestamp 时出错: {e}，返回默认值 1")
            return 1

    @sign_in_timestamp.setter
    def sign_in_timestamp(self, value: int):
        try:
            self.data['sign_in_timestamp'] = str(int(value))
        except (ValueError, TypeError) as e:
            logging.error(f"设置 sign_in_timestamp 时出错: {e}，不更新该值")

    @property
    def hp(self) -> int:
        try:
            return int(self.data.get('hp', 100))
        except (ValueError, TypeError) as e:
            logging.error(f"解析 hp 时出错: {e}，返回默认值 100")
            return 100

    @hp.setter
    def hp(self, value: int):
        try:
            self.data['hp'] = str(int(value))
            if int(self.data['hp']) < 0:
                self.data['hp'] = str(0)
        except (ValueError, TypeError) as e:
            logging.error(f"设置 hp 时出错: {e}，不更新该值")

    @property
    def max_hp(self) -> int:
        try:
            return int(self.data.get('max_hp', 100))
        except (ValueError, TypeError) as e:
            logging.error(f"解析 max_hp 时出错: {e}，返回默认值 100")
            return 100

    @max_hp.setter
    def max_hp(self, value: int):
        try:
            self.data['max_hp'] = str(int(value))
        except (ValueError, TypeError) as e:
            logging.error(f"设置 max_hp 时出错: {e}，不更新该值")

    @property
    def attack(self) -> int:
        try:
            return int(self.data.get('attack', 10))
        except (ValueError, TypeError) as e:
            logging.error(f"解析 attack 时出错: {e}，返回默认值 10")
            return 10

    @attack.setter
    def attack(self, value: int):
        try:
            self.data['attack'] = str(int(value))
        except (ValueError, TypeError) as e:
            logging.error(f"设置 attack 时出错: {e}，不更新该值")

    @property
    def defense(self) -> int:
        try:
            return int(self.data.get('defense', 5))
        except (ValueError, TypeError) as e:
            logging.error(f"解析 defense 时出错: {e}，返回默认值 5")
            return 5

    @defense.setter
    def defense(self, value: int):
        try:
            self.data['defense'] = str(int(value))
        except (ValueError, TypeError) as e:
            logging.error(f"设置 defense 时出错: {e}，不更新该值")

    @property
    def exp(self) -> int:
        """获取经验值，确保返回整数"""
        try:
            return int(float(self.data.get('exp', '0')))
        except (ValueError, TypeError) as e:
            logging.error(f"解析 exp 时出错: {e}，返回默认值 0")
            return 0

    @exp.setter
    def exp(self, value: int):
        """设置经验值，确保存储为整数字符串"""
        try:
            self.data['exp'] = str(int(value))
        except (ValueError, TypeError) as e:
            logging.error(f"设置 exp 时出错: {e}，设置为 0")
            self.data['exp'] = '0'

    @property
    def max_exp(self) -> int:
        """获取经验值，确保返回整数"""
        try:
            return int(float(self.data.get('max_exp', '0')))
        except (ValueError, TypeError) as e:
            logging.error(f"解析 max_exp 时出错: {e}，返回默认值 0")
            return 0

    @max_exp.setter
    def max_exp(self, value: int):
        """设置经验值，确保存储为整数字符串"""
        try:
            self.data['max_exp'] = str(int(value))
        except (ValueError, TypeError) as e:
            logging.error(f"设置 max_exp 时出错: {e}，设置为 0")
            self.data['max_exp'] = '0'

    @property
    def inventory(self) -> dict:
        """
        获取库存信息，以字典形式返回。
        字典的键为物品的名称，值为物品的详细信息。
        """
        inventory_data = self.data.get('inventory', {})  # 默认值是空字典

        # 如果从 data 中获取的 inventory 数据是字符串，尝试解析它
        if isinstance(inventory_data, str):
            try:
                inventory = json.loads(inventory_data)
                if isinstance(inventory, dict):
                    return inventory
                else:
                    logging.error(f"Inventory 不是字典类型: {inventory_data}")
                    return {}
            except json.JSONDecodeError as e:
                logging.error(f"JSON解析错误: {e}，Inventory内容: {inventory_data}")
                return {}

        # 如果 inventory_data 已经是字典，直接返回
        elif isinstance(inventory_data, dict):
            return inventory_data
        else:
            logging.error(f"获取的 inventory 不是字符串或字典类型: {type(inventory_data)}")
            return {}

    @inventory.setter
    def inventory(self, value: dict):
        """
        设置库存信息，接受一个字典类型的参数。
        字典的键应为物品的名称，值为物品的详细信息。
        """
        if not isinstance(value, dict):
            logging.error(f"设置 inventory 时出错: 期望字典类型，但收到 {type(value)}")
            return  # 不更新该值

        # 验证每个物品的结构
        for name, item in value.items():
            if not isinstance(item, dict):
                logging.error(f"物品 '{name}' 的值不是字典类型: {item}，不更新该值！")
                return  # 不更新该值

        # 尝试序列化为 JSON 字符串并更新
        try:
            self.data['inventory'] = json.dumps(value, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            logging.error(f"设置 inventory 时出错: {e}，不更新该值")

    @property
    def multiple(self) -> dict:
        """
        获取库存信息，以字典形式返回。
        字典的键为物品的名称，值为物品的详细信息。
        """
        multiple_data = self.data.get('multiple', {})  # 默认值是空字典

        # 如果从 data 中获取的 multiple 数据是字符串，尝试解析它
        if isinstance(multiple_data, str):
            try:
                multiple = json.loads(multiple_data)
                if isinstance(multiple, dict):
                    return multiple
                else:
                    logging.error(f"multiple 不是字典类型: {multiple_data}")
                    return {}
            except json.JSONDecodeError as e:
                logging.error(f"JSON解析错误: {e}，multiple内容: {multiple_data}")
                return {}

        # 如果 inventory_data 已经是字典，直接返回
        elif isinstance(multiple_data, dict):
            return multiple_data
        else:
            logging.error(f"获取的 multiple 不是字符串或字典类型: {type(multiple_data)}")
            return {}

    @multiple.setter
    def multiple(self, value: dict):
        """
        设置库存信息，接受一个字典类型的参数。
        字典的键应为加成的类型，值为加成的说明。
        """
        if not isinstance(value, dict):
            logging.error(f"设置 multiple 时出错: 期望字典类型，但收到 {type(value)}")
            return  # 不更新该值

        # 验证每个物品的结构
        for name, item in value.items():
            if not isinstance(item, dict):
                logging.error(f"物品 '{name}' 的值不是字典类型: {item}，不更新该值！")
                return  # 不更新该值

        # 尝试序列化为 JSON 字符串并更新
        try:
            self.data['multiple'] = json.dumps(value, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            logging.error(f"设置 multiple 时出错: {e}，不更新该值")

    @property
    def equipped_weapon(self) -> str:
        try:
            return self.data.get('equipped_weapon', '')
        except Exception as e:
            logging.error(f"获取 equipped_weapon 时出错: {e}")
            return ''

    @equipped_weapon.setter
    def equipped_weapon(self, value: str):
        try:
            self.data['equipped_weapon'] = value
        except Exception as e:
            logging.error(f"设置 equipped_weapon 时出错: {e}，不更新该值")

    @property
    def equipped_armor(self) -> str:
        try:
            return self.data.get('equipped_armor', '')
        except Exception as e:
            logging.error(f"获取 equipped_armor 时出错: {e}")
            return ''

    @equipped_armor.setter
    def equipped_armor(self, value: str):
        try:
            self.data['equipped_armor'] = value
        except Exception as e:
            logging.error(f"设置 equipped_armor 时出错: {e}，不更新该值")

    @property
    def challenge_proposal(self) -> str:
        try:
            return self.data.get('challenge_proposal', '')
        except Exception as e:
            logging.error(f"获取 challenge_proposal 时出错: {e}")
            return ''

    @challenge_proposal.setter
    def challenge_proposal(self, value: str):
        try:
            self.data['challenge_proposal'] = value
        except Exception as e:
            logging.error(f"设置 challenge_proposal 时出错: {e}，不更新该值")

    @property
    def is_pay_rent(self) -> int:
        try:
            return int(self.data.get('is_pay_rent', 0))
        except (ValueError, TypeError) as e:
            logging.error(f"解析 is_pay_rent 时出错: {e}，返回默认值 0")
            return 0

    @is_pay_rent.setter
    def is_pay_rent(self, value: int):
        try:
            self.data['is_pay_rent'] = str(int(value))
        except (ValueError, TypeError) as e:
            logging.error(f"设置 is_pay_rent 时出错: {e}，不更新该值")

    @property
    def last_attack(self) -> int:
        try:
            return int(self.data.get('last_attack', 0))
        except (ValueError, TypeError) as e:
            logging.error(f"解析 last_attack 时出错: {e}，返回默认值 0")
            return 0

    @last_attack.setter
    def last_attack(self, value: int):
        try:
            self.data['last_attack'] = str(int(value))
        except (ValueError, TypeError) as e:
            logging.error(f"设置 last_attack 时出错: {e}，不更新该值")

    @property
    def adventure_last_attack(self) -> int:
        try:
            return int(self.data.get('adventure_last_attack', 0))
        except (ValueError, TypeError) as e:
            logging.error(f"解析 adventure_last_attack 时出错: {e}，返回默认值 0")
            return 0

    @adventure_last_attack.setter
    def adventure_last_attack(self, value: int):
        try:
            self.data['adventure_last_attack'] = str(int(value))
        except (ValueError, TypeError) as e:
            logging.error(f"设置 adventure_last_attack 时出错: {e}，不更新该值")

    @property
    def equipment_fishing_rod(self) -> dict:
        """
        获取库存信息，以字典形式返回。
        字典的键为物品的名称，值为物品的详细信息。
        """
        equipment_fishing_rod_data = self.data.get('equipment_fishing_rod', {})  # 默认值是空字典

        # 如果从 data 中获取的 equipment_fishing_rod 数据是字符串，尝试解析它
        if isinstance(equipment_fishing_rod_data, str):
            try:
                equipment_fishing_rod = json.loads(equipment_fishing_rod_data)
                if isinstance(equipment_fishing_rod, dict):
                    return equipment_fishing_rod
                else:
                    logging.error(f"equipment_fishing_rod 不是字典类型: {equipment_fishing_rod_data}")
                    return {}
            except json.JSONDecodeError as e:
                logging.error(f"JSON解析错误: {e}，equipment_fishing_rod内容: {equipment_fishing_rod_data}")
                return {}

        # 如果 equipment_fishing_rod_data 已经是字典，直接返回
        elif isinstance(equipment_fishing_rod_data, dict):
            return equipment_fishing_rod_data
        else:
            logging.error(f"获取的 equipment_fishing_rod 不是字符串或字典类型: {type(equipment_fishing_rod_data)}")
            return {}

    @equipment_fishing_rod.setter
    def equipment_fishing_rod(self, value: dict):
        """
        设置库存信息，接受一个字典类型的参数。
        字典的键应为物品的名称，值为物品的详细信息。
        """
        if not isinstance(value, dict):
            logging.error(f"设置 equipment_fishing_rod 时出错: 期望字典类型，但收到 {type(value)}")
            return  # 不更新该值

        # 验证每个物品的结构
        for name, item in value.items():
            if not isinstance(item, dict):
                logging.error(f"物品 '{name}' 的值不是字典类型: {item}，不更新该值！")
                return  # 不更新该值

        # 尝试序列化为 JSON 字符串并更新
        try:
            self.data['equipment_fishing_rod'] = json.dumps(value, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            logging.error(f"设置 equipment_fishing_rod 时出错: {e}，不更新该值")

    @property
    def equipment_armor(self) -> str:
        try:
            return self.data.get('equipment_armor', '')
        except (ValueError, TypeError) as e:
            logging.error(f"解析 equipment_armor 时出错: {e}，返回默认值 0")
            return 0

    @equipment_armor.setter
    def equipment_armor(self, value: str):
        try:
            self.data['equipment_armor'] = value
        except (ValueError, TypeError) as e:
            logging.error(f"设置 equipment_armor 时出错: {e}，不更新该值")

    @property
    def equipment_weapon(self) -> str:
        try:
            return self.data.get('equipment_weapon', '')
        except (ValueError, TypeError) as e:
            logging.error(f"解析 equipment_weapon 时出错: {e}，返回默认值 0")
            return 0

    @equipment_weapon.setter
    def equipment_weapon(self, value: str):
        try:
            self.data['equipment_weapon'] = value
        except (ValueError, TypeError) as e:
            logging.error(f"设置 equipment_weapon 时出错: {e}，不更新该值")

    @property
    def last_fishing(self) -> str:
        try:
            return self.data.get('last_fishing', '')
        except Exception as e:
            logging.error(f"获取 last_fishing 时出错: {e}")
            return ''

    @last_fishing.setter
    def last_fishing(self, value: str):
        try:
            self.data['last_fishing'] = value
        except Exception as e:
            logging.error(f"设置 last_fishing 时出错: {e}，不更新该值")

    @property
    def equipped_fishing_rod(self) -> str:
        try:
            return self.data.get('equipped_fishing_rod', '')
        except Exception as e:
            logging.error(f"获取 equipped_fishing_rod 时出错: {e}")
            return ''

    @equipped_fishing_rod.setter
    def equipped_fishing_rod(self, value: str):
        try:
            self.data['equipped_fishing_rod'] = value
        except Exception as e:
            logging.error(f"设置 equipped_fishing_rod 时出错: {e}，不更新该值")

    @property
    def position(self) -> int:
        """获取玩家位置"""
        try:
            return int(self.data.get('position', 0))
        except (ValueError, TypeError) as e:
            logging.error(f"解析 position 时出错: {e}，返回默认值 0")
            return 0

    @position.setter
    def position(self, value: int):
        """设置玩家位置"""
        try:
            self.data['position'] = int(value)
        except (ValueError, TypeError) as e:
            logging.error(f"设置 position 时出错: {e}，不更新该值")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return self.data

    @classmethod
    def create_new(cls, user_id: str, nickname: str) -> 'Player':
        """创建新玩家"""
        data = {
            'user_id': user_id,
            'nickname': nickname,
            'gold': constants.PLAYER_BASE_GOLD,
            'level': 1,
            'sign_in_timestamp': 0,
            'inventory': '{}',
            'hp': constants.PLAYER_BASE_MAX_HP + constants.PLAYER_LEVEL_UP_APPEND_HP,
            'max_hp': constants.PLAYER_BASE_MAX_HP + constants.PLAYER_LEVEL_UP_APPEND_HP,
            'attack': constants.PLAYER_BASE_ATTACK + constants.PLAYER_LEVEL_UP_APPEND_ATTACK,
            'defense': constants.PLAYER_BASE_DEFENSE + constants.PLAYER_LEVEL_UP_APPEND_DEFENSE,
            'exp': 0,
            'max_exp': 0,
            'last_fishing': 0,
            'last_attack': 0,
            'adventure_last_attack': 0,
            'equipment_weapon': '',
            'equipment_armor': '',
            'equipment_fishing_rod': '',
            'multiple': '{}',
            'challenge_proposal': '',
            'is_pay_rent': 0,
            'position': 0
        }
        return cls(data)

    def get_inventory_display(self, content: str) -> str:
        """获取格式化的背包显示，支持分页，确保分类标题跨页连续"""

        if not self.inventory:
            return "🍃 背包是空的"

        # 从 content 中提取页码
        try:
            page_str = content.split("背包")[1].strip() if "背包" in content else "1"
            page_num = int(page_str) if page_str.isdigit() else 1
        except (IndexError, ValueError):
            page_num = 1

        # 按类型分类物品
        categorized_items = {
            "⚔️ 武器:": [],
            "🛡️ 防具:": [],
            "🎣 鱼竿:": [],
            "🎁 消耗品:": [],
            "📈 加成道具:": [],
            "🌌 特殊物品:": [],
            "🐟 鱼类:": [],
            "📦 其他物品:": [],
        }

        for item_name in self.inventory:
            item = self.inventory.get(item_name, {})
            item_type = item.get("type", "")
            item_amount = item.get("amount", 0)
            item_rarity = item.get("rarity", 0)
            item_level = item.get("level", 0)
            item_description = item.get("description", {}) if item_type == "fishing_rod" else None

            rarity_str = f"{constants.RARITY_EMOJIS[item_rarity]}" if item_type in ["weapon", "armor"] else ""
            item_level_str = f"[Lv.{item_level}]" if item_level > 0 else ""
            item_durability_str = f"[耐久度: {item_description['durability']}]" if item_description else ""

            item_str = f"{item_name}{item_level_str}{rarity_str}{item_durability_str} x{item_amount}"

            if item_type == "weapon":
                categorized_items["⚔️ 武器:"].append(item_str)
            elif item_type == "armor":
                categorized_items["🛡️ 防具:"].append(item_str)
            elif item_type == "fishing_rod":
                categorized_items["🎣 鱼竿:"].append(item_str)
            elif item_type == "consumable":
                categorized_items["🎁 消耗品:"].append(item_str)
            elif item_type in ["boor_potion", "coward_potion", "double_exp_card", "double_gold_card"]:
                categorized_items["📈 加成道具:"].append(item_str)
            elif item_type in ["name_change_card"]:
                categorized_items["🌌 特殊物品:"].append(item_str)
            elif item_type == "fish":
                categorized_items["🐟 鱼类:"].append(item_str)
            else:
                categorized_items["📦 其他物品:"].append(item_str)

        # 展平分类，同时保留标题与内容
        all_items = []
        for category, items in categorized_items.items():
            if items:
                all_items.append((category, items))

        # 分页逻辑
        items_per_page = 15
        paged_items = []
        current_page_items = []
        current_item_count = 0

        for category, items in all_items:
            # 如果当前页已经满了，保存并开启下一页
            if current_item_count + len(items) + 1 > items_per_page:
                if current_page_items:
                    paged_items.append(current_page_items)
                    current_page_items = []
                    current_item_count = 0

            # 如果当前页已有内容但放不下所有物品，继续拆分
            if current_item_count + len(items) + 1 > items_per_page:
                current_page_items.append(category)
                for item in items:
                    if current_item_count + 1 > items_per_page:
                        paged_items.append(current_page_items)
                        current_page_items = [category]
                        current_item_count = 0
                    current_page_items.append(f" └─ {item}")
                    current_item_count += 1
            else:
                # 正常加入当前页
                current_page_items.append(category)
                for item in items:
                    current_page_items.append(f" └─ {item}")
                    current_item_count += 1

        # 添加最后一页
        if current_page_items:
            paged_items.append(current_page_items)

        # 页码处理
        total_pages = len(paged_items)
        if page_num < 1 or page_num > total_pages:
            return f"⚠️ 页码无效，请输入正确的页码 (1 - {total_pages})"

        # 构造结果
        result = [f"🎒 背包物品 - 第 {page_num}/{total_pages} 页"]
        result.extend(paged_items[page_num - 1])

        if total_pages > 1:
            result.append("──────────────")
            result.append(f"💡 发送 背包 [页码] 查看指定页")

        return "\n".join(result)

    def has_item(self, item_name: str) -> bool:
        """检查是否拥有指定物品"""
        return item_name in self.inventory

    @classmethod
    def get_player(cls, player_info: dict) -> Optional['Player']:
        """从文件中获取玩家数据

        Args:
            user_id: 用户ID
            player_info: 从数据库读取到的玩家数据

        Returns:
            Optional[Player]: 玩家实例,如果未找到则返回 None
        """
        try:
            if player_info :
                return cls(player_info)
            else:
                return None
        except FileNotFoundError:
            logger.error(f"未获取到玩家信息")
            return None
        except Exception as e:
            logger.error(f"获取玩家信息出错: {e}")
            return None

    def get_exp_for_next_level(self, level):
        """
        计算当前等级升级到下一等级所需的经验值
        :param level: 当前等级 (int)
        :param growth_factor: 经验增长因子 (默认1.5，非线性增长)
        :return: 当前等级升级到下一级所需的经验值 (int)
        """
        if level < 1:
            raise ValueError("等级必须大于等于 1")
        base_exp = constants.PLAYER_BASE_EXP

        if level <= 10:
            # 前10级使用较低的增长因子，实现快速升级
            required_exp = int(base_exp * (level ** 1.1))
        elif level > 10 and level <= 20:
            # 增长因子递增
            required_exp = int(base_exp * (level ** 1.2))
        elif level > 20 and level <= 30:
            # 增长因子递增
            required_exp = int(base_exp * (level ** 1.3))
        elif level > 30 and level <= 40:
            # 增长因子递增
            required_exp = int(base_exp * (level ** 1.4))
        elif level > 40 and level <= 50:
            # 增长因子递增
            required_exp = int(base_exp * (level ** 1.5))
        elif level > 50 and level <= 60:
            # 增长因子递增
            required_exp = int(base_exp * (level ** 1.6))
        elif level > 60 and level <= 70:
            # 增长因子递增
            required_exp = int(base_exp * (level ** 1.7))
        elif level > 70 and level <= 80:
            # 增长因子递增
            required_exp = int(base_exp * (level ** 1.8))
        elif level > 80 and level <= 90:
            # 增长因子递增
            required_exp = int(base_exp * (level ** 1.9))
        else:
            # 90-100
            required_exp = int(base_exp * (level ** 2))

        return required_exp

    def get_player_status(self, detail) -> str:
        """获取家状态

        Args:
            user_id: 用户ID
            items_info: 物品信息字典

        Returns:
            str: 格式化的玩家状态信息
        """

        status = []

        # 记录玩家基础属性
        needs_update = False
        update_info = {}
        player_level = self.level
        player_exp = self.exp
        player_hp = self.hp
        player_max_hp = self.max_hp
        player_attack = self.attack
        player_defense = self.defense

        # 检查玩家当前加成情况
        attack_multiple = 1
        defense_multiple = 1
        max_hp_multiple = 1
        attack_multiple_str = ""
        defense_multiple_str = ""
        max_hp_multiple_str = ""
        exp_multiple_str = ""
        gold_multiple_str = ""
        multiple = self.multiple

        # 获取装备加成
        equipped_weapon = self.game.rouge_equipment_system.get_equipment_by_id(self.equipment_weapon)
        equipped_armor = self.game.rouge_equipment_system.get_equipment_by_id(self.equipment_armor)
        equipped_fishing_rod = self.equipment_fishing_rod
        max_hp_bonus = 0
        attack_bonus = 0
        defense_bonus = 0
        # 获取武器加成
        if equipped_weapon:
            # 获取装备等级
            item_level = equipped_weapon.get('level', 1)
            # 获取稀有度
            item_rarity = equipped_weapon.get('rarity', 1)
            rarity_str = f"[lv.{item_level}]{constants.RARITY_EMOJIS[item_rarity]}"
            # 获取装备三维加成
            weapon_stats = []
            if equipped_weapon.get('attack_bonus', 0) != 0:
                weapon_stats.append(f"⚔️{equipped_weapon['attack_bonus']}")
                # 获取攻击加成
                attack_bonus = int(equipped_weapon['attack_bonus'])
            # 获取技能词条
            skills = equipped_weapon.get('skills', [])
            skill_str = []
            if skills:
                for skill in skills:
                    skill_str.append(f"      - [{skill.get('name', '未知技能')}] {skill.get('description', '无描述')} {skill.get('trigger_probability', 0)}% 概率发动。")
                attribute_info = "\n".join(skill_str)
                skill_section = f"\n      技能：\n{attribute_info}"
            else:
                # 如果没有技能，置空技能部分
                skill_section = ""

            # 格式化装备说明
            if detail:
                # 详细说明
                weapon_str = f"{equipped_weapon['name']}{rarity_str}\n      加成：{'/'.join(weapon_stats)}{skill_section}"
            else:
                # 简单说明
                weapon_str = f"{equipped_weapon['name']}{rarity_str}"
        else:
            weapon_str = "无"

        # 获取护甲加成
        if equipped_armor:
            # 获取装备等级
            item_level = equipped_armor.get('level', 1)
            # 获取稀有度
            item_rarity = equipped_armor.get('rarity', 1)
            rarity_str = f"[lv.{item_level}]{constants.RARITY_EMOJIS[item_rarity]}"
            # 获取装备三维加成
            armor_stats = []
            if equipped_armor.get('defense_bonus', 0) != 0:
                armor_stats.append(f"🛡️{equipped_armor['defense_bonus']}")
                # 获取防御加成
                defense_bonus = int(equipped_armor['defense_bonus'])
            if equipped_armor.get('max_hp_bonus', 0) != 0:
                armor_stats.append(f"❤️{equipped_armor['max_hp_bonus']}")
                # 获取最大生命加成
                max_hp_bonus = int(equipped_armor['max_hp_bonus'])
            # 获取技能词条
            skills = equipped_armor.get('skills', [])
            skill_str = []
            if skills:
                for skill in skills:
                    skill_str.append(f"      - [{skill.get('name', '未知技能')}] {skill.get('description', '无描述')} {skill.get('trigger_probability', 0)}% 概率发动。")
                attribute_info = "\n".join(skill_str)
                skill_section = f"\n      技能：\n{attribute_info}"
            else:
                # 如果没有技能，置空技能部分
                skill_section = ""
            # 格式化装备说明
            if detail:
                # 详细说明
                armor_str = f"{equipped_armor['name']}{rarity_str}\n      加成：{'/'.join(armor_stats)}{skill_section}"
            else:
                # 简单说明
                armor_str = f"{equipped_armor['name']}{rarity_str}"
        else:
            armor_str = "无"

        # 检查玩家等级
        if player_level > constants.PLAYER_MAX_LEVEL:
            # 玩家等级异常，需要修正
            player_level = constants.PLAYER_MAX_LEVEL
            player_exp = self.get_exp_for_next_level(constants.PLAYER_MAX_LEVEL)
            needs_update = True

        # 获取玩家加成
        if multiple:
            # 计算加成
            attack_multiple, attack_multiple_str = get_multiple('attack', multiple)
            defense_multiple, defense_multiple_str = get_multiple('defense', multiple)
            max_hp_multiple, max_hp_multiple_str = get_multiple('max_hp', multiple)
            exp_multiple_str = get_multiple('exp', multiple)[1]
            gold_multiple_str = get_multiple('gold', multiple)[1]

        # 理论血量上限
        theory_max_hp = int(((player_level * constants.PLAYER_LEVEL_UP_APPEND_HP + constants.PLAYER_BASE_MAX_HP) + max_hp_bonus) * max_hp_multiple)
        # 检查玩家血量上限是否符合预期
        if player_max_hp != theory_max_hp:
            # 血量上限异常，需要修正
            player_max_hp = theory_max_hp
            # 调整当前血量
            if player_hp > player_max_hp:
                player_hp = player_max_hp
            needs_update = True

        # 理论攻击力
        theory_attack = int(((player_level * constants.PLAYER_LEVEL_UP_APPEND_ATTACK + constants.PLAYER_BASE_ATTACK) + attack_bonus) * attack_multiple)
        # 检查玩家攻击力是否符合预期
        if player_attack != theory_attack:
            # 攻击力异常，需要修正
            player_attack = theory_attack
            needs_update = True

        # 理论防御力
        theory_defense = int(((player_level * constants.PLAYER_LEVEL_UP_APPEND_DEFENSE + constants.PLAYER_BASE_DEFENSE) + defense_bonus) * defense_multiple)
        # 检查玩家防御力是否符合预期
        if player_defense != theory_defense:
            # 防御力异常，需要修正
            player_defense = theory_defense
            needs_update = True

        if needs_update:
            update_info['level'] = str(player_level)
            update_info['exp'] = str(player_exp)
            update_info['hp'] = str(player_hp)
            update_info['max_hp'] = str(player_max_hp)
            update_info['attack'] = str(player_attack)
            update_info['defense'] = str(player_defense)

        # 构建状态信息
        status = [
            f"🏷️ 玩家: {self.nickname}",
            f"💳 余额: {self.gold}",
            f"📈 等级: {player_level}",
            f"📚 经验: {player_exp}/{int(self.get_exp_for_next_level(self.level))}",
            f"❤️ 生命: {player_hp}/{player_max_hp}",
            f"⚔️ 攻击力: {player_attack}",
            f"🛡️ 防御力: {player_defense}",
        ]

        # 如果发现异常，更新数据
        if needs_update:
            self.game._update_player_data(self.user_id, update_info)
            status.insert(1, "⚠️ 检测到玩家异常，已自动修正")

        # 检查玩家是否装备武器
        if equipped_weapon:
            status.append(f"🗡️ 装备武器: {weapon_str}")

        # 检查玩家是否装备防具
        if equipped_armor:
            status.append(f"🎽 装备护甲: {armor_str}")

        # 如果装备了鱼竿，显示鱼竿信息
        if equipped_fishing_rod:
            # rod_durability = self.rod_durability.get(equipped_fishing_rod, 100)
            # status.append(f"🎣 装备鱼竿: {equipped_fishing_rod} [耐久度:{rod_durability}%]")
            fishing_rod = self.equipment_fishing_rod
            fishing_rod_name = fishing_rod.get('name', '未知鱼竿')
            fishing_rod_description = fishing_rod.get("description", {})
            status.append(f"🎣 装备鱼竿: {fishing_rod_name} [耐久度: {fishing_rod_description['durability']}]")

        # 构建非空加成的列表
        additions = [
            f"📊 加成: {attack_multiple_str}" if attack_multiple_str else "",
            defense_multiple_str if defense_multiple_str else "",
            max_hp_multiple_str if max_hp_multiple_str else "",
            gold_multiple_str if gold_multiple_str else "",
            exp_multiple_str if exp_multiple_str else "",
        ]

        # 过滤掉空字符串，并用 | 拼接
        additions_str = "|".join(filter(lambda x: x != "", additions))

        # 如果最终有内容才添加到 status
        if additions_str:
            status.append(additions_str)

        if self.challenge_proposal:
            # 如果玩家有挑战者，打印挑战者的信息
            challenge = self.game.get_player(self.challenge_proposal)
            if challenge:
                status.append(f"🥊 挑战者: {challenge.nickname}[Lv.{challenge.level}]")
            else:
                # 如果找不到挑战者，打印错误信息
                status.append(f"🥊 挑战者: 无效的挑战者ID[{self.challenge_proposal}]")

        return "\n".join(status)
