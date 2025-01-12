import json
import random
import os
from typing import Dict, List, Optional


class MonopolySystem:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.map_file = os.path.join(data_dir, "map_config.json")
        self.adventure_map_file = os.path.join(data_dir, "adventure_map_config.json")
        self.events_file = os.path.join(data_dir, "events_config.json")
        self.properties_file = os.path.join(data_dir, "properties.json")

        # 初始化地图和事件数据
        self._init_map_config()
        self._init_events_config()
        self._init_properties()

        # 加载数据
        self.map_data = self._load_json(self.map_file)
        self.adventure_map_data = self._load_json(self.adventure_map_file)
        self.events_data = self._load_json(self.events_file)
        self.properties_data = self._load_json(self.properties_file)

    def _init_map_config(self):
        """初始化地图配置"""
        if not os.path.exists(self.map_file):
            default_map = {
                "total_blocks": 50,
                "blocks": {
                    "0": {"type": "起点", "name": "首都北京", "description": "每次经过可获得200金币", "region": "直辖市"},
                    "12": {"type": "直辖市", "name": "上海", "description": "繁华的国际大都市", "region": "直辖市"},
                    "25": {"type": "直辖市", "name": "重庆", "description": "山城魅力", "region": "直辖市"},
                    "37": {"type": "直辖市", "name": "天津", "description": "北方港口城市", "region": "直辖市"},

                    "5": {"type": "省会", "name": "广州", "description": "广东省会", "region": "省会"},
                    "17": {"type": "省会", "name": "成都", "description": "四川省会", "region": "省会"},
                    "30": {"type": "省会", "name": "杭州", "description": "浙江省会", "region": "省会"},
                    "42": {"type": "省会", "name": "南京", "description": "江苏省会", "region": "省会"},
                    "6": {"type": "省会", "name": "武汉", "description": "湖北省会", "region": "省会"},
                    "18": {"type": "省会", "name": "长沙", "description": "湖南省会", "region": "省会"},
                    "31": {"type": "省会", "name": "西安", "description": "陕西省会", "region": "省会"},
                    "43": {"type": "省会", "name": "郑州", "description": "河南省会", "region": "省会"},

                    "7": {"type": "地级市", "name": "苏州", "description": "江苏重要城市", "region": "地级市"},
                    "20": {"type": "地级市", "name": "青岛", "description": "山东重要城市", "region": "地级市"},
                    "32": {"type": "地级市", "name": "厦门", "description": "福建重要城市", "region": "地级市"},
                    "45": {"type": "地级市", "name": "大连", "description": "辽宁重要城市", "region": "地级市"},
                    "8": {"type": "地级市", "name": "宁波", "description": "浙江重要城市", "region": "地级市"},
                    "21": {"type": "地级市", "name": "无锡", "description": "江苏重要城市", "region": "地级市"},
                    "33": {"type": "地级市", "name": "珠海", "description": "广东重要城市", "region": "地级市"},
                    "46": {"type": "地级市", "name": "深圳", "description": "广东重要城市", "region": "地级市"},

                    "2": {"type": "县城", "name": "周庄古镇", "description": "江南水乡", "region": "县城"},
                    "15": {"type": "县城", "name": "凤凰古城", "description": "湘西名城", "region": "县城"},
                    "27": {"type": "县城", "name": "婺源县", "description": "徽派建筑", "region": "县城"},
                    "40": {"type": "县城", "name": "丽江古城", "description": "云南名城", "region": "县城"},
                    "3": {"type": "县城", "name": "乌镇", "description": "浙江古镇", "region": "县城"},
                    "16": {"type": "县城", "name": "平遥古城", "description": "山西古城", "region": "县城"},
                    "28": {"type": "县城", "name": "西塘古镇", "description": "江南古镇", "region": "县城"},
                    "41": {"type": "县城", "name": "阳朔县", "description": "桂林山水", "region": "县城"},

                    "10": {"type": "乡村", "name": "婺源篁岭", "description": "徽州晒秋", "region": "乡村"},
                    "22": {"type": "乡村", "name": "阿坝草原", "description": "四川草原", "region": "乡村"},
                    "35": {"type": "乡村", "name": "婺源晓起", "description": "徽州村落", "region": "乡村"},
                    "47": {"type": "乡村", "name": "云南梯田", "description": "哈尼梯田", "region": "乡村"},
                    "11": {"type": "乡村", "name": "江西武功山", "description": "高山草甸", "region": "乡村"},
                    "23": {"type": "乡村", "name": "新疆喀纳斯", "description": "图瓦人村落", "region": "乡村"},
                    "36": {"type": "乡村", "name": "福建土楼", "description": "客家文化", "region": "乡村"},
                    "48": {"type": "乡村", "name": "西双版纳", "description": "傣族村寨", "region": "乡村"},
                    "9": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},
                    "19": {"type": "机遇", "name": "命运转盘", "description": "触发随机事件", "region": "机遇"},
                    "34": {"type": "机遇", "name": "幸运空间", "description": "触发随机事件", "region": "机遇"},
                },
                "default_block": {"type": "机遇", "name": "命运空间", "description": "触发随机事件", "region": "机遇"}
            }
            adventure_map = {
                "total_blocks": 24,
                "blocks": {
                    "0" : {"type": "森林", "name": "怪物巢穴", "description": "阴暗的巢穴，怪物可能会突然袭击，小心埋伏。", "region": "副本"},
                    "1" : {"type": "森林", "name": "古树之心", "description": "一棵巨大的古树，周围萦绕着神秘能量，可能存在强大生物。", "region": "副本"},
                    "2" : {"type": "森林", "name": "迷雾谷地", "description": "笼罩在浓雾中的森林低地，能见度极低，危险潜伏四周。", "region": "副本"},
                    "3" : {"type": "森林", "name": "幽灵空地", "description": "空无一人的开阔地，传说这里曾发生过一场激烈战斗，鬼魂仍在游荡。", "region": "副本"},
                    "4" : {"type": "森林", "name": "腐烂树林", "description": "树木腐朽散发异味，小心脚下的陷阱和隐藏其中的怪物。", "region": "副本"},
                    "5" : {"type": "森林", "name": "灵兽栖息地", "description": "灵气浓厚的区域，强大的灵兽在此守护着未知的宝藏。", "region": "副本"},
                    "6" : {"type": "森林", "name": "毒沼密林", "description": "密林深处隐藏着毒雾沼泽，触碰毒气可能引发严重的危机。", "region": "副本"},
                    "7" : {"type": "森林", "name": "月光草原", "description": "一片开阔的森林空地，在夜晚被月光照耀，敌人会利用闪避和潜行。", "region": "副本"},
                    "8" : {"type": "森林", "name": "荒弃村落", "description": "一个长期荒废的村庄，建筑坍塌，有危险生物潜伏其中。", "region": "副本"},
                    "9" : {"type": "森林", "name": "暗影森林", "description": "阳光难以穿透的森林深处，到处充满暗影与未知生物的气息。", "region": "副本"},
                    "10": {"type": "山脉", "name": "绝壁险峰", "description": "陡峭的山峰，怪物可能从高处发动偷袭，注意脚下的危险。", "region": "副本"},
                    "11": {"type": "山脉", "name": "熔岩洞窟", "description": "炽热的洞窟，周围充满熔岩流动的声音，强大的火焰生物潜伏其中。", "region": "副本"},
                    "12": {"type": "山脉", "name": "风暴山巅", "description": "狂风呼啸的山顶，敌人可能利用风暴掩护自己的行动。", "region": "副本"},
                    "13": {"type": "沙漠", "name": "流沙之地", "description": "广袤的沙漠中隐藏着流沙陷阱，敌人可能突然从沙中出现。", "region": "副本"},
                    "14": {"type": "沙漠", "name": "烈日废墟", "description": "沙漠深处的废墟，炽热的阳光让战斗变得更加艰难，怪物潜伏在阴影中。", "region": "副本"},
                    "15": {"type": "沙漠", "name": "沙暴迷城", "description": "被沙暴掩埋的古老城市，能见度极低，敌人可能躲藏在废墟中。", "region": "副本"},
                    "16": {"type": "冰原", "name": "寒冰峡谷", "description": "寒风呼啸的峡谷，冰雪覆盖的地面让战斗更加危险。", "region": "副本"},
                    "17": {"type": "冰原", "name": "冻土遗迹", "description": "冰原深处的遗迹，寒冷让人难以忍受，敌人隐藏在冰雪之下。", "region": "副本"},
                    "18": {"type": "沼泽", "name": "毒雾沼泽", "description": "沼泽地中弥漫着毒雾，敌人可能隐藏在泥潭深处。", "region": "副本"},
                    "19": {"type": "沼泽", "name": "枯骨之地", "description": "沼泽深处堆满了枯骨，传说这里是强大怪物的狩猎场。", "region": "副本"},
                    "20": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},
                    "21": {"type": "机遇", "name": "命运转盘", "description": "触发随机事件", "region": "机遇"},
                    "22": {"type": "机遇", "name": "幸运空间", "description": "触发随机事件", "region": "机遇"},
                    "23": {"type": "机遇", "name": "命运空间", "description": "触发随机事件", "region": "机遇"}
                }
            }
            self._save_json(self.map_file, default_map)
            self._save_json(self.adventure_map_file, adventure_map)

    def _init_events_config(self):
        """初始化事件配置"""
        if not os.path.exists(self.events_file):
            default_events = {
                "good_events": [
                    {
                        "id": "treasure",
                        "name": "发现宝藏",
                        "description": "你发现了一个古老的宝箱",
                        "effect": {
                            "gold": 500
                        }
                        },
                        {
                        "id": "lottery",
                        "name": "中奖啦",
                        "description": "你买的彩票中奖了",
                        "effect": {
                            "gold": 300
                        }
                        },
                        {
                        "id": "found_job",
                        "name": "找到工作",
                        "description": "你找到了一个高薪工作",
                        "effect": {
                            "gold": 400
                        }
                        },
                        {
                        "id": "found_silver_mine",
                        "name": "发现银矿",
                        "description": "你发现了一座银矿，获得了大量银矿资源",
                        "effect": {
                            "gold": 600
                        }
                        },
                        {
                        "id": "birthday_gift",
                        "name": "生日礼物",
                        "description": "朋友送给你一份精美的生日礼物",
                        "effect": {
                            "gold": 150
                        }
                        },
                        {
                        "id": "inherited_money",
                        "name": "继承财富",
                        "description": "你继承了一笔家族遗产",
                        "effect": {
                            "gold": 1000
                        }
                        },
                        {
                        "id": "found_gem",
                        "name": "发现宝石",
                        "description": "在探险中你发现了一颗宝石",
                        "effect": {
                            "gold": 200
                        }
                        },
                        {
                        "id": "business_success",
                        "name": "生意成功",
                        "description": "你的生意取得了巨大成功，利润丰厚",
                        "effect": {
                            "gold": 800
                        }
                        },
                        {
                        "id": "gift_from_friend",
                        "name": "朋友馈赠",
                        "description": "朋友送给你一份珍贵的礼物",
                        "effect": {
                            "gold": 250
                        }
                        },
                        {
                        "id": "sale_profit",
                        "name": "出售物品获利",
                        "description": "你成功出售了一些物品，获得了可观的利润",
                        "effect": {
                            "gold": 300
                        }
                        },
                        {
                        "id": "bonus",
                        "name": "年终奖金",
                        "description": "你获得了丰厚的年终奖金",
                        "effect": {
                            "gold": 700
                        }
                        },
                        {
                        "id": "investment_gain",
                        "name": "投资获利",
                        "description": "你的投资取得了不错的回报",
                        "effect": {
                            "gold": 500
                        }
                        },
                        {
                        "id": "found_artwork",
                        "name": "发现艺术品",
                        "description": "你偶然发现了一件艺术品并成功出售",
                        "effect": {
                            "gold": 350
                        }
                        },
                        {
                        "id": "royalty_payment",
                        "name": "版税收入",
                        "description": "你的作品获得了版税收入",
                        "effect": {
                            "gold": 400
                        }
                        },
                        {
                        "id": "surprise_cash",
                        "name": "意外现金",
                        "description": "某人无意中给了你一笔现金",
                        "effect": {
                            "gold": 100
                        }
                        },
                        {
                        "id": "found_natural_resource",
                        "name": "发现自然资源",
                        "description": "你找到了一种有价值的自然资源",
                        "effect": {
                            "gold": 600
                        }
                        },
                        {
                        "id": "successful_trade",
                        "name": "成功交易",
                        "description": "你完成了一笔成功的交易，获利颇丰",
                        "effect": {
                            "gold": 450
                        }
                        },
                        {
                        "id": "volunteer_reward",
                        "name": "志愿奖励",
                        "description": "你参与志愿活动获得了奖励",
                        "effect": {
                            "gold": 120
                        }
                        },
                        {
                        "id": "sale_discount",
                        "name": "物品折扣",
                        "description": "你在特卖会上以折扣价购得物品，增加了财富",
                        "effect": {
                            "gold": 200
                        }
                        },
                        {
                        "id": "royal_grant",
                        "name": "王室赐予",
                        "description": "王室向你颁发了特别津贴",
                        "effect": {
                            "gold": 800
                        }
                        },
                        {
                        "id": "found_medicinal_herbs",
                        "name": "发现药草",
                        "description": "你发现了一些珍贵的药用草药",
                        "effect": {
                            "gold": 300
                        }
                        },
                        {
                        "id": "publishing_success",
                        "name": "出版成功",
                        "description": "你的书籍出版后大获成功，销售火爆",
                        "effect": {
                            "gold": 500
                        }
                        },
                        {
                        "id": "stock_market_gain",
                        "name": "股市获利",
                        "description": "你的股票投资获得了显著回报",
                        "effect": {
                            "gold": 700
                        }
                        },
                        {
                        "id": "winning_battle",
                        "name": "战斗胜利",
                        "description": "你在一场战斗中获得了胜利，收获了战利品",
                        "effect": {
                            "gold": 250
                        }
                        },
                        {
                        "id": "reward_from_quest",
                        "name": "任务奖励",
                        "description": "你成功完成了一个任务，获得了奖励",
                        "effect": {
                            "gold": 400
                        }
                        },
                        {
                        "id": "fortune_cookie",
                        "name": "幸运饼干",
                        "description": "你在餐馆里吃到了一张幸运饼干，获得奖金",
                        "effect": {
                            "gold": 100
                        }
                        },
                        {
                        "id": "charity_donation",
                        "name": "慈善捐赠",
                        "description": "你收到了一笔来自慈善组织的捐赠",
                        "effect": {
                            "gold": 500
                        }
                        },
                        {
                        "id": "found_ancient_relic",
                        "name": "发现古物",
                        "description": "你找到了一件古老的文物，并成功售出",
                        "effect": {
                            "gold": 600
                        }
                        }
                    ],
                "bad_events": [
                    {
                    "id": "tax",
                    "name": "缴税",
                    "description": "需要缴纳一些税款",
                    "effect": {
                        "gold": -200
                    }
                    },
                    {
                    "id": "robbery",
                    "name": "被偷窃",
                    "description": "你的钱包被偷了",
                    "effect": {
                        "gold": -100
                    }
                    },
                    {
                    "id": "beaten",
                    "name": "被打",
                    "description": "你被他人袭击，损失了一些财物",
                    "effect": {
                        "gold": -100
                    }
                    },
                    {
                    "id": "car_accident",
                    "name": "车祸",
                    "description": "你发生了一起车祸，损失了部分财物",
                    "effect": {
                        "gold": -300
                    }
                    },
                    {
                    "id": "fall_ill",
                    "name": "生病",
                    "description": "你突然生病，需要支付医疗费用",
                    "effect": {
                        "gold": -250
                    }
                    },
                    {
                    "id": "job_lost",
                    "name": "失业",
                    "description": "因为经济不景气，你失去了工作",
                    "effect": {
                        "gold": -400
                    }
                    },
                    {
                    "id": "natural_disaster",
                    "name": "自然灾害",
                    "description": "你遭遇了一场自然灾害，财产受损",
                    "effect": {
                        "gold": -500
                    }
                    },
                    {
                    "id": "theft",
                    "name": "盗窃",
                    "description": "你家中被盗，损失了一些贵重物品",
                    "effect": {
                        "gold": -350
                    }
                    },
                    {
                    "id": "fire_damage",
                    "name": "火灾损失",
                    "description": "你的房屋遭受火灾，损失惨重",
                    "effect": {
                        "gold": -600
                    }
                    },
                    {
                    "id": "legal_fine",
                    "name": "法律罚款",
                    "description": "因违反规定，你需要支付罚款",
                    "effect": {
                        "gold": -300
                    }
                    },
                    {
                    "id": "vehicle_breakdown",
                    "name": "车辆故障",
                    "description": "你的车辆在重要时刻发生故障，需要维修",
                    "effect": {
                        "gold": -150
                    }
                    },
                    {
                    "id": "property_tax",
                    "name": "房产税",
                    "description": "你需要缴纳一笔房产税",
                    "effect": {
                        "gold": -200
                    }
                    },
                    {
                    "id": "legal_lawsuit",
                    "name": "法律诉讼",
                    "description": "你因纠纷被起诉，需要支付律师费",
                    "effect": {
                        "gold": -400
                    }
                    },
                    {
                    "id": "bankruptcy",
                    "name": "破产",
                    "description": "你的企业破产，需要承担债务",
                    "effect": {
                        "gold": -1000
                    }
                    },
                    {
                    "id": "personal_debt",
                    "name": "个人债务",
                    "description": "你背负了高额的个人债务",
                    "effect": {
                        "gold": -500
                    }
                    },
                    {
                    "id": "accidental_damage",
                    "name": "意外损坏",
                    "description": "你不小心损坏了他人的财物，需要赔偿",
                    "effect": {
                        "gold": -250
                    }
                    },
                    {
                    "id": "theft_by_friend",
                    "name": "朋友偷窃",
                    "description": "一个朋友背叛了你，偷走了你的财物",
                    "effect": {
                        "gold": -300
                    }
                    },
                    {
                    "id": "health_expense",
                    "name": "医疗费用",
                    "description": "你因健康问题支付了一大笔医疗费用",
                    "effect": {
                        "gold": -350
                    }
                    },
                    {
                    "id": "vehicle_accident",
                    "name": "车辆事故",
                    "description": "你在驾驶时发生了车辆事故，损失惨重",
                    "effect": {
                        "gold": -400
                    }
                    },
                    {
                    "id": "property_damage",
                    "name": "财产损失",
                    "description": "你的财产因意外受损，需要修复",
                    "effect": {
                        "gold": -300
                    }
                    },
                    {
                    "id": "income_tax",
                    "name": "所得税",
                    "description": "你需要缴纳一笔所得税",
                    "effect": {
                        "gold": -250
                    }
                    },
                    {
                    "id": "investment_loss",
                    "name": "投资亏损",
                    "description": "你的投资失败，导致财务损失",
                    "effect": {
                        "gold": -550
                    }
                    },
                    {
                    "id": "garage_sale_failure",
                    "name": "义卖失败",
                    "description": "你的义卖活动未能达到预期收益",
                    "effect": {
                        "gold": -150
                    }
                    },
                    {
                    "id": "natural_caused_damage",
                    "name": "自然原因损坏",
                    "description": "因自然原因造成财物损坏，需要赔偿",
                    "effect": {
                        "gold": -400
                    }
                    },
                    {
                    "id": "scam",
                    "name": "诈骗",
                    "description": "你被诈骗，损失了部分资金",
                    "effect": {
                        "gold": -300
                    }
                    },
                    {
                    "id": "fraud_charge",
                    "name": "欺诈指控",
                    "description": "你被指控参与欺诈，需支付高额罚款",
                    "effect": {
                        "gold": -600
                    }
                    }
                ]
            }
            self._save_json(self.events_file, default_events)

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
            print(f"加载{file_path}失败: {e}")
            return {}

    def _save_json(self, file_path: str, data: dict):
        """保存JSON文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存{file_path}失败: {e}")

    def roll_dice(self) -> int:
        """掷骰子"""
        return random.randint(1, 6)

    def get_block_info(self, position: int) -> dict:
        """获取指定位置的地块信息"""
        position = position % self.map_data["total_blocks"]
        return self.map_data["blocks"].get(str(position), self.map_data["default_block"])

    def get_adventure_block_info(self, seed: int) -> dict:
        """获取冒险场地图信息"""
        seed = seed % self.adventure_map_data["total_blocks"]
        return self.adventure_map_data["blocks"].get(str(seed), None)

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
        base_price = 500

        # 根据地区类型设置基础价格
        region_multipliers = {
            "直辖市": 5.0,
            "省会": 3.0,
            "地级市": 2.0,
            "县城": 1.5,
            "乡村": 1.0,
            "其他": 1.0
        }

        # 根据距离起点的远近调整价格
        distance_factor = 1 + (position % 10) * 0.1

        # 计算最终价格
        final_price = int(base_price * region_multipliers[block["region"]] * distance_factor)
        return final_price

    def calculate_rent(self, position: int) -> int:
        """计算租金"""
        property_data = self.properties_data.get(str(position))
        if not property_data:
            return 0

        block = self.get_block_info(position)
        base_rent = property_data["price"] * 0.1

        # 根据地区类型设置租金倍率
        region_multipliers = {
            "直辖市": 2.0,
            "省会": 1.5,
            "地级市": 1.3,
            "县城": 1.2,
            "乡村": 1.0,
            "其他": 1.0
        }

        # 根据地产等级增加租金
        level_multiplier = property_data["level"] * 0.5

        # 计算最终租金
        final_rent = int(base_rent * region_multipliers[block["region"]] * (1 + level_multiplier))
        return final_rent

    def get_property_info(self, position: int) -> dict:
        """获取地产详细信息"""
        property_data = self.properties_data.get(str(position))
        if not property_data:
            return None

        block = self.get_block_info(position)
        return {
            "name": block["name"],
            "type": block["type"],
            "region": block["region"],
            "level": property_data["level"],
            "price": property_data["price"],
            "rent": self.calculate_rent(position),
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
