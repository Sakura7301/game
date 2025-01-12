import csv
import json
from typing import Dict, Any, Optional
from common.log import logger
import os


class Item:
    """物品类,用于管理物品属性和操作"""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.item_file = f"{data_dir}/items.csv"

    def get_all_items(self) -> Dict[str, Dict[str, Any]]:
        """获取所有物品信息"""
        items_info = {}
        try:
            # 读取物品数据
            with open(self.item_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    items_info[row['name']] = row
            return items_info
        except Exception as e:
            logger.error(f"读取物品数据出错: {e}")
            return {}

    def init_default_items(self):
        """初始化默认物品数据"""
        if not os.path.exists(self.item_file):
            with open(self.item_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # 添加价格和稀有度字段
                writer.writerow(['name', 'desc', 'type', 'hp', 'attack', 'defense', 'price', 'rarity'])
                # 写入默认数据
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
                    ['如意金箍棒', '重一万三千五百斤', 'weapon', '0', '100', '0', '10000', '5'],
                    ['破衣烂衫', '你也不想当流浪汉，对吧', 'armor', '10', '0', '1', '100', '1'],
                    ['斗篷', '提供基本保护的斗篷', 'armor', '30', '0', '3', '300', '1'],
                    ['布甲', '简单的布制护甲', 'armor', '50', '0', '5', '500', '1'],
                    ['乌萨奇睡衣', '乌拉呀哈~呀哈乌拉~', 'armor', '70', '0', '7', '700', '1'],
                    ['皮甲', '轻便的皮质护甲', 'armor', '100', '0', '10', '1000', '2'],
                    ['帝骑腰带', '都闪开，我要开始装B了', 'armor', '150', '0', '15', '1500', '2'],
                    ['铁甲', '轻便的皮质护甲', 'armor', '180', '0', '18', '1800', '2'],
                    ['锁子甲', '由链环组成的护甲', 'armor', '250', '0', '25', '2500', '3'],
                    ['精钢甲', '精钢打造的铠甲', 'armor', '300', '0', '30', '3000', '3'],
                    ['秘银铠甲', '帅是一辈子的事', 'armor', '380', '0', '38', '3800', '4'],
                    ['初音未来cos服', '可爱捏~~等等，你刚刚说了你要穿着这玩意去打架，对吧？？？', 'armor', '100', '10', '4', '4000', '4'],
                    ['荆棘铠甲', '你最好别碰我，兄弟，我不开玩笑', 'armor', '400', '15', '40', '4000', '4'],
                    ['龙鳞甲', '龙鳞制成的铠甲', 'armor', '600', '0', '60', '6000', '5'],
                    ['神圣铠甲', '具有神圣力量的铠甲', 'armor', '700', '0', '70', '7000', '6'],
                    ['永恒战甲', '传说中的不朽铠甲', 'armor', '800', '0', '70', '8000', '7'],
                    ['面包', '普普通通的面包，没什么特别的，回复20点生命值', 'consumable', '20', '0', '0', '20', '1'],
                    ['药水', '出门必备的小药水，回复50点生命值', 'consumable', '50', '0', '0', '50', '2'],
                    ['急救包', '出事儿了就得靠它，回复150点生命值', 'consumable', '80', '0', '0', '150', '3'],
                    ['治疗卷轴', '麻瓜总是很难理解卷轴上的符文到底是怎么发挥作用的，回复200点生命值', 'consumable', '100', '0', '0', '200', '4'],
                    ['元素瓶', '不死人的果粒橙', 'consumable', '400', '0', '0', '400', '5'],
                    ['女神的祝福', '来自太阳长女葛温德林的祝福，回复800点生命值', 'consumable', '500', '0', '0', '800', '5'],
                    ['海龙王', '稀有海龙王', 'fish', '0', '0', '0', '4500', '5'],
                    ['绿蠵龟', '我滴龟龟！！！', 'fish', '0', '0', '0', '800', '5'],
                    ['蓝鲸', '布什戈门，你说你用一根破木棍子把这玩意钓上来了？', 'fish', '0', '0', '0', '3000', '5'],
                    ['海鲈', '清淡海鲈', 'fish', '0', '0', '0', '130', '2'],
                    ['鲷鱼', '鲜活鲷鱼', 'fish', '0', '0', '0', '100', '2'],
                    ['带鱼', '长条带鱼', 'fish', '0', '0', '0', '120', '2'],
                    ['虾虎', '活力虾虎', 'fish', '0', '0', '0', '95', '2'],
                    ['翡翠螺', '绿色翡翠躏', 'fish', '0', '0', '0', '75', '2'],
                    ['珍珠螺', '珍珠光泽螺', 'fish', '0', '0', '0', '140', '3'],
                    ['彩色珊瑚鱼', '色彩斑斓珊瑚鱼', 'fish', '0', '0', '0', '500', '4'],
                    ['鲨鱼', '听说鲨鱼的皮肤会用来排泄，所以它的肉肯定不好吃，当然我是猜的。真的，童叟无欺', 'fish', '0', '0', '0', '600', '4'],
                    ['小鱼', '一条小鱼', 'fish', '0', '0', '0', '50', '1'],
                    ['鲫鱼', '普通的鲫鱼', 'fish', '0', '0', '0', '70', '2'],
                    ['鲈鱼', '适合清蒸', 'fish', '0', '0', '0', '100', '2'],
                    ['青鱼', '清爽的青鱼', 'fish', '0', '0', '0', '200', '3'],
                    ['鲍鱼', '优质鲍鱼', 'fish', '0', '0', '0', '800', '4'],
                    ['龙虾', '鲜美多汁', 'fish', '0', '0', '0', '500', '4'],
                    ['海参', '高档海参', 'fish', '0', '0', '0', '2000', '5'],
                    ['海胆', '新鲜海胆', 'fish', '0', '0', '0', '300', '3'],
                    ['海蜇', '清凉海蜇', 'fish', '0', '0', '0', '70', '1'],
                    ['比目鱼', '有谁记得鲁迅小时候的对子：“独角兽，比目鱼”', 'fish', '0', '0', '0', '120', '2'],
                    ['梭子蟹', '活梭子蟹', 'fish', '0', '0', '0', '400', '4'],
                    ['蛏子', '新鲜蛏子', 'fish', '0', '0', '0', '90', '2'],
                    ['虾仁', '细嫩虾仁', 'fish', '0', '0', '0', '50', '1'],
                    ['帝王蟹', '鲜美~~~', 'fish', '0', '0', '0', '900', '4'],
                    ['鳗鱼', '香糯鳗鱼', 'fish', '0', '0', '0', '250', '3'],
                    ['海鳗', '长条海鳗', 'fish', '0', '0', '0', '280', '3'],
                    ['红蟳', '活红蟳', 'fish', '0', '0', '0', '600', '4'],
                    ['毛蟹', '毛茸茸毛蟹', 'fish', '0', '0', '0', '450', '4'],
                    ['石斑鱼', '周星驰的配音(bushi)', 'fish', '0', '0', '0', '320', '4'],
                    ['金枪鱼', '好吃！爱吃！！', 'fish', '0', '0', '0', '450', '4'],
                    ['大比目', '巨型大比目鱼', 'fish', '0', '0', '0', '310', '4'],
                    ['海马', '细长海马', 'fish', '0', '0', '0', '400', '4'],
                    ['海雀', '彩色海雀', 'fish', '0', '0', '0', '160', '3'],
                    ['琵琶虾', '弯曲琵琶虾', 'fish', '0', '0', '0', '130', '3'],
                    ['水母鱼', '透明水母鱼', 'fish', '0', '0', '0', '75', '2'],
                    ['银鲹', '闪亮银鲹(这字儿到底怎么读？)', 'fish', '0', '0', '0', '100', '2'],
                    ['金鲳', '金色鲳鱼', 'fish', '0', '0', '0', '500', '4'],
                    ['带虾', '大号带虾', 'fish', '0', '0', '0', '85', '2'],
                    ['墨鱼', '有话好好说，别喷我一身', 'fish', '0', '0', '0', '500', '3'],
                    ['章鱼', '你老实跟我说，你跟克总什么关系？', 'fish', '0', '0', '0', '400', '3'],
                    ['珍珠贝', '光滑珍珠贝', 'fish', '0', '0', '0', '250', '3'],
                    ['紫菜', '新鲜紫菜', 'fish', '0', '0', '0', '10', '1'],
                    ['海螺', '美丽海螺', 'fish', '0', '0', '0', '40', '1'],
                    ['海胆卵', '珍贵海胆卵', 'fish', '0', '0', '0', '900', '4'],
                    ['海蛇', '活泼海蛇', 'fish', '0', '0', '0', '290', '3'],
                    ['海马草', '特殊海马草', 'fish', '0', '0', '0', '500', '4'],
                    ['红珊瑚', '珊瑚中的红色品种', 'fish', '0', '0', '0', '750', '4'],
                    ['蓝珊瑚', '珊瑚中的蓝色品种', 'fish', '0', '0', '0', '800', '4'],
                    ['绿珊瑚', '珊瑚中的绿色品种', 'fish', '0', '0', '0', '700', '4'],
                    ['木制鱼竿', '众所周知，没有鱼竿你就无法钓鱼', 'fishing_rod', '0', '1', '0', '200', '1'],
                    ['铁制鱼竿', '更好的铁制鱼竿，不容易坏', 'fishing_rod', '0', '2', '0', '500', '2'],
                    ['金制鱼竿', '哇！金色传说！！！', 'fishing_rod', '0', '3', '0', '1000', '3'],
                ]
                writer.writerows(default_items)

    def get_shop_items(self) -> Dict[str, Dict[str, Any]]:
        """获取商店物品信息"""
        items = {}
        try:
            # 读取物品数据
            with open(self.item_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 只返回非鱼类物品
                    if row.get('type') != 'fish':
                        items[row['name']] = row
            return items
        except Exception as e:
            logger.error(f"读取商店物品数据出错: {e}")
            return {}
