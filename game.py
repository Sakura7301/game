import os
import re
import time
import json
import random
import plugins
import sqlite3
import datetime
import threading
from . import constants
from plugins import *
from .shop import Shop
from .player import Player
from datetime import datetime, time as datetime_time
from typing import Optional, Dict, Any
from common.log import logger
from .rouge_equipment import RougeEquipment
from .monopoly import MonopolySystem
from .fishing_system import FishingSystem
from bridge.reply import Reply, ReplyType
from channel.chat_message import ChatMessage
from bridge.context import ContextType, Context


@plugins.register(
    name="Game",
    desc="一个简单的文字游戏系统",
    version="0.2.4",
    author="assistant",
    desire_priority=0
)
class Game(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        # 获取协议类型
        self.channel_type = conf().get("channel_type")
        # 初始化锁
        self.lock = threading.Lock()
        # 使用线程本地存储
        self.local = threading.local()
        try:
            # 检查data目录
            self.data_dir = os.path.join(os.path.dirname(__file__), "data")
            os.makedirs(self.data_dir, exist_ok=True)
            # 初始化配置
            self.config = super().load_config()
            # 加载文件路径
            self.player_db_path = os.path.join(self.data_dir, "players.db")
            # 加载管理员密码
            self.admin_password = self.config.get("admin_password")
            # 初始化管理员列表
            self.admin_list = []
            # 游戏系统状态
            self.game_status = True
            # 初始化钓鱼系统
            self.fishing_system = FishingSystem(self.data_dir)
            # 初始化商店系统
            self.shop_system = Shop(self)
            # 初始化玩家类中的静态变量
            Player.set_game_handle(self)
            # 初始化随机装备系统
            self.rouge_equipment_system = RougeEquipment(self.data_dir)
            # 初始化大富翁系统
            self.monopoly = MonopolySystem(self.data_dir)
            # 连接到Player SQLite数据库
            try:
                self._connect()
                self._initialize_database()
                logger.debug(f"玩家数据库连接成功！")
            except sqlite3.Error as e:
                logger.error(f"玩家数据库连接或初始化失败: {e}")
                raise
            logger.info("[Game] 插件初始化完毕")
        except Exception as e:
            logger.error(f"初始化游戏系统出错: {e}")
            raise

    def _get_connection(self) -> sqlite3.Connection:
        """
        获取数据库连接，如果连接不存在则创建。
        """
        if not hasattr(self, 'conn') or self.conn is None:
            try:
                self.conn = sqlite3.connect(self.player_db_path, check_same_thread=False)
                self.conn.row_factory = sqlite3.Row
                logger.debug("数据库连接已创建并保持打开状态。")
            except sqlite3.Error as e:
                logger.error(f"创建数据库连接失败: {e}")
                raise
        return self.conn

    def _connect(self) -> None:
        """
        初始化连接（通过 _get_connection 实现）。
        """
        self._get_connection()

    def _initialize_database(self) -> None:
        """
        创建 players 表和必要的索引，如果它们尚不存在。
        """
        create_table_query = """
        CREATE TABLE IF NOT EXISTS players (
            user_id TEXT PRIMARY KEY,
            nickname TEXT UNIQUE,
            gold INTEGER,
            level INTEGER,
            sign_in_timestamp INTEGER,
            inventory TEXT,
            hp INTEGER,
            max_hp INTEGER,
            attack INTEGER,
            defense INTEGER,
            exp INTEGER,
            max_exp INTEGER,
            last_fishing INTEGER,
            last_attack INTEGER,
            adventure_last_attack INTEGER,
            equipment_weapon TEXT,
            equipment_armor TEXT,
            equipment_fishing_rod TEXT,
            challenge_proposal TEXT,
            position TEXT
        )
        """
        create_index_query = "CREATE UNIQUE INDEX IF NOT EXISTS idx_nickname ON players(nickname);"
        try:
            conn = self._get_connection()
            with conn:
                conn.execute(create_table_query)
                conn.execute(create_index_query)
            logger.debug("成功初始化数据库表和索引。")
        except sqlite3.Error as e:
            logger.error(f"初始化数据库表或索引失败: {e}")
            raise

    def get_player_data(self, name, *fields):
        """
        根据 name 检索指定数据条目，并返回指定字段的值。

        :param name: 要检索的玩家名称
        :param fields: 要返回的字段名称（可变参数）
        :return: 字段值的元组，如果未找到数据则返回 None
        """
        if not fields:
            raise ValueError("必须指定至少一个字段名进行查询。")

        fields_str = ", ".join(fields)  # 动态拼接字段名
        query = f"SELECT {fields_str} FROM players WHERE nickname = ?"

        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (name,))
            result = cursor.fetchone()
            if result is None:
                return None
            return tuple(result[field] for field in fields)
        except sqlite3.Error as e:
            logger.error(f"数据库操作出错: {e}")
            return None

    def insert_player_to_db(self, player: Player):
        """
        将玩家对象插入到数据库中
        :param player: Player 类的实例
        """
        player_data = player.data
        standard_fields = [
            'user_id',
            'nickname',
            'gold',
            'level',
            'sign_in_timestamp',
            'inventory',
            'hp',
            'max_hp',
            'attack',
            'defense',
            'exp',
            'max_exp',
            'last_fishing',
            'last_attack',
            'adventure_last_attack',
            'equipment_weapon',
            'equipment_armor',
            'equipment_fishing_rod',
            'challenge_proposal',
            'position'
        ]
        complete_player_data = {}
        for field in standard_fields:
            value = player_data.get(field, None)
            # 根据字段类型进行转换
            if field in ['user_id', 'gold', 'level', 'sign_in_timestamp', 'hp', 'max_hp', 'attack', 'defense', 'exp', 'max_exp', 'last_fishing', 'last_attack', 'adventure_last_attack']:
                if field == 'user_id':
                    # user_id 作为字符串处理
                    complete_player_data[field] = str(value) if value is not None else None
                else:
                    if value is not None:
                        try:
                            complete_player_data[field] = int(value)
                        except ValueError:
                            logger.error(f"字段 {field} 需要整数值，但收到: {value}")
                            complete_player_data[field] = None  # 或者设定一个默认值
                    else:
                        complete_player_data[field] = None
            elif field == 'inventory':
                if value is not None:
                    try:
                        # 假设 inventory 是一个字典，需要序列化为 JSON 字符串
                        complete_player_data[field] = json.dumps(value)
                    except (TypeError, ValueError) as e:
                        logger.error(f"字段 {field} 序列化失败: {e}")
                        complete_player_data[field] = json.dumps({})
                else:
                    complete_player_data[field] = json.dumps({})
            else:
                # 其他文本字段，确保是字符串
                complete_player_data[field] = str(value) if value is not None else None

        insert_query = f"""
        INSERT INTO players (
            {", ".join(standard_fields)}
        ) VALUES (
            {", ".join([f":{field}" for field in standard_fields])}
        )
        """
        try:
            conn = self._get_connection()
            with conn:
                conn.execute(insert_query, complete_player_data)
            logger.info(f"玩家 {complete_player_data['nickname']} 已成功插入数据库！")
        except sqlite3.IntegrityError as e:
            logger.error(f"插入玩家数据时发生完整性错误（可能是重复的 user_id 或 nickname）: {e} | 数据: {complete_player_data}")
        except sqlite3.Error as e:
            logger.error(f"插入玩家数据时出错: {e} | 数据: {complete_player_data}")

    def nickname_exists(self, nickname: str) -> bool:
        """
        根据昵称检查数据库中是否已有对应的玩家条目
        :param nickname: 玩家昵称
        :return: 如果存在返回 True，否则返回 False
        """
        query = """
        SELECT COUNT(*) FROM players WHERE nickname = :nickname
        """
        try:
            conn = self._get_connection()
            with conn:
                cursor = conn.execute(query, {'nickname': nickname})
                count = cursor.fetchone()[0]
                return count > 0  # 如果 count 大于 0，表示存在该昵称
        except sqlite3.Error as e:
            logger.error(f"查询昵称 '{nickname}' 时出错: {e}")
            return False  # 出现错误时返回 False

    def get_player_by_user_id(self, user_id: str) -> dict:  # 更改参数类型为 str
        """
        通过 user_id 获取对应的玩家数据条目。

        :param user_id: 玩家唯一标识符
        :return: 包含玩家数据的字典，如果未找到则返回 None
        """
        query = "SELECT * FROM players WHERE user_id = ?"
        try:
            conn = self._get_connection()
            cursor = conn.execute(query, (user_id,))
            row = cursor.fetchone()
            if row:
                player_data = {key: row[key] for key in row.keys()}
                # 处理 inventory 字段，确保它是字典
                if 'inventory' in player_data:
                    inventory_str = player_data['inventory']
                    if isinstance(inventory_str, str):
                        try:
                            # 解析为字典
                            player_data['inventory'] = json.loads(inventory_str)
                        except json.JSONDecodeError:
                            logger.error(f"无法解析 inventory 字符串: {inventory_str}，将使用默认空字典。")
                            player_data['inventory'] = {}
                logger.info(f"成功获取 user_id 为 {user_id} 的玩家数据。")
                return player_data
            else:
                logger.debug(f"未找到 user_id 为 {user_id} 的玩家。")
                return None
        except sqlite3.Error as e:
            logger.error(f"查询玩家数据失败: {e}")
            raise

    def get_all_players(self) -> list:
        """
        获取所有玩家的数据条目。

        :return: 包含所有玩家数据的列表，如果未找到任何玩家则返回空列表
        """
        query = "SELECT * FROM players"
        players_data = []
        try:
            conn = self._get_connection()
            cursor = conn.execute(query)
            rows = cursor.fetchall()  # 获取所有行
            for row in rows:
                player_data = {key: row[key] for key in row.keys()}
                # 处理 inventory 字段，确保它是字典
                if 'inventory' in player_data:
                    inventory_str = player_data['inventory']
                    if isinstance(inventory_str, str):
                        try:
                            # 解析为字典
                            player_data['inventory'] = json.loads(inventory_str)
                        except json.JSONDecodeError:
                            logger.error(f"无法解析 inventory 字符串: {inventory_str}，将使用默认空字典。")
                            player_data['inventory'] = {}
                players_data.append(player_data)  # 将玩家数据添加到列表中

            logger.info(f"成功获取所有玩家数据，共 {len(players_data)} 位玩家。")
            return players_data

        except sqlite3.Error as e:
            logger.error(f"查询所有玩家数据失败: {e}")
            raise

    def get_player_by_nickname(self, nickname: str) -> dict:
        """
        通过 nickname 获取对应的玩家数据条目。

        :param nickname: 玩家昵称
        :return: 包含玩家数据的字典，如果未找到则返回 None
        """
        query = "SELECT * FROM players WHERE nickname = ?"
        try:
            conn = self._get_connection()
            cursor = conn.execute(query, (nickname,))
            row = cursor.fetchone()
            if row:
                player_data = {key: row[key] for key in row.keys()}
                # 处理 inventory 字段，确保它是字典
                if 'inventory' in player_data:
                    inventory_str = player_data['inventory']
                    if isinstance(inventory_str, str):
                        try:
                            # 解析为字典
                            player_data['inventory'] = json.loads(inventory_str)
                        except json.JSONDecodeError:
                            logger.error(f"无法解析 inventory 字符串: {inventory_str}，将使用默认空字典。")
                            player_data['inventory'] = {}
                logger.info(f"成功获取 nickname 为 {nickname} 的玩家数据。")
                return player_data
            else:
                logger.debug(f"未找到 nickname 为 {nickname} 的玩家。")
                return None
        except sqlite3.Error as e:
            logger.error(f"查询玩家数据失败: {e}")
            raise

    def on_handle_context(self, e_context: EventContext):
        if e_context['context'].type != ContextType.TEXT:
            return

        content = e_context['context'].content.strip()
        msg: ChatMessage = e_context['context']['msg']

        # 获取用户ID作为主要标识符
        current_id = msg.actual_user_id if msg.is_group else msg.from_user_id

        if self.channel_type == "gewechat":
            # gewe协议获取群名
            nickname = msg.actual_user_nickname
        else:
            # 使用 sender 作为昵称
            nickname = msg.actual_user_nickname if msg.is_group else msg.from_user_nickname

        # 检查是否有用户ID
        if not current_id:
            return "无法获取您的ID，请确保ID已设置"

        if not self.game_status and content not in ['注册', '注销', '开机', '关机', '充值']:
            return "游戏系统当前已关闭"

        logger.debug(f"当前用户信息 - current_id: {current_id}")

        # 修改这里：更新 lambda 函数定义，使其接受两个参数
        cmd_handlers = {
            "注册": lambda id: self.register_player(id, content),
            "注销": lambda id: self.unregister_player(id),
            "状态": lambda id: self.get_player_status(id, False),
            "详细状态": lambda id: self.get_player_status(id, True),
            "签到": lambda id: self.daily_checkin(id),
            "商店": lambda id: self.shop_system.show_shop(content),
            "购买": lambda id: self.shop_system.buy_item(id, content),
            "背包": lambda id: self.show_inventory(id),
            "装备": lambda id: self.equip_from_inventory(id, content),
            "游戏菜单": lambda id: self.game_help(),
            "赠送": lambda id: self.give_item(id, content, msg),
            "钓鱼": lambda id: self.fishing(id),
            "图鉴": lambda id: self.show_fish_collection(id, content),
            "出售": lambda id: self.shop_system.sell_item(id, content),
            "下注": lambda id: self.gamble(id, content),
            "外出": lambda id: self.go_out(id),
            "冒险": lambda id: self.go_adventure(id),
            "使用": lambda id: self.use_item(id, content),
            "排行": lambda id: self.show_leaderboard(id, content),
            "排行榜": lambda id: self.show_leaderboard(id, content),
            "挑战": lambda id: self.attack_player(id, content, msg),
            "接受挑战": lambda id: self.accept_challenge(id),
            "拒绝挑战": lambda id: self.refuse_challenge(id),
            "鉴权": lambda id: self.authenticate("鉴权", id, content),
            "认证": lambda id: self.authenticate("认证", id, content),
            "auth": lambda id: self.authenticate("auth", id, content),
            "开机": lambda id: self.toggle_game_system(id, 'start'),
            "关机": lambda id: self.toggle_game_system(id, 'stop'),
            "充值": lambda id: self.toggle_recharge(id, content),
            "购买地块": lambda id: self.buy_property(id),
            "升级地块": lambda id: self.upgrade_property(id),
            "我的地产": lambda id: self.show_properties(id),
            "地图": lambda id: self.show_map(id),
        }

        cmd = content.split()[0]
        with self.lock:  # 获取锁
            if cmd in cmd_handlers:
                try:
                    if constants.SYSTEM_BIT:
                        if self.is_admin(current_id):
                            # 系统维护期间仅管理员可使用
                            reply = cmd_handlers[cmd](current_id)
                        else:
                            reply = f"🚧 内部维护中，暂不支持[{cmd}]功能!"
                    else:
                        # 公测
                        reply = cmd_handlers[cmd](current_id)
                    e_context['reply'] = Reply(ReplyType.TEXT, reply)
                    e_context.action = EventAction.BREAK_PASS
                except Exception as e:
                    logger.error(f"处理指令 '{cmd}' 时出错: {e}")
                    e_context['reply'] = Reply(ReplyType.TEXT, "⚠️ 处理您的指令时发生错误，请稍后再试。")
                    e_context.action = EventAction.BREAK_PASS
            else:
                e_context.action = EventAction.CONTINUE

    def game_help(self):
        return """
🎮 游戏指令大全 🎮

基础指令
————————————
📝 注册 [用户名] - 注册新玩家
🚪 注销 - 注销你的账号
📊 状态 - 查看当前状态
📊 详细状态 - 查看当前详细状态
📅 签到 - 抽取你的幸运签

物品相关
————————————
🏪 商店 - 查看商店物品
💰 购买 [物品名] - 购买物品
🎒 背包 - 查看背包物品
⚔️ 装备 [物品名] - 装备物品
🎁 赠送 [@用户] [物品名] [数量] - 赠送物品
💊 使用 [物品名] - 使用背包中的道具

交易相关
————————————
💸 出售 [物品名] [数量] - 出售物品
🏪 出售某一类别物品 - 出售 所有[物品级别][物品类别]

冒险
————————————
🎣 钓鱼 - 进行钓鱼获取金币
📖 图鉴 - 查看鱼类图鉴
🤺 冒险 - 随即前往一个区域冒险
👊 挑战 [@用户] - 向其他玩家发起挑战
👌 接受挑战 - 同意其他玩家的挑战请求
🫸 拒绝挑战 - 拒绝其他玩家的挑战请求

大富翁
————————————
🌄 外出 - 外出开始大富翁游戏
🏠 我的地产 - 查看玩家地产
🏘️ 购买地块 - 购买地块
🔧 升级地块 - 升级地块
🗺️ 地图 - 查看大富翁游戏地图

其他功能
————————————
🎲 下注 [大/小/豹子/顺子/对子] 数额 - 按照指定类型押注进行下注
🏆 排行榜 [类型] - 查看排行榜

管理员功能
————————————
🔑 认证/鉴权/auth [密码] - 认证管理员身份
🔧 开机 - 开启游戏系统
🔧 关机 - 关闭游戏系统
💴 充值 [@用户] 数额 - 为指定用户充值指定数额的金币

系统时间: {}
""".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

    def regex_match(self, cmd: str, content: str) -> str:
        match = re.search(rf'{cmd}(.*)', content)
        if match:
            return match.group(1).strip()
        return None

    def register_player(self, user_id, content=None):
        """注册新玩家

        Args:
            user_id: 玩家ID
            content: 玩家输入的指令，将用于提取玩家ID
        """
        if not user_id:
            return "❌ 无法获取您的ID，请确保ID已设置"

        # 检查是否已注册
        if self.get_player(user_id):
            return "✅ 您已经注册过了"

        nickname = self.regex_match("注册", content)

        try:
            # 如果没有提供昵称，使用user_id作为默认昵称
            if not nickname:
                return f"❌ 请提供一个有效昵称！\n\n格式: 注册 [昵称]"

            # 检查昵称是否已被占用
            if self.nickname_exists(nickname):
                return f"❌ 昵称[{nickname}]已被占用，注册失败！"

            # 创建新玩家
            player = Player.create_new(user_id, nickname)
            self.insert_player_to_db(player)
            return f"📝 玩家 [{nickname}] 注册成功！"
        except Exception as e:
            logger.error(f"注册玩家出错: {e}")
            return "⚠️ 注册失败，请稍后再试"

    def delete_player_by_user_id(self, user_id: str):
        """
        根据 user_id 删除对应的玩家数据条目。

        :param user_id: 玩家唯一标识符
        """
        # 确保 user_id 为字符串类型
        if not isinstance(user_id, str):
            logger.error(f"user_id 需要是字符串类型，但收到: {type(user_id)}")
            return

        delete_query = """
        DELETE FROM players
        WHERE user_id = :user_id
        """

        try:
            conn = self._get_connection()
            with conn:
                cursor = conn.execute(delete_query, {'user_id': user_id})
                if cursor.rowcount > 0:
                    logger.info(f"用户 {user_id} 的数据已成功删除！")
                else:
                    logger.warning(f"未找到用户 {user_id}，无法删除。")
        except sqlite3.Error as e:
            logger.error(f"删除玩家数据时出错: {e} | user_id: {user_id}")

    def unregister_player(self, user_id):
        """
            注销玩家：只能自己为自己注销

            Args:
                user_id: 玩家ID
        """
        if not user_id:
            return "❌ 无法获取您的ID，请确保ID已设置"

        # 检查是否已注册
        player = self.get_player(user_id)
        if not player:
            return "❌ 您还没注册,请先注册!"

        try:
            self.delete_player_by_user_id(user_id)
            return f"🔚 玩家 [{player.nickname}] 已注销！"
        except Exception as e:
            logger.error(f"注销玩家出错: {e}")
            return "❌ 注销失败，请稍后再试"

    def get_player(self, user_id) -> Optional[Player]:
        """获取玩家数据"""
        try:
            player_info = self.get_player_by_user_id(user_id)
            if player_info:
                player = Player.get_player(player_info)
                return player
            else:
                logger.debug(f"未找到用户ID为 {user_id} 的玩家数据")
        except Exception as e:
            logger.error(f"获取玩家数据出错: {e}")
            raise

    def _get_player_by_nickname(self, nickname) -> Optional[Player]:
        """获取玩家数据"""
        try:
            player_info = self.get_player_by_nickname(nickname)
            if player_info:
                player = Player.get_player(player_info)
                return player
            else:
                logger.debug(f"未找到用户名为 {nickname} 的玩家数据")
        except Exception as e:
            logger.error(f"获取玩家数据出错: {e}")
            raise

    def check_player_upgrade(self, player: Player, exp_award):
        # 初始化当前等级、经验和最大经验
        current_level = player.level
        current_exp = player.exp
        # 更新总经验
        total_exp = current_exp + exp_award

        # 循环，通过获得的经验尝试进行升级
        while True:
            # 获取当前等级所需的升级经验
            max_exp = player.get_exp_for_next_level(current_level)

            # 检查当前等级是否已达到上限
            if current_level >= constants.PLAYER_MAX_LEVEL:
                # 如果已达到100级，限制经验为最大经验
                total_exp = min(total_exp, max_exp)
                break

            # 检查当前总经验是否达到升级所需的经验
            if total_exp >= max_exp:
                # 升级
                total_exp -= max_exp
                current_level += 1
            else:
                # 如果未达到升级要求，退出循环
                break

        # 返回包含等级、剩余的经验和下一级所需的最大经验的字典
        return {
            'level': current_level,
            'exp': total_exp,
            'max_exp': player.get_exp_for_next_level(current_level)
        }

    def get_player_level_up_data(self, player: Player, upgrade, updates):
        level_up_str = []
        # 获取升级后的经验条和等级
        new_level = upgrade['level']
        new_exp = upgrade['exp']
        new_max_exp = upgrade['max_exp']
        # 获取等级差
        level_difference = upgrade['level'] - player.level
        # 计算新的三维
        new_max_hp = player.max_hp + (constants.PLAYER_LEVEL_UP_APPEND_HP * level_difference)
        new_attack = player.attack + (constants.PLAYER_LEVEL_UP_APPEND_ATTACK * level_difference)
        new_defense = player.defense + (constants.PLAYER_LEVEL_UP_APPEND_DEFENSE * level_difference)
        # 更新玩家数据
        updates['level'] = new_level
        updates['exp'] = new_exp
        updates['max_exp'] = new_max_exp
        if new_level > player.level:
            # 升级了，需要更新数据
            updates['hp'] = new_max_hp
            updates['max_hp'] = new_max_hp
            updates['attack'] = new_attack
            updates['defense'] = new_defense
            # 格式化升级提示
            level_up_str.append(f"🆙 升级啦！")
            level_up_str.append(f"[{player.nickname}] Lv.{new_level}")
            level_up_str.append(f"Exp: {new_exp}/{new_max_exp}")
            level_up_str.append(f"Hp : {new_max_hp}/{new_max_hp}")
            level_up_str.append("💪 属性提升：")
            level_up_str.append(f"❤️ 基础生命上限 +{constants.PLAYER_LEVEL_UP_APPEND_HP * level_difference}")
            level_up_str.append(f"⚔️ 基础攻击力 +{constants.PLAYER_LEVEL_UP_APPEND_ATTACK * level_difference}")
            level_up_str.append(f"🛡️ 基础防御力 +{constants.PLAYER_LEVEL_UP_APPEND_DEFENSE * level_difference}")

        return "\n".join(level_up_str)

    def fishing(self, user_id):
        """钓鱼"""
        player = self.get_player(user_id)
        if not player:
            return "❌ 您还没注册,请先注册"

        if not player.equipment_fishing_rod:
            return "🤷‍♂️ 您必须先装备一个鱼竿才能钓鱼"

        # 获取背包
        inventory = player.inventory

        # 检查冷却时间
        current_time = int(time.time())
        last_fishing = player.last_fishing
        cooldown = constants.FISH_COOLDOWN

        # 检查冷却时间
        if current_time - last_fishing < cooldown:
            remaining = cooldown - (current_time - last_fishing)
            return f"⏳ 钓鱼冷却中，还需等待 {remaining} 秒"

        # 调用钓鱼系统
        result = self.fishing_system.go_fishing(player)

        # 更新玩家数据
        updates = {
            'last_fishing': current_time
        }

        # 预定义升级播报
        level_up_str = ""

        # 如果钓到鱼
        if result['success']:
            # 获取鱼
            fish_item = result['fish']
            # 检查背包是否易经有该种类的鱼，如果有，仅仅增加数量即可
            if fish_item['name'] in inventory:
                inventory[fish_item['name']]['amount'] += 1
            else:
                fish_item['amount'] = 1
                # 将鱼添加到背包
                inventory[result['fish']['name']] = result['fish']

            updates['inventory'] = inventory
            # 添加金币奖励
            new_gold = int(player.gold) + result['coins_reward']
            updates['gold'] = new_gold
            # 根据获得经验判断玩家是否升级
            level_up_result = self.check_player_upgrade(player, result['exp'])
            level_up_report = self.get_player_level_up_data(player, level_up_result, updates)
            # 获取升级播报
            if len(level_up_report) > 0:
                level_up_str = f"\n{level_up_report}\n"
            # 使用钓鱼系返回的完整消息
            message = result['message']
        else:
            message = result['message']

        # 更新鱼竿耐久度
        fishing_rod = player.equipment_fishing_rod
        durability = fishing_rod['description']['durability']
        durability -= constants.FISHING_ROD_DURABILITY_CONSUME
        if durability <= 0:
            durability_str = f"\n❗️ [{fishing_rod['name']}]已经报废！"
            # 从装备栏移除此道具（已经报废）
            updates['equipment_fishing_rod'] = ""
        else:
            # 更新耐久度
            fishing_rod['description']['durability'] = durability
            updates['equipment_fishing_rod'] = fishing_rod
            durability_str = f"\n🎣 [{fishing_rod['name']}] 耐久度: {durability}"

        # 更新玩家数据
        self._update_player_data(user_id, updates)
        return f"{message}{level_up_str}{durability_str}"

    def show_fish_collection(self, user_id, content=""):
        """显示鱼类图鉴"""
        player = self.get_player(user_id)
        if not player:
            return "❌ 您还没有注册,请先注册 "

        # 解析命令参数
        parts = content.split()
        page = 1
        search_term = ""

        if len(parts) > 1:
            if parts[1].isdigit():
                page = int(parts[1])
            else:
                search_term = parts[1]

        return self.fishing_system.show_collection(player, page, search_term)

    def check_drop_equipment_has_same_name(self, drop_equipment, player, updates_info):
        # 获取等级（因为玩家可能已经升级）
        if 'level' in updates_info:
            player_level = updates_info['level']
        else:
            player_level = player.level
        # 获取金币
        if 'gold' in updates_info:
            player_gold = updates_info['gold']
        else:
            player_gold = player.gold
        # 获取背包
        if 'inventory' in updates_info:
            inventory = updates_info['inventory']
        else:
            inventory = player.inventory
        player_get_gold = 0
        # 创建掉落物字典
        drop_item_explain = self.rouge_equipment_system.get_equipment_info(drop_equipment)
        drop_dict = {
            'uuid': drop_equipment['id'],
            'name': drop_equipment['name'],
            'type': drop_equipment['type'],
            'level': drop_equipment['level'],
            'rarity': drop_equipment['rarity'],
            'price': drop_equipment['price'],
            'amount': 1,
            'explain': drop_item_explain
        }
        # 获取掉落物属性
        drop_equipment_rarity = drop_dict['rarity']
        drop_name = drop_dict['name']
        drop_type = drop_dict['type']
        report = []
        if drop_name in inventory:
            # 掉落物与背包物品同名
            inventory_equipment_rarity = inventory[drop_name]["rarity"]
            if drop_equipment_rarity <= inventory_equipment_rarity:
                # 背包中的品质更好，掉落物直接折算为金币
                player_get_gold = int(drop_dict['price'] * 0.8)
                player_gold += player_get_gold
                report.append(f"{drop_item_explain}\n\n❗️ 你已经拥有更好品质的[{drop_name}]，掉落物将被直接折算为金币奖励！\n💰 获得金币：{player_get_gold}")
            else:
                # 掉落物与背包物品同名，但掉落物品质更好
                # 将背包物品折算为金币
                player_get_gold = int(inventory[drop_name]['price'] * 0.8)
                player_gold += player_get_gold
                # 删除背包已有的同名物品
                inventory.pop(drop_name)
                # 将掉落物放进背包
                inventory[drop_name] = drop_dict
                updates_info['inventory'] = inventory
                report.append(f"{drop_item_explain}\n\n❗️ 这件[{drop_name}]比你背包中的品质更好，已将背包中的[{drop_name}]折算为金币奖励！\n💰 获得金币：{player_get_gold}")
        else:
            if drop_type == 'weapon':
                is_equipped_uuid = player.equipment_weapon
            elif drop_type == 'armor':
                is_equipped_uuid = player.equipment_armor
            # 获取已装备的物品
            is_equipped_prop = self.rouge_equipment_system.get_equipment_by_id(is_equipped_uuid)
            # 检查已装备物品是否同名
            if is_equipped_prop and (drop_name == is_equipped_prop['name']):
                # 掉落物与已装备物品同名
                if drop_equipment_rarity <= is_equipped_prop['rarity']:
                    # 掉落物与已装备的物品同名，但是已装备的品质更好，掉落物直接折算为金币
                    player_get_gold = int(drop_dict['price'] * 0.8)
                    player_gold += player_get_gold
                    report.append(f"{drop_item_explain}\n\n❗️ 你已经装备了更好品质的[{drop_name}]，掉落物将被直接折算为金币奖励！\n💰 获得金币：{player_get_gold}")
                else:
                    # 掉落物与已装备物品同名，但掉落物品质更好，已装备的物品折算为金币
                    player_get_gold = int(is_equipped_prop['price'] * 0.8)
                    player_gold += player_get_gold
                    # 将掉落物装备
                    if drop_type == 'weapon':
                        updates_info['equipment_weapon'] = drop_dict['uuid']
                        # 新的攻击力 = 武器加成 + 等级加成 + 玩家基本数值
                        new_attack = drop_dict['attack_bonus'] + (player_level * constants.PLAYER_LEVEL_UP_APPEND_ATTACK + constants.PLAYER_BASE_ATTACK)
                        # 更新玩家数据
                        updates_info['attack'] = new_attack
                    elif drop_type == 'armor':
                        updates_info['equipment_armor'] = drop_dict['uuid']
                        # 新的防御力 = 防具加成 + 等级加成 + 玩家基本数值
                        new_defense = drop_dict['defense_bonus'] + (player_level * constants.PLAYER_LEVEL_UP_APPEND_DEFENSE + constants.PLAYER_BASE_DEFENSE)
                        # 新的最大生命值 = 防具加成 + 等级加成 + 玩家基本数值
                        new_max_hp = drop_dict['max_hp_bonus'] + (player_level * constants.PLAYER_LEVEL_UP_APPEND_HP + constants.PLAYER_BASE_MAX_HP)
                        # 更新玩家数据
                        updates_info['max_hp'] = new_max_hp
                        updates_info['defense'] = new_defense
                    report.append(f"{drop_item_explain}\n\n❗️ 已为你装备了更好品质的[{drop_name}]，属性更差的[{drop_name}]将被折算为金币奖励！\n💰 获得金币：{player_get_gold}")
            else:
                # 掉落物与已装备物品和背包物品都不同名，直接加入背包即可
                inventory[drop_name] = drop_dict
                updates_info['inventory'] = inventory
                report.append(f"{drop_item_explain}")
        updates_info['gold'] = player_gold
        return "\n".join(report)

    def random_drop_consumables(self, player, updates_info, num)-> str:
        result = []
        # 随机获得消耗品
        while (num > 0):
            consumable = random.choice(self.shop_system.shop_items)
            item_name = consumable['name']
            # 获取背包
            if 'inventory' in updates_info:
                inventory = updates_info['inventory']
            else:
                inventory = player.inventory
            # 使用当前时间作为随机数种子
            random.seed(time.time_ns())
            # 生成[0.0, 1.0)之间的随机数
            rand = random.random()
            if rand < 0.8:
                # 80%的概率得到一个
                item_num = 1
            else:
                # 20%的概率得到两个
                item_num = 2
            # 如果背包已经有这个物品,则增加数量
            if item_name in inventory:
                inventory[item_name]["amount"] += item_num
            else:
                consumable["amount"] = item_num
                inventory[item_name] = consumable
            result.append(f"📦 {consumable['name']} x{item_num}")
            num -= 1
            updates_info['inventory'] = inventory
        return "\n".join(result)

    #  外出打怪
    def go_out(self, user_id):
        """外出探险或漫步"""
        player = self.get_player(user_id)
        if not player:
            return "🤷‍♂️ 您还没有注册游戏"

        # 检查玩家状态
        if int(player.hp) <= 0:
            return "😵 您的生命值不足，请先使用药品恢复"

        # 检查冷却时间
        current_time = int(time.time())
        last_attack_time = int(player.last_attack)
        cooldown = constants.GO_OUT_CD

        if current_time - last_attack_time < cooldown:
            remaining = cooldown - (current_time - last_attack_time)
            return f"⏳ 您刚刚进行过活动,请等待 {remaining} 秒后再次外出"

        # 掷骰子
        steps = self.monopoly.roll_dice()

        # 获取当前位置
        current_position = int(player.position) if hasattr(player, 'position') else 0
        new_position = (current_position + steps) % self.monopoly.map_data["total_blocks"]

        # 获取地块信息
        block = self.monopoly.get_block_info(new_position)

        # 更新玩家位置
        self._update_player_data(user_id, {
            'position': str(new_position),
            'last_attack': str(current_time)
        })

        # 根据地块类型显示不同符号
        symbol = constants.MAP_TYPE_SYMBOLS.get(block['type'], "⬜")

        result = [
            f"🎲 掷出 {steps} 点",
            f"🌍 来到了 {symbol} {block['name']}",
            f"━━━━━━━━━━━━━"
        ]

        updates_info = {}
        # 经过起点的奖励结算
        if (current_position + steps) > self.monopoly.map_data["total_blocks"]:
            updates_info['gold'] = player.gold + constants.GO_OUT_START_POINT_REWARD
            result.append(f"💰 经过起点获得 {constants.GO_OUT_START_POINT_REWARD} 金币")

        # 检查特殊事件
        if block['type'] == '机遇':
            event = self.monopoly.trigger_random_event()
            result.append(f"🤞 触发事件: {event['name']}")
            result.append(f"“{event['description']}”")
            if 'effect' in event:
                inventory = player.inventory
                for key, value in event['effect'].items():
                    if key == 'gold':
                        # 金币变化
                        new_gold = player.gold + value
                        if new_gold < 0:
                            new_gold = 0
                        updates_info['gold'] = new_gold
                        # 添加金币变化提示
                        if value > 0:
                            result.append(f"💰 获得 {value} 金币")
                        else:
                            result.append(f"💸 失去 {abs(value)} 金币")
                    elif key == 'hp':
                        # 血量变化
                        new_hp = player.hp + value
                        if new_hp < 0:
                            new_hp = 0
                        updates_info['hp'] = new_hp
                        # 添加血量变化提示
                        if value > 0:
                            result.append(f"❤️ 血量增加 {value}")
                        else:
                            result.append(f"💔 血量减少 {abs(value)}")
                    elif key == 'exp':
                        # 添加经验变化提示
                        if value > 0:
                            result.append(f"✨ 经验增加 {value}")
                        # 根据获得经验判断玩家是否升级
                        level_up_result = self.check_player_upgrade(player, value)
                        if level_up_result['level'] > player.level:
                            # 玩家升级了
                            updates_info['level'] = level_up_result['level']
                            # 获取升级信息
                            level_up_str = self.get_player_level_up_data(player, level_up_result, updates_info)
                            result.append(level_up_str)
                        else:
                            # 没升级，更新经验即可
                            updates_info['exp'] = level_up_result['exp']
                    elif key == 'lost_item':
                        # 使用当前时间作为随机数种子
                        random.seed(time.time_ns())
                        # 生成[0.0, 1.0)之间的随机数
                        rand = random.random()
                        if rand < 0.8:
                            # 80%的概率失去一个
                            lost_num = 1
                        else:
                            # 20%的概率失去两个
                            lost_num = 2
                        while lost_num > 0:
                            # 随机失去一件物品
                            lost_item_name = random.choice(list(inventory.keys()))
                            lost_item = inventory[key]
                            # 判断此物品剩余数量
                            if lost_item['amount'] == 1:
                                inventory.pop(lost_item_name)
                            else:
                                lost_item['amount'] -= 1
                            updates_info['inventory'] = inventory
                            result.append(f"🗑️ 丢失了: {lost_item_name} x1")
                            logger.debug(f"玩家 {user_id} 丢失 {lost_item_name} x1")
                            lost_num -= 1
                    elif key == 'weapon':
                        # 随机获得一件武器
                        weapon = self.rouge_equipment_system.get_random_equipment(player.level, 'weapon')
                        report_str = self.check_drop_equipment_has_same_name(weapon, player, updates_info)
                        result.append(f"{report_str}")
                    elif key == 'armor':
                        # 随机获得一件防具
                        armor = self.rouge_equipment_system.get_random_equipment(player.level, 'armor')
                        report_str = self.check_drop_equipment_has_same_name(armor, player, updates_info)
                        result.append(f"{report_str}")
                    elif key == 'consumable':
                        # 随机获得消耗品
                        while (value > 0):
                            consumable = random.choice(self.shop_system.shop_items)
                            item_name = consumable['name']
                            # 如果背包已经有这个物品,则增加数量
                            if item_name in inventory:
                                inventory[item_name]["amount"] += 1
                            else:
                                consumable["amount"] = 1
                                inventory[item_name] = consumable
                            result.append(f"📦 获得了 {consumable['name']}")
                            logger.debug(f"玩家 {user_id} 获得了 {consumable['name']}")
                            value -= 1
                        updates_info['inventory'] = inventory
                    else:
                        # 暂未支持的key
                        result.append(f"暂不支持的事件: {key}")
        elif block['type'] in ['空地', '直辖市', '省会', '地级市', '县城', '乡村']:
            property_info = self.monopoly.get_property_owner(new_position)
            if property_info is None or 'owner' not in property_info:
                # 可以购买
                price = self.monopoly.calculate_property_price(new_position)
                result.append(f"🌳 这块地还没有主人")
                result.append(f"🗺 区域类型: {block['region']}")
                result.append(f"💴 需要 {price} 金币")
                result.append("\n发送'购买地块'即可购买")
                logger.debug(f"玩家 {user_id} 访问了未拥有的地块，位置: {new_position}, 价格: {price}")
            else:
                # 需要付租金
                owner = property_info['owner']

                if user_id != owner:  # 不是自己的地产才需要付租金
                    owner_player = self.get_player(owner)
                    if owner_player:
                        rent = self.monopoly.calculate_rent(new_position)
                        if int(player.gold) >= rent:
                            # 扣除玩家金币
                            new_player_gold = int(player.gold) - rent
                            self._update_player_data(user_id, {'gold': str(new_player_gold)})

                            # 增加房主金币
                            owner_new_gold = int(owner_player.gold) + rent
                            self._update_player_data(owner, {'gold': str(owner_new_gold)})

                            result.append(f"🕵️‍♂️ 这是 {owner_player.nickname} 的地盘")
                            result.append(f"🗺 区域类型: {block['region']}")
                            result.append(f"💸 支付租金 {rent} 金币")
                            result.append(f"💰 当前金币: {new_player_gold}")
                            logger.debug(f"玩家 {user_id} 支付了 {rent} 金币租金给 {owner_player.nickname}，剩余金币: {new_player_gold}")
                        else:
                            result.append(f"\n你的金币不足以支付 {rent} 金币的租金！")
                            logger.debug(f"玩家 {user_id} 的金币不足以支付租金，当前金币: {player.gold}, 需要租金: {rent}")
                            # sakura_debug 不足以支付租金，不允许玩家前进
                    else:
                        result.append("⚠️ 地产所有者信息异常，请联系管理员")
                        logger.error(f"法获取地产所有者 {owner} 的信息，位置: {new_position}")
                else:
                    result.append("这是你的地盘")
                    result.append(f"🗺 区域类型: {block['region']}")
                    if property_info.get('level', 0) < 3:
                        rent = self.monopoly.calculate_rent(new_position)
                        result.append(f"🏘️ 等级: {property_info['level']}")
                        result.append(f"💴 租金: {rent}")
                        result.append("\n可以发送'升级地块'进行升级")
                    logger.debug(f"玩家 {user_id} 访问了自己的地盘，位置: {new_position}")

        # 更新玩家信息
        self._update_player_data(user_id, updates_info)
        return "\n".join(result)

    # 冒险
    def go_adventure(self, user_id):
        """冒险"""
        player = self.get_player(user_id)
        if not player:
            return "🤷‍♂️ 您还没有注册游戏"

        # 检查冷却时间（冒险cd: 10s）
        current_time = int(time.time())
        adventure_last_attack = player.adventure_last_attack
        cooldown = cooldown = constants.ADVENTURE_COOLDOWN

        # 检查冷却时间
        if current_time - adventure_last_attack < cooldown:
            remaining = cooldown - (current_time - adventure_last_attack)
            return f"⏳ 您刚刚进行过冒险活动,请等待 {remaining} 秒后再次进行冒险"

        # 检查玩家状态
        if int(player.hp) <= 0:
            return "😵 您的生命值不足，请先使用药品恢复"

        # 更新玩家冒险计时
        self._update_player_data(user_id, {
            'adventure_last_attack': str(current_time)
        })

        string_array = {
            "👹怪物巢穴": "阴暗的巢穴，怪物可能会突然袭击，小心埋伏。",
            "🌳古树之心": "一棵巨大的古树，周围萦绕着神秘能量，可能存在强大生物。",
            "🌫️迷雾谷地": "笼罩在浓雾中的森林低地，能见度极低，危险潜伏四周。",
            "👻幽灵空地": "空无一人的开阔地，传说这里曾发生过一场激烈战斗，鬼魂仍在游荡。",
            "🌳腐烂树林": "树木腐朽散发异味，小心脚下的陷阱和隐藏其中的怪物。",
            "🦌灵兽栖息地": "灵气浓厚的区域，强大的灵兽在此守护着未知的宝藏。",
            "🟢毒沼密林": "密林深处隐藏着毒雾沼泽，触碰毒气可能引发严重的危机。",
            "🌙月光草原": "一片开阔的森林空地，在夜晚被月光照耀，敌人会利用闪避和潜行。",
            "🏚️荒弃村落": "一个长期荒废的村庄，建筑坍塌，有危险生物潜伏其中。",
            "🌳暗影森林": "阳光难以穿透的森林深处，到处充满暗影与未知生物的气息。",
            "⛰️绝壁险峰": "陡峭的山峰，怪物可能从高处发动偷袭，注意脚下的危险。",
            "🔥熔岩洞窟": "炽热的洞窟，周围充满熔岩流动的声音，强大的火焰生物潜伏其中。",
            "🏜️流沙之地": "广袤的沙漠中隐藏着流沙陷阱，敌人可能突然从沙中出现。",
            "☀烈日废墟": "沙漠深处的废墟，炽热的阳光让战斗变得更加艰难，怪物潜伏在阴影中。",
            "🌪️沙暴迷城": "被沙暴掩埋的古老城市，能见度极低，敌人可能躲藏在废墟中。",
            "❄️寒冰峡谷": "寒风呼啸的峡谷，冰雪覆盖的地面让战斗更加危险。",
            "🏯冻土遗迹": "冰原深处的遗迹，寒冷让人难以忍受，敌人隐藏在冰雪之下。",
            "🟢毒雾沼泽": "沼泽地中弥漫着毒雾，敌人可能隐藏在泥潭深处。",
            "☠️枯骨之地": "沼泽深处堆满了枯骨，传说这里是强大怪物的狩猎场。"
        }

        # 随机选择一个场景
        random_pos = random.choice(list(string_array))

        # 获取对应值
        random_value = string_array[random_pos]

        result = [
            f"[{player.nickname}] 来到了 [{random_pos}]\n\n「{random_value}」\n"
        ]

        # 触发战斗
        battle_result = self._battle(user_id, self._generate_monster(player, random_pos))
        result.append(battle_result)

        return "\n".join(result)

    def _generate_monster(self, player, scene):
        """
        根据玩家等级和场景生成怪物

        :param player: 玩家对象，需有 `level` 属性
        :param scene: 场景名称，对应 "怪物巢穴"、"古树之心" 等
        :return: 生成的怪物字典信息
        """
        # 校验传入的玩家等级合法性
        player_level = max(1, int(player.level))

        # 使用毫秒级时间戳作为随机数种子
        current_time_ms = int(time.time_ns())
        random.seed(current_time_ms)
        # 怪物的等级随机(根据玩家等级上下浮动)
        random_level = random.randint(-2, 2)
        # 计算怪物等级
        monster_level = max(1, player_level + random_level)
        # 计算等级因子
        level_factor = 1 + (monster_level - 1) * 0.3

        # 定义怪物库
        monsters = {
            "👹怪物巢穴": [
                {'name': '森林史莱姆🍄', 'hp': int(60 * level_factor), 'attack': int(1.3 * 10 * level_factor), 'defense': int(6 * level_factor), 'exp': int(20 * level_factor), 'gold': int(10 * 30 * level_factor)},
                {'name': '潜伏狼蛛🕷️', 'hp': int(80 * level_factor), 'attack': int(1.3 * 15 * level_factor), 'defense': int(8 * level_factor), 'exp': int(25 * level_factor), 'gold': int(10 * 35 * level_factor)},
                {'name': '巢穴蝙蝠🦇', 'hp': int(50 * level_factor), 'attack': int(1.3 * 12 * level_factor), 'defense': int(5 * level_factor), 'exp': int(18 * level_factor), 'gold': int(10 * 28 * level_factor)},
                {'name': '毒刺蜂🐝', 'hp': int(70 * level_factor), 'attack': int(1.3 * 18 * level_factor), 'defense': int(7 * level_factor), 'exp': int(22 * level_factor), 'gold': int(10 * 32 * level_factor)},
                {'name': '黑影潜伏者🌑', 'hp': int(100 * level_factor), 'attack': int(1.3 * 20 * level_factor), 'defense': int(10 * level_factor), 'exp': int(30 * level_factor), 'gold': int(10 * 40 * level_factor)}
            ],
            "🌳古树之心": [
                {'name': '树精守卫🌳', 'hp': int(120 * level_factor), 'attack': int(1.3 * 25 * level_factor), 'defense': int(15 * level_factor), 'exp': int(35 * level_factor), 'gold': int(10 * 50 * level_factor)},
                {'name': '魔化藤蔓🌿', 'hp': int(90 * level_factor), 'attack': int(1.3 * 20 * level_factor), 'defense': int(12 * level_factor), 'exp': int(28 * level_factor), 'gold': int(10 * 45 * level_factor)},
                {'name': '树灵幽影🌲', 'hp': int(80 * level_factor), 'attack': int(1.3 * 22 * level_factor), 'defense': int(10 * level_factor), 'exp': int(30 * level_factor), 'gold': int(10 * 42 * level_factor)},
                {'name': '腐化树妖🌳', 'hp': int(150 * level_factor), 'attack': int(1.3 * 30 * level_factor), 'defense': int(18 * level_factor), 'exp': int(40 * level_factor), 'gold': int(10 * 60 * level_factor)},
                {'name': '古树之魂🌌', 'hp': int(200 * level_factor), 'attack': int(1.3 * 35 * level_factor), 'defense': int(20 * level_factor), 'exp': int(50 * level_factor), 'gold': int(10 * 70 * level_factor)}
            ],
            "🌫️迷雾谷地": [
                {'name': '雾影幽魂👻', 'hp': int(70 * level_factor), 'attack': int(1.3 * 18 * level_factor), 'defense': int(8 * level_factor), 'exp': int(25 * level_factor), 'gold': int(10 * 35 * level_factor)},
                {'name': '迷雾猎手🏹', 'hp': int(90 * level_factor), 'attack': int(1.3 * 22 * level_factor), 'defense': int(10 * level_factor), 'exp': int(30 * level_factor), 'gold': int(10 * 45 * level_factor)},
                {'name': '隐匿毒蛇🐍', 'hp': int(60 * level_factor), 'attack': int(1.3 * 20 * level_factor), 'defense': int(6 * level_factor), 'exp': int(22 * level_factor), 'gold': int(10 * 32 * level_factor)},
                {'name': '雾中行者🚶', 'hp': int(110 * level_factor), 'attack': int(1.3 * 28 * level_factor), 'defense': int(12 * level_factor), 'exp': int(35 * level_factor), 'gold': int(10 * 50 * level_factor)},
                {'name': '迷雾巨兽🐺', 'hp': int(150 * level_factor), 'attack': int(1.3 * 32 * level_factor), 'defense': int(18 * level_factor), 'exp': int(45 * level_factor), 'gold': int(10 * 65 * level_factor)}
            ],
            "👻幽灵空地": [
                {'name': '幽灵战士💀', 'hp': int(100 * level_factor), 'attack': int(1.3 * 25 * level_factor), 'defense': int(12 * level_factor), 'exp': int(35 * level_factor), 'gold': int(10 * 50 * level_factor)},
                {'name': '亡灵弓手🏹', 'hp': int(80 * level_factor), 'attack': int(1.3 * 28 * level_factor), 'defense': int(10 * level_factor), 'exp': int(32 * level_factor), 'gold': int(10 * 48 * level_factor)},
                {'name': '怨灵法师🧙', 'hp': int(90 * level_factor), 'attack': int(1.3 * 30 * level_factor), 'defense': int(8 * level_factor), 'exp': int(38 * level_factor), 'gold': int(10 * 52 * level_factor)},
                {'name': '幽魂骑士🏇', 'hp': int(140 * level_factor), 'attack': int(1.3 * 35 * level_factor), 'defense': int(15 * level_factor), 'exp': int(45 * level_factor), 'gold': int(10 * 65 * level_factor)},
                {'name': '复仇亡灵💀', 'hp': int(160 * level_factor), 'attack': int(1.3 * 40 * level_factor), 'defense': int(18 * level_factor), 'exp': int(50 * level_factor), 'gold': int(10 * 70 * level_factor)}
            ],
            "🌳腐烂树林": [
                {'name': '腐朽树妖🌳', 'hp': int(120 * level_factor), 'attack': int(1.3 * 20 * level_factor), 'defense': int(15 * level_factor), 'exp': int(35 * level_factor), 'gold': int(10 * 45 * level_factor)},
                {'name': '毒液史莱姆🟢', 'hp': int(70 * level_factor), 'attack': int(1.3 * 18 * level_factor), 'defense': int(8 * level_factor), 'exp': int(25 * level_factor), 'gold': int(10 * 35 * level_factor)},
                {'name': '腐化狼蛛🕷️', 'hp': int(80 * level_factor), 'attack': int(1.3 * 22 * level_factor), 'defense': int(10 * level_factor), 'exp': int(30 * level_factor), 'gold': int(10 * 40 * level_factor)},
                {'name': '腐木傀儡🌳', 'hp': int(150 * level_factor), 'attack': int(1.3 * 28 * level_factor), 'defense': int(18 * level_factor), 'exp': int(40 * level_factor), 'gold': int(10 * 55 * level_factor)},
                {'name': '树根潜伏者🌳', 'hp': int(100 * level_factor), 'attack': int(1.3 * 25 * level_factor), 'defense': int(12 * level_factor), 'exp': int(35 * level_factor), 'gold': int(10 * 50 * level_factor)}
            ],
            "🦌灵兽栖息地": [
                {'name': '灵气鹿🦌', 'hp': int(80 * level_factor), 'attack': int(1.3 * 15 * level_factor), 'defense': int(12 * level_factor), 'exp': int(25 * level_factor), 'gold': int(10 * 40 * level_factor)},
                {'name': '守护灵兽🦄', 'hp': int(120 * level_factor), 'attack': int(1.3 * 30 * level_factor), 'defense': int(18 * level_factor), 'exp': int(45 * level_factor), 'gold': int(10 * 55 * level_factor)},
                {'name': '灵狐幻影🦊', 'hp': int(70 * level_factor), 'attack': int(1.3 * 22 * level_factor), 'defense': int(10 * level_factor), 'exp': int(28 * level_factor), 'gold': int(10 * 38 * level_factor)},
                {'name': '秘境猛虎🐯', 'hp': int(140 * level_factor), 'attack': int(1.3 * 35 * level_factor), 'defense': int(15 * level_factor), 'exp': int(50 * level_factor), 'gold': int(10 * 65 * level_factor)},
                {'name': '灵域飞龙🐉', 'hp': int(180 * level_factor), 'attack': int(1.3 * 40 * level_factor), 'defense': int(20 * level_factor), 'exp': int(60 * level_factor), 'gold': int(10 * 80 * level_factor)}
            ],
            "🟢毒沼密林": [
                {'name': '毒液巨蛛🕷️', 'hp': int(100 * level_factor), 'attack': int(1.3 * 25 * level_factor), 'defense': int(12 * level_factor), 'exp': int(35 * level_factor), 'gold': int(10 * 50 * level_factor)},
                {'name': '毒气史莱姆🟢', 'hp': int(80 * level_factor), 'attack': int(1.3 * 20 * level_factor), 'defense': int(10 * level_factor), 'exp': int(28 * level_factor), 'gold': int(10 * 38 * level_factor)},
                {'name': '瘴气妖藤🌿', 'hp': int(120 * level_factor), 'attack': int(1.3 * 28 * level_factor), 'defense': int(15 * level_factor), 'exp': int(40 * level_factor), 'gold': int(10 * 55 * level_factor)},
                {'name': '毒雾蜥蜴🦎', 'hp': int(90 * level_factor), 'attack': int(1.3 * 22 * level_factor), 'defense': int(10 * level_factor), 'exp': int(30 * level_factor), 'gold': int(10 * 42 * level_factor)},
                {'name': '瘴气守护者🗿', 'hp': int(160 * level_factor), 'attack': int(1.3 * 35 * level_factor), 'defense': int(20 * level_factor), 'exp': int(50 * level_factor), 'gold': int(10 * 70 * level_factor)}
            ],
            "🌙月光草原": [
                {'name': '草原狼群🐺', 'hp': int(80 * level_factor), 'attack': int(1.3 * 20 * level_factor), 'defense': int(10 * level_factor), 'exp': int(28 * level_factor), 'gold': int(10 * 40 * level_factor)},
                {'name': '隐匿猎手🏹', 'hp': int(90 * level_factor), 'attack': int(1.3 * 25 * level_factor), 'defense': int(12 * level_factor), 'exp': int(35 * level_factor), 'gold': int(10 * 50 * level_factor)},
                {'name': '月光幽灵👻', 'hp': int(100 * level_factor), 'attack': int(1.3 * 30 * level_factor), 'defense': int(10 * level_factor), 'exp': int(40 * level_factor), 'gold': int(10 * 55 * level_factor)},
                {'name': '夜影刺客🔪', 'hp': int(110 * level_factor), 'attack': int(1.3 * 35 * level_factor), 'defense': int(15 * level_factor), 'exp': int(45 * level_factor), 'gold': int(10 * 60 * level_factor)},
                {'name': '草原巨熊🐻', 'hp': int(200 * level_factor), 'attack': int(1.3 * 50 * level_factor), 'defense': int(25 * level_factor), 'exp': int(60 * level_factor), 'gold': int(10 * 80 * level_factor)}
            ],
            "🏚️荒弃村落": [
                {'name': '村落幽魂👻', 'hp': int(90 * level_factor), 'attack': int(1.3 * 20 * level_factor), 'defense': int(10 * level_factor), 'exp': int(30 * level_factor), 'gold': int(10 * 40 * level_factor)},
                {'name': '腐化村民💀', 'hp': int(100 * level_factor), 'attack': int(1.3 * 25 * level_factor), 'defense': int(15 * level_factor), 'exp': int(35 * level_factor), 'gold': int(10 * 50 * level_factor)},
                {'name': '废墟潜伏者🕵️', 'hp': int(80 * level_factor), 'attack': int(1.3 * 22 * level_factor), 'defense': int(12 * level_factor), 'exp': int(28 * level_factor), 'gold': int(10 * 38 * level_factor)},
                {'name': '憎恶尸鬼💀', 'hp': int(150 * level_factor), 'attack': int(1.3 * 30 * level_factor), 'defense': int(18 * level_factor), 'exp': int(50 * level_factor), 'gold': int(10 * 65 * level_factor)},
                {'name': '村落恶鬼👹', 'hp': int(120 * level_factor), 'attack': int(1.3 * 35 * level_factor), 'defense': int(15 * level_factor), 'exp': int(45 * level_factor), 'gold': int(10 * 60 * level_factor)}
            ],
            "🌳暗影森林": [
                {'name': '暗影猎手🔪', 'hp': int(100 * level_factor), 'attack': int(1.3 * 30 * level_factor), 'defense': int(15 * level_factor), 'exp': int(40 * level_factor), 'gold': int(10 * 55 * level_factor)},
                {'name': '黑暗幽灵👻', 'hp': int(90 * level_factor), 'attack': int(1.3 * 25 * level_factor), 'defense': int(12 * level_factor), 'exp': int(35 * level_factor), 'gold': int(10 * 45 * level_factor)},
                {'name': '夜行毒蛇🐍', 'hp': int(80 * level_factor), 'attack': int(1.3 * 20 * level_factor), 'defense': int(10 * level_factor), 'exp': int(28 * level_factor), 'gold': int(10 * 38 * level_factor)},
                {'name': '暗影潜伏者🔪', 'hp': int(120 * level_factor), 'attack': int(1.3 * 35 * level_factor), 'defense': int(18 * level_factor), 'exp': int(45 * level_factor), 'gold': int(10 * 65 * level_factor)},
                {'name': '黑暗树妖🌳', 'hp': int(150 * level_factor), 'attack': int(1.3 * 40 * level_factor), 'defense': int(20 * level_factor), 'exp': int(55 * level_factor), 'gold': int(10 * 75 * level_factor)}
            ],
            "⛰️绝壁险峰": [
                {'name': '山崖猛禽🦅', 'hp': int(80 * level_factor), 'attack': int(1.3 * 25 * level_factor), 'defense': int(10 * level_factor), 'exp': int(30 * level_factor), 'gold': int(10 * 50 * level_factor)},
                {'name': '岩石巨人🗿', 'hp': int(150 * level_factor), 'attack': int(1.3 * 40 * level_factor), 'defense': int(30 * level_factor), 'exp': int(60 * level_factor), 'gold': int(10 * 70 * level_factor)},
                {'name': '爬山毒蛇🐍', 'hp': int(70 * level_factor), 'attack': int(1.3 * 15 * level_factor), 'defense': int(10 * level_factor), 'exp': int(25 * level_factor), 'gold': int(10 * 35 * level_factor)},
                {'name': '峭壁蝙蝠🦇', 'hp': int(60 * level_factor), 'attack': int(1.3 * 10 * level_factor), 'defense': int(8 * level_factor), 'exp': int(20 * level_factor), 'gold': int(10 * 30 * level_factor)},
                {'name': '崖顶恶鹰🦅', 'hp': int(130 * level_factor), 'attack': int(1.3 * 35 * level_factor), 'defense': int(12 * level_factor), 'exp': int(50 * level_factor), 'gold': int(10 * 65 * level_factor)}
            ],
            "🔥熔岩洞窟": [
                {'name': '火焰元素🔥', 'hp': int(100 * level_factor), 'attack': int(1.3 * 30 * level_factor), 'defense': int(12 * level_factor), 'exp': int(40 * level_factor), 'gold': int(10 * 60 * level_factor)},
                {'name': '熔岩巨人🗿', 'hp': int(180 * level_factor), 'attack': int(1.3 * 50 * level_factor), 'defense': int(20 * level_factor), 'exp': int(70 * level_factor), 'gold': int(10 * 90 * level_factor)},
                {'name': '火焰蝙蝠🦇', 'hp': int(80 * level_factor), 'attack': int(1.3 * 25 * level_factor), 'defense': int(10 * level_factor), 'exp': int(35 * level_factor), 'gold': int(10 * 50 * level_factor)},
                {'name': '熔岩魔蛇🐍', 'hp': int(90 * level_factor), 'attack': int(1.3 * 20 * level_factor), 'defense': int(15 * level_factor), 'exp': int(30 * level_factor), 'gold': int(10 * 42 * level_factor)},
                {'name': '炎爆恶魔😈', 'hp': int(200 * level_factor), 'attack': int(1.3 * 60 * level_factor), 'defense': int(25 * level_factor), 'exp': int(80 * level_factor), 'gold': int(10 * 100 * level_factor)}
            ],
            "🏜️流沙之地": [
                {'name': '流沙巨蟒🐍', 'hp': int(120 * level_factor), 'attack': int(1.3 * 30 * level_factor), 'defense': int(10 * level_factor), 'exp': int(40 * level_factor), 'gold': int(10 * 55 * level_factor)},
                {'name': '沙漠蝎子🦂', 'hp': int(100 * level_factor), 'attack': int(1.3 * 25 * level_factor), 'defense': int(12 * level_factor), 'exp': int(35 * level_factor), 'gold': int(10 * 50 * level_factor)},
                {'name': '沙尘潜伏者🔪', 'hp': int(80 * level_factor), 'attack': int(1.3 * 20 * level_factor), 'defense': int(8 * level_factor), 'exp': int(28 * level_factor), 'gold': int(10 * 40 * level_factor)},
                {'name': '沙之傀儡🗿', 'hp': int(160 * level_factor), 'attack': int(1.3 * 40 * level_factor), 'defense': int(20 * level_factor), 'exp': int(60 * level_factor), 'gold': int(10 * 70 * level_factor)},
                {'name': '沙漠猎犬🐕', 'hp': int(90 * level_factor), 'attack': int(1.3 * 22 * level_factor), 'defense': int(10 * level_factor), 'exp': int(32 * level_factor), 'gold': int(10 * 45 * level_factor)}
            ],
            "☀烈日废墟": [
                {'name': '炎蝎🦂', 'hp': int(100 * level_factor), 'attack': int(1.3 * 30 * level_factor), 'defense': int(10 * level_factor), 'exp': int(40 * level_factor), 'gold': int(10 * 55 * level_factor)},
                {'name': '废墟幽魂👻', 'hp': int(120 * level_factor), 'attack': int(1.3 * 28 * level_factor), 'defense': int(15 * level_factor), 'exp': int(45 * level_factor), 'gold': int(10 * 60 * level_factor)},
                {'name': '火焰殉教者🧕', 'hp': int(140 * level_factor), 'attack': int(1.3 * 40 * level_factor), 'defense': int(20 * level_factor), 'exp': int(60 * level_factor), 'gold': int(10 * 75 * level_factor)},
                {'name': '石化蜥蜴🦎', 'hp': int(80 * level_factor), 'attack': int(1.3 * 25 * level_factor), 'defense': int(12 * level_factor), 'exp': int(35 * level_factor), 'gold': int(10 * 50 * level_factor)},
                {'name': '烈日幻影👻', 'hp': int(70 * level_factor), 'attack': int(1.3 * 23 * level_factor), 'defense': int(8 * level_factor), 'exp': int(28 * level_factor), 'gold': int(10 * 40 * level_factor)}
            ],
            "🌪️沙暴迷城": [
                {'name': '沙暴刺客🔪', 'hp': int(90 * level_factor), 'attack': int(1.3 * 28 * level_factor), 'defense': int(12 * level_factor), 'exp': int(35 * level_factor), 'gold': int(10 * 50 * level_factor)},
                {'name': '废墟守卫👮‍♂️', 'hp': int(150 * level_factor), 'attack': int(1.3 * 35 * level_factor), 'defense': int(18 * level_factor), 'exp': int(50 * level_factor), 'gold': int(10 * 70 * level_factor)},
                {'name': '迷城幽魂👻', 'hp': int(110 * level_factor), 'attack': int(1.3 * 25 * level_factor), 'defense': int(10 * level_factor), 'exp': int(38 * level_factor), 'gold': int(10 * 55 * level_factor)},
                {'name': '黄沙巫师🧙', 'hp': int(80 * level_factor), 'attack': int(1.3 * 22 * level_factor), 'defense': int(8 * level_factor), 'exp': int(30 * level_factor), 'gold': int(10 * 45 * level_factor)},
                {'name': '沙暴元素🌪️', 'hp': int(130 * level_factor), 'attack': int(1.3 * 40 * level_factor), 'defense': int(15 * level_factor), 'exp': int(55 * level_factor), 'gold': int(10 * 65 * level_factor)}
            ],
            "❄️寒冰峡谷": [
                {'name': '极地狼群🐺', 'hp': int(120 * level_factor), 'attack': int(1.3 * 28 * level_factor), 'defense': int(15 * level_factor), 'exp': int(40 * level_factor), 'gold': int(10 * 55 * level_factor)},
                {'name': '冰原独角兽🦄', 'hp': int(150 * level_factor), 'attack': int(1.3 * 35 * level_factor), 'defense': int(18 * level_factor), 'exp': int(50 * level_factor), 'gold': int(10 * 65 * level_factor)},
                {'name': '寒霜飞鹰🦅', 'hp': int(90 * level_factor), 'attack': int(1.3 * 22 * level_factor), 'defense': int(10 * level_factor), 'exp': int(32 * level_factor), 'gold': int(10 * 45 * level_factor)},
                {'name': '冰霜元素❄️', 'hp': int(130 * level_factor), 'attack': int(1.3 * 30 * level_factor), 'defense': int(12 * level_factor), 'exp': int(45 * level_factor), 'gold': int(10 * 55 * level_factor)},
                {'name': '极寒古龙🐲', 'hp': int(200 * level_factor), 'attack': int(1.3 * 50 * level_factor), 'defense': int(25 * level_factor), 'exp': int(80 * level_factor), 'gold': int(10 * 100 * level_factor)}
            ],
            "🏯冻土遗迹": [
                {'name': '遗迹守护者🗿', 'hp': int(140 * level_factor), 'attack': int(1.3 * 40 * level_factor), 'defense': int(20 * level_factor), 'exp': int(60 * level_factor), 'gold': int(10 * 75 * level_factor)},
                {'name': '冰冻骷髅💀', 'hp': int(120 * level_factor), 'attack': int(1.3 * 30 * level_factor), 'defense': int(15 * level_factor), 'exp': int(45 * level_factor), 'gold': int(10 * 55 * level_factor)},
                {'name': '冻土游魂👻', 'hp': int(100 * level_factor), 'attack': int(1.3 * 25 * level_factor), 'defense': int(12 * level_factor), 'exp': int(38 * level_factor), 'gold': int(10 * 50 * level_factor)},
                {'name': '霜冻教徒🧙', 'hp': int(80 * level_factor), 'attack': int(1.3 * 22 * level_factor), 'defense': int(10 * level_factor), 'exp': int(30 * level_factor), 'gold': int(10 * 42 * level_factor)},
                {'name': '寒霜傀儡❄️', 'hp': int(160 * level_factor), 'attack': int(1.3 * 35 * level_factor), 'defense': int(18 * level_factor), 'exp': int(50 * level_factor), 'gold': int(10 * 65 * level_factor)}
            ],
            "🟢毒雾沼泽": [
                {'name': '毒鳞鱼人🧜‍♂️', 'hp': int(90 * level_factor), 'attack': int(1.3 * 20 * level_factor), 'defense': int(12 * level_factor), 'exp': int(32 * level_factor), 'gold': int(10 * 42 * level_factor)},
                {'name': '腐臭鳄鱼🐊', 'hp': int(120 * level_factor), 'attack': int(1.3 * 30 * level_factor), 'defense': int(15 * level_factor), 'exp': int(45 * level_factor), 'gold': int(10 * 60 * level_factor)},
                {'name': '瘴气魔鹰🦅', 'hp': int(70 * level_factor), 'attack': int(1.3 * 18 * level_factor), 'defense': int(8 * level_factor), 'exp': int(25 * level_factor), 'gold': int(10 * 38 * level_factor)},
                {'name': '泥潭刺客🎭', 'hp': int(150 * level_factor), 'attack': int(1.3 * 40 * level_factor), 'defense': int(20 * level_factor), 'exp': int(60 * level_factor), 'gold': int(10 * 75 * level_factor)},
                {'name': '沼泽魔神👹', 'hp': int(200 * level_factor), 'attack': int(1.3 * 50 * level_factor), 'defense': int(25 * level_factor), 'exp': int(80 * level_factor), 'gold': int(10 * 100 * level_factor)}
            ],
            "☠️枯骨之地": [
                {'name': '枯骨战士☠️', 'hp': int(100 * level_factor), 'attack': int(1.3 * 28 * level_factor), 'defense': int(12 * level_factor), 'exp': int(38 * level_factor), 'gold': int(10 * 50 * level_factor)},
                {'name': '沼泽骷髅💀', 'hp': int(90 * level_factor), 'attack': int(1.3 * 20 * level_factor), 'defense': int(10 * level_factor), 'exp': int(30 * level_factor), 'gold': int(10 * 45 * level_factor)},
                {'name': '不死巫师🧙', 'hp': int(130 * level_factor), 'attack': int(1.3 * 35 * level_factor), 'defense': int(18 * level_factor), 'exp': int(50 * level_factor), 'gold': int(10 * 65 * level_factor)},
                {'name': '亡灵巨兽🐺', 'hp': int(160 * level_factor), 'attack': int(1.3 * 40 * level_factor), 'defense': int(20 * level_factor), 'exp': int(60 * level_factor), 'gold': int(10 * 75 * level_factor)},
                {'name': '骨堆恶灵👹', 'hp': int(200 * level_factor), 'attack': int(1.3 * 50 * level_factor), 'defense': int(25 * level_factor), 'exp': int(80 * level_factor), 'gold': int(10 * 100 * level_factor)}
            ]
        }

        # 校验场景是否有效
        if scene not in monsters:
            raise ValueError(f"无效的场景名称：{scene}")

        # 随机选择该场景中的一个怪物
        monster = random.choice(monsters[scene])
        # 增加怪物等级
        monster['level'] = monster_level

        # 判断是否生成变异怪物
        if self._is_mutant():  # 使用抽象方法判断是否变异
            monster = self._apply_mutation(monster)

        return monster

    def _is_mutant(self):
        """
        判断怪物是否变异
        :return: True if mutant, otherwise False
        """
        return random.random() < 0.15  # 15% 的变异概率

    def _apply_mutation(self, monster):
        """
        对怪物应用变异属性
        :param monster: 原怪物数据
        :return: 变异后的怪物字典
        """
        monster['name'] = f"变异的{monster['name']}"
        monster['hp'] = int(monster['hp'] * 1.5)
        monster['attack'] = int(monster['attack'] * 1.3)
        monster['defense'] = int(monster['defense'] * 1.2)
        monster['exp'] = int(monster['exp'] * 1.5)
        monster['gold'] = int(monster['gold'] * 1.5)
        return monster

    def _battle(self, user_id, monster):
        """战斗系统"""
        player = self.get_player(user_id)

        # 需要更新的玩家信息
        updates_info = {}

        # 初始化升级标志
        level_up = False

        # 玩家属性
        player_level = player.level
        player_hp = int(player.hp)
        player_max_hp = int(player.max_hp)
        player_attack = int(player.attack)
        player_defense = int(player.defense)
        player_name = player.nickname
        player_total_damage = 0

        # 怪物属性
        monster_level = monster['level']
        monster_hp = monster['hp']
        monster_max_hp = monster['hp']
        monster_attack = monster['attack']
        monster_defense = monster['defense']
        monster_name = monster.get('name', '未知怪物')
        monster_total_damage = 0

        #日志打印怪物属性
        logger.debug(f"玩家[{player_name}]属性: 生命值: {player_hp}/{player_max_hp}, 攻击力: {player_attack}, 防御力: {player_defense}")
        logger.debug(f"怪物[{monster_name}]属性: 生命值: {monster_hp}, 攻击力: {monster_attack}, 防御力: {monster_defense}")

        battle_log = [f"⚔️ 遭遇了 {monster['name']}！"]
        battle_log.append(f"\n{player_name} Lv.{player_level}\n❤️[{player_hp}/{player_max_hp}]\n⚔️[{player_attack}]\n🛡️[{str(player_defense)}]")
        battle_log.append(f"\n{monster_name} Lv.{monster_level}\n❤️[{monster_hp}/{monster_max_hp}]\n⚔️[{monster_attack}]\n🛡️[{str(monster_defense)}]")

        # 怪物是否狂暴状态
        is_berserk = False

        round_num = 1
        important_events = []

        while player_hp > 0 and monster_hp > 0:

            if constants.WEATHER_TO_KEEP_A_BATTLE_LOG:
                if round_num <= constants.REPORT_THE_NUMBER_OF_ROUNDS:
                    battle_log.append(f"\n第{round_num}回合")

            # 计算玩家伤害
            player_final_damage, player_explain_str = self.damage_calculation(player_attack, monster_defense)

            # 减少怪物血量
            monster_hp -= player_final_damage
            player_total_damage += player_final_damage

            if constants.WEATHER_TO_KEEP_A_BATTLE_LOG:
                # 记录战斗日志（前4回合）
                if round_num <= constants.REPORT_THE_NUMBER_OF_ROUNDS:
                    battle_log.append(f"{player_explain_str} [{player_name}] 对 [{monster_name}] 造成 {player_final_damage} 点伤害")

            # 检查怪物是否死亡
            if monster_hp <= 0:
                break

            # 检查怪物是否进入狂暴状态
            if not is_berserk and monster_hp < monster_max_hp * 0.3 and random.random() < 0.4:
                is_berserk = True
                # 提升怪物伤害
                monster_attack = int(monster_attack * 1.5)
                if constants.WEATHER_TO_KEEP_A_BATTLE_LOG:
                    if round_num <= constants.REPORT_THE_NUMBER_OF_ROUNDS:
                        battle_log.append(f"💢 {monster['name']}进入狂暴状态！")
                    else:
                        important_events.append(f"第{round_num}回合: {monster['name']}进入狂暴状态！")

            # 怪物反击
            if monster_hp > 0:
                # 计算怪物伤害
                monster_final_damage, monster_explain_str = self.damage_calculation(monster_attack, player_defense)
                # 减少玩家生命值
                player_hp -= monster_final_damage
                monster_total_damage += monster_final_damage

                life_steal = 0

                # 狂暴状态下吸血
                if is_berserk:
                    life_steal = int(monster_final_damage * 0.3)
                    monster_hp = min(monster_max_hp, monster_hp + life_steal)
                    if constants.WEATHER_TO_KEEP_A_BATTLE_LOG:
                        if round_num <= constants.REPORT_THE_NUMBER_OF_ROUNDS:
                            battle_log.append(f"{monster_explain_str} [{monster['name']}] 对 [{player_name}] 造成 {monster_final_damage} 点伤害，并吸取了 {life_steal} 点生命值")
                else:
                    if constants.WEATHER_TO_KEEP_A_BATTLE_LOG:
                        if round_num <= constants.REPORT_THE_NUMBER_OF_ROUNDS:
                            battle_log.append(f"{monster_explain_str} [{monster['name']}] 对 [{player_name}] 造成 {monster_final_damage} 点伤害")

            round_num += 1

        if player_hp < 0:
            battle_log.append(f"\n[{player_name}] 被打败了！😵")

        if monster_hp < 0:
            battle_log.append(f"\n[{monster_name}] 被打败了！😵")

        # 战斗结束
        battle_log.append(f"战斗持续了{round_num}回合")

        # 重要事件统计
        if important_events:
            battle_log.append("重要事件:")
            battle_log.extend(important_events)

        # 添加战斗只有一回合时的特殊战报
        if round_num == 1 and player_hp > 0:
            battle_log.append(f"{player_name}：一刀秒了，有什么好说的？")
        elif round_num == 1 and monster_hp > 0:
            battle_log.append(f"{monster_name}：一刀秒了，有什么好说的？")

        # 向战斗结果中添加玩家和怪物造成的总伤害
        battle_log.append(f"\n📊 伤害统计:")
        battle_log.append(f"[{player_name}]: {player_total_damage}")
        battle_log.append(f"[{monster_name}]: {monster_total_damage}")

        if player_hp > 0:
            drop_explain = None
            drop_consumables_str = None
            # 获取怪物基础经验值
            default_exp = monster['exp']

            # 每高一级增加4%经验
            exp_multiplier = 1 + (player.level * 0.04)

            # 结算经验/金币
            award_exp = int(default_exp * exp_multiplier)
            award_gold = int(min(player.level * 0.1, 1) * monster['gold'])
            actual_gain_gold = player.gold + award_gold
            updates_info['gold'] = actual_gain_gold

            # 根据获得经验判断玩家是否升级
            level_up_result = self.check_player_upgrade(player, award_exp)
            new_level = level_up_result['level']
            new_exp = level_up_result['exp']
            if new_level > player_level:
                # 玩家升级了
                level_up = True
                updates_info['level'] = new_level
                updates_info['exp'] = new_exp
            # 获取升级信息
            level_up_str = self.get_player_level_up_data(player, level_up_result, updates_info)
            # 物品掉落标志
            drop_flag = False
            if level_up_result['level'] == player_level:
                # 未升级，更新玩家血量
                updates_info['hp'] = player_hp
            # 判断是否掉落物品
            random.seed(time.time_ns())
            drop_num = random.randint(1, 100)
            if drop_num <= constants.EQUIPMENT_DROP_PROBABILITY:
                # 掉落装备
                drop_item = self.rouge_equipment_system.get_random_equipment(new_level)
                drop_explain = self.check_drop_equipment_has_same_name(drop_item, player, updates_info)
                # 设置掉落标志
                drop_flag = True

            random.seed(time.time_ns())
            drop_num = random.randint(1, 100)
            if drop_num <= constants.CONSUMABLE_DROP_PROBABILITY:
                # 随机掉落消耗品
                # 生成[0.0, 1.0)之间的随机数
                rand = random.random()
                if rand < 0.6:
                    # 60%的概率得到一种消耗品
                    num = 1
                elif rand < 0.6 + 0.3:
                    # 30%的概率得到两种消耗品
                    num = 2
                else:
                    # 剩下10%的概率得到三种消耗品
                    num = 3
                # 随机获得消耗品
                drop_consumables_str =  self.random_drop_consumables(player, updates_info, num)
                drop_flag = True

            # 更新玩家数据
            self._update_player_data(user_id, updates_info)

            player = self.get_player(user_id)

            # 战斗结算
            battle_log.append(f"\n🎉 战斗胜利")
            battle_log.append(f"✨ 获得 {award_exp} 经验值")
            battle_log.append(f"💰 获得 {award_gold} 金币")

            if drop_flag:
                battle_log.append(f"\n战利品：")
                if drop_consumables_str:
                    battle_log.append(f"{drop_consumables_str}")
                if drop_explain:
                    battle_log.append(f"{drop_explain}")

            if level_up:
                battle_log.append(f"\n{level_up_str}")
            else:
                battle_log.append(f"\n[{player_name}] Lv.{player.level}\nExp: {player.exp}/{player.max_exp}\nHp : {player.hp}/{player.max_hp}")
        else:
            # 更新玩家血量
            self._update_player_data(user_id, {
                'hp': '0',
            })
            battle_log.append(f"\n💀 战斗失败！")
            battle_log.append(f"\n[{monster_name}] Lv.{monster_level}\nHp  : {monster_hp}/{monster_max_hp}")

        return "\n".join(battle_log)

    def use_item(self, user_id, content):
        """使用物品功能"""
        try:
            # 解析命令，格式为 "使用 物品名" 或 "使用 物品名 数量"
            parts = content.split()
            if len(parts) < 2:
                return "❌ 使用格式错误！请使用: 使用 物品名 [数量]"

            item_name = parts[1]
            amount = 1  # 默认使用1个
            if len(parts) > 2:
                amount = int(parts[2])
                if amount <= 0:
                    return "❌ 使用数量至少为一个"
        except (IndexError, ValueError):
            return "❌ 使用格式错误！请使用: 使用 物品名 [数量]"

        # 检查玩家是否存在
        player = self.get_player(user_id)
        if not player:
            return "❌ 您还没注册,请先注册 "

        # 获取背包字典
        inventory = player.inventory

        # 获取物品信息
        if item_name not in inventory:
            return f"🤷‍♂️ 你没有物品 [{item_name}]"

        item_type = inventory.get(item_name, {}).get("type", "other")

        # 判断物品类型
        if item_type != 'consumable':
            return f"🤷‍♂️ 物品 [{item_name}] 并非消耗品"

        item_description = inventory.get(item_name, {}).get("description", {})

        item_hp = item_description.get("hp", 0)
        # 检查背包中是否有足够的物品
        item_count = inventory[item_name]["amount"]
        if item_count < amount:
            return f"🤷‍♂️ 背包中只有 {item_count} 个 {item_name}"

        if player.hp == player.max_hp:
            return "🙅‍♂️ 您的生命值已满，无需回复。"

        # 计算恢复效果
        current_hp = int(player.hp)
        max_hp = int(player.max_hp)
        heal_amount = item_hp * amount

        # 计算新的生命值
        new_hp = min(current_hp + heal_amount, max_hp)

        # 从背包中移除物品
        if item_count == amount:
            del inventory[item_name]
        else:
            inventory[item_name]["amount"] -= amount

        # 更新玩家数据时添加使用时间
        updates = {
            'inventory': inventory,
            'hp': new_hp
        }

        self._update_player_data(user_id, updates)

        return f"使用 {amount} 个 {item_name}，恢复 {new_hp - current_hp} 点生命值！\n当前生命值: {new_hp}/{max_hp}"

    def get_player_status(self, user_id, detail=False):
        """获取玩家状态"""
        player = self.get_player(user_id)
        if not player:
            return "❌ 您还没注册,请先注册 "

        # 使用Player类的get_player_status方法
        return player.get_player_status(detail)

    def daily_checkin(self, user_id):
        """每日签到"""
        try:
            logger.info(f"用户 {user_id} 尝试进行每日签到")
            player = self.get_player(user_id)
            if not player:
                logger.warning(f"用户 {user_id} 未注册，无法签到")
                return "❌ 您还没注册,请先注册 "

            # 获取今天的日期
            today = datetime.today().date()
            # 创建一个时间对象，时分秒为00:00:00
            midnight_time = datetime_time(0, 0, 0)
            # 组合日期和时间
            datetime_combined = datetime.combine(today, midnight_time)
            # 获取时间戳（以秒为单位）
            today_timestamp = int(datetime_combined.timestamp())

            # 检查签到状态
            if player.sign_in_timestamp == today_timestamp:
                logger.info(f"用户 {user_id} 今天已经签到过了")
                return "📝 您今天已经签到过了"

            # 预定义需要返回给玩家的信息
            report_log = []
            updates = {}

            # 定义吉的加成和诗句
            fortune_bonuses = {
                "大吉": 1.0,
                "中吉": 0.5,
                "小吉": 0.2,
                "末吉": 0.0
            }

            # 随机选择吉的状态
            current_time_ms = int(time.time_ns())
            random.seed(current_time_ms)
            fortune = random.choice(list(fortune_bonuses.keys()))
            bonus_multiplier = fortune_bonuses[fortune]

            # 计算奖励
            base_reward = constants.SIGN_IN_GOLD_BONUS
            base_exp_reward = constants.SIGN_IN_EXP_BONUS
            reward = int(base_reward * (1 + bonus_multiplier))
            exp_reward = int(base_exp_reward * (1 + bonus_multiplier) * player.level)

            logger.info(f"用户 {user_id} 签到奖励: {reward}金币, {exp_reward}经验, 状态: {fortune}")
            # 根据获得经验判断玩家是否升级
            level_up_result = self.check_player_upgrade(player, exp_reward)
            # 获取升级播报
            level_up_str = self.get_player_level_up_data(player, level_up_result, updates)

            # 更新数据
            updates['gold'] = player.gold + reward
            updates['sign_in_timestamp'] = today_timestamp

            self._update_player_data(user_id, updates)
            logger.info(f"用户 {user_id} 数据更新成功: {updates}")

            # 随机选择一首诗
            poem = random.choice(constants.SIGN_IN_POEMS[fortune])

            report_log.append(f"🎉 签到成功！")
            report_log.append(f"🍀 今日运势：{fortune}")
            report_log.append(f"💰 金币奖励：{reward}")
            report_log.append(f"📈 经验奖励：{exp_reward}")
            if len(level_up_str) > 0:
                # 玩家升级
                report_log.append(f"\n {level_up_str}")
            report_log.append(f"\n「{poem}」")

            return "\n".join(report_log)

        except Exception as e:
            logger.error(f"用户 {user_id} 签到出错: {e}")
            return f"⚠️ 签到失败: {str(e)}"

    def give_item(self, user_id, content, msg: ChatMessage):
        # 解析命令参数
        parts = content.split()
        if len(parts) < 4:
            return "❌ 格式错误！请使用: 赠送 @用户 物品名 数量"

        target_id = None
        # 解析@后面的用户名
        for part in parts:
            if part.startswith('@'):
                target_name = part[1:]  # 去掉@符号
                # 遍历players.csv查找匹配的用户
                target_player = self._get_player_by_nickname(target_name)
                target_id = target_player.user_id
                break  # 找到第一个@用户后就退出
        if not target_id:
            return "🔍 无法找到目标用户，请确保该用户已注册游戏"

        # 从消息内容中提取物品名和数量
        # 跳过第一个词"赠送"和@用户名
        remaining_parts = [p for p in parts[1:] if not p.startswith('@')]
        if len(remaining_parts) < 2:
            return "❌ 请指定物品名称和数量"

        item_name = remaining_parts[0]
        try:
            amount = int(remaining_parts[1])
            if amount <= 0:
                return "❌ 赠送数量必须大于0"
        except (IndexError, ValueError):
            return "❌ 请正确指定赠送数量"

        # 检查双方是否都已注册
        sender = self.get_player(user_id)
        if not sender:
            return "❌ 您还没注册,请先注册"

        receiver = self.get_player(target_id)
        if not receiver:
            return "🙅‍♂️ 对方还没有注册游戏"

        # 检查发送者是否拥有足够的物品
        sender_inventory = sender.inventory
        receiver_inventory = receiver.inventory
        if sender_inventory[item_name]["amount"] < amount:
            return f"🤷‍♂️ 您没有足够的 {item_name}\n当前拥有: {sender_inventory[item_name]['amount']}"
        else:
            give_you_item = sender_inventory[item_name]
            if sender_inventory[item_name]["amount"] == amount:
                # 如果发送者的物品数量等于赠送数量，直接删除该物品
                sender_inventory.pop(item_name)
            else:
                # 赠送物品的一方需要减少物品数量
                sender_inventory[item_name]["amount"] -= amount

            # 检查对方是否拥有此物品
            if item_name in receiver.inventory:
                # 如果对方已经拥有该物品，增加数量
                receiver_inventory[item_name]["amount"] += amount
            else:
                # 将物品添加到对方的背包
                receiver_inventory[item_name] = give_you_item

        # 更新双方的背包
        self._update_player_data(user_id, {
            'inventory': sender_inventory
        })
        self._update_player_data(target_id, {
            'inventory': receiver_inventory
        })

        return f"[{sender.nickname}] 成功将 {amount} 个 {item_name}🎁 赠送给了 {receiver.nickname}"

    def show_leaderboard(self, user_id, content):
        """显示排行榜"""
        try:
            # 默认显示金币排行
            board_type = "金币"
            if content and len(content.split()) > 1:
                board_type = content.split()[1]

            if board_type not in ["金币", "等级"]:
                return "⚠️ 目前支持的排行榜类型：金币/等级"

            # 读取所有玩家数据
            players = self.get_all_players()

            if not players:
                return "🔍 暂无玩家数据"

            # 根据类型排序
            if board_type == "金币":
                players.sort(key=lambda x: int(x.get('gold', 0)), reverse=True)
                title = "金币排行榜"
                value_key = 'gold'
                suffix = "金币"
            else:  # 等级排行榜
                # 使用元组排序，先按等级后按经验
                players.sort(
                    key=lambda x: (
                        int(x.get('level', 1)),
                        int(x.get('exp', 0))
                    ),
                    reverse=True
                )
                title = "等级排行榜"
                value_key = 'level'
                suffix = "级"

            # 生成排行榜
            result = f"{title}:\n"
            result += "-" * 30 + "\n"

            # 只显示前10名
            for i, player in enumerate(players[:10], 1):
                nickname = player['nickname']
                value = int(player[value_key])

                # 为等级排行榜添加经验值显示
                exp_info = f" (经验: {int(player.get('exp', '0'))})" if board_type == "等级" else ""

                # 添加排名
                rank_mark = "👑" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."

                result += f"{rank_mark} {nickname}: {value}{suffix}{exp_info}\n"

            # 如果当前用户不在前10名，显示其排名
            current_player = next((p for p in players if p['nickname'] == user_id), None)
            if current_player:
                current_rank = players.index(current_player) + 1
                if current_rank > 10:
                    result += "-" * 30 + "\n"
                    value = current_player[value_key]
                    exp_info = f" (经验: {int(current_player.get('exp', '0'))})" if board_type == "等级" else ""
                    result += f"你的排名: {current_rank}. {current_player['nickname']}: {value}{suffix}{exp_info}"

            return result

        except Exception as e:
            logger.error(f"显示排行榜出错: {e}")
            return "⚠️ 显示排行榜时发生错误"

    def damage_calculation(self, attack, defense):
        """计算造成的实际伤害"""
        damage_reduction = min(defense/1000, 0.8)
        damage = int(attack * (1- damage_reduction))
        # 玩家1伤害修正：确保减伤后伤害至少为1
        damage = max(1, damage)

        explain_str = ""

        # 使用当前时间作为随机数种子
        current_time_ms = int(time.time_ns())
        random.seed(current_time_ms)

        # 生成1到100之间的随机数
        random_num = random.randint(1, 100)

        if random_num > 80:
            # 暴击（20% 概率）
            final_damage = int(damage * random.uniform(1.5, 1.8))
            explain_str = "💥暴击！"
        elif random_num < 20:
            # 失手（20% 概率）
            final_damage = max(1, int(damage * random.uniform(0.5, 0.7)))
            explain_str = "🤦‍♂️失手了！"
        else:
            # 正常命中（60% 概率）
            final_damage = int(damage)
            explain_str = ""

        # 确保最终伤害至少为1点
        final_damage = max(1, final_damage)

        return final_damage, explain_str

    def calculate_compensation(self, round_num, total_money) -> int:
        """
        根据比赛的轮数与失败者的总金钱，计算赔付金额。
        :param round_num: 比赛轮数 (int)
        :param total_money: 总金钱 (float)
        :return: 赔付金额 (float)
        """
        # 最高百分比 (10%) 和最低百分比 (1%)
        max_rate = 10 / 100   # 10%
        min_rate = 1 / 100    # 1%

        # 计算当前轮数的赔付比例
        # 每轮减少 0.5%，即 (round_num - 1) * 0.5%
        current_rate = max_rate - (round_num - 1) * 0.5 / 100

        # 确保赔付比例不低于最低百分比
        compensation_rate = max(current_rate, min_rate)

        # 根据比例计算赔付金额
        compensation_amount = int(total_money * compensation_rate)

        return compensation_amount  # 保留两位小数

    def random_boolean(self):
        """
        使用当前时间作为随机数种子，随机返回 True 或 False。
        """
        # 使用当前时间作为随机数种子
        current_time_ms = int(time.time_ns())
        random.seed(current_time_ms)

        # 随机生成 True 或 False
        return random.choice([True, False])

    def pvp_close_an_acount(self, round_num, winner: Player, winner_hp, loser: Player) -> str:
        # 计算扣除金币
        penalty_gold = self.calculate_compensation(round_num, loser.gold)
        new_loser_gold = int(loser.gold) - penalty_gold
        new_winner_gold = int(winner.gold) + penalty_gold

        # 更新失败者数据
        self._update_player_data(loser.user_id, {
            'hp': '0',
            'gold': str(new_loser_gold)
        })

        # 更新胜利者数据
        self._update_player_data(winner.user_id, {
            'hp': str(winner_hp),
            'gold': str(new_winner_gold)
        })

        result = f"✌️ {winner.nickname} 获胜!\n{loser.nickname} 赔偿 {penalty_gold} 金币\n"

        return result

    def pvp_combat(self, player_1: Player, player_2: Player) -> str:
        """PVP战斗"""
        # 攻击玩家属性
        player_1_level = player_1.level
        player_1_hp = int(player_1.hp)
        player_1_max_hp = int(player_1.max_hp)
        player_1_attack = int(player_1.attack)
        player_1_defense = int(player_1.defense)
        player_1_name = player_1.nickname
        player_1_total_damage = 0

        # 目标玩家属性
        player_2_level = player_2.level
        player_2_hp = int(player_2.hp)
        player_2_max_hp = int(player_2.max_hp)
        player_2_attack = int(player_2.attack)
        player_2_defense = int(player_2.defense)
        player_2_name = player_2.nickname
        player_2_total_damage = 0

        # 更新战斗日志显示
        battle_log = [
            "🥋接受挑战！\n⚔️ PVP战斗开始 ⚔️\n",
            f"[{player_1_name}] Lv.{player_1_level}\n❤️[{player_1_hp}/{player_1_max_hp}]\n⚔️[{player_1_attack}]\n🛡️[{str(player_1_defense)}]",
            f"VS\n",
            f"[{player_2_name}] Lv.{player_2_level}\n❤️[{player_2_hp}/{player_2_max_hp}]\n⚔️[{player_2_attack}]\n🛡️[{str(player_2_defense)}]"
        ]

        # 战斗逻辑
        round_num = 1
        while player_1_hp > 0 and player_2_hp > 0:
            if constants.WEATHER_TO_KEEP_A_BATTLE_LOG:
                if round_num <= constants.REPORT_THE_NUMBER_OF_ROUNDS:
                    battle_log.append(f"\n第{round_num}回合")

            # 计算玩家1的本轮造成伤害
            player_1_final_damage, player_1_explain_str = self.damage_calculation(player_1_attack, player_2_defense)
            # 计算玩家2的本轮造成伤害
            player_2_final_damage, player_2_explain_str = self.damage_calculation(player_2_attack, player_1_defense)
            # 获取本轮先手情况
            player_1_on_the_offensive = self.random_boolean()
            if player_1_on_the_offensive:
                # ---------玩家1先手---------
                # 减少目标玩家血量
                player_2_hp -= player_1_final_damage
                # 统计玩家1伤害
                player_1_total_damage += player_1_final_damage
                # 记录战斗日志（前4回合）
                if constants.WEATHER_TO_KEEP_A_BATTLE_LOG:
                    if round_num <= constants.REPORT_THE_NUMBER_OF_ROUNDS:
                        battle_log.append(f"{player_1_explain_str}{player_1_name}对{player_2_name}造成 {player_1_final_damage} 点伤害")
                # 检查玩家2是否已被击败
                if player_2_hp <= 0:
                    battle_log.append(f"\n{player_2_name}被打败了！😵")
                    break

                # 减少攻击玩家血量
                player_1_hp -= player_2_final_damage
                # 统计玩家2伤害
                player_2_total_damage += player_2_final_damage
                # 记录战斗日志（前4回合）
                if constants.WEATHER_TO_KEEP_A_BATTLE_LOG:
                    if round_num <= constants.REPORT_THE_NUMBER_OF_ROUNDS:
                        battle_log.append(f"{player_2_explain_str}{player_2_name}对{player_1_name}造成 {player_2_final_damage} 点伤害")
                # 检查玩家1是否已被击败
                if player_1_hp <= 0:
                    battle_log.append(f"\n{player_1_name}被打败了！😵")
                    break
            else:
                # ---------玩家2先手---------
                # 减少攻击玩家血量
                player_1_hp -= player_2_final_damage
                # 统计玩家2伤害
                player_2_total_damage += player_2_final_damage
                # 记录战斗日志（前4回合）
                if constants.WEATHER_TO_KEEP_A_BATTLE_LOG:
                    if round_num <= constants.REPORT_THE_NUMBER_OF_ROUNDS:
                        battle_log.append(f"{player_2_explain_str}{player_2_name}对{player_1_name}造成 {player_2_final_damage} 点伤害")
                # 检查玩家1是否已被击败
                if player_1_hp <= 0:
                    battle_log.append(f"\n{player_1_name}被打败了！😵")
                    break

                # 减少目标玩家血量
                player_2_hp -= player_1_final_damage
                # 统计玩家1伤害
                player_1_total_damage += player_1_final_damage
                # 记录战斗日志（前4回合）
                if constants.WEATHER_TO_KEEP_A_BATTLE_LOG:
                    if round_num <= constants.REPORT_THE_NUMBER_OF_ROUNDS:
                        battle_log.append(f"{player_1_explain_str}{player_1_name}对{player_2_name}造成 {player_1_final_damage} 点伤害")
                # 检查玩家2是否已被击败
                if player_2_hp <= 0:
                    battle_log.append(f"\n{player_2_name}被打败了！😵")
                    break
            round_num += 1

        # 战斗结束
        battle_log.append(f"\n战斗持续了{round_num}回合")

        if player_2_hp <= 0:
            # 发起挑战的玩家胜利，进行pvp结算
            result = self.pvp_close_an_acount(round_num, player_1, player_1_hp, player_2)
        else:
            # 接受挑战的玩家胜利，进行pvp结算
            result = self.pvp_close_an_acount(round_num, player_2, player_2_hp, player_1)

        # 向战斗结果中添加玩家和怪物造成的总伤害
        battle_log.append(f"\n📊 伤害统计:")
        battle_log.append(f"{player_1_name}: {player_1_total_damage}")
        battle_log.append(f"{player_2_name}: {player_2_total_damage}\n")

        battle_log.append(result)
        return "\n".join(battle_log)

    def attack_player(self, user_id, content, msg: ChatMessage):
        """ PVP 挑战其他玩家 """
        if not msg.is_group:
            return "❌ 只能在群聊中使用攻击功能"

        # 解析命令参数
        parts = content.split()
        if len(parts) < 2 or not parts[1].startswith('@'):
            return "❌ 请使用正确的格式：攻击 @用户名"

        target_name = parts[1][1:]  # 去掉@符号
        # 根据昵称获取玩家
        target = self._get_player_by_nickname(target_name)
        if not target:
            return "🔍 找不到目标玩家，请确保输入了正确的用户名"

        # 获取攻击者信息
        attacker = self.get_player(user_id)
        if not attacker:
            return "🤷‍♂️ 您还没有注册游戏"

        # 不能攻击自己
        if attacker.nickname == target.nickname:
            return "🤡 我知道你很勇，但是自己打自己这种事未免过于抽象。。。"

        if attacker.hp == 0:
            return "🤡 你的生命值为0，即便如此，你也想要起舞吗？"

        if target.hp == 0:
            return "🥴 对方生命值为0，做个人吧，孩子！"

        if target.challenge_proposal:
            player = self.get_player(target.challenge_proposal)
            return f"😂 对方已经有一个待处理的挑战请求，来自玩家 [{player.nickname}]"

        # 更新目标玩家的挑战请求，使用挑战者的user_id
        self._update_player_data(target.user_id, {
            'challenge_proposal': user_id
        })

        return f"💪 您向 {target_name} 发起了挑战请求，等待对方回应。被挑战的玩家可以发送 '接受挑战' 或 '拒绝挑战' 来决定是否开始PVP游戏。"

    def refuse_challenge(self, user_id):
        """拒绝挑战"""
        player = self.get_player(user_id)
        if not player:
            return "🤷‍♂️ 您还没有注册游戏"

        proposal = player.challenge_proposal
        if not proposal:
            return "🤡 虽然但是，并没有人挑战你啊，兄嘚~"

        # 使用昵称获取挑战者信息
        proposer = self.get_player(proposal)
        if not proposer:
            # 清除无效的挑战请求
            self._update_player_data(user_id, {
                'challenge_proposal': ''
            })
            return "🔍 挑战者信息不存在或已注销账号"

        # 更新自身的挑战者
        self._update_player_data(user_id, {
            'challenge_proposal': ''
        })

        return f"🙅‍♂️ 您拒绝了 {proposal} 的挑战请求"

    def accept_challenge(self, user_id):
        """接受挑战"""
        player = self.get_player(user_id)
        if not player:
            return "🤷‍♂️ 您还没有注册游戏"

        proposal = player.challenge_proposal
        if not proposal:
            return "🤷‍♂️ 您没有待处理的挑战请求"

        # 使用昵称获取挑战者信息
        proposer = self.get_player(proposal)
        if not proposer:
            # 清除无效的挑战请求
            self._update_player_data(user_id, {
                'challenge_proposal': ''
            })
            return "🥴 挑战者信息不存在或已注销账号"

        # 更新自身的挑战者
        self._update_player_data(user_id, {
            'challenge_proposal': ''
        })

        # 开始pvp战斗
        return self.pvp_combat(proposer, player)

    def _update_player_data(self, user_id: str, update_data: dict):
        """
        更新指定 user_id 对应的玩家部分数据。

        :param user_id: 玩家唯一标识符
        :param update_data: 包含要更新的字段及其新值的字典
        """
        # 确保 user_id 为字符串类型
        if not isinstance(user_id, str):
            logger.error(f"user_id 需要是字符串类型，但收到: {type(user_id)}")
            return

        # 如果 update_data 中有 inventory 字段，确保将其序列化
        if 'inventory' in update_data:
            inventory_value = update_data['inventory']
            if isinstance(inventory_value, dict):
                update_data['inventory'] = json.dumps(inventory_value, ensure_ascii=False)
            elif not isinstance(inventory_value, str):
                logger.error(f"inventory 字段类型不支持: {type(inventory_value)}")
                return  # 不更新该值

        # 如果 update_data 中有 equipment_fishing_rod 字段，确保将其序列化
        if 'equipment_fishing_rod' in update_data:
            inventory_value = update_data['equipment_fishing_rod']
            if isinstance(inventory_value, dict):
                update_data['equipment_fishing_rod'] = json.dumps(inventory_value, ensure_ascii=False)
            elif not isinstance(inventory_value, str):
                logger.error(f"equipment_fishing_rod 字段类型不支持: {type(inventory_value)}")
                return  # 不更新该值

        # 构建 SET 子句及参数字典
        set_clause = ", ".join([f"{field} = :{field}" for field in update_data.keys()])
        update_query = f"""
        UPDATE players
        SET {set_clause}
        WHERE user_id = :user_id
        """

        # 添加 user_id 到更新参数中
        update_data['user_id'] = user_id

        try:
            conn = self._get_connection()
            with conn:
                conn.execute(update_query, update_data)
            logger.info(f"用户 {user_id} 的数据已成功部分更新！")
        except sqlite3.Error as e:
            logger.error(f"更新玩家数据时出错: {e} | 数据: {update_data}")

    def show_inventory(self, user_id):
        player = self.get_player(user_id)
        if not player:
            return "🥴 您还没注册..."

        return player.get_inventory_display()

    def equip_from_inventory(self, user_id: str, content: str) -> str:
        """从背包装备物品

        Args:
            user_id: 玩家ID
            content: 完整的命令内容

        Returns:
            str: 装备结果提示
        """
        try:
            # 解析命令
            parts = content.split()
            if len(parts) < 2:
                return "装备格式错误！请使用: 装备 物品名"

            item_name = parts[1]
            item_level = 1
            updates_info = {}
            new_attack = 0
            new_defense = 0
            new_max_hp = 0

            # 获取player
            player = self.get_player(user_id)
            if not player:
                return "🥴 您还没注册..."
            # 检查背包中是否有玩家想要装备的物品
            inventory = player.inventory
            if not inventory:
                return f"🤷‍♂️ 玩家 [{player.nickname}] 的背包是空的！"
            if item_name not in inventory:
                return f"🤷‍♂️ 玩家 [{player.nickname}] 未持有物品 [{item_name}]！"

            # 获取装备UUID
            equipment_uuid = inventory[item_name]['uuid']
            # 定义已装备的道具
            is_equipped_prop = None
            is_equipped_fishing_rod = None

            if inventory[item_name]['type'] == 'fishing_rod':
                if player.equipment_fishing_rod:
                    # 玩家已装备鱼竿，先卸下
                    is_equipped_fishing_rod = player.equipment_fishing_rod
                fishing_rod = inventory[item_name]
                # 添加鱼竿名称
                fishing_rod['name'] = item_name
                # 从背包移除该鱼竿(已装备)
                inventory.pop(item_name)

                if is_equipped_fishing_rod:
                    # 将卸下的鱼竿放回背包
                    inventory[is_equipped_fishing_rod['name']] = is_equipped_fishing_rod
                    unload_explain = f"\n[{is_equipped_fishing_rod['name']}] 已放回背包。"
                else:
                    unload_explain = ""

                # 准备需要更新的字典
                updates_info = {
                    'inventory': inventory,
                    'equipment_fishing_rod': fishing_rod
                }
                # 更新数据
                self._update_player_data(user_id, updates_info)

                return f"🎉 玩家 [{player.nickname}] 装备 [{item_name}] 成功！{unload_explain}"
            else:
                # 获取装备信息
                equipment = self.rouge_equipment_system.get_equipment_by_id(equipment_uuid)
                if equipment is None:
                    return f"🤷‍♂️ 数据库中找不到装备 [{item_name}] 的信息！"

                # 获取装备等级
                item_level = equipment.get('level', 1)
                if player.level < item_level:
                    # 等级不足无法穿戴装备
                    return f"🤷‍♂️ 玩家 [{player.nickname} Lv.{player.level}] 等级不足，无法穿戴装备 [{item_name} Lv.{item_level}] ！"

                if equipment['type'] == 'weapon':
                    # 新的攻击力 = 武器加成 + 等级加成 + 玩家基本数值
                    new_attack = equipment['attack_bonus'] + (player.level * constants.PLAYER_LEVEL_UP_APPEND_ATTACK + constants.PLAYER_BASE_ATTACK)
                    # 记录武器UUID
                    updates_info['equipment_weapon'] = equipment_uuid
                    # 从背包移除本次装备的武器
                    inventory.pop(item_name)
                    # 检查是否已装备武器
                    if player.equipment_weapon and (player.equipment_weapon != equipment_uuid):
                        is_equipped_prop = player.equipment_weapon
                elif equipment['type'] == 'armor':
                    # 新的防御力 = 防具加成 + 等级加成 + 玩家基本数值
                    new_defense = equipment['defense_bonus'] + (player.level * constants.PLAYER_LEVEL_UP_APPEND_DEFENSE + constants.PLAYER_BASE_DEFENSE)
                    # 新的最大生命值 = 防具加成 + 等级加成 + 玩家基本数值
                    new_max_hp = equipment['max_hp_bonus'] + (player.level * constants.PLAYER_LEVEL_UP_APPEND_HP + constants.PLAYER_BASE_MAX_HP)
                    # 记录防具UUID
                    updates_info['equipment_armor'] = equipment_uuid
                    # 从背包移除本次装备的防具
                    inventory.pop(item_name)
                    # 检查是否已装备防具
                    if player.equipment_armor and (player.equipment_armor!= equipment_uuid):
                        is_equipped_prop = player.equipment_armor
                else:
                    # 不支持的装备类型
                    return f"🙅‍♂️ 不支持的装备类型: {equipment['type']}"

                if is_equipped_prop:
                    # 把身上原本就装备的道具放回背包
                    is_equipped = self.rouge_equipment_system.get_equipment_by_id(is_equipped_prop)
                    is_equipped_explain = self.rouge_equipment_system.get_equipment_info(is_equipped)
                    equipment_dict = {
                        'uuid': is_equipped['id'],
                        'type': is_equipped['type'],
                        'rarity': is_equipped['rarity'],
                        'price': is_equipped['price'],
                        'amount': 1,
                        'explain': is_equipped_explain
                    }
                    inventory[is_equipped['name']] = equipment_dict
                    unload_explain = f"\n[{is_equipped['name']}] 已放回背包。"
                else:
                    unload_explain = ""
                # 更新背包
                updates_info['inventory'] = inventory

                # 更新玩家三维
                if new_attack != 0:
                    updates_info['attack'] = new_attack
                if new_defense!= 0:
                    updates_info['defense'] = new_defense
                if new_max_hp!= 0:
                    updates_info['max_hp'] = new_max_hp

                # 更新玩家数据
                self._update_player_data(user_id, updates_info)

                return f"🎉 玩家 [{player.nickname}] 装备 [{item_name}] 成功！{unload_explain}"
        except Exception as e:
            logger.error(f"装备物品出错: {e}")
            return "装备物品时发生错误"

    def authenticate(self, cmd_str, user_id, content):
        """验证玩家密码"""
        password = self.regex_match(cmd_str, content)
        # 检查密码是否正确
        if password == self.admin_password:
            # 认证成功，将用户添加到管理员列表中
            self.admin_list.append(user_id)
            return "[Game] 认证成功"
        else:
            return "[Game] 认证失败"

    def toggle_game_system(self, user_id, action='toggle'):
        """切换游戏系统状态"""
        try:
            if not self.is_admin(user_id):
                return "🙅‍♂️ 你没有管理员权限！无法切换游戏系统状态！"

            if action == 'toggle':
                self.game_status = not self.game_status
            elif action == 'start':
                self.game_status = True
            elif action == 'stop':
                self.game_status = False

            return f"✅ 游戏系统已{'开启' if self.game_status else '关闭'}"
        except Exception as e:
            logger.error(f"切换游戏系统状态出错: {e}")
            return "❌ 操作失败，请检查系统状态"

    def extract_username_and_amount(self, text):
        """
        从字符串中提取用户名和金额。

        参数:
            text (str): 输入的字符串，例如 '充值 @用户名 1000'

        返回:
            tuple: (用户名, 金额) 如果匹配失败，则返回 (None, None)
        """
        # 定义正则表达式模式
        pattern = r'充值\s+@(\w+)\s+(\d+)'
        match = re.search(pattern, text)

        if match:
            username = match.group(1)
            amount = int(match.group(2))
            return username, amount
        else:
            return None, None

    def toggle_recharge(self, user_id, content):
        """充值系统"""
        try:
            if not self.is_admin(user_id):
                return "🙅‍♂️ 你没有管理员权限！无法充值！"

            target_name, amount = self.extract_username_and_amount(content)

            if target_name and amount:
                logger.info(f"充值目标：{target_name}，金额：{amount}")
                # 根据昵称获取玩家
                target = self._get_player_by_nickname(target_name)
                if not target:
                    return "🔍 找不到目标玩家，请确保输入了正确的用户名"
                else:
                    target_gold = target.gold + amount
                    updates_info = {
                        "gold": target_gold,
                    }

                    # 保存更新后的玩家数据
                    self._update_player_data(target.user_id, updates_info)
                    return f"已为 {target.nickname} 用户充值 {amount} 金币。"
            else:
                return "⚠️ 请使用正确的格式：充值 @用户名 金额"
        except Exception as e:
            logger.error(f"充值出错: {e}")
            return "⚠️ 充值失败，请联系管理员。"

    def is_admin(self, user_id):
        """检查玩家是否是管理员"""
        return any(admin in user_id for admin in self.admin_list)

    def buy_property(self, user_id):
        """购买当前位置的地块"""
        player = self.get_player(user_id)
        if not player:
            return "🤷‍♂️ 您还没有注册游戏"

        # 获取玩家当前位置
        current_position = int(getattr(player, 'position', 0))
        block = self.monopoly.get_block_info(current_position)

        # 检查是否是可购买的地块
        purchasable_types = ['空地', '直辖市', '省会', '地级市', '县城', '乡村']
        if block['type'] not in purchasable_types:
            return "🙅‍♂️ 当前位置不是可购买的地块"

        # 检查是否已被购买
        if self.monopoly.get_property_owner(current_position):
            return "🤷‍♂️ 这块地已经被购买了"

        # 计算地块价格
        base_prices = {
            '直辖市': 2000,
            '省会': 1500,
            '地级市': 1000,
            '县城': 500,
            '乡村': 300,
            '空地': 200
        }
        base_price = base_prices.get(block['type'], 500)
        distance_factor = 1 + (current_position // 10) * 0.2  # 每10格增加20%价格
        price = int(base_price * distance_factor)

        # 检查玩家金币是否足够
        if int(player.gold) < price:
            return f"🤷‍♂️ 购买这块地需要 {price} 金币，您的金币不足"

        # 扣除金币并购买地块
        new_gold = int(player.gold) - price
        if self.monopoly.buy_property(current_position, user_id, price):
            self._update_player_data(user_id, {'gold': str(new_gold)})
            return f"""🎉 成功购买地块！\n📍 位置: {block['name']}\n🏛️ 类型: {block['type']}\n💴 花费: {price} 金币\n💰 当前金币: {new_gold}"""
        else:
            return "😵 购买失败，请稍后再试"

    def upgrade_property(self, user_id):
        """升级当前位置的地块"""
        player = self.get_player(user_id)
        if not player:
            return "🤷‍♂️ 您还没有注册游戏"

        # 获取玩家当前位置
        current_position = int(getattr(player, 'position', 0))

        # 检查是否是玩家的地产
        property_data = self.monopoly.properties_data.get(str(current_position))
        if not property_data or property_data.get('owner') != user_id:
            return "🤷‍♂️ 这不是您的地产"

        # 检查是否达到最高等级
        current_level = property_data.get('level', 1)
        if current_level >= 3:
            return "💪 地产已达到最高等级"

        # 计算升级费用
        base_price = property_data.get('price', 500)
        upgrade_cost = int(base_price * 0.5 * current_level)

        # 检查玩家金币是否足够
        if int(player.gold) < upgrade_cost:
            return f"🤷‍♂️ 升级需要 {upgrade_cost} 金币，您的金币不足"

        # 扣除金币并升级地产
        new_gold = int(player.gold) - upgrade_cost
        if self.monopoly.upgrade_property(current_position):
            self._update_player_data(user_id, {'gold': str(new_gold)})
            return f"""🏗️ 地产升级成功！
位置: {current_position}
当前等级: {current_level + 1}
花费: {upgrade_cost} 金币
当前金币: {new_gold}"""
        else:
            return "😵 升级失败，请稍后再试"

    def show_properties(self, user_id):
        """显示玩家的地产"""
        player = self.get_player(user_id)
        if not player:
            return "🤷‍♂️ 您还没有注册游戏"

        properties = self.monopoly.get_player_properties(user_id)
        if not properties:
            return "🤷‍♂️ 您还没有购买任何地产"

        result = ["您的地产列表："]
        for pos in properties:
            prop_info = self.monopoly.get_property_info(pos)
            if prop_info:
                result.append(f"\n{prop_info['name']} ({prop_info['region']})")
                result.append(f"📈 等级: {prop_info['level']}")
                result.append(f"💵 价值: {prop_info['price']} 金币")
                result.append(f"💲 当前租金: {prop_info['rent']} 金币")

        return "\n".join(result)

    def show_map(self, user_id):
        """显示地图状态"""
        player = self.get_player(user_id)
        if not player:
            return "🤷‍♂️ 您还没有注册游戏"

        # 获取玩家当前位置
        current_position = int(getattr(player, 'position', 0))

        # 获取地图总格子数
        total_blocks = self.monopoly.map_data["total_blocks"]

        result = ["🗺️ 大富翁地图"]
        result.append("————————————")

        # 生成地图显示
        for pos in range(total_blocks):
            block = self.monopoly.get_block_info(pos)
            property_data = self.monopoly.properties_data.get(str(pos), {})
            owner_id = property_data.get('owner')

            # 获取地块显示符号
            if pos == current_position:
                symbol = "👤"  # 玩家当前位置
            elif block['type'] == '起点':
                symbol = "🏁"
            elif owner_id:
                # 如果有主人，显示房屋等级
                level = property_data.get('level', 1)
                symbols = ["🏚️", "🏡", "🏢"]  # 不同等级的显示
                symbol = symbols[level - 1]
            else:
                # 根据地块类型显示不同符号
                symbol = constants.MAP_TYPE_SYMBOLS.get(block['type'], "⬜")

            # 添加地块信息
            block_info = f"{symbol} {pos}:{block['name']}"
            if owner_id:
                owner_player = self.get_player(owner_id)
                if owner_player:
                    block_info += f"({owner_player.nickname})"
                else:
                    block_info += f"(未知)"

            if pos == current_position:
                block_info += " ← 当前位置"

            result.append(block_info)

            # 每5个地块换行
            if (pos + 1) % 5 == 0:
                result.append("————————————")

        return "\n".join(result)

    def gamble(self, user_id, bet_str):
        """
        处理赌博命令，解析下注类型和金额，模拟掷骰子，并计算结果。

        参数:
            bet_str (str): 输入的下注字符串，格式如 '下注 大 5000'

        返回:
            dict: 包含骰子结果、是否获胜以及收益或亏损金额
        """

        # 获取玩家对象
        player = self.get_player(user_id)
        if not player:
            return "🤷‍♂️ 您还没有注册游戏"

        # 定义下注类型及对应的赔率
        odds = {
            '大': 1,       # 赔率 1:1
            '小': 1,       # 赔率 1:1
            '豹子': 35,    # 赔率 35:1
            '顺子': 8,      # 赔率 8:1
            '对子': 2      # 赔率 2:1
        }

        DICE_EMOJI = {
            1: '⚀',  # ⚀
            2: '⚁',  # ⚁
            3: '⚂',  # ⚂
            4: '⚃',  # ⚃
            5: '⚄',  # ⚄
            6: '⚅',  # ⚅
        }

        # 使用正则表达式解析输入字符串
        pattern = r'^下注\s+(大|小|豹子|顺子|对子)\s+(\d+)$'
        match = re.match(pattern, bet_str.strip())

        if not match:
            return "❌ 输入格式不正确。正确格式如：下注 大 5000"

        bet_type, amount_str = match.groups()
        amount = int(amount_str)

        # 验证下注金额是否为正整数
        if amount <= 0:
            return "下注金额必须为正整数。"

        # 判断玩家本金是否足够下注
        player_gold = int(player.gold)
        if player_gold < amount:
            return f"🤷‍♂️ 您的本金不足，无法进行下注。\n💵 您的余额：{player_gold} 金币"

        # 使用当前时间作为随机数种子
        current_time_ms = int(time.time_ns())
        random.seed(current_time_ms)

        # 模拟掷三颗骰子
        dice = [random.randint(1, 6) for _ in range(3)]
        total = sum(dice)

        dice_faces = ' '.join([DICE_EMOJI.get(d, '❓') for d in dice])

        # 判断是否获胜
        win = False
        payout = 0

        if bet_type == '大':
            if 11 <= total <= 18:
                win = True
                payout = int(amount * odds[bet_type])
        elif bet_type == '小':
            if 3 <= total <= 10:
                win = True
                payout = int(amount * odds[bet_type])
        elif bet_type == '豹子':
            if dice[0] == dice[1] == dice[2]:
                win = True
                payout = int(amount * odds[bet_type])
        elif bet_type == '对子':
            if (dice[0] == dice[1]) or (dice[1] == dice[2]) or (dice[0] ==dice[2]):
                win = True
                payout = int(amount * odds[bet_type])
        elif bet_type == '顺子':
            # 列出所有有效的顺子组合，包括循环顺子
            valid_straights = [
                [1, 2, 3],
                [2, 3, 4],
                [3, 4, 5],
                [4, 5, 6],
                [1, 5, 6],
                [1, 2, 6]
            ]
            # 检查骰子是否构成顺子
            sorted_dice = sorted(dice)
            if sorted_dice in valid_straights:
                win = True
                payout = int(amount * odds[bet_type])

        # 计算结果
        if win:
            result = {
                'dice': dice,
                'result': '胜利',
                'payout': payout
            }
        else:
            payout = -amount
            result = {
                'dice': dice,
                'result': '失败',
                'payout': payout
            }

        # 结算赌博收入
        player.gold = int(player.gold) + payout
        # 更新目标玩家的金币数据
        self._update_player_data(player.user_id, {
            'gold': str(player.gold)
        })

        payout = abs(payout)
        result_str = f"━━━━━━━━━━━━━━━\n🎲点数: {dice_faces}\n\n💴下注: {amount}金币\n{'💵 恭喜您赢得了' if win else '😞 很遗憾，您输了'} {payout} 金币\n\n(游戏娱乐，切勿当真，热爱生活，远离赌博)\n━━━━━━━━━━━━━━━"

        return result_str
