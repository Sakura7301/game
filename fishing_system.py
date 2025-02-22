import csv
import uuid
import math
import random
import json
import datetime
from . import constants
import os
import sqlite3
from common.log import logger
from collections import Counter


class FishingSystem:
    def __init__(self, data_dir):
        self.data_dir = data_dir

    def __init__(self, game):
        self.game = game
        try:
            # 获取当前目录
            self.data_dir = os.path.join(os.path.dirname(__file__), "data")
            self.shop_fish_path = os.path.join(self.data_dir, "fish.db")
            # 连接到SQLite数据库
            try:
                self._connect()
                self._initialize_database()
            except sqlite3.Error as e:
                logger.error(f"数据库连接或初始化失败: {e}")
                raise
            # 读取所有鱼的物品
            self.fish_items = self.read_all_entries()
        except Exception as e:
            logger.error(f"初始化鱼的系统出错: {e}")
            raise

    def _connect(self) -> None:
        """
        连接到 SQLite 数据库，启用 WAL 模式以提高并发性，并启用外键约束。
        """
        try:
            self.conn = sqlite3.connect(self.shop_fish_path, check_same_thread=False)
            # 通过列名访问数据
            self.conn.row_factory = sqlite3.Row
            logger.debug("成功连接到鱼类数据库。")
        except sqlite3.Error as e:
            logger.error(f"连接数据库失败: {e}")
            raise

    def _initialize_database(self) -> None:
        """
        创建鱼的数据表，如果它尚不存在。
        """
        # 处理数据，生成 uuid 并保留所需字段
        all_fish_items = [
            {
                "uuid": str(uuid.uuid4()), # 生成唯一的 uuid
                "name": item[0],
                "explain": item[1],
                "type": "fish",
                "price": item[2],
                "rarity": item[3],
            }
            for item in constants.FISH_ITEMS
        ]
        try:
            with self.conn:
                # 创建数据表
                self.conn.execute('''
                CREATE TABLE IF NOT EXISTS fish (
                    uuid TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    explain TEXT NOT NULL,
                    type TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    rarity INTEGER NOT NULL
                )
                ''')

                # 检查表中是否已有数据
                cursor = self.conn.execute('SELECT COUNT(*) FROM fish')
                record_count = cursor.fetchone()[0]

                # 只有表为空时才插入数据
                if record_count == 0:
                    # 插入数据
                    self.conn.executemany('''
                    INSERT INTO fish (uuid, name, explain, type, price, rarity)
                    VALUES (:uuid, :name, :explain, :type, :price, :rarity)
                    ''', all_fish_items)
                    logger.debug("成功初始化鱼的数据表并插入数据。")
                else:
                    logger.debug("鱼的数据表已存在并包含数据，跳过插入操作。")
            logger.debug("成功初始化鱼的数据表。")
        except sqlite3.Error as e:
            logger.error(f"初始化鱼的数据表失败: {e}")
            raise

    def read_all_entries(self, table_name="fish"):
        """
        读取数据表的所有条目并返回

        :param db_path: 数据库文件路径（对于MySQL等数据库，也是对应配置参数）
        :param table_name: 数据表名称
        :return: 返回查询到的所有条目（列表形式）
        """
        try:
            cursor = self.conn.cursor()

            # 构造查询语句，读取所有条目
            query = f"SELECT * FROM {table_name}"
            cursor.execute(query)

            # 获取所有查询结果
            rows = cursor.fetchall()

            items = []

            # 创建 Task 对象并添加到 self.tasks 列表
            for row in rows:
                item = {
                    "uuid": row[0],
                    "name": row[1],
                    "explain": row[2],
                    "type": row[3],
                    "price": row[4],
                    "rarity": row[5]
                }
                items.append(item)

            # 关闭游标(连接不关闭)
            cursor.close()

            # 返回结果列表
            return items
        except sqlite3.Error as e:
            logger.error(f"读取鱼的数据库错误: {e}")
            return None

    def go_fishing(self, player):
        """钓鱼主逻辑"""

        fishing_rod = player.equipment_fishing_rod
        fishing_rod_description = fishing_rod.get("description", {})
        lucky = fishing_rod_description['lucky']
        gold_bonus = fishing_rod_description['gold_bonus']
        exp_bonus = fishing_rod_description['exp_bonus']
        # 随机判断是否钓到鱼
        if random.random() < lucky:
            # 随机选择一条鱼
            caught_fish = random.choice(self.fish_items)

            # 获取鱼的基本价值
            base_reward = int(caught_fish.get('price', 0))

            # 计算金币奖励
            coins_reward = int(base_reward * (gold_bonus + 0.1 * math.log2(player.level)))

            # 计算经验奖励
            exp_reward = int(coins_reward * (exp_bonus + 0.01 * player.level))

            # 生成钓鱼信息
            fishing_messages = [
                "🎯 哇！鱼儿上钩了！",
                "🎣 成功钓到一条鱼！",
                "🌊 收获颇丰！",
                "✨ 技术不错！",
                "🎪 今天运气不错！"
            ]

            stars = "⭐" * int(caught_fish.get('rarity', 1))
            message = f"{random.choice(fishing_messages)}\n"
            message += f"──────────────\n"
            message += f"🎣 你钓到了 {caught_fish['name']}\n"
            message += f"      \"{caught_fish['explain']}\"\n"
            message += f"📊 稀有度: {stars}\n"
            message += f"💰 基础价值: {caught_fish.get('price', '0')}金币\n"
            message += f"🪙 金币奖励: {coins_reward}金币\n"
            message += f"📚 经验奖励: {exp_reward}经验\n"
            message += f"──────────────"

            return {
                'success': True,
                'fish': caught_fish,
                'coins_reward': coins_reward,
                'exp': exp_reward,
                'message': message
            }
        else:
            # 未钓到鱼时的处理逻辑保持不变
            fail_messages = [
                "🌊 鱼儿溜走了...",
                "💨 这次什么都没钓到",
                "❌ 差一点就抓到了",
                "💪 继续努力！",
                "🎣 下次一定能钓到！"
            ]

            message = f"{random.choice(fail_messages)}\n"
            message += f"──────────────\n"

            return {
                'success': False,
                'message': message
            }

    def show_collection(self, player, page=1, search_term=""):
        """显示鱼类图鉴"""
        # 读取玩家背包
        inventory = player.inventory

        # 预初始化鱼的数量
        fish_counts = 0

        # 读取所有鱼类信息
        fish_data = {}
        for item_name in inventory:
            if inventory[item_name]['type'] == 'fish':
                fish_data[item_name] = inventory[item_name]
                fish_counts += 1

        # 按稀有度排序
        sorted_fish = sorted(fish_data.items(), key=lambda x: (-x[1]['rarity'], x[0]))

        # 搜索过滤
        if search_term:
            sorted_fish = [(name, data) for name, data in sorted_fish if search_term in name]
            if not sorted_fish:
                return f"未找到包含 '{search_term}' 的鱼类"

        # 分页处理
        items_per_page = 5
        total_pages = (len(sorted_fish) + items_per_page - 1) // items_per_page

        if page < 1 or page > total_pages:
            page = 1

        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_fish = sorted_fish[start_idx:end_idx]

        # 生成图鉴信息
        collection = f"📖 鱼类图鉴 (第{page}/{total_pages}页)\n"
        collection += "──────────────\n"

        for fish_name, data in page_fish:
            count = data['amount']
            stars = "⭐" * data['rarity']
            collection += f"🐟 {fish_name}\n"
            collection += f"   说明: {data['explain']}\n"
            collection += f"   收集数量: {count}\n"
            collection += f"   稀有度: {stars}\n"
            collection += f"   价值: 💰{data['price']}金币\n"
            collection += "──────────────\n"

        if total_pages > 1:
            collection += "💡 发送 图鉴 [页码] - 查看指定页\n"
        collection += "💡 发送 图鉴 [鱼名] - 搜索特定鱼类"

        return collection
