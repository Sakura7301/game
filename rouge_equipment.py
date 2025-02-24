import os
import json
import time
import uuid
import sqlite3
import random
import secrets
from . import constants
from common.log import logger
from typing import Optional, Dict, Any


class RougeEquipment:
    """
    随机装备生成类：
        可以根据等级随机生成不同品质的武器和防具
    """

    def __init__(self, game):
        # 检查data目录
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        self.rouge_equipment_db_path = os.path.join(self.data_dir, "rouge_equipment.db")

        self.game = game
        # 技能触发次数
        self.SKILL_TRIGGER_ONCE = 1
        self.SKILL_TRIGGER_MULTIPLE = 999

        # 技能持续回合数
        self.SKILL_NON_CONTINUOUS = 0

        # 技能依赖属性
        self.SKILL_DEPEND_ON_NONE = 0
        self.SKILL_DEPEND_ON_SELF_HP = 1
        self.SKILL_DEPEND_ON_SELF_ATTACK = 2
        self.SKILL_DEPEND_ON_SELF_DEFENSE = 3
        self.SKILL_DEPEND_ON_OPPONENT_ATTACK = 4
        self.SKILL_DEPEND_ON_OPPONENT_DEFENSE = 5

        # 通用技能集合
        self.COMMON_SKILLS = [
            self.make_skill_general_active_immunity,
            self.make_skill_general_precedence_immunity,
            self.make_skill_general_promoting_attributes,
            self.make_skill_general_weaken_attributes,
        ]

        # 武器专属技能集合
        self.WEAPON_SKILLS = [
            self.make_skill_weapon_once_damage,
            self.make_skill_weapon_duration_damage,
            self.make_skill_weapon_real_damage,
            self.make_skill_weapon_once_life_steal,
            self.make_skill_weapon_duration_life_steal,
            self.make_skill_paralysis
        ]

        # 防具专属技能集合
        self.ARMOR_SKILLS = [
            self.make_skill_armor_reflect,
            self.make_skill_armor_assimilate,
            self.make_skill_armor_shield,
            self.make_skill_armor_once_heal,
            self.make_skill_armor_duration_heal,
        ]

        # 连接到SQLite数据库
        try:
            self._connect()
            self._initialize_database()
        except sqlite3.Error as e:
            logger.error(f"数据库连接或初始化失败: {e}")
            raise

    def _connect(self) -> None:
        """
        连接到 SQLite 数据库，启用 WAL 模式以提高并发性，并启用外键约束。
        """
        try:
            conn = sqlite3.connect(self.rouge_equipment_db_path, check_same_thread=False)
            # 通过列名访问数据
            conn.row_factory = sqlite3.Row
            self.conn = conn
            logger.debug("成功连接到Rouge装备数据库。")
        except sqlite3.Error as e:
            logger.error(f"连接数据库失败: {e}")
            raise

    def _initialize_database(self) -> None:
        """
        创建 equipment 表，如果它尚不存在。
        """
        create_table_query = """
        CREATE TABLE IF NOT EXISTS equipment (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            name TEXT NOT NULL,
            rarity INTEGER,
            rarity_str TEXT,
            level INTEGER,
            attack_bonus INTEGER,
            defense_bonus INTEGER,
            max_hp_bonus INTEGER,
            price INTEGER,
            skills TEXT  -- 使用 TEXT 类型存储 JSON 数据
        );
        """
        try:
            with self.conn:
                self.conn.execute(create_table_query)
            logger.debug("成功初始化数据库表。")
        except sqlite3.Error as e:
            logger.error(f"初始化数据库表失败: {e}")
            raise

    def insert_equipment(self, equipment_data: Dict[str, Any]) -> None:
        """
        插入新的装备数据。

        :param equipment_data: 包含装备信息的字典
        :raises sqlite3.IntegrityError: 如果装备 ID 已存在
        """
        insert_query = """
        INSERT INTO equipment (
            id, type, name, rarity, rarity_str, level, attack_bonus, defense_bonus, max_hp_bonus, price, skills
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        try:
            with self.conn:
                self.conn.execute(insert_query, (
                    equipment_data['id'],
                    equipment_data['type'],
                    equipment_data['name'],
                    equipment_data.get('rarity', 0),
                    equipment_data.get('rarity_str', ''),
                    equipment_data.get('level', 0),
                    equipment_data.get('attack_bonus', 0),
                    equipment_data.get('defense_bonus', 0),
                    equipment_data.get('max_hp_bonus', 0),
                    equipment_data.get('price', 0),
                    json.dumps(equipment_data.get('skills', []), ensure_ascii=False)
                ))
            logger.debug(f"成功插入装备 ID: {equipment_data['id']}")
        except sqlite3.IntegrityError as e:
            logger.error(f"插入装备失败，可能是重复的 ID: {equipment_data['id']}，错误: {e}")
            raise
        except sqlite3.Error as e:
            logger.error(f"插入装备时发生数据库错误: {e}")
            raise
        except (TypeError, ValueError) as e:
            logger.error(f"插入装备时数据格式错误: {e}")
            raise

    def get_equipment_by_id(self, equipment_id: str) -> Optional[Dict[str, Any]]:
        """
        根据装备 ID 查询装备信息。

        :param equipment_id: 装备的唯一标识符
        :return: 包含装备信息的字典，或 None 如果未找到
        """
        select_query = "SELECT * FROM equipment WHERE id = ?;"
        try:
            cursor = self.conn.cursor()
            cursor.execute(select_query, (equipment_id,))
            row = cursor.fetchone()
            cursor.close()
            if row:
                try:
                    skills = json.loads(row['skills']) if row['skills'] else []
                except json.JSONDecodeError:
                    logger.warning(f"装备 ID {equipment_id} 的技能数据 JSON 解析失败。返回空列表。")
                    skills = []
                equipment = {
                    'id': row['id'],
                    'type': row['type'],
                    'name': row['name'],
                    'rarity': row['rarity'],
                    'rarity_str': row['rarity_str'],
                    'level': row['level'],
                    'attack_bonus': row['attack_bonus'],
                    'defense_bonus': row['defense_bonus'],
                    'max_hp_bonus': row['max_hp_bonus'],
                    'price': row['price'],
                    'skills': skills
                }
                logger.info(f"成功获取装备， ID: {equipment_id}")
                return equipment
            else:
                logger.info(f"未找到装备， ID: {equipment_id}")
                return None
        except sqlite3.Error as e:
            logger.error(f"查询装备 ID {equipment_id} 时发生数据库错误: {e}")
            return None

    def close(self) -> None:
        """
        关闭数据库连接。
        """
        try:
            self.conn.close()
            logger.info("成功关闭数据库连接。")
        except sqlite3.Error as e:
            logger.error(f"关闭数据库连接时发生错误: {e}")
            raise

    def generate_id(self):
        """
        生成一个24字节的唯一装备ID，包含小写字母和数字。

        Returns:
            str: 唯一的24字节长装备ID
        """
        while True:
            # 生成随机ID
            new_id = ''.join(secrets.choice(self.charset) for _ in range(self.id_length))
            # 如果ID不在已生成集合中
            if new_id not in self.generated_ids:
                self.generated_ids.add(new_id)  # 记录新生成的ID
                return new_id

    def make_skill_weapon_once_damage(self, factor):
        """
        一次性伤害技能示例：
        - trigger_probability: 20% ~ 50%
        - duration: 0(不需要持续)
        """
        skill_name = random.choice(constants.SKILL_NAMES["once_damage"])
        damage = random.uniform(0.8, 2.5) + factor/2
        prob = random.randint(20, 50) + int(factor * 5)

        return {
            "name": skill_name,
            "skill_type": "once_damage",
            "limit_of_times": self.SKILL_TRIGGER_MULTIPLE,
            "trigger_probability": prob,
            "dependent_properties": self.SKILL_DEPEND_ON_SELF_ATTACK,
            "value": damage,
            "duration": self.SKILL_NON_CONTINUOUS,
            "description": f"造成当前攻击 {damage:.1f} 倍 的伤害。"
        }

    def make_skill_weapon_real_damage(self, factor):
        """
        真实伤害技能示例：
        - trigger_probability: 20% ~ 40%
        - duration: 0(不需要持续)
        """
        skill_name = random.choice(constants.SKILL_NAMES["real_damage"])
        damage = random.uniform(0.5, 2) + factor/2
        prob = random.randint(20, 40) + int(factor * 5)

        return {
            "name": skill_name,
            "skill_type": "real_damage",
            "limit_of_times": self.SKILL_TRIGGER_MULTIPLE,
            "trigger_probability": prob,
            "dependent_properties": self.SKILL_DEPEND_ON_SELF_ATTACK,
            "value": damage,
            "duration": self.SKILL_NON_CONTINUOUS,
            "description": f"造成当前攻击 {damage:.1f} 倍 的真实伤害。"
        }

    def make_skill_weapon_duration_damage(self, factor):
        """
        持续性伤害技能示例：
        - duration: 2 ~ 4 回合
        - trigger_probability: 20% ~ 50%
        """
        skill_name = random.choice(constants.SKILL_NAMES["duration_damage"])
        damage = random.randint(10, 30) + int(factor/2)
        duration = random.randint(2, 4)
        prob = random.randint(20, 50) + int(factor * 5)

        return {
            "name": skill_name,
            "skill_type": "duration_damage",
            "limit_of_times": self.SKILL_TRIGGER_MULTIPLE,
            "trigger_probability": prob,
            "dependent_properties": self.SKILL_DEPEND_ON_SELF_ATTACK,
            "value": damage,
            "duration": duration,
            "description": f"每回合造成当前攻击 {damage}% 伤害，持续 {duration} 回合。"
        }

    def make_skill_armor_shield(self, factor):
        """
        护盾技能示例：
        - duration: 1 ~ 3 回合
        - trigger_probability: 10% ~ 40%
        """
        skill_name = random.choice(constants.SKILL_NAMES["shield"])
        value = random.randint(10, 20) + int(factor * 5)
        duration = random.randint(2, 4)
        prob = random.randint(10, 40) + int(factor * 5)
        return {
            "name": skill_name,
            "skill_type": "shield",
            "limit_of_times": self.SKILL_TRIGGER_MULTIPLE,
            "trigger_probability": prob,
            "dependent_properties": self.SKILL_DEPEND_ON_SELF_HP,
            "value": value,
            "duration": duration,
            "description": f"获得生命上限 {value}% 护盾，持续 {duration} 回合。"
        }

    def make_skill_armor_once_heal(self, factor):
        """
        单次生命回复技能示例：
        - duration: 0(不需要持续)
        - trigger_probability: 20% ~ 40%
        """
        skill_name = random.choice(constants.SKILL_NAMES["once_heal"])
        heal_val = random.randint(10, 30) + int(factor * 5)
        prob = random.randint(20, 40) + int(factor * 5)
        return {
            "name": skill_name,
            "skill_type": "once_heal",
            "limit_of_times": self.SKILL_TRIGGER_MULTIPLE,
            "trigger_probability": prob,
            "dependent_properties": self.SKILL_DEPEND_ON_SELF_HP,
            "value": heal_val,
            "duration": self.SKILL_NON_CONTINUOUS,
            "description": f"回复生命上限 {heal_val}% 的生命值。"
        }

    def make_skill_armor_duration_heal(self, factor):
        """
        持续型生命回复技能示例：
        - duration: 999
        - trigger_probability: 100% 或自定
        """
        skill_name = random.choice(constants.SKILL_NAMES["duration_heal"])
        heal_val = random.randint(1, 8) + int(factor * 2)
        # 持续回合数
        duration = 999

        return {
            "name": skill_name,
            "skill_type": "duration_heal",
            "limit_of_times": self.SKILL_TRIGGER_ONCE,
            "trigger_probability": constants.SKILL_MUST_TRIGGER,
            "dependent_properties": self.SKILL_DEPEND_ON_SELF_HP,
            "value": heal_val,
            "duration": duration,
            "description": f"每回合固定回复生命上限 {heal_val}% 的生命值。"
        }

    def make_skill_paralysis(self, factor):
        """
        麻痹技能示例：
        - duration: 1 ~ 2 回合
        - trigger_probability: 10% ~ 30%
        """
        skill_name = random.choice(constants.SKILL_NAMES["paralysis"])
        duration = random.randint(1, 2)
        prob = random.randint(10, 30) + int(factor * 5)

        return {
            "name": skill_name,
            "skill_type": "paralysis",
            "limit_of_times": self.SKILL_TRIGGER_MULTIPLE,
            "trigger_probability": prob,
            "dependent_properties": self.SKILL_DEPEND_ON_NONE,
            "value": 0,
            "duration": duration,
            "description": f"令目标 {duration} 回合内无法行动。"
        }

    def make_skill_general_active_immunity(self, factor):
        """
        免疫技能示例：
        - duration: 1 ~ 2 回合
        - trigger_probability: 10% ~ 40%
        """
        skill_name = random.choice(constants.SKILL_NAMES["active_immunity"])
        duration = random.randint(1, 2)
        prob = random.randint(10, 40) + int(factor * 5)
        return {
            "name": skill_name,
            "skill_type": "active_immunity",
            "limit_of_times": self.SKILL_TRIGGER_MULTIPLE,
            "trigger_probability": prob,
            "dependent_properties": self.SKILL_DEPEND_ON_NONE,
            "value": 0,
            "duration": duration,
            "description": f"释放后 {duration} 回合内免疫异常状态。"
        }

    def make_skill_general_precedence_immunity(self, factor):
        """
        优先免疫技能示例：
            即开局发动，指定回合内不受到任何负面效果的免疫机能，此类技能只会发动一次
        - duration: 2 ~ 4 回合
        - trigger_probability: 100%
        """
        skill_name = random.choice(constants.SKILL_NAMES["precedence_immunity"])
        duration = random.randint(2, 4) + int(factor/2)
        return {
            "name": skill_name,
            "skill_type": "precedence_immunity",
            "limit_of_times": self.SKILL_TRIGGER_ONCE,
            "trigger_probability": constants.SKILL_MUST_TRIGGER,
            "dependent_properties": self.SKILL_DEPEND_ON_NONE,
            "value": 0,
            "duration": duration,
            "description": f"战斗前 {duration} 回合内免疫所有异常状态。"
        }

    def make_skill_weapon_once_life_steal(self, factor):
        """
        单次吸血技能示例：
        - trigger_probability: 10% ~ 50%
        - duration: 0 (一次性触发)
        """
        skill_name = random.choice(constants.SKILL_NAMES["once_life_steal"])
        percent = random.randint(20, 30) + int(factor * 3)
        prob = random.randint(20, 50) + int(factor * 5)
        return {
            "name": skill_name,
            "skill_type": "once_life_steal",
            "limit_of_times": self.SKILL_TRIGGER_MULTIPLE,
            "trigger_probability": prob,
            "dependent_properties": self.SKILL_DEPEND_ON_SELF_ATTACK,
            "value": percent,
            "duration": self.SKILL_NON_CONTINUOUS,
            "description": f"发动一次等同于普通攻击的伤害，本次攻击造成伤害的 {percent}% 转化为自身生命。"
        }

    def make_skill_weapon_duration_life_steal(self, factor):
        """
        持续型吸血技能示例：战前发动，本次战斗中造成的所有普通攻击都能够固定偷取生命值
        - trigger_probability: 10% ~ 50%
        - duration: 0 (一次性触发)
        """
        skill_name = random.choice(constants.SKILL_NAMES["duration_life_steal"])
        percent = random.randint(5, 20) + int(factor * 4)
        prob = random.randint(10, 50) + int(factor * 5)
        # 持续回合数
        duration = 999
        return {
            "name": skill_name,
            "skill_type": "duration_life_steal",
            "limit_of_times": self.SKILL_TRIGGER_ONCE,
            "trigger_probability": prob,
            "dependent_properties": self.SKILL_DEPEND_ON_SELF_ATTACK,
            "value": percent,
            "duration": duration,
            "description": f"战斗中造成的所有普通攻击都能够将造成伤害的 {percent}% 转化为自身生命。"
        }

    def make_skill_general_promoting_attributes(self, factor):
        """
        '提升属性'技能：随机提升(攻击 / 防御 / 生命) 其中一种。
        """
        skill_name = random.choice(constants.SKILL_NAMES["promoting_attributes"])
        # 随机选择要提升的属性
        attributes_str = random.randint(self.SKILL_DEPEND_ON_SELF_HP, self.SKILL_DEPEND_ON_SELF_DEFENSE)
        duration = random.randint(2, 4)
        # 提升的数值
        value = random.randint(5, 15) + int(factor * 3)
        # 触发概率设为随机 20~30%
        prob = random.randint(20, 30) + int(factor * 3)
        # 获取属性名
        if attributes_str == self.SKILL_DEPEND_ON_SELF_HP:
            attribute_name = "自身生命"
        elif attributes_str == self.SKILL_DEPEND_ON_SELF_ATTACK:
            attribute_name = "自身攻击"
        elif attributes_str == self.SKILL_DEPEND_ON_SELF_DEFENSE:
            attribute_name = "自身防御"

        return {
            "name": skill_name,
            "skill_type": "promoting_attributes",
            "limit_of_times": self.SKILL_TRIGGER_MULTIPLE,
            "trigger_probability": prob,
            "dependent_properties": attributes_str,
            "value": value,
            "duration": duration,
            "description": f"提升 {value}% {attribute_name}，持续 {duration} 回合。"
        }

    def make_skill_general_weaken_attributes(self, factor):
        """
        '削弱属性'技能：随机削弱(攻击 / 防御 / 生命) 其中一种。
        """
        skill_name = random.choice(constants.SKILL_NAMES["weaken_attributes"])
        # 随机选择要削弱的属性
        attributes_str = random.randint(self.SKILL_DEPEND_ON_OPPONENT_ATTACK, self.SKILL_DEPEND_ON_OPPONENT_DEFENSE)
        duration = random.randint(2, 4)
        # 削弱的数值
        value = random.randint(5, 15) + int(factor * 3)
        # 触发概率设为随机 20~30%
        prob = random.randint(20, 30) + int(factor * 10)
        # 获取属性名
        if attributes_str == self.SKILL_DEPEND_ON_OPPONENT_ATTACK:
            attribute_name = "对手攻击"
        elif attributes_str == self.SKILL_DEPEND_ON_OPPONENT_DEFENSE:
            attribute_name = "对手防御"

        return {
            "name": skill_name,
            "skill_type": "weaken_attributes",
            "limit_of_times": self.SKILL_TRIGGER_MULTIPLE,
            "trigger_probability": prob,
            "dependent_properties": attributes_str,
            "value": value,
            "duration": duration,
            "description": f"削弱 {value}% {attribute_name}，持续 {duration} 回合。"
        }

    def make_skill_armor_reflect(self, factor):
        """
        '反伤'：在回合进行阶段，对攻击者造成自身防御值的10%-20%。
        同样为100%触发。且仅触发一次
        """
        skill_name = random.choice(constants.SKILL_NAMES["reflect"])
        # 提升的数值
        value = random.randint(5, 20) + int(factor * 8)

        return {
            "name": skill_name,
            "skill_type": "reflect",
            "limit_of_times": self.SKILL_TRIGGER_MULTIPLE,
            "trigger_probability": constants.SKILL_MUST_TRIGGER,
            "dependent_properties": self.SKILL_DEPEND_ON_SELF_DEFENSE,
            "value": value,
            "duration": self.SKILL_NON_CONTINUOUS,
            "description": f"被动技能，在受到普通攻击时，对攻击者造成自身防御值 {value}% 伤害。"
        }

    def make_skill_armor_assimilate(self, factor):
        """
        '伤害吸收'：收到任何伤害时，都能够吸收一定比例的伤害，使其无效
        同样为100%触发。且仅触发一次
        """
        skill_name = random.choice(constants.SKILL_NAMES["assimilate"])
        # 提升的数值
        value = random.randint(5, 20) + int(factor * 4)

        return {
            "name": skill_name,
            "skill_type": "assimilate",
            "limit_of_times": self.SKILL_TRIGGER_MULTIPLE,
            "trigger_probability": constants.SKILL_MUST_TRIGGER,
            "dependent_properties": self.SKILL_DEPEND_ON_SELF_DEFENSE,
            "value": value,
            "duration": self.SKILL_NON_CONTINUOUS,
            "description": f"被动技能，受到任何伤害时，都能够吸收伤害来源 {value}% 的伤害，使其无效。"
        }

    def pick_rarity(self):
        """
            -------------------------------------------------
            辅助函数：随机获取稀有度
            -------------------------------------------------
        """
        random.seed(time.time_ns())
        rand_val = random.random()
        cumulative = 0.0
        for (name, prob, skill_count, factor) in constants.RARITY_DATA:
            cumulative += prob
            if rand_val <= cumulative:
                return (name, skill_count, factor)
        # 浮点误差的兜底
        return constants.RARITY_DATA[-1][0], constants.RARITY_DATA[-1][2], constants.RARITY_DATA[-1][3]

    def generate_weapon_name(self, skill_count):
        """
            -------------------------------------------------
            辅助函数：生成武器名称
            -------------------------------------------------
        """
        random.seed(time.time_ns())
        if skill_count >= 2:
            weapon_name = random.choice(constants.WEAPON_PREFIX) + random.choice(constants.WEAPON_NAME)
            if skill_count == 4:
                return f"卓越{weapon_name}"
            else:
                return weapon_name
        else:
            return random.choice(constants.WEAPON_NAME)

    def generate_armor_name(self, skill_count):
        """
            -------------------------------------------------
            辅助函数：生成防具名称
            -------------------------------------------------
        """
        random.seed(time.time_ns())
        if skill_count >= 2:
            armor_name = random.choice(constants.ARMOR_PREFIX) + random.choice(constants.ARMOR_NAME)
            if skill_count == 4:
                return f"卓越{armor_name}"
            else:
                return armor_name
        else:
            return random.choice(constants.ARMOR_NAME)

    def calculate_weapon_attributes(self, level, factor):
        """
            -------------------------------------------------
            辅助函数：武器属性计算
            -------------------------------------------------
        """
        random.seed(time.time_ns())
        attack = int(round((10 + 5 * level) * factor * (1 + random.uniform(-0.1, 0.2))))
        defense = 0
        max_hp = 0
        price = price = int(round((100 * level) * factor * 5))
        return attack, defense, max_hp, price

    def calculate_armor_attributes(self, level, factor):
        """
            -------------------------------------------------
            辅助函数：防具属性计算
            -------------------------------------------------
        """
        random.seed(time.time_ns())
        attack = 0
        defense = int(round((10 + 5 * level) * factor * (1 + random.uniform(-0.1, 0.2))))
        max_hp = int(round((10 + 10 * level) * factor * (1 + random.uniform(-0.1, 0.2))))
        price = int(round((150 * level) * factor * 5))
        return attack, defense, max_hp, price

    def pick_skills(self, equipment_type, factor, skill_count):
        """
            -------------------------------------------------
            生成技能
                1) 先根据稀有度确定技能数量
                2) 对于武器：从（self.COMMON_SKILLS + self.WEAPON_SKILLS）中抽取
                    对于防具：从（self.COMMON_SKILLS + self.ARMOR_SKILLS）中抽取
            -------------------------------------------------
        """
        if skill_count <= 0:
            return []
        if equipment_type == "weapon":
            skill_candidates = self.COMMON_SKILLS + self.WEAPON_SKILLS
        else:
            skill_candidates = self.COMMON_SKILLS + self.ARMOR_SKILLS

        # 随机抽取 skill_count 个技能(不重复)
        chosen_funcs = random.sample(skill_candidates, k=skill_count)

        # 针对每个技能，生成效果描述
        skill_list = []
        for func in chosen_funcs:
            random.seed(time.time_ns())
            # 动态调用
            skill_desc = func(factor)
            skill_list.append(skill_desc)
        return skill_list

    def get_random_equipment(self, level, equipment_type=None):
        """
            -------------------------------------------------
            核心函数：根据类型与等级生成随机装备
            -------------------------------------------------
        """
        # 1) 确定稀有度
        rarity_name, skill_count, factor = self.pick_rarity()

        random.seed(time.time())
        get_weapon = random.choice([True, False])

        if not equipment_type:
            if get_weapon:
                equipment_type = "weapon"
            else:
                equipment_type = "armor"

        # 2) 生成装备名称
        if equipment_type == "weapon":
            eq_name = self.generate_weapon_name(skill_count)
        else:
            eq_name = self.generate_armor_name(skill_count)

        # 3) 生成装备等级
        equipment_level = random.randint(max(1, level - 10), min(100, level + 10))

        # 4) 计算基础属性
        if equipment_type == "weapon":
            attack, defense, max_hp, price = self.calculate_weapon_attributes(equipment_level, factor)
        else:
            attack, defense, max_hp, price = self.calculate_armor_attributes(equipment_level, factor)

        # 5) 随机生成技能
        skills = self.pick_skills(equipment_type, factor, skill_count)

        # 6) 整合信息
        equipment = {
            "id": str(uuid.uuid4()),
            "type": "weapon" if equipment_type == "weapon" else "armor",
            "name": eq_name,
            "rarity": skill_count,
            "rarity_str": rarity_name,
            "level": equipment_level,
            "attack_bonus": attack,
            "defense_bonus": defense,
            "max_hp_bonus": max_hp,
            "price": price,
            "skills": skills
        }

        logger.info(f"生成随机装备{equipment_type}：{equipment}")

        self.insert_equipment(equipment)
        return equipment

    def get_equipment_info(self, equipment):
            """
            打印装备的详细信息，使用emoji增强视觉效果。

            :param equipment: 装备信息的字典
            """
            # 映射稀有度到对应的emoji
            rarity_emojis = {
                '普通': '🟢',
                '精良': '🔵',
                '稀有': '🟣',
                '史诗': '🟠',
                '传奇': '✨'
            }

            # 获取稀有度对应的emoji
            rarity_emoji = rarity_emojis.get(equipment.get('rarity_str', '普通'), '🟢')
            stars = "★" * (equipment.get('rarity', 1) + 1)

            # 装备类型emoji
            type_emoji = '🗡️' if equipment.get('type') == 'weapon' else '🛡️'

            # 基础信息
            base_info = (
                f"{type_emoji} [{equipment.get('name', '未知')}{rarity_emoji}]\n"
                # f"🆔 ID：{equipment.get('id')}\n"
                f"  📈 等级：{equipment.get('level', 1)}\n"
                f"  💎 稀有度：{stars}\n"
                f"  💰 价值：{equipment.get('price', 0)} 金币\n"
            )

            # 属性信息
            lines = []
            attack_bonus = equipment.get('attack_bonus', 0)
            if attack_bonus != 0:
                lines.append(f"  ⚔️  攻击加成：{attack_bonus}")

            defense_bonus = equipment.get('defense_bonus', 0)
            if defense_bonus != 0:
                lines.append(f"  🛡️  防御加成：{defense_bonus}")

            max_hp_bonus = equipment.get('max_hp_bonus', 0)
            if max_hp_bonus != 0:
                lines.append(f"  ❤️  最大生命加成：{max_hp_bonus}")

            # 技能信息
            skills = equipment.get('skills', [])
            if skills:
                lines.append(f"  🔮 技能：")
                for skill in skills:
                    lines.append(f"    - [{skill.get('name', '未知技能')}]：{skill.get('description', '无描述')} {skill.get('trigger_probability', 0)}% 概率发动。")

            attribute_info = "\n".join(lines)

            # 整合所有信息
            equipment_info = base_info + attribute_info

            # 打印装备信息
            # print(equipment_info)

            return equipment_info.rstrip('\n')
