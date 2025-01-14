import os
import re
import csv
import json
import time
import random
import random
import plugins
import shutil
import datetime
import threading
from plugins import *
from .shop import Shop
from .item import Item
from .player import Player
from typing import Optional
from common.log import logger
from .equipment import Equipment
from .monopoly import MonopolySystem
from .fishing_system import FishingSystem
from bridge.reply import Reply, ReplyType
from channel.chat_message import ChatMessage
from bridge.context import ContextType, Context


@plugins.register(
    name="Game",
    desc="一个简单的文字游戏系统",
    version="0.2.3",
    author="assistant",
    desire_priority=0
)
class Game(Plugin):
    # 将 STANDARD_FIELDS 定义为类变量
    STANDARD_FIELDS = [
        'user_id', 'nickname', 'gold', 'level', 'last_checkin',
        'inventory', 'hp', 'max_hp', 'attack', 'defense', 'exp',
        'last_fishing', 'rod_durability', 'equipped_weapon', 'equipped_armor',
        'last_item_use', 'spouse', 'marriage_proposal', 'challenge_proposal', 'last_attack', 'adventure_last_attack',
        'position'
    ]

    # 添加开关机状态和进程锁相关变量
    PROCESS_LOCK_FILE = "game_process.lock"
    game_status = True  # 游戏系统状态
    scheduled_tasks = {}  # 定时任务字典

    # 添加新的类变量
    REMINDER_COST = 50  # 每条提醒消息的费用
    REMINDER_DURATION = 24 * 60 * 60  # 提醒持续时间(24小时)

    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        # 初始化锁
        self.lock = threading.Lock()
        # 添加进程锁和状态恢复逻辑
        try:
            self.data_dir = os.path.join(os.path.dirname(__file__), "data")
            os.makedirs(self.data_dir, exist_ok=True)

            # 初始化进程锁文件路径
            self.process_lock_file = os.path.join(self.data_dir, self.PROCESS_LOCK_FILE)

            # 恢复游戏状态和定时任务
            self._restore_game_state()

            # 确保数据目录"""  """存在
            self.player_file = os.path.join(self.data_dir, "players.csv")
            self.shop_file = os.path.join(self.data_dir, "shop_items.csv")

            # 初始化物品系统
            self.item_system = Item(self.data_dir)
            self.item_system.init_default_items()

            # 初始化商店数据文件
            if not os.path.exists(self.shop_file):
                with open(self.shop_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['name', 'price'])
                    # 写入默认商品
                    default_items = [
                        ['木剑', '小孩子过家家玩的', 'weapon', '0', '5', '0', '500', '1'],
                        ['匕首', '小巧的匕首，看起来很精致', 'weapon', '0', '8', '0', '800', '2'],
                        ['铁剑', '更坚固的铁剑', 'weapon', '0', '12', '0', '1200', '2'],
                        ['铁锤', '大锤八十。兄弟', 'weapon', '0', '20', '0', '2000', '3'],
                        ['长枪', '一寸长，一寸强', 'weapon', '0', '25', '0', '2500', '3'],
                        ['精钢剑', '由精钢打造的利剑', 'weapon', '0', '30', '0', '3000', '3'],
                        ['讨伐棒', '可以发射火药的讨伐棒，乌萨奇严选', 'weapon', '0', '30', '0', '3000', '4'],
                        ['战斧', '哥们现在是维京人了！', 'weapon', '0', '35', '0', '3500', '4'],
                        ['青铜剑', '古老的青铜剑', 'weapon', '0', '40', '0', '4000', '4'],
                        ['唐刀', '帅就完了', 'weapon', '0', '45', '0', '4500', '4'],
                        ['双手巨剑', '魂1神器', 'weapon', '0', '50', '0', '5000', '4'],
                        ['秘银剑', '魔法工匠打造的秘银剑', 'weapon', '0', '60', '0', '6000', '5'],
                        ['湖女之剑', '我知道这把剑很强，但是它是不是来错片场了？是吧杰洛特。', 'weapon', '0', '70', '0', '7000', '5'],
                        ['如意金箍棒', '我这棍，本是东洋大海龙宫里得来的，唤做天河镇底神珍铁，又唤做如意金箍棒。重一万三千五百斤', 'weapon', '0', '80', '0', '8000', '5'],
                        ['三尖两刃刀', '那真君抖擞神威，摇身一变，变得身高万丈，两只手，举着三尖两刃神锋，好便似华山顶上之峰。', 'weapon', '0', '80', '0', '8000', '5'],
                        ['破衣烂衫', '你也不想当流浪汉，对吧', 'armor', '1', '0', '1', '200', '1'],
                        ['斗篷', '提供基本保护的斗篷', 'armor', '3', '0', '3', '600', '1'],
                        ['布甲', '简单的布制护甲', 'armor', '5', '0', '5', '1000', '1'],
                        ['乌萨奇睡衣', '乌拉呀哈~呀哈乌拉~', 'armor', '7', '0', '7', '1400', '1'],
                        ['皮甲', '轻便的皮质护甲', 'armor', '10', '0', '10', '2000', '2'],
                        ['帝骑腰带', '都闪开，我要开始装B了', 'armor', '15', '0', '15', '3000', '2'],
                        ['铁甲', '轻便的皮质护甲', 'armor', '18', '0', '18', '3600', '2'],
                        ['锁子甲', '由链环组成的护甲', 'armor', '25', '0', '25', '5000', '3'],
                        ['精钢甲', '精钢打造的铠甲', 'armor', '30', '0', '30', '6000', '3'],
                        ['秘银铠甲', '帅是一辈子的事', 'armor', '38', '0', '38', '7600', '4'],
                        ['初音未来cos服', '可爱捏~~等等，你刚刚说了你要穿着这玩意去打架，对吧？？？', 'armor', '10', '10', '4', '4000', '4'],
                        ['荆棘铠甲', '你最好别碰我，兄弟，我不开玩笑', 'armor', '40', '15', '40', '8000', '4'],
                        ['龙鳞甲', '龙鳞制成的铠甲', 'armor', '60', '0', '60', '1200', '5'],
                        ['神圣铠甲', '具有神圣力量的铠甲', 'armor', '70', '0', '70', '1400', '6'],
                        ['永恒战甲', '传说中的不朽铠甲', 'armor', '80', '0', '70', '1600', '7'],
                        ['面包', '普普通通的面包，没什么特别的，回复50点生命值', 'consumable', '50', '0', '0', '25', '1'],
                        ['药水', '出门必备的小药水，回复100点生命值', 'consumable', '100', '0', '0', '50', '2'],
                        ['急救包', '出事儿了就得靠它，回复300点生命值', 'consumable', '300', '0', '0', '150', '3'],
                        ['治疗卷轴', '麻瓜总是很难理解卷轴上的符文到底是怎么发挥作用的，回复400点生命值', 'consumable', '400', '0', '0', '200', '4'],
                        ['原素瓶', '不死人的果粒橙，回复1000点生命值', 'consumable', '1000', '0', '0', '500', '5'],
                        ['杰克的酒', '卡塔利纳的杰克·巴尔多赠予的酒，非常好喝！回复2000点生命值', 'consumable', '2000', '0', '0', '1000', '5']
                        ['女神的祝福', '来自太阳长女葛温德林的祝福，回复全部生命值', 'consumable', '9999', '0', '0', '2000', '5']
                    ]
                    writer.writerows(default_items)

            # 初始化玩家数据文件
            if not os.path.exists(self.player_file):
                with open(self.player_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(self.STANDARD_FIELDS)

            # 初始化钓鱼系统
            self.fishing_system = FishingSystem(self.data_dir)
            self.shop = Shop(self)

            # 初始化装备系统
            self.equipment_system = Equipment(self)

            # 初始化提醒系统
            self.reminders = {}  # 格式: {user_id: {'content': str, 'expire_time': int}}
            self._load_reminders()  # 从文件加载提醒

            # 初始化配置文件
            config_file = os.path.join(self.data_dir, "config.json")
            if not os.path.exists(config_file):
                default_config = {
                    # 默认管理员列表
                    "admins": ["野欲", "小鲨匕", "老B登", "上海-小鲨匕"]
                }
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, ensure_ascii=False, indent=2)

            # 初始化大富翁系统
            self.monopoly = MonopolySystem(self.data_dir)

        except Exception as e:
            logger.error(f"初始化游戏系统出错: {e}")
            raise

    def _migrate_data_files(self):
        """数据文件迁移和兼容性检查"""
        # 标准字段列表
        standard_player_fields = [
            'user_id', 'nickname', 'gold', 'level', 'last_checkin',
            'inventory', 'hp', 'max_hp', 'attack', 'defense', 'exp',
            'last_fishing', 'rod_durability', 'equipped_weapon', 'equipped_armor',
            'last_item_use', 'spouse', 'marriage_proposal', 'challenge_proposal', 'last_attack', 'adventure_last_attack'
        ]

        # 默认值设置
        default_values = {
            'gold': '0',
            'level': '1',
            'hp': '100',
            'max_hp': '100',
            'attack': '10',
            'defense': '5',
            'exp': '0',
            'inventory': '[]',
            'rod_durability': '{}',
            'equipped_weapon': '',
            'equipped_armor': '',
            'last_item_use': '0',
            'spouse': '',
            'marriage_proposal': '',
            'challenge_proposal': '',
            'last_attack': '0',
            'adventure_last_attack': '0'
        }

        if os.path.exists(self.player_file):
            try:
                # 读取所有现有数据
                all_players = {}
                with open(self.player_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictdReader(f)
                    for row in reader:
                        # 跳过空行或无效数据
                        if not row.get('user_id') and not row.get('nickname'):
                            continue

                        # 使用user_id作为主键，如果没有user_id则使用nickname
                        key = row.get('user_id') or row.get('nickname')
                        if not key:
                            continue

                        # 如果已存在玩家记录，合并数据
                        if key in all_players:
                            # 保留非空值
                            for field in standard_player_fields:
                                if row.get(field):
                                    all_players[key][field] = row[field]
                        else:
                            # 创建新记录
                            player_data = default_values.copy()
                            for field in standard_player_fields:
                                if row.get(field):
                                    player_data[field] = row[field]
                            all_players[key] = player_data

                            # 确保user_id和nickname字段
                            if row.get('user_id'):
                                player_data['user_id'] = row['user_id']
                            if row.get('nickname'):
                                player_data['nickname'] = row['nickname']

                # 写入整理后的数据
                with open(self.player_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=standard_player_fields)
                    writer.writeheader()
                    for player_data in all_players.values():
                        # 确保所有��要字段都存在
                        for field in standard_player_fields:
                            if field not in player_data:
                                player_data[field] = default_values.get(field, '')
                        writer.writerow(player_data)

            except Exception as e:
                logger.error(f"数据迁移出错: {e}")
                # 创建备份
                backup_file = f"{self.player_file}.bak"
                if os.path.exists(self.player_file):
                    shutil.copy2(self.player_file, backup_file)

    def _load_reminders(self):
        """从文件加载提醒数据"""
        reminder_file = os.path.join(self.data_dir, "reminders.json")
        if os.path.exists(reminder_file):
            try:
                with open(reminder_file, 'r', encoding='utf-8') as f:
                    self.reminders = json.load(f)
                # 清理过期提醒
                current_time = int(time.time())
                self.reminders = {
                    k: v for k, v in self.reminders.items()
                    if v['expire_time'] > current_time
                }
            except Exception as e:
                logger.error(f"加载提醒数据出错: {e}")
                self.reminders = {}

    def _save_reminders(self):
        """保存提醒数据到文件"""
        reminder_file = os.path.join(self.data_dir, "reminders.json")
        try:
            with open(reminder_file, 'w', encoding='utf-8') as f:
                json.dump(self.reminders, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存提醒数据出错: {e}")

    def set_reminder(self, user_id, content):
        """设置提醒"""
        player = self.get_player(user_id)
        if not player:
            return "您还没有注册游戏"

        if len(content.split()) < 2:
            return "请使用正确的格式：提醒 内容"

        reminder_content = ' '.join(content.split()[1:])
        # 去除感叹号和加号
        reminder_content = reminder_content.replace('!', '').replace('！', '').replace('+', '')

        if len(reminder_content) > 50:  # 限制提醒长度
            return "提醒内容不能超过50个字符"

        # 检查金币是否足够
        if int(player.gold) < self.REMINDER_COST:
            return f"设置提醒需要{self.REMINDER_COST}金币，金币不足"

        # 扣除金币
        new_gold = int(player.gold) - self.REMINDER_COST
        self._update_player_data(user_id, {'gold': str(new_gold)})

        # 保存提醒
        self.reminders[user_id] = {
            'content': reminder_content,
            'expire_time': int(time.time()) + self.REMINDER_DURATION
        }
        self._save_reminders()

        return f"提醒设置成功！消息将在24小时内显示在每条游戏回复后面\n花费: {self.REMINDER_COST}金币"

    def get_active_reminders(self):
        """获取所有有效的提醒"""
        current_time = int(time.time())
        active_reminders = []

        for user_id, reminder in self.reminders.items():
            if reminder['expire_time'] > current_time:
                player = self.get_player(user_id)
                if player:
                    active_reminders.append(f"[{player.nickname}]: {reminder['content']}")

        return "\n".join(active_reminders) if active_reminders else ""

    def on_handle_context(self, e_context: EventContext):
        if e_context['context'].type != ContextType.TEXT:
            return

        # 在处理任何命令前，先检查定时任务
        self._check_scheduled_tasks()

        content = e_context['context'].content.strip()
        msg: ChatMessage = e_context['context']['msg']

        # 获取用户ID作为主要标识符
        current_id = msg.actual_user_id if msg.is_group else msg.from_user_id

        # 使用 sender 作为昵称
        nickname = msg.actual_user_nickname if msg.is_group else msg.from_user_nickname

        if not current_id:
            return "无法获取您的ID，请确保ID已设置"

        if not self.game_status and content not in ['注册', '开机', '关机', '充值', '定时', '查看定时', '取消定时', '清空定时']:
            return "游戏系统当前已关闭"

        logger.debug(f"当前用户信息 - current_id: {current_id}")

        # 修改这里：更新 lambda 函数定义，使其接受两个参数
        cmd_handlers = {
            "注册": lambda i, n: self.register_player(i, n),
            "状态": lambda i, n: self.get_player_status(i),
            "个人状态": lambda i, n: self.get_player_status(i),
            "签到": lambda i, n: self.daily_checkin(i),
            "商店": lambda i, n: self.shop.show_shop(content),
            "购买": lambda i, n: self.shop.buy_item(i, content),
            "背包": lambda i, n: self.show_inventory(i),
            "装备": lambda i, n: self.equip_from_inventory(i, content),
            "游戏菜单": lambda i, n: self.game_help(),
            "赠送": lambda i, n: self.give_item(i, content, msg),
            "钓鱼": lambda i, n: self.fishing(i),
            "图鉴": lambda i, n: self.show_fish_collection(i, content),
            "出售": lambda i, n: self.shop.sell_item(i, content),
            "出售所有物品": lambda i, n: self.shop.sell_item(i, content),
            "批量出售": lambda i, n: self.shop.sell_item(i, content),
            "下注": lambda i, n: self.gamble(i, content),
            "外出": lambda i, n: self.go_out(i),
            "冒险": lambda i, n: self.go_adventure(i),
            "使用": lambda i, n: self.use_item(i, content),
            "排行": lambda i, n: self.show_leaderboard(i, content),
            "排行榜": lambda i, n: self.show_leaderboard(i, content),
            "求婚": lambda i, n: self.propose_marriage(i, content, msg),
            "同意求婚": lambda i, n: self.accept_marriage(i),
            "拒绝求婚": lambda i, n: self.reject_marriage(i),
            "离婚": lambda i, n: self.divorce(i),
            "挑战": lambda i, n: self.attack_player(i, content, msg),
            "同意挑战": lambda i, n: self.accept_challenge(i),
            "拒绝挑战": lambda i, n: self.refuse_challenge(i),
            "开机": lambda i, n: self.toggle_game_system(i, 'start'),
            "关机": lambda i, n: self.toggle_game_system(i, 'stop'),
            "充值": lambda i, n: self.toggle_recharge(i, content),
            "定时": lambda i, n: self.schedule_game_system(i, content),
            "查看定时": lambda i, n: self.show_scheduled_tasks(i),
            "取消定时": lambda i, n: self.cancel_scheduled_task(i, content),
            "清空定时": lambda i, n: self.clear_scheduled_tasks(i),
            "提醒": lambda i, n: self.set_reminder(i, content),
            "删除提醒": lambda i, n: self.delete_reminder(i),
            "购买地块": lambda i, n: self.buy_property(i),
            "升级地块": lambda i, n: self.upgrade_property(i),
            "我的地产": lambda i, n: self.show_properties(i),
            "地图": lambda i, n: self.show_map(i),
        }

        cmd = content.split()[0]
        with self.lock:  # 获取锁
            if cmd in cmd_handlers:
                try:
                    reply = cmd_handlers[cmd](current_id, nickname)
                    # 添加活动提醒
                    reminders = self.get_active_reminders()
                    if reminders:
                        reply += f"\n\n📢 当前提醒:\n{reminders}"
                        reply += "\n📢 如何使用提醒:\n设置提醒: 提醒 内容"
                    e_context['reply'] = Reply(ReplyType.TEXT, reply)
                    e_context.action = EventAction.BREAK_PASS
                except Exception as e:
                    logger.error(f"处理指令 '{cmd}' 时出错: {e}")
                    e_context['reply'] = Reply(ReplyType.TEXT, "处理您的指令时发生错误，请稍后再试。")
                    e_context.action = EventAction.BREAK_PASS
            else:
                e_context.action = EventAction.CONTINUE

    def game_help(self):
        return """
🎮 游戏指令大全 🎮

基础指令
————————————
📝 注册 - 注册新玩家
📊 状态 - 查看当前状态
📅 签到 - 每日签到领取金币

物品相关
————————————
🏪 商店 - 查看商店物品
💰 购买 [物品名] - 购买物品
🎒 背包 - 查看背包物品
⚔️ 装备 [物品名] - 装备物品
🎁 赠送 [@用户] [物品名] [数量] - 赠送物品
💊 使用 [物品名] - 使用消耗品

交易相关
————————————
💸 出售 [物品名] [数量] - 出售物品
🏪 出售所有物品 - 出售背包中的所有物品(武器和防具除外)
📦 批量出售 [类型] - 批量出售背包物品
🎲 下注 [大/小/豹子/顺子] 数额 - 按照指定类型押注进行下注

冒险相关
————————————
🎣 钓鱼 - 进行钓鱼获取金币
📖 图鉴 - 查看鱼类图鉴
🌄 外出 - 外出开始大富翁游戏
🤺 冒险 - 冒险打怪升级
👊 挑战 [@用户] - 向其他玩家发起挑战
👌 同意挑战 - 同意其他玩家的挑战请求
🫸 拒绝挑战 - 拒绝其他玩家的挑战请求
🗺️ 地图 - 查看游戏地图

地产相关
————————————
🏠 我的地产 - 查看玩家地产
🏘️ 购买地块 - 购买地块
🏘️ 升级地块 - 升级地块

社交系统
————————————
💕 求婚 [@用户] - 向玩家求婚
💑 同意求婚 - 同意求婚请求
💔 拒绝求婚 - 拒绝求婚请求
⚡️ 离婚 - 解除婚姻关系

其他功能
————————————
🏆 排行榜 [类型] - 查看排行榜
🔔 提醒 [内容] - 设置提醒
🗑️ 删除提醒 - 删除提醒

管理员功能
————————————
🔧 开机 - 开启游戏系统
🔧 关机 - 关闭游戏系统
💴 充值 [@用户] 数额 - 为指定用户充值指定数额的金币
⏰ 定时 [开机/关机] [时间] [每天] - 设置定时任务
📋 查看定时 - 查看定时任务
❌ 取消定时 [开机/关机] [时间] - 取消定时任务
🗑️ 清空定时 - 清空所有定时任务

系统时间: {}
""".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

    def register_player(self, user_id, nickname=None):
        """注册新玩家

        Args:
            user_id: 玩家ID
            nickname: 玩家昵称，如果未提供则使用user_id
        """
        if not user_id:
            return "无法获取您的ID，请确保ID已设置"

        # 检查是否已注册
        if self.get_player(user_id):
            return "您已经注册过了"

        try:
            # 如果没有提供昵称，使用user_id作为默认昵称
            if not nickname:
                nickname = str(user_id)

            # 创建新玩家
            player = Player.create_new(user_id, nickname)
            player.player_file = self.player_file
            player.standard_fields = self.STANDARD_FIELDS

            # 保存玩家数据
            with open(self.player_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.STANDARD_FIELDS)
                writer.writerow(player.to_dict())

            return f"注册成功！"
        except Exception as e:
            logger.error(f"注册玩家出错: {e}")
            return "注册失败，请稍后再试"

    def get_player(self, user_id) -> Optional[Player]:
        """获取玩家数据"""
        try:
            player = Player.get_player(user_id, self.player_file)
            if player:
                # 设置必要的文件信息
                player.player_file = self.player_file
                player.standard_fields = self.STANDARD_FIELDS
            return player
        except Exception as e:
            logger.error(f"获取玩家数据出错: {e}")
            raise

    def fishing(self, user_id):
        """钓鱼"""
        player = self.get_player(user_id)
        if not player:
            return "您还没注册,请先注册"

        # 检查是否有鱼竿
        inventory = player.inventory
        rod = None
        for item in inventory:
            if item in ['木制鱼竿', '铁制鱼竿', '金制鱼竿']:
                rod = item
                break

        if not rod:
            return "您需要先购买一个鱼竿才能钓鱼"

        # 检查冷却时间
        now = datetime.datetime.now()
        last_fishing_str = player.last_fishing

        if last_fishing_str:
            last_fishing = datetime.datetime.strptime(last_fishing_str, '%Y-%m-%d %H:%M:%S')
            cooldown = datetime.timedelta(minutes=1)  # 1分钟冷却时间
            if now - last_fishing < cooldown:
                remaining = cooldown - (now - last_fishing)
                return f"钓鱼冷却中，还需等待 {remaining.seconds} 秒"

        # 调用钓鱼系统
        result = self.fishing_system.go_fishing(player, rod)

        # 更新玩家数据
        updates = {
            'last_fishing': now.strftime('%Y-%m-%d %H:%M:%S')
        }

        # 处理耐久度
        rod_durability = player.rod_durability
        new_durability = max(0, rod_durability.get(rod, 100) - result['durability_cost'])
        rod_durability[rod] = new_durability
        updates['rod_durability'] = json.dumps(rod_durability)

        # 如果钓到鱼
        if result['success']:
            new_inventory = inventory + [result['fish']['name']]
            updates['inventory'] = json.dumps(new_inventory)
            # 添加金币奖励
            new_gold = int(player.gold) + result['coins_reward']
            updates['gold'] = str(new_gold)
            message = result['message']  # 使用钓鱼系返回的完整消息
        else:
            message = result['message']

        # 处理鱼竿损坏
        if new_durability <= 0:
            inventory.remove(rod)
            updates['inventory'] = json.dumps(inventory)
            durability_warning = f"\n💔 {rod}已损坏，已从背包移除"
        elif new_durability < 30:
            durability_warning = f"\n⚠️警告：{rod}耐久度不足30%"
        else:
            durability_warning = ""

        self._update_player_data(user_id, updates)
        return f"{message}{durability_warning}"

    def show_fish_collection(self, user_id, content=""):
        """显示鱼类图鉴"""
        player = self.get_player(user_id)
        if not player:
            return "您还没有注册,请先注册 "

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

    #  外出打怪
    def go_out(self, user_id):
        """外出探险或漫步"""
        player = self.get_player(user_id)
        if not player:
            return "您还没有注册游戏"

        # 检查玩家状态
        if int(player.hp) <= 0:
            return "您的生命值不足，请先使用药品恢复"

        # 检查冷却时间
        current_time = int(time.time())
        last_attack_time = int(player.last_attack)
        cooldown = 60

        if current_time - last_attack_time < cooldown:
            remaining = cooldown - (current_time - last_attack_time)
            return f"您刚刚进行过活动,请等待 {remaining} 秒后再次外出"

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

        result = [
            f"🎲 掷出 {steps} 点",
            f"来到了 {block['name']}"
        ]

        if block['type'] == '起点':
            bonus = 2000
            new_gold = int(player.gold) + bonus
            self._update_player_data(user_id, {'gold': str(new_gold)})
            result.append(f"经过起点获得 {bonus} 金币")
        elif block['type'] == '机遇':
            event = self.monopoly.trigger_random_event()
            if 'effect' in event:
                for key, value in event['effect'].items():
                    if key == 'gold':
                        new_gold = int(player.gold) + value
                        self._update_player_data(user_id, {'gold': str(new_gold)})
                        # 添加金币变化提示
                        if value > 0:
                            result.append(f"💰 获得 {value} 金币")
                        else:
                            result.append(f"💸 失去 {abs(value)} 金币")
            result.append(f"🎲 触发事件: {event['name']}")
            result.append(event['description'])
        elif block['type'] in ['空地', '直辖市', '省会', '地级市', '县城', '乡村']:
            property_info = self.monopoly.get_property_owner(new_position)
            if property_info is None or 'owner' not in property_info:
                # 可以购买
                price = self.monopoly.calculate_property_price(new_position)
                result.append(f"这块地还没有主人")
                result.append(f"区域类型: {block['region']}")
                result.append(f"需要 {price} 金币购买")
                result.append("发送'购买地块'即可购买")
                print(f"[DEBUG] 玩家 {user_id} 访问了未拥有的地块，位置: {new_position}, 价格: {price}")
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

                            result.append(f"这是 {owner_player.nickname} 的地盘")
                            result.append(f"区域类型: {block['region']}")
                            result.append(f"支付租金 {rent} 金币")
                            result.append(f"当前金币: {new_player_gold}")
                            print(f"[INFO] 玩家 {user_id} 支付了 {rent} 金币租金给 {owner_player.nickname}，剩余金币: {new_player_gold}")
                        else:
                            result.append(f"你的金币不足以支付 {rent} 金币的租金！")
                            print(f"[WARNING] 玩家 {user_id} 的金币不足以支付租金，当前金币: {player.gold}, 需要租金: {rent}")
                    else:
                        result.append("地产所有者信息异常，请联系管理员")
                        print(f"[ERROR] 无法获取地产所有者 {owner} 的信息，位置: {new_position}")
                else:
                    result.append("这是你的地盘")
                    result.append(f"区域类型: {block['region']}")
                    if property_info.get('level', 0) < 3:
                        result.append("可以发送'升级地块'进行升级")
                    print(f"[INFO] 玩家 {user_id} 访问了自己的地盘，位置: {new_position}")

        return "\n".join(result)

    # 冒险
    def go_adventure(self, user_id):
        """冒险"""
        player = self.get_player(user_id)
        if not player:
            return "您还没有注册游戏"

        # 检查冷却时间（冒险cd: 10s）
        current_time = int(time.time())
        adventure_last_attack = player.adventure_last_attack
        cooldown = 10

        # 检查冷却时间
        if current_time - adventure_last_attack < cooldown:
            remaining = cooldown - (current_time - adventure_last_attack)
            return f"您刚刚进行过冒险活动,请等待 {remaining} 秒后再次进行冒险"

        # 检查玩家状态
        if int(player.hp) <= 0:
            return "您的生命值不足，请先使用药品恢复"

        # 更新玩家冒险计时
        self._update_player_data(user_id, {
            'adventure_last_attack': str(current_time)
        })

        # 掷骰子
        steps = self.monopoly.roll_dice()

        # 获取冒险地图信息
        block = self.monopoly.get_adventure_block_info(steps)

        logger.info(f"[DEBUG] 玩家 {user_id} 冒险，位置: {steps}, 地图信息: {block}")

        result = [
            f"🎲 掷出 {steps} 点",
            f"[{player.nickname}] 来到了 [{block['name']}]\n\n{block['description']}\n"
        ]

        if block['type'] == '森林':
            string_array = ["怪物巢穴", "古树之心", "迷雾谷地", "幽灵空地", "腐烂树林", "灵兽栖息地", "毒沼密林", "月光草原", "荒弃村落", "暗影森林"]
            # 随机进入一个场景
            scene = random.choice(string_array)
        if block['type'] == '山脉':
            string_array = ["绝壁险峰", "熔岩洞窟", "风暴山巅"]
            # 随机进入一个场景
            scene = random.choice(string_array)
        if block['type'] == '沙漠':
            string_array = ["流沙之地", "烈日废墟", "沙暴迷城"]
            # 随机进入一个场景
            scene = random.choice(string_array)
        if block['type'] == '冰原':
            string_array = ["寒冰峡谷", "冻土遗迹"]
            # 随机进入一个场景
            scene = random.choice(string_array)
        if block['type'] == '沼泽':
            string_array = ["毒雾沼泽", "枯骨之地"]
            # 随机进入一个场景
            scene = random.choice(string_array)

        # 触发战斗
        battle_result = self._battle(user_id, self._generate_monster(player, scene))
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

        # 设置随机种子为当前时间戳
        random.seed(time.time())
        # 怪物的等级随机(根据玩家等级上下浮动)
        random_level = random.randint(-2, 2)
        # 计算怪物等级
        monster_level = max(1, player_level + random_level)
        # 计算等级因子
        level_factor = 1 + (monster_level - 1) * 0.3

        # 定义怪物库
        monsters = {
            "怪物巢穴": [
                {'name': '森林史莱姆', 'hp': int(60 * level_factor), 'attack': int(1.3 * 10 * level_factor), 'defense': int(6 * level_factor), 'exp': int(20 * level_factor), 'gold': int(10 * 30 * level_factor)},
                {'name': '潜伏狼蛛', 'hp': int(80 * level_factor), 'attack': int(1.3 * 15 * level_factor), 'defense': int(8 * level_factor), 'exp': int(25 * level_factor), 'gold': int(10 * 35 * level_factor)},
                {'name': '巢穴蝙蝠', 'hp': int(50 * level_factor), 'attack': int(1.3 * 12 * level_factor), 'defense': int(5 * level_factor), 'exp': int(18 * level_factor), 'gold': int(10 * 28 * level_factor)},
                {'name': '毒刺蜂', 'hp': int(70 * level_factor), 'attack': int(1.3 * 18 * level_factor), 'defense': int(7 * level_factor), 'exp': int(22 * level_factor), 'gold': int(10 * 32 * level_factor)},
                {'name': '黑影潜伏者', 'hp': int(100 * level_factor), 'attack': int(1.3 * 20 * level_factor), 'defense': int(10 * level_factor), 'exp': int(30 * level_factor), 'gold': int(10 * 40 * level_factor)}
            ],
            "古树之心": [
                {'name': '树精守卫', 'hp': int(120 * level_factor), 'attack': int(1.3 * 25 * level_factor), 'defense': int(15 * level_factor), 'exp': int(35 * level_factor), 'gold': int(10 * 50 * level_factor)},
                {'name': '魔化藤蔓', 'hp': int(90 * level_factor), 'attack': int(1.3 * 20 * level_factor), 'defense': int(12 * level_factor), 'exp': int(28 * level_factor), 'gold': int(10 * 45 * level_factor)},
                {'name': '树灵幽影', 'hp': int(80 * level_factor), 'attack': int(1.3 * 22 * level_factor), 'defense': int(10 * level_factor), 'exp': int(30 * level_factor), 'gold': int(10 * 42 * level_factor)},
                {'name': '腐化树妖', 'hp': int(150 * level_factor), 'attack': int(1.3 * 30 * level_factor), 'defense': int(18 * level_factor), 'exp': int(40 * level_factor), 'gold': int(10 * 60 * level_factor)},
                {'name': '古树之魂', 'hp': int(200 * level_factor), 'attack': int(1.3 * 35 * level_factor), 'defense': int(20 * level_factor), 'exp': int(50 * level_factor), 'gold': int(10 * 70 * level_factor)}
            ],
            "迷雾谷地": [
                {'name': '雾影幽魂', 'hp': int(70 * level_factor), 'attack': int(1.3 * 18 * level_factor), 'defense': int(8 * level_factor), 'exp': int(25 * level_factor), 'gold': int(10 * 35 * level_factor)},
                {'name': '迷雾猎手', 'hp': int(90 * level_factor), 'attack': int(1.3 * 22 * level_factor), 'defense': int(10 * level_factor), 'exp': int(30 * level_factor), 'gold': int(10 * 45 * level_factor)},
                {'name': '隐匿毒蛇', 'hp': int(60 * level_factor), 'attack': int(1.3 * 20 * level_factor), 'defense': int(6 * level_factor), 'exp': int(22 * level_factor), 'gold': int(10 * 32 * level_factor)},
                {'name': '雾中行者', 'hp': int(110 * level_factor), 'attack': int(1.3 * 28 * level_factor), 'defense': int(12 * level_factor), 'exp': int(35 * level_factor), 'gold': int(10 * 50 * level_factor)},
                {'name': '迷雾巨兽', 'hp': int(150 * level_factor), 'attack': int(1.3 * 32 * level_factor), 'defense': int(18 * level_factor), 'exp': int(45 * level_factor), 'gold': int(10 * 65 * level_factor)}
            ],
            "幽灵空地": [
                {'name': '幽灵战士', 'hp': int(100 * level_factor), 'attack': int(1.3 * 25 * level_factor), 'defense': int(12 * level_factor), 'exp': int(35 * level_factor), 'gold': int(10 * 50 * level_factor)},
                {'name': '亡灵弓手', 'hp': int(80 * level_factor), 'attack': int(1.3 * 28 * level_factor), 'defense': int(10 * level_factor), 'exp': int(32 * level_factor), 'gold': int(10 * 48 * level_factor)},
                {'name': '怨灵法师', 'hp': int(90 * level_factor), 'attack': int(1.3 * 30 * level_factor), 'defense': int(8 * level_factor), 'exp': int(38 * level_factor), 'gold': int(10 * 52 * level_factor)},
                {'name': '幽魂骑士', 'hp': int(140 * level_factor), 'attack': int(1.3 * 35 * level_factor), 'defense': int(15 * level_factor), 'exp': int(45 * level_factor), 'gold': int(10 * 65 * level_factor)},
                {'name': '复仇亡灵', 'hp': int(160 * level_factor), 'attack': int(1.3 * 40 * level_factor), 'defense': int(18 * level_factor), 'exp': int(50 * level_factor), 'gold': int(10 * 70 * level_factor)}
            ],
            "腐烂树林": [
                {'name': '腐朽树妖', 'hp': int(120 * level_factor), 'attack': int(1.3 * 20 * level_factor), 'defense': int(15 * level_factor), 'exp': int(35 * level_factor), 'gold': int(10 * 45 * level_factor)},
                {'name': '毒液史莱姆', 'hp': int(70 * level_factor), 'attack': int(1.3 * 18 * level_factor), 'defense': int(8 * level_factor), 'exp': int(25 * level_factor), 'gold': int(10 * 35 * level_factor)},
                {'name': '腐化狼蛛', 'hp': int(80 * level_factor), 'attack': int(1.3 * 22 * level_factor), 'defense': int(10 * level_factor), 'exp': int(30 * level_factor), 'gold': int(10 * 40 * level_factor)},
                {'name': '腐木傀儡', 'hp': int(150 * level_factor), 'attack': int(1.3 * 28 * level_factor), 'defense': int(18 * level_factor), 'exp': int(40 * level_factor), 'gold': int(10 * 55 * level_factor)},
                {'name': '树根潜伏者', 'hp': int(100 * level_factor), 'attack': int(1.3 * 25 * level_factor), 'defense': int(12 * level_factor), 'exp': int(35 * level_factor), 'gold': int(10 * 50 * level_factor)}
            ],
            "灵兽栖息地": [
                {'name': '灵气鹿', 'hp': int(80 * level_factor), 'attack': int(1.3 * 15 * level_factor), 'defense': int(12 * level_factor), 'exp': int(25 * level_factor), 'gold': int(10 * 40 * level_factor)},
                {'name': '守护灵兽', 'hp': int(120 * level_factor), 'attack': int(1.3 * 30 * level_factor), 'defense': int(18 * level_factor), 'exp': int(45 * level_factor), 'gold': int(10 * 55 * level_factor)},
                {'name': '灵狐幻影', 'hp': int(70 * level_factor), 'attack': int(1.3 * 22 * level_factor), 'defense': int(10 * level_factor), 'exp': int(28 * level_factor), 'gold': int(10 * 38 * level_factor)},
                {'name': '秘境猛虎', 'hp': int(140 * level_factor), 'attack': int(1.3 * 35 * level_factor), 'defense': int(15 * level_factor), 'exp': int(50 * level_factor), 'gold': int(10 * 65 * level_factor)},
                {'name': '灵域飞龙', 'hp': int(180 * level_factor), 'attack': int(1.3 * 40 * level_factor), 'defense': int(20 * level_factor), 'exp': int(60 * level_factor), 'gold': int(10 * 80 * level_factor)}
            ],
            "毒沼密林": [
                {'name': '毒液巨蛛', 'hp': int(100 * level_factor), 'attack': int(1.3 * 25 * level_factor), 'defense': int(12 * level_factor), 'exp': int(35 * level_factor), 'gold': int(10 * 50 * level_factor)},
                {'name': '毒气史莱姆', 'hp': int(80 * level_factor), 'attack': int(1.3 * 20 * level_factor), 'defense': int(10 * level_factor), 'exp': int(28 * level_factor), 'gold': int(10 * 38 * level_factor)},
                {'name': '瘴气妖藤', 'hp': int(120 * level_factor), 'attack': int(1.3 * 28 * level_factor), 'defense': int(15 * level_factor), 'exp': int(40 * level_factor), 'gold': int(10 * 55 * level_factor)},
                {'name': '毒雾蜥蜴', 'hp': int(90 * level_factor), 'attack': int(1.3 * 22 * level_factor), 'defense': int(10 * level_factor), 'exp': int(30 * level_factor), 'gold': int(10 * 42 * level_factor)},
                {'name': '瘴气守护者', 'hp': int(160 * level_factor), 'attack': int(1.3 * 35 * level_factor), 'defense': int(20 * level_factor), 'exp': int(50 * level_factor), 'gold': int(10 * 70 * level_factor)}
            ],
            "月光草原": [
                {'name': '草原狼群', 'hp': int(80 * level_factor), 'attack': int(1.3 * 20 * level_factor), 'defense': int(10 * level_factor), 'exp': int(28 * level_factor), 'gold': int(10 * 40 * level_factor)},
                {'name': '隐匿猎手', 'hp': int(90 * level_factor), 'attack': int(1.3 * 25 * level_factor), 'defense': int(12 * level_factor), 'exp': int(35 * level_factor), 'gold': int(10 * 50 * level_factor)},
                {'name': '月光幽灵', 'hp': int(100 * level_factor), 'attack': int(1.3 * 30 * level_factor), 'defense': int(10 * level_factor), 'exp': int(40 * level_factor), 'gold': int(10 * 55 * level_factor)},
                {'name': '夜影刺客', 'hp': int(110 * level_factor), 'attack': int(1.3 * 35 * level_factor), 'defense': int(15 * level_factor), 'exp': int(45 * level_factor), 'gold': int(10 * 60 * level_factor)},
                {'name': '草原巨熊', 'hp': int(200 * level_factor), 'attack': int(1.3 * 50 * level_factor), 'defense': int(25 * level_factor), 'exp': int(60 * level_factor), 'gold': int(10 * 80 * level_factor)}
            ],
            "荒弃村落": [
                {'name': '村落幽魂', 'hp': int(90 * level_factor), 'attack': int(1.3 * 20 * level_factor), 'defense': int(10 * level_factor), 'exp': int(30 * level_factor), 'gold': int(10 * 40 * level_factor)},
                {'name': '腐化村民', 'hp': int(100 * level_factor), 'attack': int(1.3 * 25 * level_factor), 'defense': int(15 * level_factor), 'exp': int(35 * level_factor), 'gold': int(10 * 50 * level_factor)},
                {'name': '废墟潜伏者', 'hp': int(80 * level_factor), 'attack': int(1.3 * 22 * level_factor), 'defense': int(12 * level_factor), 'exp': int(28 * level_factor), 'gold': int(10 * 38 * level_factor)},
                {'name': '憎恶尸鬼', 'hp': int(150 * level_factor), 'attack': int(1.3 * 30 * level_factor), 'defense': int(18 * level_factor), 'exp': int(50 * level_factor), 'gold': int(10 * 65 * level_factor)},
                {'name': '村落恶鬼', 'hp': int(120 * level_factor), 'attack': int(1.3 * 35 * level_factor), 'defense': int(15 * level_factor), 'exp': int(45 * level_factor), 'gold': int(10 * 60 * level_factor)}
            ],
            "暗影森林": [
                {'name': '暗影猎手', 'hp': int(100 * level_factor), 'attack': int(1.3 * 30 * level_factor), 'defense': int(15 * level_factor), 'exp': int(40 * level_factor), 'gold': int(10 * 55 * level_factor)},
                {'name': '黑暗幽灵', 'hp': int(90 * level_factor), 'attack': int(1.3 * 25 * level_factor), 'defense': int(12 * level_factor), 'exp': int(35 * level_factor), 'gold': int(10 * 45 * level_factor)},
                {'name': '夜行毒蛇', 'hp': int(80 * level_factor), 'attack': int(1.3 * 20 * level_factor), 'defense': int(10 * level_factor), 'exp': int(28 * level_factor), 'gold': int(10 * 38 * level_factor)},
                {'name': '暗影潜伏者', 'hp': int(120 * level_factor), 'attack': int(1.3 * 35 * level_factor), 'defense': int(18 * level_factor), 'exp': int(45 * level_factor), 'gold': int(10 * 65 * level_factor)},
                {'name': '黑暗树妖', 'hp': int(150 * level_factor), 'attack': int(1.3 * 40 * level_factor), 'defense': int(20 * level_factor), 'exp': int(55 * level_factor), 'gold': int(10 * 75 * level_factor)}
            ],
            "绝壁险峰": [
                {'name': '山崖猛禽', 'hp': int(80 * level_factor), 'attack': int(1.3 * 25 * level_factor), 'defense': int(10 * level_factor), 'exp': int(30 * level_factor), 'gold': int(10 * 50 * level_factor)},
                {'name': '岩石巨人', 'hp': int(150 * level_factor), 'attack': int(1.3 * 40 * level_factor), 'defense': int(30 * level_factor), 'exp': int(60 * level_factor), 'gold': int(10 * 70 * level_factor)},
                {'name': '爬山毒蛇', 'hp': int(70 * level_factor), 'attack': int(1.3 * 15 * level_factor), 'defense': int(10 * level_factor), 'exp': int(25 * level_factor), 'gold': int(10 * 35 * level_factor)},
                {'name': '峭壁蝙蝠', 'hp': int(60 * level_factor), 'attack': int(1.3 * 10 * level_factor), 'defense': int(8 * level_factor), 'exp': int(20 * level_factor), 'gold': int(10 * 30 * level_factor)},
                {'name': '崖顶恶鹰', 'hp': int(130 * level_factor), 'attack': int(1.3 * 35 * level_factor), 'defense': int(12 * level_factor), 'exp': int(50 * level_factor), 'gold': int(10 * 65 * level_factor)}
            ],
            "熔岩洞窟": [
                {'name': '火焰元素', 'hp': int(100 * level_factor), 'attack': int(1.3 * 30 * level_factor), 'defense': int(12 * level_factor), 'exp': int(40 * level_factor), 'gold': int(10 * 60 * level_factor)},
                {'name': '熔岩巨人', 'hp': int(180 * level_factor), 'attack': int(1.3 * 50 * level_factor), 'defense': int(20 * level_factor), 'exp': int(70 * level_factor), 'gold': int(10 * 90 * level_factor)},
                {'name': '火焰蝙蝠', 'hp': int(80 * level_factor), 'attack': int(1.3 * 25 * level_factor), 'defense': int(10 * level_factor), 'exp': int(35 * level_factor), 'gold': int(10 * 50 * level_factor)},
                {'name': '熔岩魔蛇', 'hp': int(90 * level_factor), 'attack': int(1.3 * 20 * level_factor), 'defense': int(15 * level_factor), 'exp': int(30 * level_factor), 'gold': int(10 * 42 * level_factor)},
                {'name': '炎爆恶魔', 'hp': int(200 * level_factor), 'attack': int(1.3 * 60 * level_factor), 'defense': int(25 * level_factor), 'exp': int(80 * level_factor), 'gold': int(10 * 100 * level_factor)}
            ],
            "流沙之地": [
                {'name': '流沙巨蟒', 'hp': int(120 * level_factor), 'attack': int(1.3 * 30 * level_factor), 'defense': int(10 * level_factor), 'exp': int(40 * level_factor), 'gold': int(10 * 55 * level_factor)},
                {'name': '沙漠蝎子', 'hp': int(100 * level_factor), 'attack': int(1.3 * 25 * level_factor), 'defense': int(12 * level_factor), 'exp': int(35 * level_factor), 'gold': int(10 * 50 * level_factor)},
                {'name': '沙尘潜伏者', 'hp': int(80 * level_factor), 'attack': int(1.3 * 20 * level_factor), 'defense': int(8 * level_factor), 'exp': int(28 * level_factor), 'gold': int(10 * 40 * level_factor)},
                {'name': '沙之傀儡', 'hp': int(160 * level_factor), 'attack': int(1.3 * 40 * level_factor), 'defense': int(20 * level_factor), 'exp': int(60 * level_factor), 'gold': int(10 * 70 * level_factor)},
                {'name': '沙漠猎犬', 'hp': int(90 * level_factor), 'attack': int(1.3 * 22 * level_factor), 'defense': int(10 * level_factor), 'exp': int(32 * level_factor), 'gold': int(10 * 45 * level_factor)}
            ],
            "烈日废墟": [
                {'name': '炎蝎', 'hp': int(100 * level_factor), 'attack': int(1.3 * 30 * level_factor), 'defense': int(10 * level_factor), 'exp': int(40 * level_factor), 'gold': int(10 * 55 * level_factor)},
                {'name': '废墟幽魂', 'hp': int(120 * level_factor), 'attack': int(1.3 * 28 * level_factor), 'defense': int(15 * level_factor), 'exp': int(45 * level_factor), 'gold': int(10 * 60 * level_factor)},
                {'name': '火焰殉教者', 'hp': int(140 * level_factor), 'attack': int(1.3 * 40 * level_factor), 'defense': int(20 * level_factor), 'exp': int(60 * level_factor), 'gold': int(10 * 75 * level_factor)},
                {'name': '石化蜥蜴', 'hp': int(80 * level_factor), 'attack': int(1.3 * 25 * level_factor), 'defense': int(12 * level_factor), 'exp': int(35 * level_factor), 'gold': int(10 * 50 * level_factor)},
                {'name': '烈日幻影', 'hp': int(70 * level_factor), 'attack': int(1.3 * 23 * level_factor), 'defense': int(8 * level_factor), 'exp': int(28 * level_factor), 'gold': int(10 * 40 * level_factor)}
            ],
            "沙暴迷城": [
                {'name': '沙暴刺客', 'hp': int(90 * level_factor), 'attack': int(1.3 * 28 * level_factor), 'defense': int(12 * level_factor), 'exp': int(35 * level_factor), 'gold': int(10 * 50 * level_factor)},
                {'name': '废墟守卫', 'hp': int(150 * level_factor), 'attack': int(1.3 * 35 * level_factor), 'defense': int(18 * level_factor), 'exp': int(50 * level_factor), 'gold': int(10 * 70 * level_factor)},
                {'name': '迷城幽魂', 'hp': int(110 * level_factor), 'attack': int(1.3 * 25 * level_factor), 'defense': int(10 * level_factor), 'exp': int(38 * level_factor), 'gold': int(10 * 55 * level_factor)},
                {'name': '黄沙巫师', 'hp': int(80 * level_factor), 'attack': int(1.3 * 22 * level_factor), 'defense': int(8 * level_factor), 'exp': int(30 * level_factor), 'gold': int(10 * 45 * level_factor)},
                {'name': '沙暴元素', 'hp': int(130 * level_factor), 'attack': int(1.3 * 40 * level_factor), 'defense': int(15 * level_factor), 'exp': int(55 * level_factor), 'gold': int(10 * 65 * level_factor)}
            ],
            "寒冰峡谷": [
                {'name': '极地狼群', 'hp': int(120 * level_factor), 'attack': int(1.3 * 28 * level_factor), 'defense': int(15 * level_factor), 'exp': int(40 * level_factor), 'gold': int(10 * 55 * level_factor)},
                {'name': '冰原独角兽', 'hp': int(150 * level_factor), 'attack': int(1.3 * 35 * level_factor), 'defense': int(18 * level_factor), 'exp': int(50 * level_factor), 'gold': int(10 * 65 * level_factor)},
                {'name': '寒霜飞鹰', 'hp': int(90 * level_factor), 'attack': int(1.3 * 22 * level_factor), 'defense': int(10 * level_factor), 'exp': int(32 * level_factor), 'gold': int(10 * 45 * level_factor)},
                {'name': '冰霜元素', 'hp': int(130 * level_factor), 'attack': int(1.3 * 30 * level_factor), 'defense': int(12 * level_factor), 'exp': int(45 * level_factor), 'gold': int(10 * 55 * level_factor)},
                {'name': '极寒古龙', 'hp': int(200 * level_factor), 'attack': int(1.3 * 50 * level_factor), 'defense': int(25 * level_factor), 'exp': int(80 * level_factor), 'gold': int(10 * 100 * level_factor)}
            ],
            "冻土遗迹": [
                {'name': '遗迹守护者', 'hp': int(140 * level_factor), 'attack': int(1.3 * 40 * level_factor), 'defense': int(20 * level_factor), 'exp': int(60 * level_factor), 'gold': int(10 * 75 * level_factor)},
                {'name': '冰冻骷髅', 'hp': int(120 * level_factor), 'attack': int(1.3 * 30 * level_factor), 'defense': int(15 * level_factor), 'exp': int(45 * level_factor), 'gold': int(10 * 55 * level_factor)},
                {'name': '冻土游魂', 'hp': int(100 * level_factor), 'attack': int(1.3 * 25 * level_factor), 'defense': int(12 * level_factor), 'exp': int(38 * level_factor), 'gold': int(10 * 50 * level_factor)},
                {'name': '霜冻教徒', 'hp': int(80 * level_factor), 'attack': int(1.3 * 22 * level_factor), 'defense': int(10 * level_factor), 'exp': int(30 * level_factor), 'gold': int(10 * 42 * level_factor)},
                {'name': '寒霜傀儡', 'hp': int(160 * level_factor), 'attack': int(1.3 * 35 * level_factor), 'defense': int(18 * level_factor), 'exp': int(50 * level_factor), 'gold': int(10 * 65 * level_factor)}
            ],
            "毒雾沼泽": [
                {'name': '毒鳞鱼人', 'hp': int(90 * level_factor), 'attack': int(1.3 * 20 * level_factor), 'defense': int(12 * level_factor), 'exp': int(32 * level_factor), 'gold': int(10 * 42 * level_factor)},
                {'name': '腐臭鳄鱼', 'hp': int(120 * level_factor), 'attack': int(1.3 * 30 * level_factor), 'defense': int(15 * level_factor), 'exp': int(45 * level_factor), 'gold': int(10 * 60 * level_factor)},
                {'name': '瘴气渡鸦', 'hp': int(70 * level_factor), 'attack': int(1.3 * 18 * level_factor), 'defense': int(8 * level_factor), 'exp': int(25 * level_factor), 'gold': int(10 * 38 * level_factor)},
                {'name': '泥潭刺客', 'hp': int(150 * level_factor), 'attack': int(1.3 * 40 * level_factor), 'defense': int(20 * level_factor), 'exp': int(60 * level_factor), 'gold': int(10 * 75 * level_factor)},
                {'name': '沼泽魔神', 'hp': int(200 * level_factor), 'attack': int(1.3 * 50 * level_factor), 'defense': int(25 * level_factor), 'exp': int(80 * level_factor), 'gold': int(10 * 100 * level_factor)}
            ],
            "枯骨之地": [
                {'name': '枯骨战士', 'hp': int(100 * level_factor), 'attack': int(1.3 * 28 * level_factor), 'defense': int(12 * level_factor), 'exp': int(38 * level_factor), 'gold': int(10 * 50 * level_factor)},
                {'name': '沼泽骷髅', 'hp': int(90 * level_factor), 'attack': int(1.3 * 20 * level_factor), 'defense': int(10 * level_factor), 'exp': int(30 * level_factor), 'gold': int(10 * 45 * level_factor)},
                {'name': '不死巫师', 'hp': int(130 * level_factor), 'attack': int(1.3 * 35 * level_factor), 'defense': int(18 * level_factor), 'exp': int(50 * level_factor), 'gold': int(10 * 65 * level_factor)},
                {'name': '亡灵巨兽', 'hp': int(160 * level_factor), 'attack': int(1.3 * 40 * level_factor), 'defense': int(20 * level_factor), 'exp': int(60 * level_factor), 'gold': int(10 * 75 * level_factor)},
                {'name': '骨堆恶灵', 'hp': int(200 * level_factor), 'attack': int(1.3 * 50 * level_factor), 'defense': int(25 * level_factor), 'exp': int(80 * level_factor), 'gold': int(10 * 100 * level_factor)}
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
        monster['name'] = f"变异{monster['name']}"
        monster['hp'] = int(monster['hp'] * 1.5)
        monster['attack'] = int(monster['attack'] * 1.3)
        monster['defense'] = int(monster['defense'] * 1.2)
        monster['exp'] = int(monster['exp'] * 1.5)
        monster['gold'] = int(monster['gold'] * 1.5)
        return monster

    def _battle(self, user_id, monster):
        """战斗系统"""
        player = self.get_player(user_id)

        # 玩家属性
        player_level = player.level
        player_hp = int(player.hp)
        player_max_hp = int(player.max_hp)
        player_attack = int(player.attack)
        player_defense = int(player.defense)
        player_name = player.nickname
        # 减伤率为防御值的10%，最高不超过80%
        player_damage_reduction = min(player_defense/1000, 0.8)
        player_total_damage = 0

        # 怪物属性
        monster_level = monster['level']
        monster_hp = monster['hp']
        monster_max_hp = monster['hp']
        monster_attack = monster['attack']
        monster_defense = monster['defense']
        monster_name = monster.get('name', '未知怪物')
        # 减伤率为防御值的10%，最高不超过80%
        monster_damage_reduction = min(monster_defense/1000, 0.8)
        monster_total_damage = 0

        #日志打印怪物属性
        logger.debug(f"玩家[{player_name}]属性: 生命值: {player_hp}/{player_max_hp}, 攻击力: {player_attack}, 防御力: {player_defense}")
        logger.debug(f"怪物[{monster_name}]属性: 生命值: {monster_hp}, 攻击力: {monster_attack}, 防御力: {monster_defense}")

        battle_log = [f"⚔️ 遭遇了 {monster['name']}！"]
        battle_log.append(f"\n{player_name} Lv.{player_level}\n❤️[{player_hp}]\n⚔️[{player_attack}]\n🛡️[{str(player_defense)}]")
        battle_log.append(f"\n{monster_name} Lv.{monster_level}\n❤️[{monster_hp}]\n⚔️[{monster_attack}]\n🛡️[{str(monster_defense)}]")

        # 怪物是否狂暴状态
        is_berserk = False

        round_num = 1
        important_events = []

        while player_hp > 0 and monster_hp > 0:

            if round_num <= 4:
                battle_log.append(f"\n第{round_num}回合")

            # 计算玩家伤害
            player_damage = int(player_attack * (1- monster_damage_reduction))

            # 伤害修正：确保减伤后伤害至少为1
            player_damage = max(1, player_damage)

            player_explain_str = ""

            # 设置随机种子为当前时间戳
            random.seed(time.time())
            # 生成1到100之间的随机数
            random_number = random.randint(1, 100)
            if random_number > 80:
                # 暴击
                player_final_damage = int(player_damage * random.uniform(1.5, 1.8))
                player_explain_str = "💥暴击！"
            elif random_number < 20:
                # 失手
                player_final_damage = max(1, int(player_damage * random.uniform(0.5, 0.7)))
                player_explain_str = "🤦‍♂️失手了！"
            else:
                # 正常命中
                player_final_damage = int(player_damage)

            # 确保最终伤害至少为1点
            player_final_damage = max(1, player_final_damage)

            # 减少怪物血量
            monster_hp -= player_final_damage
            player_total_damage += player_final_damage

            # 记录战斗日志（前4回合）
            if round_num <= 4:
                battle_log.append(f"{player_explain_str}你对{monster_name}造成 {player_final_damage} 点伤害")

            # 检查怪物是否死亡
            if monster_hp <= 0:
                break

            # 检查怪物是否进入狂暴状态
            if not is_berserk and monster_hp < monster_max_hp * 0.3 and random.random() < 0.4:
                is_berserk = True
                # 提升怪物伤害
                monster_attack = int(monster_attack * 1.5)
                if round_num <= 4:
                    battle_log.append(f"💢 {monster['name']}进入狂暴状态！")
                else:
                    important_events.append(f"第{round_num}回合: {monster['name']}进入狂暴状态！")

            # 怪物反击
            if monster_hp > 0:
                # 计算怪物伤害
                monster_damage = int(monster_attack * (1- player_damage_reduction))

                # 确保减伤后伤害至少为1
                monster_damage = max(1, monster_damage)

                explain_str = ""

                # 设置随机种子为当前时间戳
                random.seed(time.time())
                # 生成1到100之间的随机数
                random_number = random.randint(1, 100)
                if random_number > 80:
                    # 暴击
                    monster_final_damage = int(monster_damage * random.uniform(1.5, 1.8))
                    explain_str = "💥暴击！"
                elif random_number < 20:
                    # 失手
                    monster_final_damage = max(1, int(monster_damage * random.uniform(0.5, 0.7)))
                    explain_str = "🤦‍♂️失手了！"
                else:
                    # 正常命中，应用随机波动
                    monster_final_damage = int(monster_damage)

                # 减少玩家生命值
                player_hp -= monster_final_damage
                monster_total_damage += monster_final_damage

                life_steal = 0

                # 狂暴状态下吸血
                if is_berserk:
                    life_steal = int(monster_damage * 0.3)
                    monster_hp = min(monster_max_hp, monster_hp + life_steal)
                    if round_num <= 4:
                        battle_log.append(f"{explain_str}{monster['name']}对你造成 {monster_final_damage} 点伤害，并吸取了 {life_steal} 点生命值")
                else:
                    if round_num <= 4:
                        battle_log.append(f"{explain_str}{monster['name']}对你造成 {monster_final_damage} 点伤害")

                logger.debug(f"\n-------------------------------------------------------------\n玩家[{player_name} 减伤：{player_damage_reduction}， 怪物[{monster_name}]减伤：{monster_damage_reduction}\n玩家在第{round_num}回合造成的实际伤害为：{player_final_damage}\n怪物在第{round_num}回合造成的实际伤害为：{monster_final_damage}，吸取血量：{life_steal}\n玩家剩余生命值：{player_hp}，怪物剩余生命值：{monster_hp}")

            round_num += 1

        if player_hp < 0:
            battle_log.append(f"\n{player_name}被打败了！")

        if monster_hp < 0:
            battle_log.append(f"\n{monster_name}被打败了！")

        # 战斗结束
        battle_log.append(f"\n战斗持续了{round_num}回合")

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
        battle_log.append(f"\n伤害统计:")
        battle_log.append(f"{player_name}: {player_total_damage}")
        battle_log.append(f"{monster_name}: {monster_total_damage}")

        if player_hp > 0:
            # 获取怪物基础经验值
            default_exp = monster['exp']

            # 每高一级增加4%经验
            exp_multiplier = 1 + (player.level * 0.04)

            # 结算经验/金币
            award_exp = int(default_exp * exp_multiplier)
            award_gold = int(min(player.level * 0.1, 1) * monster['gold'])
            actual_gain_gold = player.gold + award_gold

            # 初始化升级标志
            level_up = False

            # 计算等级提升所需要的经验值
            exp_required_to_level_up = player.get_exp_for_next_level(player_level) - player.exp
            # 判断本次获得的经验是否足够升级
            if award_exp >= exp_required_to_level_up:
                # 升级
                new_level = int(player.level) + 1
                new_exp = award_exp - exp_required_to_level_up
                level_up = True

                # 使用固定增长值
                hp_increase = 50      # 每级+50血量
                attack_increase = 10  # 每级+10攻击
                defense_increase = 10 # 每级+10防御

                new_max_hp = int(player.max_hp) + hp_increase
                new_attack = int(player.attack) + attack_increase
                new_defense = int(player.defense) + defense_increase
            else :
                # 不升级
                new_level = player.level
                new_exp = player.exp + award_exp
                new_max_hp = player.max_hp
                new_attack = player.attack
                new_defense = player.defense

            # 更新玩家数据
            self._update_player_data(user_id, {
                'level': str(new_level),
                'exp': str(new_exp),
                'hp': str(player_hp),
                'max_hp': str(new_max_hp),
                'attack': str(new_attack),
                'defense': str(new_defense),
                'gold': str(actual_gain_gold)
            })

            battle_log.append(f"\n🎉 战斗胜利")
            battle_log.append(f"获得 {award_exp} 经验值")
            battle_log.append(f"获得 {award_gold} 金币")

            if level_up:
                battle_log.append(f"\n🆙 升级啦！当前等级 {new_level}")
                battle_log.append(f"\n[{player_name}] Lv.{player.level}  Exp:{new_exp}/{player.get_exp_for_next_level(new_level)}")
                battle_log.append("属性提升：")
                battle_log.append(f"❤️ 生命上限 +{hp_increase}")
                battle_log.append(f"⚔️ 攻击力 +{attack_increase}")
                battle_log.append(f"🛡️ 防御力 +{defense_increase}")
            else:
                battle_log.append(f"\n[{player_name}] Lv.{player.level}  Exp:{new_exp}/{player.get_exp_for_next_level(new_level)}")
        else:
            # 更新玩家血量
            self._update_player_data(user_id, {
                'hp': '0',
            })
            battle_log.append(f"\n💀 战斗失败！")

        return "\n".join(battle_log)

    def use_item(self, user_id, content):
        """使用物品功能"""
        try:
            # 解析命令，格式为 "使用 物品名" 或 "使用 物品名 数量"
            parts = content.split()
            if len(parts) < 2:
                return "使用格式错误！请使用: 使用 物品名 [数量]"

            item_name = parts[1]
            amount = 1  # 默认使用1个
            if len(parts) > 2:
                amount = int(parts[2])
                if amount <= 0:
                    return "使用数量必须大于0"
        except (IndexError, ValueError):
            return "使用格式错误！请使用: 使用 物品名 [数量]"

        # 检查玩家是否存在
        player = self.get_player(user_id)
        if not player:
            return "您还没注册,请先注册 "

        # 获取物品信息
        items = self.get_shop_items()
        if item_name not in items:
            return "没有这个物品"

        # 检查背包中是否有足够的物品
        inventory = player.inventory  # 直接使用列表，不需要json.loads
        item_count = inventory.count(item_name)
        if item_count < amount:
            return f"背包中只有 {item_count} 个 {item_name}"

        # 获取物品类型和效果
        item = items[item_name]

        # 判断物品类型
        if item.get('type') != 'consumable':
            return "该物品不能直接使用"

        # 计算恢复效果
        current_hp = int(player.hp)
        max_hp = int(player.max_hp)
        heal_amount = int(item.get('hp', 0)) * amount

        # 计算新的生命值
        new_hp = min(current_hp + heal_amount, max_hp)

        # 从背包中移除物品
        for _ in range(amount):
            inventory.remove(item_name)

        # 添加物品使用冷却时间
        current_time = int(time.time())
        try:
            last_use = player.last_item_use
        except AttributeError:
            # 如果属性不存在，则默认为0
            last_use = 0

        if current_time - int(last_use) < 5:  # 5秒冷却时间
            return f"物品使用太频繁，请等待{5 - (current_time - int(last_use))}秒"

        # 更新玩家数据时添加使用时间
        updates = {
            'inventory': json.dumps(inventory),
            'hp': str(new_hp),
            'last_item_use': str(current_time)
        }

        # 如果玩家数据中没有last_item_use字段，确保它被添加到标准字段中
        if hasattr(player, 'standard_fields') and player.standard_fields and 'last_item_use' not in player.standard_fields:
            player.standard_fields.append('last_item_use')

        player.update_data(updates)

        return f"使用 {amount} 个 {item_name}，恢复 {new_hp - current_hp} 点生命值！\n当前生命值: {new_hp}/{max_hp}"

    def get_player_status(self, user_id):
        """获取玩家状态"""
        player = self.get_player(user_id)
        if not player:
            return "您还没注册,请先注册 "

        # 获取物品信息
        items_info = self.item_system.get_all_items()

        # 使用Player类的get_player_status方法
        return player.get_player_status(items_info)

    def daily_checkin(self, user_id):
        """每日签到"""
        try:
            logger.info(f"用户 {user_id} 尝试进行每日签到")
            player = self.get_player(user_id)
            if not player:
                logger.warning(f"用户 {user_id} 未注册，无法签到")
                return "您还没注册,请先注册 "

            today = datetime.datetime.now().strftime('%Y-%m-%d')
            logger.info(f"当前日期: {today}")

            # 检查签到状态
            if player.last_checkin == today:
                logger.info(f"用户 {user_id} 今天已经签到过了")
                return "您今天已经签到过了"

            # 计算奖励
            reward = 2000  # 签到奖励2000金币
            exp_reward = 100  # 签到奖励100经验
            logger.info(f"用户 {user_id} 签到奖励: {reward}金币, {exp_reward}经验")

            # 更新数据
            updates = {
                'gold': player.gold + reward,
                'exp': player.exp + exp_reward,
                'last_checkin': today
            }

            self._update_player_data(user_id, updates)
            logger.info(f"用户 {user_id} 数据更新成功: {updates}")

            return f"签到成功 获得{reward}金币，经验{exp_reward}，当前金币: {player.gold + reward}"

        except Exception as e:
            logger.error(f"用户 {user_id} 签到出错: {e}")
            return f"签到失败: {str(e)}"

    def get_shop_items(self) -> dict:
        """获取商店物品列表"""
        return self.item_system.get_shop_items()

    def give_item(self, user_id, content, msg: ChatMessage):
        # 解析命令参数
        parts = content.split()
        if len(parts) < 4:
            return "格式错误！请使用: 赠送 @用户 物品名 数量"

        # 获取被赠送者ID
        if not msg.is_group:
            return "只能在群聊中使用赠送功能"

        target_id = None
        # 解析@后面的用户名
        for part in parts:
            if part.startswith('@'):
                target_name = part[1:]  # 去掉@符号
                # 遍历players.csv查找匹配的用户
                with open(self.player_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row['nickname'] == target_name:
                            target_id = row['user_id']
                            break
                break  # 找到第一个@用户后就退出

        if not target_id:
            return "无法找到目标用户，请确保该用户已注册游戏"

        # 从消息内容中提取物品名和数量
        # 跳过第一个词"赠送"和@用户名
        remaining_parts = [p for p in parts[1:] if not p.startswith('@')]
        if len(remaining_parts) < 2:
            return "请指定物品名称和数量"

        item_name = remaining_parts[0]
        try:
            amount = int(remaining_parts[1])
            if amount <= 0:
                return "赠送数量必须大于0"
        except (IndexError, ValueError):
            return "请正确指定赠送数量"

        # 检查双方是否都已注册
        sender = self.get_player(user_id)
        if not sender:
            return "您还没注册,请先注册"

        receiver = self.get_player(target_id)
        if not receiver:
            return "对方还没有注册游戏"

        # 检查发送者是否拥有足够的物品
        sender_inventory = sender.inventory
        equipped_count = 0

        # 检查是否是装备中的物品
        if item_name == sender.equipped_weapon or item_name == sender.equipped_armor:
            equipped_count = 1

        # 计算可赠送数量（排除装备的物品）
        available_count = sender_inventory.count(item_name) - equipped_count

        if available_count < amount:
            if equipped_count > 0:
                return f"背包中只有 {available_count} 个未装备的 {item_name}，无法赠送 {amount} 个"
            else:
                return f"背包中只有 {available_count} 个 {item_name}"

        # 更新双方的背包
        for _ in range(amount):
            sender_inventory.remove(item_name)

        receiver_inventory = receiver.inventory
        receiver_inventory.extend([item_name] * amount)

        # 保存更新
        self._update_player_data(user_id, {
            'inventory': sender_inventory
        })
        self._update_player_data(target_id, {
            'inventory': receiver_inventory
        })

        return f"成功将 {amount} 个 {item_name} 赠送给了 {receiver.nickname}"

    def show_leaderboard(self, user_id, content):
        """显示排行榜"""
        try:
            # 默认显示金币排行
            board_type = "金币"
            if content and len(content.split()) > 1:
                board_type = content.split()[1]

            if board_type not in ["金币", "等级"]:
                return "目前支持的排行榜类型：金币、等级"

            # 读取所有玩家数据
            players = []
            with open(self.player_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                players = list(reader)

            if not players:
                return "暂无玩家数据"

            # 安全的数值转换函数
            def safe_int(value, default=0):
                try:
                    # 先转换为浮点数，再转换为整数
                    return int(float(str(value).replace(',', '')))
                except (ValueError, TypeError):
                    return default

            # 根据类型排序
            if board_type == "金币":
                players.sort(key=lambda x: safe_int(x.get('gold', 0)), reverse=True)
                title = "金币排行榜"
                value_key = 'gold'
                suffix = "金币"
            else:  # 等级排行榜
                # 使用元组排序，先按等级后按经验
                players.sort(
                    key=lambda x: (
                        safe_int(x.get('level', 1)),
                        safe_int(x.get('exp', 0))
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
                value = safe_int(player[value_key])

                # 为等级排行榜添加经验值显示
                exp_info = f" (经验: {safe_int(player.get('exp', '0'))})" if board_type == "等级" else ""

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
                    exp_info = f" (经验: {safe_int(current_player.get('exp', '0'))})" if board_type == "等级" else ""
                    result += f"你的排名: {current_rank}. {current_player['nickname']}: {value}{suffix}{exp_info}"

            return result

        except Exception as e:
            logger.error(f"显示排行榜出错: {e}")
            return "显示排行榜时发生错误"

    def propose_marriage(self, user_id, content, msg: ChatMessage):
        """求婚"""
        if not msg.is_group:
            return "只能在群聊中使用求婚功能"

        # 获取求婚者信息
        proposer = self.get_player(user_id)
        if not proposer:
            return "您还没有注册游戏"

        # 解析命令参数
        parts = content.split()
        logger.info(f"求婚命令参数: {parts}")
        if len(parts) < 2 or not parts[1].startswith('@'):
            return "请使用正确的格式：求婚 @用户名"

        target_name = parts[1][1:]  # 去掉@符号
        # 根据昵称获取玩家
        target = Player.get_player_by_nickname(target_name, self.player_file)
        if not target:
            return "找不到目标玩家，请确保输入了正确的用户名"

        if target.user_id == user_id:  # 使用user_id比较
            return "不能向自己求婚"

        # 检查是否已经是配偶
        proposer_spouses = proposer.spouse.split(',') if proposer.spouse else []
        if target.user_id in [s for s in proposer_spouses if s]:
            return "你们已经是夫妻了"

        if target.marriage_proposal:
            return "对方已经有一个待处理的求婚请求"

        # 更新目标玩家的求婚请求，使用求婚者的user_id
        self._update_player_data(target.user_id, {  # 修改：使用target.user_id而不是target.nickname
            'marriage_proposal': user_id  # 存储求婚者的user_id
        })

        return f"您向 {target_name} 发起了求婚请求，等待对方回应"

    def accept_marriage(self, user_id):
        """同意求婚"""
        player = self.get_player(user_id)
        if not player:
            return "您还没有注册游戏"

        proposal = player.marriage_proposal
        if not proposal:
            return "您没有待处理的求婚请求"

        # 使用昵称获取求婚者信息
        proposer = self.get_player(proposal)
        if not proposer:
            # 清除无效的求婚请求
            self._update_player_data(user_id, {
                'marriage_proposal': ''
            })
            return "求婚者信息不存在或已注销账号"

        # 获取现有配偶列表
        current_spouses = player.spouse.split(',') if player.spouse else []
        proposer_spouses = proposer.spouse.split(',') if proposer.spouse else []

        # 过滤掉空字符串
        current_spouses = [s for s in current_spouses if s]
        proposer_spouses = [s for s in proposer_spouses if s]

        # 添加新配偶
        current_spouses.append(proposer.nickname)
        proposer_spouses.append(player.nickname)

        # 更新双方的婚姻状态，使用user_id而不是nickname
        self._update_player_data(user_id, {
            'spouse': ','.join(current_spouses),
            'marriage_proposal': ''
        })
        self._update_player_data(proposer.user_id, {
            'spouse': ','.join(proposer_spouses)
        })

        return f"恭喜！您接受了 {proposer.nickname} 的求婚！现在你们是夫妻了！"

    def reject_marriage(self, user_id):
        """拒绝求婚"""
        player = self.get_player(user_id)
        if not player:
            return "您还没有注册游戏"

        proposal = player.marriage_proposal
        if not proposal:
            return "您没有待处理的求婚请求"

        # 清除求婚请求
        self._update_player_data(user_id, {
            'marriage_proposal': ''
        })

        return f"您拒绝了 {proposal} 的求婚请求"

    def divorce(self, user_id):
        """离婚"""
        player = self.get_player(user_id)
        if not player:
            return "您还没有注册游戏"

        # 获取所有配偶
        spouses = player.spouse.split(',') if player.spouse else []
        if not spouses:
            return "您还没有结婚"

        # 解除与所有配偶的婚姻关系
        for spouse_name in spouses:
            if spouse_name:
                spouse = self.get_player(spouse_name)
                if spouse:
                    # 从配偶的婚姻列表中移除当前玩家
                    spouse_list = spouse.spouse.split(',')
                    spouse_list = [s for s in spouse_list if s and s != player.nickname]
                    self._update_player_data(spouse_name, {
                        'spouse': ','.join(spouse_list)
                    })

        # 清空玩家的婚姻状态
        self._update_player_data(user_id, {
            'spouse': ''
        })

        return f"您已经与所有配偶离婚"

    def pvp_combat(self, player_1: Player, player_2: Player) -> str:
        """PVP战斗"""
        # 攻击玩家属性
        player_1_level = player_1.level
        player_1_hp = int(player_1.hp)
        player_1_max_hp = int(player_1.max_hp)
        player_1_attack = int(player_1.attack)
        player_1_defense = int(player_1.defense)
        player_1_name = player_1.nickname

        # 目标玩家属性
        player_2_level = player_2.level
        player_2_hp = int(player_2.hp)
        player_2_max_hp = int(player_2.max_hp)
        player_2_attack = int(player_2.attack)
        player_2_defense = int(player_2.defense)
        player_2_name = player_2.nickname

        # 更新战斗日志显示
        battle_log = [
            "同意挑战！\n⚔️ PVP战斗开始 ⚔️\n",
            f"[{player_1_name}] Lv.{player_1_level}\n❤️[{player_1_hp/player_1_max_hp}]\n⚔️[{player_1_attack}]\n🛡️[{str(player_1_defense)}]",
            f"VS\n",
            f"[{player_2_name}] Lv.{player_2_level}\n❤️[{player_2_hp/player_2_max_hp}]\n⚔️[{player_2_attack}]\n🛡️[{str(player_2_defense)}]"
        ]

        # 战斗逻辑
        round_num = 1
        while player_1_hp > 0 and player_2_hp > 0:

            # 减伤率为防御值的10%，最高不超过80%
            player_2_damage_reduction = min(player_2_defense/1000, 0.8)
            player_1_damage = int(player_1_attack * (1- player_2_damage_reduction))

            # 伤害修正：确保减伤后伤害至少为1
            player_1_damage = max(1, player_1_damage)

            player_1_explain_str = ""

            # 应用随机因素
            rand_val = random.random()
            if rand_val < 0.2:
                # 暴击
                player_1_final_damage = int(player_1_damage * random.uniform(1.5, 1.8))
                player_1_explain_str = "💥暴击！"
            elif rand_val < 0.2:
                # 失手
                player_1_final_damage = max(1, int(player_1_damage * random.uniform(0.5, 0.7)))
                player_1_explain_str = "🤦‍♂️失手了！"
            else:
                # 正常命中
                player_1_final_damage = int(player_1_damage)

            # 确保最终伤害至少为1点
            player_1_final_damage = max(1, player_1_final_damage)

            # 减少目标玩家血量
            player_2_hp -= player_1_final_damage

            # 减伤率为防御值的10%，最高不超过80%
            player_1_damage_reduction = min(player_1_defense/1000, 0.8)
            player_2_damage = int(player_2_attack * (1- player_1_damage_reduction))

            # 伤害修正：确保减伤后伤害至少为1
            player_2_damage = max(1, player_2_damage)

            player_2_explain_str = ""

            # 应用随机因素
            rand_val = random.random()
            if rand_val < 0.2:
                # 暴击
                player_2_final_damage = int(player_2_damage * random.uniform(1.5, 1.8))
                player_2_explain_str = "💥暴击！"
            elif rand_val < 0.2:
                # 失手
                player_2_final_damage = max(1, int(player_2_damage * random.uniform(0.5, 0.7)))
                player_2_explain_str = "🤦‍♂️失手了！"
            else:
                # 正常命中
                player_2_final_damage = int(player_2_damage)

            # 确保最终伤害至少为1点
            player_2_final_damage = max(1, player_2_final_damage)

            # 减少攻击玩家血量
            player_1_hp -= player_2_final_damage

            # 记录战斗日志（前4回合）
            if round_num <= 4:
                battle_log.append(f"\n第{round_num}回合")
                battle_log.append(f"{player_1_explain_str}{player_1_name}对{player_2_name}造成 {player_1_final_damage} 点伤害")
                battle_log.append(f"{player_2_explain_str}{player_2_name}对{player_1_name}造成 {player_2_final_damage} 点伤害")

            round_num += 1
            if round_num > 10:  # 限制最大回合数
                break

        # 计算惩罚金币比例(回合数越多惩罚越少)
        penalty_rate = max(0.1, 0.3 - (round_num - 1) * 0.05)  # 每回合减少5%,最低10%
        battle_log.append("\n战斗结果:")

        # 直接使用inventory列表
        player_1_items = None
        player_2_items = None
        if player_1.inventory:
            player_1_items = player_1.inventory
        if player_2.inventory:
            player_2_items = player_2.inventory

        if player_1_hp <= 0:
            # 目标玩家胜利
            # 扣除金币
            player_1_gold = int(player_1.gold)
            penalty_gold = int(player_1_gold * penalty_rate)
            new_player_1_gold = player_1_gold - penalty_gold
            new_player_2_gold = int(player_2.gold) + penalty_gold

            # 随机赔付一件物品给对方
            lost_item = None
            if player_1_items:
                lost_item = random.choice(player_1_items)
                player_1_items.remove(lost_item)
                player_2_items.extend([lost_item] * 1)

            # 更新数据
            self._update_player_data(player_1.user_id, {
                'hp': '0',
                'gold': str(new_player_1_gold),
                'inventory': player_1_items,  # _update_player_data会处理列表到JSON的转换
            })
            self._update_player_data(player_2.user_id, {  # 这里改为使用user_id
                'hp': str(player_2_hp),
                'gold': str(new_player_2_gold),
                'inventory': player_2_items,  # _update_player_data会处理列表到JSON的转换
            })

            result = f"{player_2.nickname} 获胜!\n{player_1.nickname} 赔偿 {penalty_gold} 金币"
            if lost_item:
                result += f"\n{player_1_name} 的 {lost_item} 被 {player_2_name} 夺走！"

        else:
            # 攻击玩家胜利
            # 扣除金币
            player_2_gold = int(player_2.gold)
            penalty_gold = int(player_2_gold * penalty_rate)
            new_player_2_gold = player_2_gold - penalty_gold
            new_player_1_gold = int(player_1.gold) + penalty_gold

            # 随机赔付一件物品给对方
            player_2_items = player_2.inventory  # 直接使用inventory列表
            lost_item = None
            if player_2_items:
                lost_item = random.choice(player_2_items)
                player_2_items.remove(lost_item)
                player_1_items.extend([lost_item] * 1)

            # 更新数据
            self._update_player_data(player_2.user_id, {  # 使用player_2_id而不是nickname
                'hp': '0',
                'gold': str(new_player_2_gold),
                'inventory': player_2_items,  # _update_player_data会处理列表到JSON的转换
            })

            self._update_player_data(player_1.user_id, {
                'hp': str(player_1_hp),
                'gold': str(new_player_1_gold),
                'inventory': player_1_items
            })

            result = f"{player_1_name} 获胜!\n{player_2.nickname} 赔偿 {penalty_gold} 金币"
            if lost_item:
                result += f"\n{player_2_name} 的 {lost_item} 被 {player_1_name} 夺走！"

        battle_log.append(result)
        return "\n".join(battle_log)

    def attack_player(self, user_id, content, msg: ChatMessage):
        """ PVP 挑战其他玩家 """
        if not msg.is_group:
            return "只能在群聊中使用攻击功能"

        # 解析命令参数
        parts = content.split()
        if len(parts) < 2 or not parts[1].startswith('@'):
            return "请使用正确的格式：攻击 @用户名"

        target_name = parts[1][1:]  # 去掉@符号
        # 根据昵称获取玩家
        target = Player.get_player_by_nickname(target_name, self.player_file)
        if not target:
            return "找不到目标玩家，请确保输入了正确的用户名"

        # 获取攻击者信息
        attacker = self.get_player(user_id)
        if not attacker:
            return "您还没有注册游戏"

        # 不能攻击自己
        if attacker.nickname == target.nickname:
            return "我知道你很勇，但是自己打自己这种事未免过于抽象。。。"

        if attacker.hp == 0:
            return "你的生命值为0，即便如此，你也想要起舞吗？"

        if target.hp == 0:
            return "对方生命值为0，做个人吧，孩子！"

        if target.challenge_proposal:
            return "对方已经有一个待处理的挑战请求"

        # 更新目标玩家的挑战请求，使用挑战者的user_id
        self._update_player_data(target.user_id, {
            'challenge_proposal': user_id
        })

        return f"您向 {target_name} 发起了挑战请求，等待对方回应"

    def refuse_challenge(self, user_id):
        """拒绝挑战"""
        player = self.get_player(user_id)
        if not player:
            return "您还没有注册游戏"

        proposal = player.challenge_proposal
        if not proposal:
            return "虽然但是，并没有人挑战你啊，兄嘚~"

        # 使用昵称获取挑战者信息
        proposer = self.get_player(proposal)
        if not proposer:
            # 清除无效的挑战请求
            self._update_player_data(user_id, {
                'challenge_proposal': ''
            })
            return "挑战者信息不存在或已注销账号"

        # 更新自身的挑战者
        self._update_player_data(user_id, {
            'challenge_proposal': ''
        })

        return f"您拒绝了 {proposal} 的挑战请求"

    def accept_challenge(self, user_id):
        """同意挑战"""
        player = self.get_player(user_id)
        if not player:
            return "您还没有注册游戏"

        proposal = player.challenge_proposal
        if not proposal:
            return "您没有待处理的挑战请求"

        # 使用昵称获取挑战者信息
        proposer = self.get_player(proposal)
        if not proposer:
            # 清除无效的挑战请求
            self._update_player_data(user_id, {
                'challenge_proposal': ''
            })
            return "挑战者信息不存在或已注销账号"

        # 更新自身的挑战者
        self._update_player_data(user_id, {
            'challenge_proposal': ''
        })

        # 开始pvp战斗
        return self.pvp_combat(proposer, player)

    def _update_player_data(self, user_id, updates: dict):
        """更新玩家数据

        Args:
            user_id: 玩家ID
            updates: 需要更新的字段和值的字典
        """
        try:
            # 确保使用user_id查找玩家
            player = self.get_player(str(user_id))
            if not player:
                logger.error(f"找不到玩家: {user_id}")
                raise ValueError(f"找不到玩家: {user_id}")

            # 设置必要的文件信息
            player.player_file = self.player_file
            player.standard_fields = self.STANDARD_FIELDS

            # 数据类型转换和验证
            for key, value in updates.items():
                if isinstance(value, (int, float)):
                    updates[key] = str(value)
                elif isinstance(value, (list, dict)):
                    updates[key] = json.dumps(value)

            # 使用Player类的update_data方法
            player.update_data(updates)

        except Exception as e:
            logger.error(f"更新玩家数据出错: {e}")
            raise

    def show_inventory(self, user_id):
        player = self.get_player(user_id)
        if not player:
            return "您还没注册..."

        items_info = self.item_system.get_all_items()
        return player.get_inventory_display(items_info)

    def equip_item(self, user_id: str, item_name: str) -> str:
        """装备物品的包装方法"""
        return self.equipment_system.equip_item(user_id, item_name)

    def unequip_item(self, user_id: str, item_type: str) -> str:
        """卸下装备的包装方法"""
        return self.equipment_system.unequip_item(user_id, item_type)

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

            # 调用装备系统的装备方法
            return self.equipment_system.equip_item(user_id, item_name)

        except Exception as e:
            logger.error(f"装备物品出错: {e}")
            return "装备物品时发生错误"

    def _restore_game_state(self):
        """从进程锁文件恢复游戏状态"""
        try:
            if os.path.exists(self.process_lock_file):
                with open(self.process_lock_file, 'r') as f:
                    data = json.load(f)
                    self.game_status = data.get('game_status', True)
                    self.scheduled_tasks = data.get('scheduled_tasks', {})

                    # 恢复定时任务
                    current_time = time.time()
                    for task_id, task in list(self.scheduled_tasks.items()):
                        if task['time'] <= current_time:
                            # 执行过期的定时任务
                            if task['action'] == 'start':
                                self.game_status = True
                            elif task['action'] == 'stop':
                                self.game_status = False
                            # 删除已执行的任务
                            del self.scheduled_tasks[task_id]

                    # 保存更新后的状态
                    self._save_game_state()
        except Exception as e:
            logger.error(f"恢复游戏状态出错: {e}")
            self.game_status = True
            self.scheduled_tasks = {}

    def _save_game_state(self):
        """保存游戏状态到进程锁文件"""
        try:
            # 清理任务ID中的receiver信息
            cleaned_tasks = {}
            for task_id, task in self.scheduled_tasks.items():
                clean_task_id = task_id.split(',')[0]
                if clean_task_id not in cleaned_tasks:  # 避免重复任务
                    cleaned_tasks[clean_task_id] = task

            self.scheduled_tasks = cleaned_tasks

            with open(self.process_lock_file, 'w') as f:
                json.dump({
                    'game_status': self.game_status,
                    'scheduled_tasks': self.scheduled_tasks
                }, f)
        except Exception as e:
            logger.error(f"保存游戏状态出错: {e}")

    def toggle_game_system(self, user_id, action='toggle'):
        """切换游戏系统状态"""
        try:
            player = self.get_player(user_id)
            if not player:
                # 检查是否是默认管理员
                config_file = os.path.join(self.data_dir, "config.json")
                if os.path.exists(config_file):
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        if user_id not in config.get("admins", []):
                            return "您还没有注册游戏"
                else:
                    return "您还没有注册游戏"
            elif not self._is_admin(player):
                return "只有管理员才能操作游戏系统开关"

            if action == 'toggle':
                self.game_status = not self.game_status
            elif action == 'start':
                self.game_status = True
            elif action == 'stop':
                self.game_status = False

            self._save_game_state()
            return f"游戏系统已{'开启' if self.game_status else '关闭'}"
        except Exception as e:
            logger.error(f"切换游戏系统状态出错: {e}")
            return "操作失败，请检查系统状态"

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
            # 获取玩家对象
            player = self.get_player(user_id)
            if not player:
                # 检查是否是默认管理员
                config_file = os.path.join(self.data_dir, "config.json")
                if os.path.exists(config_file):
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        if user_id not in config.get("admins", []):
                            return "您还没有注册游戏"
                else:
                    return "您还没有注册游戏"
            elif not self._is_admin(player):
                return "只有管理员才能进行充值操作！"

            target_name, amount = self.extract_username_and_amount(content)

            if target_name and amount:
                logger.info(f"充值目标：{target_name}，金额：{amount}")
                # 根据昵称获取玩家
                target = Player.get_player_by_nickname(target_name, self.player_file)
                if not target:
                    return "找不到目标玩家，请确保输入了正确的用户名"
                else:
                    # 执行充值操作
                    target.gold = int(target.gold) + amount
                    # 更新目标玩家的金币数据
                    self._update_player_data(target.user_id, {
                        'gold': str(target.gold)
                    })
                    return f"已为 {target.nickname} 用户充值 {amount} 金币。"
            else:
                return "请使用正确的格式：充值 @用户名 金额"
        except Exception as e:
            logger.error(f"充值出错: {e}")
            return "充值失败，请联系管理员。"

    def schedule_game_system(self, user_id, content):
        """设置定时开关机"""
        player = self.get_player(user_id)
        if not player:
            return "您还没有注册游戏"

        # 检查是否是管理员
        if not self._is_admin(player):
            return "只有管理员才能设置定时任务"

        try:
            # 解析命令格式: 定时 开机/关机 HH:MM [每天]
            parts = content.split()
            if len(parts) < 3:
                return "格式错误！请使用: 定时 开机/关机 HH:MM [每天]"

            action = '开机' if parts[1] == '开机' else '关机' if parts[1] == '关机' else None
            if not action:
                return "请指定正确的操作(开机/关机)"

            # 解析时间
            try:
                hour, minute = map(int, parts[2].split(':'))
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    raise ValueError
            except ValueError:
                return "请输入正确的时间格式(HH:MM)"

            # 检查是否是每天执行
            is_daily = len(parts) > 3 and parts[3] == '每天'

            # 计算执行时间
            now = datetime.datetime.now()
            target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if not is_daily and target_time <= now:
                target_time += datetime.timedelta(days=1)

            # 生成任务ID，每天任务添加daily标记
            task_id = f"{'daily' if is_daily else ''}{action}_{target_time.strftime('%H%M')}"

            # 添加定时任务
            self.scheduled_tasks[task_id] = {
                'action': 'start' if action == '开机' else 'stop',
                'time': target_time.timestamp(),
                'is_daily': is_daily
            }

            self._save_game_state()
            daily_text = "每天 " if is_daily else ""
            return f"已设置{daily_text}{action}定时任务: {target_time.strftime('%H:%M')}"

        except Exception as e:
            logger.error(f"设置定时任务出错: {e}")
            return "设置定时任务失败"

    def _is_admin(self, player):
        """检查玩家是否是管理员"""
        try:
            config_file = os.path.join(self.data_dir, "config.json")
            if not os.path.exists(config_file):
                # 创建默认配置文件
                default_config = {
                    "admins": ["xxx"]  # 默认管理员列表
                }
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, ensure_ascii=False, indent=2)

            # 读取配置文件
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            return player.nickname in config.get("admins", [])
        except Exception as e:
            logger.error(f"读取管理员配置出错: {e}")
            return False

    def show_scheduled_tasks(self, user_id):
        """显示所有定时任务"""
        player = self.get_player(user_id)
        if not player:
            return "您还没有注册游戏"

        if not self._is_admin(player):
            return "只有管理员才能查看定时任务"

        if not self.scheduled_tasks:
            return "当前没有定时任务"

        # 用于去重和整理任务的字典
        unique_tasks = {}

        result = "定时任务列表:\n" + "-" * 20 + "\n"
        for task_id, task in self.scheduled_tasks.items():
            # 清理掉可能包含的receiver信息
            clean_task_id = task_id.split(',')[0]

            action = "开机" if task['action'] == 'start' else "关机"
            time_str = datetime.datetime.fromtimestamp(task['time']).strftime('%H:%M')

            # 使用间和动作作为唯一键
            task_key = f"{time_str}_{action}"

            if task.get('is_daily'):
                task_desc = f"每天 {time_str}"
            else:
                task_desc = datetime.datetime.fromtimestamp(task['time']).strftime('%Y-%m-%d %H:%M')

            unique_tasks[task_key] = f"{action}: {task_desc}"

        # 按时间排序显示任务
        for task_desc in sorted(unique_tasks.values()):
            result += f"{task_desc}\n"

        return result

    def cancel_scheduled_task(self, user_id, content):
        """取消定时任务"""
        player = self.get_player(user_id)
        if not player:
            return "您还没有注册游戏"

        if not self._is_admin(player):
            return "只有管理员才能取消定时任务"

        try:
            # 解析命令格式: 取消定时 开机/关机 HH:MM
            parts = content.split()
            if len(parts) != 3:
                return "格式错误！请使用: 取消定时 开机/关机 HH:MM"

            action = '开机' if parts[1] == '开机' else '关机' if parts[1] == '关机' else None
            if not action:
                return "请指定正确的操作(开机/���机)"

            # 解析时间
            try:
                hour, minute = map(int, parts[2].split(':'))
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    raise ValueError
            except ValueError:
                return "请输入正确的时间格式(HH:MM)"

            # 生成任务ID格式
            now = datetime.datetime.now()
            target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if target_time <= now:
                target_time += datetime.timedelta(days=1)

            task_id = f"{action}_{target_time.strftime('%Y%m%d%H%M')}"

            # 检查并删除任务
            if task_id in self.scheduled_tasks:
                del self.scheduled_tasks[task_id]
                self._save_game_state()
                return f"已取消{action}定时任务: {target_time.strftime('%Y-%m-%d %H:%M')}"
            else:
                return f"未找到指定的定时任务"

        except Exception as e:
            logger.error(f"取消定时任务出错: {e}")
            return "取消定时任务失败"

    def _check_scheduled_tasks(self):
        """检查并执行到期的定时任务"""
        try:
            current_time = time.time()
            tasks_to_remove = []

            for task_id, task in self.scheduled_tasks.items():
                if task['time'] <= current_time:
                    # 执行定时任务
                    if task['action'] == 'start':
                        self.game_status = True
                        logger.info(f"定时任务执行：开机 - {datetime.datetime.fromtimestamp(task['time']).strftime('%Y-%m-%d %H:%M')}")
                    elif task['action'] == 'stop':
                        self.game_status = False
                        logger.info(f"定时任务执行：关机 - {datetime.datetime.fromtimestamp(task['time']).strftime('%Y-%m-%d %H:%M')}")

                    if task.get('is_daily'):
                        # 更新每日任务的下一次执行时间
                        next_time = datetime.datetime.fromtimestamp(task['time']) + datetime.timedelta(days=1)
                        task['time'] = next_time.timestamp()
                    else:
                        # 将非每日任务添加到待删除列表
                        tasks_to_remove.append(task_id)

            # 删除已执行的非每日任务
            for task_id in tasks_to_remove:
                del self.scheduled_tasks[task_id]

            # 如果有任务被执行或更新，保存状态
            if tasks_to_remove or any(task.get('is_daily') for task in self.scheduled_tasks.values()):
                self._save_game_state()

        except Exception as e:
            logger.error(f"检查定时任务出错: {e}")

    def clear_scheduled_tasks(self, user_id):
        """清空所有定时任务"""
        player = self.get_player(user_id)
        if not player:
            return "您还没有注册游戏"

        if not self._is_admin(player):
            return "只有管理员才能清空定时任务"

        try:
            task_count = len(self.scheduled_tasks)
            if task_count == 0:
                return "当前没有定时任务"

            self.scheduled_tasks.clear()
            self._save_game_state()
            return f"已清空 {task_count} 个定时任务"

        except Exception as e:
            logger.error(f"清空定时任务出错: {e}")
            return "清空定时任务失败"

    def delete_reminder(self, user_id):
        """删除提醒"""
        player = self.get_player(user_id)
        if not player:
            return "您还没有注册游戏"

        if user_id not in self.reminders:
            return "您没有设置任何提醒"

        # 删除提醒
        del self.reminders[user_id]
        self._save_reminders()

        return "提醒已删除"

    def buy_property(self, user_id):
        """购买当前位置的地块"""
        player = self.get_player(user_id)
        if not player:
            return "您还没有注册游戏"

        # 获取玩家当前位置
        current_position = int(getattr(player, 'position', 0))
        block = self.monopoly.get_block_info(current_position)

        # 检查是否是可购买的地块
        purchasable_types = ['空地', '直辖市', '省会', '地级市', '县城', '乡村']
        if block['type'] not in purchasable_types:
            return "当前位置不是可购买的地块"

        # 检查是否已被购买
        if self.monopoly.get_property_owner(current_position):
            return "这块地已经被购买了"

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
            return f"购买这块地需要 {price} 金币，您的金币不足"

        # 扣除金币并购买地块
        new_gold = int(player.gold) - price
        if self.monopoly.buy_property(current_position, user_id, price):
            self._update_player_data(user_id, {'gold': str(new_gold)})
            return f"""🎉 成功购买地块！
位置: {block['name']}
类型: {block['type']}
花费: {price} 金币
当前金币: {new_gold}"""
        else:
            return "购买失败，请稍后再试"

    def upgrade_property(self, user_id):
        """升级当前位置的地块"""
        player = self.get_player(user_id)
        if not player:
            return "您还没有注册游戏"

        # 获取玩家当前位置
        current_position = int(getattr(player, 'position', 0))

        # 检查是否是玩家的地产
        property_data = self.monopoly.properties_data.get(str(current_position))
        if not property_data or property_data.get('owner') != user_id:
            return "这不是您的地产"

        # 检查是否达到最高等级
        current_level = property_data.get('level', 1)
        if current_level >= 3:
            return "地产已达到最高等级"

        # 计算升级费用
        base_price = property_data.get('price', 500)
        upgrade_cost = int(base_price * 0.5 * current_level)

        # 检查玩家金币是否足够
        if int(player.gold) < upgrade_cost:
            return f"升级需要 {upgrade_cost} 金币，您的金币不足"

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
            return "升级失败，请稍后再试"

    def show_properties(self, user_id):
        """显示玩家的地产"""
        player = self.get_player(user_id)
        if not player:
            return "您还没有注册游戏"

        properties = self.monopoly.get_player_properties(user_id)
        if not properties:
            return "您还没有购买任何地产"

        result = ["您的地产列表："]
        for pos in properties:
            prop_info = self.monopoly.get_property_info(pos)
            if prop_info:
                result.append(f"\n{prop_info['name']} ({prop_info['region']})")
                result.append(f"等级: {prop_info['level']}")
                result.append(f"价值: {prop_info['price']} 金币")
                result.append(f"当前租金: {prop_info['rent']} 金币")

        return "\n".join(result)

    def show_map(self, user_id):
        """显示地图状态"""
        player = self.get_player(user_id)
        if not player:
            return "您还没有注册游戏"

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
                symbols = ["🏠", "��️", "🏰"]  # 不同等级的显示
                symbol = symbols[level - 1]
            else:
                # 根据地块类型显示不同符号
                type_symbols = {
                    "直辖市": "🌆",
                    "省会": "🏢",
                    "地级市": "🏣",
                    "县城": "🏘️",
                    "乡村": "🏡",
                    "空地": "⬜"
                }
                symbol = type_symbols.get(block['type'], "⬜")

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
            return "您还没有注册游戏"

        # 定义下注类型及对应的赔率
        odds = {
            '大': 1,       # 赔率 1:1
            '小': 1,       # 赔率 1:1
            '豹子': 30,    # 赔率 30:1
            '顺子': 5      # 赔率 5:1
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
        pattern = r'^下注\s+(大|小|豹子|顺子)\s+(\d+)$'
        match = re.match(pattern, bet_str.strip())

        if not match:
            return "输入格式不正确。正确格式如：下注 大 5000"

        bet_type, amount_str = match.groups()
        amount = int(amount_str)

        # 验证下注金额是否为正整数
        if amount <= 0:
            return "下注金额必须为正整数。"

        # 判断玩家本金是否足够下注
        player_gold = int(player.gold)
        if player_gold < amount:
            return f"您的本金不足，无法进行下注。\n您的余额：{player_gold} 金币"

        # 设置随机数种子为当前时间
        current_time = time.time()
        random.seed(current_time)

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
                payout = amount * odds[bet_type]
        elif bet_type == '小':
            if 3 <= total <= 10:
                win = True
                payout = amount * odds[bet_type]
        elif bet_type == '豹子':
            if dice[0] == dice[1] == dice[2]:
                win = True
                payout = amount * odds[bet_type]
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
                payout = amount * odds[bet_type]

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

        result_str = f"━━━━━━━━━━━━━━━\n🎲点数: {dice_faces}\n\n💴下注: {amount}金币\n{'✅ 恭喜您赢得了' if win else '❌ 很遗憾，您输了'} {payout} 金币\n\n(游戏娱乐，切勿当真，热爱生活，远离赌博)\n━━━━━━━━━━━━━━━"

        return result_str
