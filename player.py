import os
import csv
import json
import time
import shutil
import logging
from datetime import datetime
from collections import Counter
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)
PLAYER_MAX_LEVEL = 81


class Player:
    """玩家类,用于管理玩家属性和状态"""
    def __init__(self, data: Dict[str, Any], player_file: str = None, standard_fields: list = None):
        if not isinstance(data, dict):
            raise TypeError("data must be a dictionary")
        self.data = data
        self.player_file = player_file
        self.standard_fields = standard_fields

        # 清理耐久度为0的记录
        if 'rod_durability' in self.data:
            rod_durability = json.loads(self.data['rod_durability'])
            cleaned_durability = {rod: durability for rod, durability in rod_durability.items() if int(durability) > 0}
            self.data['rod_durability'] = json.dumps(cleaned_durability)

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
    def inventory(self) -> list:
        inventory_str = self.data.get('inventory', '[]')
        try:
            return json.loads(inventory_str)
        except json.JSONDecodeError as e:
            logging.error(f"JSON解析错误: {e}，Inventory内容: {inventory_str}")
            return []  # 返回一个空列表或其他默认值
        except Exception as e:
            logging.error(f"解析 inventory 时出错: {e}，返回默认值 []")
            return []

    @inventory.setter
    def inventory(self, value: list):
        try:
            self.data['inventory'] = json.dumps(value)
        except (TypeError, ValueError) as e:
            logging.error(f"设置 inventory 时出错: {e}，不更新该值")

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
    def spouse(self) -> str:
        try:
            return self.data.get('spouse', '')
        except Exception as e:
            logging.error(f"获取 spouse 时出错: {e}")
            return ''

    @spouse.setter
    def spouse(self, value: str):
        try:
            self.data['spouse'] = value
        except Exception as e:
            logging.error(f"设置 spouse 时出错: {e}，不更新该值")

    @property
    def marriage_proposal(self) -> str:
        try:
            return self.data.get('marriage_proposal', '')
        except Exception as e:
            logging.error(f"获取 marriage_proposal 时出错: {e}")
            return ''

    @marriage_proposal.setter
    def marriage_proposal(self, value: str):
        try:
            self.data['marriage_proposal'] = value
        except Exception as e:
            logging.error(f"设置 marriage_proposal 时出错: {e}，不更新该值")

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
    def last_checkin(self) -> str:
        try:
            return self.data.get('last_checkin', '')
        except Exception as e:
            logging.error(f"获取 last_checkin 时出错: {e}")
            return ''

    @last_checkin.setter
    def last_checkin(self, value: str):
        try:
            self.data['last_checkin'] = value
        except Exception as e:
            logging.error(f"设置 last_checkin 时出错: {e}，不更新该值")

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
    def rod_durability(self) -> Dict:
        rod_str = self.data.get('rod_durability', '{}')
        try:
            return json.loads(rod_str)
        except json.JSONDecodeError as e:
            logging.error(f"JSON解析 rod_durability 时出错: {e}，内容: {rod_str}")
            return {}
        except Exception as e:
            logging.error(f"解析 rod_durability 时出错: {e}，返回默认值 {{}}")
            return {}

    @rod_durability.setter
    def rod_durability(self, value: Dict):
        try:
            self.data['rod_durability'] = json.dumps(value)
        except (TypeError, ValueError) as e:
            logging.error(f"设置 rod_durability 时出错: {e}，不更新该值")

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
    def last_item_use(self) -> int:
        """获取上次使用物品的时间"""
        try:
            return int(self.data.get('last_item_use', '0'))
        except (ValueError, TypeError) as e:
            logging.error(f"解析 last_item_use 时出错: {e}，返回默认值 0")
            return 0

    @last_item_use.setter
    def last_item_use(self, value: int):
        """设置上次使用物品的时间"""
        try:
            self.data['last_item_use'] = str(int(value))
        except (ValueError, TypeError) as e:
            logging.error(f"设置 last_item_use 时出错: {e}，不更新该值")

    @property
    def position(self) -> int:
        """获取玩家位置"""
        try:
            return int(self.data.get('position', '0'))
        except (ValueError, TypeError) as e:
            logging.error(f"解析 position 时出错: {e}，返回默认值 0")
            return 0

    @position.setter
    def position(self, value: int):
        """设置玩家位置"""
        try:
            self.data['position'] = str(int(value))
        except (ValueError, TypeError) as e:
            logging.error(f"设置 position 时出错: {e}，不更新该值")

    def update_data(self, updates: Dict[str, Any]) -> None:
        """更新玩家数据并保存到文件"""
        if not self.player_file or not self.standard_fields:
            raise ValueError("player_file and standard_fields must be set")

        # 更新内存中的数据
        self.data.update(updates)

        # 验证数据
        if not self.validate_data():
            raise ValueError("Invalid player data after update")

        try:
            # 读取所有玩家数据
            players_data = []
            with open(self.player_file, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['user_id'] != self.user_id:
                        players_data.append(row)

            # 添加更新后的玩家数据
            players_data.append(self.data)

            # 写回文件
            with open(self.player_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.standard_fields, quoting=csv.QUOTE_ALL)
                writer.writeheader()
                writer.writerows(players_data)

        except Exception as e:
            logger.error(f"更新玩家数据出错: {e}")
            raise

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return self.data

    @classmethod
    def create_new(cls, user_id: str, nickname: str) -> 'Player':
        """创建新玩家"""
        data = {
            'user_id': user_id,
            'nickname': nickname,
            'gold': '3000',
            'level': '1',
            'last_checkin': '',
            'inventory': '[]',
            'hp': '100',
            'max_hp': '100',
            'attack': '10',
            'defense': '5',
            'exp': '0',
            'last_fishing': '',
            'rod_durability': '{}',
            'equipped_weapon': '',
            'equipped_armor': '',
            'last_item_use': '0',
            'spouse': '',
            'marriage_proposal': '',
            'challenge_proposal': '',
            'last_attack': '0',
            'adventure_last_attack': '0',
            'position': '0'
        }
        return cls(data)

    def get_inventory_display(self, items_info: dict) -> str:
        """获取格式化的背包显示"""
        if not self.inventory:
            return "背包是空的"

        # 统计物品数量
        item_counts = Counter(self.inventory)

        # 按类型分类物品
        weapons = []
        armors = []
        consumables = []
        fish = []
        fishing_rods = []
        others = []

        for item_name, count in item_counts.items():
            item_info = items_info.get(item_name, {})
            stats = []

            # 获取物品属性
            if item_info.get('hp', '0') != '0':
                stats.append(f"生命值增加{item_info['hp']}")
            if item_info.get('attack', '0') != '0':
                stats.append(f"攻击力增加{item_info['attack']}")
            if item_info.get('defense', '0') != '0':
                stats.append(f"防御力增加{item_info['defense']}")

            stats_str = f"({', '.join(stats)})" if stats else ""
            equipped_str = ""

            if item_name == self.equipped_weapon:
                equipped_str = "⚔️已装备"
            elif item_name == self.equipped_armor:
                equipped_str = "🛡️已装备"
            elif item_name == self.equipped_fishing_rod:
                equipped_str = "🎣已装备"

            durability_str = ""
            if item_info.get('type') == 'fishing_rod':
                durability = self.rod_durability.get(item_name, 100)
                durability_str = f" [耐久度:{durability}%]"

            item_str = f"{item_name} x{count} {equipped_str} {stats_str}{durability_str}"

            # 根据物品类型分类
            item_type = item_info.get('type', '')
            if item_type == 'weapon':
                weapons.append(item_str)
            elif item_type == 'armor':
                armors.append(item_str)
            elif item_type == 'consumable':
                consumables.append(item_str)
            elif item_type == 'fishing_rod':
                fishing_rods.append(item_str)
            elif item_type == 'fish':
                fish.append(item_str)
            else:
                others.append(item_str)

        # 生成背包显示
        inventory_list = ["🎒 背包物品\n"]

        if weapons:
            inventory_list.append("⚔️ 武器:")
            inventory_list.extend(f"  {w}" for w in weapons)
            inventory_list.append("")

        if armors:
            inventory_list.append("🛡️ 防具:")
            inventory_list.extend(f"  {a}" for a in armors)
            inventory_list.append("")

        if fishing_rods:
            inventory_list.append("🎣 鱼竿:")
            inventory_list.extend(f"  {r}" for r in fishing_rods)
            inventory_list.append("")

        if consumables:
            inventory_list.append("🎁 消耗品:")
            inventory_list.extend(f"  {c}" for c in consumables)
            inventory_list.append("")

        if fish:
            inventory_list.append("🐟 鱼类:")
            inventory_list.extend(f"  {f}" for f in fish)
            inventory_list.append("")

        if others:
            inventory_list.append("📦 其他物品:")
            inventory_list.extend(f"  {o}" for o in others)

        return "\n".join(inventory_list).strip()

    def has_item(self, item_name: str) -> bool:
        """检查是否拥有指定物品"""
        return item_name in self.inventory

    @classmethod
    def get_player(cls, user_id: str, player_file: str) -> Optional['Player']:
        """从文件中获取玩家数据

        Args:
            user_id: 用户ID
            player_file: 玩家数据文件路径

        Returns:
            Optional[Player]: 玩家实例,如果未找到则返回 None
        """
        try:
            with open(player_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['user_id'] == str(user_id):
                        logger.info(f"找到用户ID为 {user_id} 的玩家数据")
                        return cls(row)
            logger.warning(f"未找到用户ID为 {user_id} 的玩家数据")
            return None
        except FileNotFoundError:
            logger.error(f"玩家数据文件 {player_file} 未找到")
            return None
        except Exception as e:
            logger.error(f"获取玩家数据出错: {e}")
            return None

    def save_player_data(self, player_file: str, standard_fields: list) -> None:
        """保存玩家数据到CSV文件

        Args:
            player_file: 玩家数据文件路径
            standard_fields: 标准字段列表
        """
        try:
            # 读取所有玩家数据
            players_data = []
            with open(player_file, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['user_id'] != self.user_id:
                        players_data.append(row)

            # 添加更新后的玩家数据
            players_data.append(self.to_dict())

            # 写回文件
            with open(player_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=standard_fields, quoting=csv.QUOTE_ALL)
                writer.writeheader()
                writer.writerows(players_data)

        except Exception as e:
            logger.error(f"保存玩家数据出错: {e}")
            raise

    def validate_data(self) -> bool:
        """验证玩家数据的完整性"""
        required_fields = {
            'user_id': str,
            'nickname': str,
            'gold': (str, int),
            'level': (str, int),
            'hp': (str, int),
            'max_hp': (str, int),
            'attack': (str, int),
            'defense': (str, int),
            'exp': (str, int),
            'position': (str, int)
        }

        try:
            for field, types in required_fields.items():
                if field not in self.data:
                    logger.error(f"Missing required field: {field}")
                    return False

                value = self.data[field]
                if isinstance(types, tuple):
                    if not isinstance(value, types):
                        try:
                            # 尝试转换为字符串
                            self.data[field] = str(value)
                        except:
                            logger.error(f"Invalid type for field {field}: {type(value)}")
                            return False
                else:
                    if not isinstance(value, types):
                        logger.error(f"Invalid type for field {field}: {type(value)}")
                        return False
            return True
        except Exception as e:
            logger.error(f"Data validation error: {e}")
            return False

    def _backup_data(self):
        """创建数据文件的备份"""
        if not self.player_file:
            return

        backup_dir = os.path.join(os.path.dirname(self.player_file), 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'players_{timestamp}.csv')

        try:
            shutil.copy2(self.player_file, backup_file)
        except Exception as e:
            logger.error(f"创建数据备份失败: {e}")

    def get_exp_for_next_level(self, level, base_exp=200, growth_factor=2):
        """
        计算当前等级升级到下一等级所需的经验值
        :param level: 当前等级 (int)
        :param base_exp: 一级所需基础经验值 (默认100)
        :param growth_factor: 经验增长因子 (默认1.5，非线性增长)
        :return: 当前等级升级到下一级所需的经验值 (int)
        """
        if level < 1:
            raise ValueError("等级必须大于等于 1")

        # 二次增长公式计算升级经验
        required_exp = int(base_exp * (level ** growth_factor))
        return required_exp

    def get_player_status(self, items_info: dict) -> str:
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
        updates = {}
        player_level = self.level
        player_exp = self.exp
        player_hp = self.hp
        player_max_hp = self.max_hp
        player_attack = self.attack
        player_defense = self.defense

        # 获取装备加成
        equipped_weapon = self.equipped_weapon
        equipped_armor = self.equipped_armor
        equipped_fishing_rod = self.equipped_fishing_rod

        # 获取武器加成
        if equipped_weapon and equipped_weapon in items_info:
            weapon_info = items_info[equipped_weapon]

            weapon_stats = []
            if weapon_info.get('attack', '0') != '0':
                weapon_stats.append(f"⚔️:{weapon_info['attack']}%")
            if weapon_info.get('defense', '0') != '0':
                weapon_stats.append(f"🛡️:{weapon_info['defense']}%")
            weapon_str = f"{equipped_weapon}({', '.join(weapon_stats)})" if weapon_stats else equipped_weapon
        else:
            weapon_str = "无"

        # 获取护甲加成
        if equipped_armor and equipped_armor in items_info:
            armor_info = items_info[equipped_armor]
            armor_stats = []
            if armor_info.get('attack', '0') != '0':
                armor_stats.append(f"⚔️:{armor_info['attack']}%")
            if armor_info.get('defense', '0') != '0':
                armor_stats.append(f"🛡️:{armor_info['defense']}%")
            if armor_info.get('hp', '0') != '0':
                armor_stats.append(f"❤️:{armor_info['hp']}%")
            armor_str = f"{equipped_armor}({', '.join(armor_stats)})" if armor_stats else equipped_armor
        else:
            armor_str = "无"

        # 检查玩家等级
        if player_level > PLAYER_MAX_LEVEL:
            # 玩家等级异常，需要修正
            player_level = PLAYER_MAX_LEVEL
            player_exp = self.get_exp_for_next_level(PLAYER_MAX_LEVEL)
            needs_update = True

        # 理论血量上限
        theory_max_hp = int((player_level * 50) * (1 + int(armor_info['hp'])/100))
        # 检查玩家血量上限是否符合预期
        if player_max_hp != theory_max_hp:
            # 血量上限异常，需要修正
            player_max_hp = theory_max_hp
            # 调整当前血量
            if player_hp > player_max_hp:
                player_hp = player_max_hp
            needs_update = True

        # 理论攻击力
        theory_attack = int((player_level * 10) * (1 + int(weapon_info['attack'])/100))
        # 检查玩家攻击力是否符合预期
        if player_attack != theory_attack:
            # 攻击力异常，需要修正
            player_attack = theory_attack
            needs_update = True

        # 理论防御力
        theory_defense = int((player_level * 10) * (1 + int(armor_info['defense'])/100))
        # 检查玩家防御力是否符合预期
        if player_defense != theory_defense:
            # 防御力异常，需要修正
            player_defense = theory_defense
            needs_update = True

        if needs_update:
            updates['level'] = str(player_level)
            updates['exp'] = str(player_exp)
            updates['hp'] = str(player_hp)
            updates['max_hp'] = str(player_max_hp)
            updates['attack'] = str(player_attack)
            updates['defense'] = str(player_defense)

        # 婚姻状态
        spouses = self.spouse.split(',') if self.spouse else []
        spouses = [s for s in spouses if s]  # 过滤空字符串

        if spouses:
            marriage_status = f"已婚 (配偶: {', '.join(spouses)})"
        else:
            marriage_status = "单身"

        if self.marriage_proposal:
            # 获取求婚者的昵称
            proposer = self.get_player(self.marriage_proposal, self.player_file)
            if proposer:
                proposer_name = proposer.nickname
            else:
                proposer_name = f"@{self.marriage_proposal}"
            marriage_status += f"\n💝 收到来自 {proposer_name} 的求婚"

        # 构建状态信息
        status = [
            f"🏷️ 玩家: {self.nickname}",
            f"💰 金币: {self.gold}",
            f"📊 等级: {player_level}",
            f"✨ 经验: {player_exp}/{int(self.get_exp_for_next_level(self.level))}",
            f"❤️ 生命值: {player_hp}/{player_max_hp}",  # 修改生命值显示
            f"⚔️ 攻击力: {player_attack}",
            f"🛡️ 防御力: {player_defense}",
            f"🗡️ 装备武器: {weapon_str}",
            f"⛓️ 装备护甲: {armor_str}",
            f"💕 婚姻状态: {marriage_status}"
        ]

        # 如果发现异常，更新数据
        if needs_update:
            self.update_data(updates)
            status.insert(1, "⚠️ 检测到玩家异常，已自动修正")

        # 如果装备了鱼竿，显示鱼竿信息
        if equipped_fishing_rod:
            rod_durability = self.rod_durability.get(equipped_fishing_rod, 100)
            status.append(f"🎣 装备鱼竿: {equipped_fishing_rod} [耐久度:{rod_durability}%]")

        return "\n".join(status)

    @classmethod
    def get_player_by_nickname(cls, nickname: str, player_file: str) -> Optional['Player']:
        """根据昵称查找玩家

        Args:
            nickname: 玩家昵称
            player_file: 玩家数据文件路径

        Returns:
            Optional[Player]: 玩家实例,如果未找到则返回 None
        """
        try:
            with open(player_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['nickname'] == nickname:
                        logger.info(f"找到昵称为 {nickname} 的玩家数据")
                        return cls(row)
            logger.warning(f"未找到昵称为 {nickname} 的玩家数据")
            return None
        except FileNotFoundError:
            logger.error(f"玩家数据文件 {player_file} 未找到")
            return None
        except Exception as e:
            logger.error(f"根据昵称获取玩家数据出错: {e}")
            return None
