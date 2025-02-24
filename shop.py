import os
import re
import csv
import uuid
import json
import sqlite3
from common.log import logger
from . import constants
from collections import Counter


class Shop:
    def __init__(self, game):
        self.game = game
        try:
            # 获取当前目录
            self.data_dir = os.path.join(os.path.dirname(__file__), "data")
            self.shop_db_path = os.path.join(self.data_dir, "shop.db")
            # 连接到SQLite数据库
            try:
                self._connect()
                self._initialize_database()
            except sqlite3.Error as e:
                logger.error(f"数据库连接或初始化失败: {e}")
                raise
            # 读取所有商店物品
            self.shop_items = self.read_all_entries()
        except Exception as e:
            logger.error(f"初始化商店系统出错: {e}")
            raise

    def _connect(self) -> None:
        """
        连接到 SQLite 数据库，启用 WAL 模式以提高并发性，并启用外键约束。
        """
        try:
            self.conn = sqlite3.connect(self.shop_db_path, check_same_thread=False)
            # 通过列名访问数据
            self.conn.row_factory = sqlite3.Row
            logger.debug("成功连接到商店数据库。")
        except sqlite3.Error as e:
            logger.error(f"连接数据库失败: {e}")
            raise

    def _initialize_database(self) -> None:
        """
        创建商店物品的数据表，并检查是否需要更新数据：当 constants.SHOP_ITEMS 中的物品多于数据库中的时候，
        会将缺失的物品插入到数据库中。
        """
        # 处理数据，生成 uuid 并保留所需字段
        all_items = [
            {
                "uuid": str(uuid.uuid4()),
                "name": item[0],
                "type": item[1],
                "explain": item[2],
                "price": item[3],
                "rarity": item[4],
                "description": json.dumps(item[5]),
            }
            for item in constants.SHOP_ITEMS
        ]
        try:
            with self.conn:
                # 创建数据表
                self.conn.execute('''
                CREATE TABLE IF NOT EXISTS shop (
                    uuid TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    explain TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    rarity INTEGER NOT NULL,
                    description TEXT NOT NULL
                )
                ''')

                # 查询数据库中已有的物品（依据name字段判断是否存在）
                cursor = self.conn.execute('SELECT name FROM shop')
                existing_names = set([row[0] for row in cursor.fetchall()])

                # 筛选出常量中存在而数据库中缺失的物品
                new_items = [item for item in all_items if item["name"] not in existing_names]

                if new_items:
                    self.conn.executemany('''
                    INSERT INTO shop (uuid, name, type, explain, price, rarity, description)
                    VALUES (:uuid, :name, :type, :explain, :price, :rarity, :description)
                    ''', new_items)
                    logger.debug(f"成功添加 {len(new_items)} 个新物品到商店数据表。")
                else:
                    logger.debug("商店数据表已包含所有物品，不需要更新。")
        except sqlite3.Error as e:
            logger.error(f"初始化商店的数据表失败: {e}")
            raise

    def read_all_entries(self, table_name="shop"):
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
                    "type": row[2],
                    "explain": row[3],
                    "price": row[4],
                    "rarity": row[5],
                    "description": json.loads(row[6]) if row[6] else {}
                }
                items.append(item)

            # 关闭游标(连接不关闭)
            cursor.close()

            return items  # 返回结果列表
        except sqlite3.Error as e:
            logger.error(f"读取商店数据库错误: {e}")
            return None

    def get_item_by_uuid(self, uuid_value: str) -> dict:
        """
        根据 UUID 从 shop_items 获取对应的数据条目

        :param uuid_value: 要查询的物品的 UUID
        :return: 匹配的物品数据条目字典，或 None 如果未找到
        """
        for item in self.shop_items:
            if item['uuid'] == uuid_value:
                return item  # 返回匹配的条目
        logger.warning(f"未找到 UUID 为 {uuid_value} 的物品。")
        return None  # 未找到时返回 None

    def parse_equipment_sale(self, text: str) -> tuple:
        """
        解析输入字符串，返回一个包含稀有度和道具类型的元组。

        输入格式：
            出售 所有[可选颜色或品质][装备|武器|消耗品|鱼竿|鱼|鱼类]

        示例：
            出售 所有绿色装备
            出售 所有精良武器
            出售 所有鱼竿
            出售 所有鱼
            出售 所有

        注意：
            如果不输入颜色或品质，则稀有度默认使用 constants.MAX_RARITY。
            如果无法解析为完整的稀有度和类型, 返回 None
        """
        # 如果输入不是字符串则直接返回 None
        if not isinstance(text, str):
            logger.error("输入必须是字符串类型")
            return None

        # 去除首尾空白字符
        text = text.strip()

        # 定义颜色和品质的映射
        color_mapping = {
            '绿色': 1,
            '蓝色': 2,
            '紫色': 3,
            '橙色': 4,
            '闪光': 5
        }

        quality_mapping = {
            '普通': 1,
            '精良': 2,
            '稀有': 3,
            '史诗': 4,
            '传奇': 5,
            '一星': 1,
            '二星': 2,
            '三星': 3,
            '四星': 4,
            '五星': 5,
            '六星': 6
        }

        type_mapping = {
            '武器': 'weapon',
            '防具': 'armor',
            '消耗品': 'consumable',
            '鱼': 'fish',
            '鱼类': 'fish',
            '鱼竿': 'fishing_rod'
        }

        # 正则表达式：匹配“出售 所有[可选颜色或品质][装备|武器|消耗品|鱼竿|鱼|鱼类]”
        # 注意：如果类型部分缺失，则认为无法解析，函数返回 None
        pattern = r'^出售 所有(?:(绿色|蓝色|紫色|橙色|闪光|普通|精良|稀有|史诗|传奇|一星|二星|三星|四星|五星|六星))?(防具|武器|消耗品|鱼竿|鱼|鱼类)$'
        match = re.fullmatch(pattern, text)

        if match:
            # 解析颜色/品质关键字（可选）
            key = match.group(1)
            # 解析道具类型，必须存在
            type_key = match.group(2)

            # 解析稀有度
            if key is None or key == '':
                rarity = constants.MAX_RARITY
            elif key in color_mapping:
                rarity = color_mapping[key]
            elif key in quality_mapping:
                rarity = quality_mapping[key]
            else:
                logger.error("无效的颜色/品质关键字")
                return None

            # 解析道具类型
            if type_key in type_mapping:
                equipment_type = type_mapping[type_key]
            else:
                logger.error("无效的道具类型")
                return None

            return (rarity, equipment_type)
        else:
            logger.error("❌ 输入的文本格式不正确，正确格式应为：出售 所有[可选颜色或品质][装备|武器|消耗品|鱼竿|鱼|鱼类]")
            return None

    def sell_item(self, user_id, content):
        """出售物品功能"""
        # 检查玩家是否存在
        player = self.game.get_player(user_id)
        if not player:
            return "🤷‍♂️ 您还没有注册游戏"

        # 预初始化稀有度和类型
        rarity = -1
        type = ""
        report = ""
        # 是否出售的标志
        sale_flag = False
        report = []

        # 解析出售内容
        result = self.parse_equipment_sale(content)
        if result:
            rarity, type = result

        # 获取背包中的物品
        inventory = player.inventory
        if not inventory:
            return "🤷‍♂️ 背包是空的,没有可以出售的物品"

        for_order_property = {}
        # 批量出售
        if rarity > -1:
            for item_name in inventory:
                if inventory[item_name]["type"] == type:
                    # 获取道具稀有度
                    item_rarity = inventory[item_name]["rarity"]
                    # 检查稀有度
                    if item_rarity <= rarity:
                        # 稀有度低于预售值，添加到待出售列表
                        for_order_property[item_name] = inventory[item_name]["amount"]
                else:
                    continue

            total_gold = 0
            # 计算售出可得金币数量
            for item_name in for_order_property:
                # 获取道具的价值
                total_gold += inventory[item_name]["price"] * for_order_property[item_name]
                # 删除被出售的道具
                inventory.pop(item_name)

            # 售出后实际所得
            actual_gold = int(total_gold * 0.8)

            # 计算更新后的金币
            player_update_gold = player.gold + actual_gold

            # 生成出售报告
            report.append("🏪 出售所有物品成功:")
            for item_name in for_order_property:
                report.append(f"   - [{item_name}]x{for_order_property[item_name]}")
            report.append(f"💰 基础价值：{total_gold}金币")
            report.append(f"♻️ 回收比例：80%")
            report.append(f"\n共获得 {actual_gold} 金币")
            # 设置售出标志
            sale_flag = True
        # 单个出售
        elif content.startswith("出售"):
            try:
                parts = content.split()
                item_name = parts[1]
                amount = int(parts[2]) if len(parts) > 2 else 1
            except (IndexError, ValueError):
                return "❌ 出售格式错误！请使用: 出售 物品名 [数量]"

            remain_num = 0
            # 获取物品属性
            if item_name in inventory:
                item_price = inventory[item_name]["price"]
                item_hold_num = inventory[item_name]["amount"]
                if item_hold_num < amount:
                    report.append(f"🎒 背包中只有 {item_hold_num} 个 {item_name}\n")
                    amount = item_hold_num
                else:
                    remain_num = item_hold_num - amount
            else:
                return f"🤷‍♂️ 玩家 [{player.nickname}] 的背包中没有物品 [{item_name}]"

            # 计算出售价格（原价的80%）
            sell_price = int(item_price * 0.8)
            total_sell_price = sell_price * amount

            if remain_num == 0:
                inventory.pop(item_name)
            else:
                inventory[item_name]["amount"] = remain_num

            # 计算更新后的金币
            player_update_gold = player.gold + total_sell_price

            report.append(f"🏪 出售物品成功:")
            report.append(f"    - {item_name}x{amount}")
            report.append(f"💰 基础价值：{item_price}金币")
            report.append(f"♻️ 回收比例：80%")
            report.append(f"\n获得 {total_sell_price} 金币")
            # 设置售出标志
            sale_flag = True
        else:
            report.append("❌ 无效的出售命令")

        if sale_flag:
            # 更新玩家数据
            updates = {
                "inventory": inventory,
                "gold": player_update_gold
            }
            # 保存更新后的玩家数据
            self.game._update_player_data(player.user_id, updates)
        return "\n".join(report)

    def get_item_quantity(self, inventory, item_name):
        return inventory.get(item_name, {}).get("amount", "0")

    def buy_item(self, user_id, content):
        """购买物品功能，支持自动调整购买数量到最大可购买量"""
        parts = content.split()
        if len(parts) < 2:
            return "🤷‍♂️ 请指定要购买的物品名称"

        item_name = parts[1]
        # 获取购买数量，默认为1
        amount = 1
        if len(parts) > 2:
            try:
                amount = int(parts[2])
                if amount <= 0:
                    return "🤷‍♂️ 购买数量必须大于0"
            except ValueError:
                return "🤷‍♂️ 购买数量必须是正整数"

        # 获取物品信息
        if not any(item["name"] == item_name for item in self.shop_items):
            return f"🤷‍♂️ 商店里没有物品 [{item_name}]"

        # 获取玩家信息
        player = self.game.get_player(user_id)
        if not player:
            return "🤷‍♂️ 您还没有注册游戏"

        # 获取玩家背包
        inventory = player.inventory

        for item in self.shop_items:
            if item["name"] == item_name:
                item_uuid = item["uuid"]
                item_type = item["type"]
                item_price = item["price"]
                item_dict = {
                    "uuid": item_uuid,
                    "type": item_type,
                    "price": item_price,
                    "rarity": item["rarity"],
                    "description": item["description"],
                    "explain": item["explain"]
                }
                break

        # 计算总价并检查金币
        adjusted = False
        total_price = item_price * amount

        # 自动调整购买数量逻辑
        if player.gold < total_price:
            max_possible = player.gold // item_price
            if max_possible <= 0:
                return f"😭 无法购买任何 [{item_name}]（单价: {item_price}🪙）\n💳 当前余额: {player.gold}🪙\n"
            adjusted = True
            amount = max_possible
            total_price = amount * item_price

        # 更新玩家金币和背包
        player.gold -= total_price
        if item_name in inventory:
            inventory[item_name]["amount"] += amount
        else:
            item_dict["amount"] = amount
            inventory[item_name] = item_dict

        # 保存数据更新
        self.game._update_player_data(player.user_id, {
            "gold": player.gold,
            "inventory": inventory
        })

        # 构建操作提示
        instructions_str = ""
        if item_type in ['weapon', 'armor']:
            equip_type = '武器' if item_type == 'weapon' else '护甲'
            instructions_str = f"\n💡 发送 [装备 {item_name}] 来装备此{equip_type}"
        elif item_type == 'fishing_rod':
            instructions_str = f"\n💡 发送 [装备 {item_name}] 来使用此鱼竿"
        elif item_type == 'consumable':
            instructions_str = f"\n💡 发送 [使用 {item_name}] 来使用此消耗品"
        elif item_type == 'name_change_card':
            instructions_str = f"\n💡 发送 [改名 新昵称] 来使用改名卡"

        # 构建返回消息
        base_msg = f"🛒 成功购买 {amount} 个 {item_name}\n💲 总花费: {total_price}🪙\n💳 当前余额: {player.gold}🪙\n"
        if adjusted:
            base_msg = f"⚠️ 余额不足，已自动调整购买数量为{amount}个\n\n{base_msg}"
        return f"{base_msg}{instructions_str}"

    def show_shop(self, content=""):
        """显示商店物品列表"""
        # 获取页码,默认第一页
        page = 1
        parts = content.split()
        if len(parts) > 1:
            try:
                page = int(parts[1])
                if page < 1:
                    page = 1
            except:
                page = 1

        item_list = self.shop_items

        # 分页处理
        items_per_page = 10
        total_pages = (len(item_list) + items_per_page - 1) // items_per_page
        if page > total_pages:
            page = total_pages

        start = (page - 1) * items_per_page
        end = start + items_per_page
        current_items = item_list[start:end]

        shop_list = f"📦 商店物品列表 (第{page}/{total_pages}页)\n"
        shop_list += "──────────────\n\n"

        for item in current_items:
            shop_list += f"🔸 {item['name']}\n"
            shop_list += f"└─ 💲 {item['price']}金币\n"
            shop_list += f"└─ 📝 {item['explain']}\n\n"

        shop_list += "──────────────\n"
        shop_list += "💡 发送 商店 [页码] 查看其他页"

        return shop_list
