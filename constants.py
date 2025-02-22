# constants.py

# 系统维护标志9(仅管理员可用)
SYSTEM_MAINTENANCE = False

# 玩家基础数值
PLAYER_MAX_LEVEL = 100
PLAYER_BASE_MAX_HP = 200
PLAYER_BASE_ATTACK = 20
PLAYER_BASE_DEFENSE = 20
PLAYER_BASE_EXP = 200
PLAYER_BASE_GOLD = 5000

# 玩家升级时三维的成长
PLAYER_LEVEL_UP_APPEND_HP = 50
PLAYER_LEVEL_UP_APPEND_ATTACK = 10
PLAYER_LEVEL_UP_APPEND_DEFENSE = 10

# 装备掉落率
EQUIPMENT_DROP_PROBABILITY = 15

# 材料掉落率
CONSUMABLE_DROP_PROBABILITY = 30

# 记录战斗日志的回合数
REPORT_THE_NUMBER_OF_ROUNDS = 2

# 是否记录战斗日志
WEATHER_TO_KEEP_A_BATTLE_LOG = True

# 映射稀有度到对应的emoji
RARITY_EMOJIS = ['🟢', '🔵', '🟣', '🟠', '✨']

# 钓鱼冷却
FISH_COOLDOWN = 30

# 鱼竿单次耐久度消耗
FISHING_ROD_DURABILITY_CONSUME = 10

# 冒险冷却
ADVENTURE_COOLDOWN = 10

# 最大稀有度(1-6)
MAX_RARITY = 6

# 签到基础经验奖励
SIGN_IN_EXP_BONUS = 100

#签到基础金币奖励
SIGN_IN_GOLD_BONUS = 2000

# 外出的冷却时间
GO_OUT_CD = 30

# 外出经过起点的奖励
GO_OUT_START_POINT_REWARD = 2000

# 技能最大触发概率枚举
SKILL_MUST_TRIGGER = 100

# -------------------------------------------------
# 稀有度与其对应掉落概率、技能数量、属性加成系数
# -------------------------------------------------
RARITY_DATA = [
    ("普通",  0.35, 0, 1.1),
    ("精良",  0.30, 1, 1.4),
    ("稀有",  0.20, 2, 1.7),
    ("史诗",  0.10, 3, 2.0),
    ("传奇",  0.05, 4, 3.0),
]

# -------------------------------------------------
# 技能名称
# -------------------------------------------------
SKILL_NAMES = {
    "once_damage":  [  # 一次性伤害技能
        "炎爆", "雷斩", "破空", "撼地", "突击",
        "轰落", "崩坏", "铁碎", "烈风", "裁决"
    ],
    "real_damage":  [  # 真实伤害技能
        "碎甲", "噬魂", "裂骨", "切割", "审判",
        "湮灭", "穿刺", "碎颅", "削天", "断罪"
    ],
    "duration_damage":  [  # 持续性伤害技能
        "灼毒", "腐蚀", "熔火", "陨落", "毒雾",
        "噬咒", "燃魂", "浓毒", "侵蚀", "灼伤"
    ],
    "shield":  [  # 护盾技能
        "铜壁", "铁卫", "圣盾", "魔障", "守御",
        "护体", "玄罩", "幻壁", "铁块", "金甲"
    ],
    "once_heal":  [  # 单次生命回复技能
        "回春", "愈合", "复苏", "归元", "弃疾",
        "留芳", "续命", "去病", "逆转", "青囊"
    ],
    "duration_heal":  [  # 持续性生命回复技能
        "再生", "滋养", "温泉", "补元", "生息",
        "续灵", "源泉", "修养", "长生", "润泽"
    ],
    "paralysis":  [  # 麻痹技能（眩晕效果）
        "麻痹", "眩晕", "震慑", "锁灵", "惊雷",
        "闪电", "禁锢", "雷噬", "失衡", "吞晕"
    ],
    "active_immunity":  [  # 免疫异常技能
        "清风", "无端", "祛邪", "除晦", "驱散",
        "解脱", "脱壳", "洗礼", "清净", "化煞"
    ],
    "precedence_immunity":  [  # 洞察类技能（开局数回合免疫）
        "预见", "先机", "透视", "识破", "观微",
        "真智", "洞悉", "天眼", "烛照", "览魂"
    ],
    "once_life_steal": [  # 单次吸血技能
        "噬血", "纳灵", "豪夺", "渴望", "噬命",
        "汲取", "寄生", "血炼", "吞髓", "饿魄"
    ],
    "duration_life_steal": [  # 持续型吸血技能
        "暗噬", "蚀命", "黑疫", "虚蚀", "泯魂",
        "血蚀", "夜噬", "阴啃", "死咒", "饮灵"
    ],
    "promoting_attributes": [  # 自身属性提升技能
        "狂暴", "强化", "孽生", "疯狂", "魂提",
        "暴增", "野蛮", "神力", "耀光", "攀升"
    ],
    "weaken_attributes": [  # 削减对手属性技能
        "迷惘", "侵蚀", "弱化", "衰败", "蚀力",
        "削弱", "减益", "败势", "剥夺", "崩解"
    ],
    "reflect": [  # 反伤技能
        "还击", "回斩", "刺返", "弹反", "借力",
        "反射", "逆伤", "却攻", "针刺", "反震"
    ],
    "assimilate": [  # 伤害吸收技能
        "化解", "抵御", "吸霞", "盾障", "摄能",
        "泯伤", "吞噬", "拦截", "减损", "遮蔽"
    ]
}

# -------------------------------------------------
# 防具前缀
# -------------------------------------------------
ARMOR_PREFIX = [
    "圣光", "暗影", "苍穹", "深渊", "雷霆", "火山", "冰川", "荒漠", "密林", "血色",
    "雾隐", "龙骨", "凤凰", "堕天", "霜寒", "灵息", "飞羽", "幽冥", "天谴", "日耀",
    "星耀", "月华", "伤痕", "迷雾", "星空", "幽夜", "烈焰", "焰魂", "远古", "破晓",
    "翡翠", "血月", "破军", "废墟", "狂风", "乱舞", "天启", "星陨", "灭世", "暗裔",
    "寂灭", "狂沙", "爆炎", "钢铁", "圣银", "幻梦", "暗月", "星火", "森罗", "魂灯"
]

# -------------------------------------------------
# 防具名
# -------------------------------------------------
ARMOR_NAME = [
    "羁绊战甲", "绝境铠甲", "鹫翼披风", "玄冥斗篷", "狂澜",
    "浩劫战衣", "风语斗篷", "曜星披挂", "藤蔓铠甲", "沧海",
    "烈焰战甲", "锦云皮甲", "幻光斗篷", "浓雾战袍", "长城",
    "翡翠铠甲", "暮色披风", "明王战衣", "苍狮斗篷", "御天",
    "无双皮甲", "虹彩战甲", "溪流披挂", "风息铠甲", "残响",
    "银灵战衣", "寒鸦斗篷", "极光战衣", "青龙铠甲", "堡垒",
    "流璃披风", "绝尘钢甲", "孤影战衣", "无常", "守望",
    "暗月之甲", "龙吟战甲", "雪灵铠甲", "罗刹", "极夜",
    "星痕斗篷", "沦陷钢甲", "林海披挂", "灭迹战衣", "明王",
    "凤舞轻甲", "白雾战甲", "薄暮法袍", "霜心披风", "苍穹"  ]

# -------------------------------------------------
# 武器前缀
# -------------------------------------------------
WEAPON_PREFIX = [
    "烈焰", "寒霜", "幽影", "逐风", "落星", "赤月", "荒骨", "神木", "雷霆", "裂空",
    "永夜", "黑曜", "白虹", "血羽", "碎日", "迷雾", "星陨", "炽焰", "蔓藤", "纵横",
    "落雷", "碎月", "浩渊", "玄冰", "星瀚", "侠骨", "暗血", "风暴", "雷鸣", "潮汐",
    "赐福", "猩红", "南冥", "冰澜", "焰魄", "天痕", "龙吟", "龙息", "地狱", "凛冬",
    "修罗", "万象", "羽落", "狱魂", "天耀", "极光", "黑蚀", "白霜", "黯星", "光影"
]

# -------------------------------------------------
# 武器名称
# -------------------------------------------------
WEAPON_NAME = [
    "双刃剑", "大剑", "战矛", "战斧", "长弓", "匕首", "法杖", "长鞭", "忍镰", "双头刀",
    "战锤", "绳镖", "钩爪", "环刃", "法杖", "弯刀", "战槌", "刺剑", "太刀", "流星锤",
    "火枪", "骨矛", "巨剑", "碎星", "哀伤", "裁决", "葬魂", "噬灭", "村雨", "梦魇",
    "斩马", "葫芦", "破空", "龙牙", "蛇吻", "虎啸", "九节鞭", "双剑", "弦月", "风暴",
    "血祭", "霜杀", "雷动", "曲剑", "白虹", "连枷", "暴君", "忍刀", "旌旗", "杀机"
]

# 签到诗句提示
SIGN_IN_POEMS = {
    "大吉": [
        "苍天已死，黄天当立。岁在甲子，天下大吉。",
        "春风得意马蹄疾，一日看尽长安花。",
        "仰天大笑出门去，我辈岂是蓬蒿人！",
        "天生我材必有用，千金散尽还复来。",
        "长风破浪会有时，直挂云帆济沧海。",
        "千里之行始于足下，万事开头难。",
        "不畏浮云遮望眼，自缘身在最高层。",
        "风雨送春归，飞雪迎春到。",
        "希望的田野上，漫舞的都是花。",
        "大展宏图，万事如意。",
        "桃花源里可耕田，双溪舴艋傍南山。",
        "问君何能尔，心似双丝网。",
        "长安不见月，白玉楼中愁。",
        "海内存知己，天涯若比邻。",
        "朝辞白帝彩云间，千里江陵一日还。",
        "举头望明月，低头思故乡。",
        "一片冰心在玉壶。",
        "问君何能尔，心似双丝网。",
        "白日依山尽，苍苍苍穹披。",
        "万里悲秋常作客，百年多病独登台。",
        "千古事，千古情，千古事，千古情。",
        "天生我才必有用，千金散尽还复来。",
        "月落乌啼霜满天，江枫渔火对愁眠。",
        "青山遮不住，毕竟东流去。",
        "一去二三里，烟村四五家。",
        "春色满园关不住，花香扑鼻欲言语。",
        "白云千载空悠悠，苍狗白牙随意走。",
        "我寄愁心与明月，随风泪滴入江流。",
        "长风破浪会有时，直挂云帆济沧海。",
        "千古风流人物，尽归豪杰。",
        "大江东去，浪淘尽，千古风流人物。",
        "人间四月芳菲尽，山寺桃花始盛开。"
    ],
    "中吉": [
        "莫愁前路无知己，天下谁人不识君。",
        "路遥知马力，日久见人心。",
        "有志者事竟成，破釜沉舟百二秦关终属楚。",
        "千淘万漉虽辛苦，吹尽狂沙始到金。",
        "一寸光阴一寸金，寸金难买寸光阴。",
        "我见青山多妩媚，料青山见我应如是。",
        "千里之行，始于足下。",
        "不经一番寒彻骨，怎得梅花扑鼻香。",
        "志不强者智不达。",
        "行百里者半九十。",
        "前事不忘，后事之师。",
        "千里之行，始于足下。",
        "天道酬勤。",
        "莫道桑榆晚，微霞尚流红。",
        "月照花林皆似霰，风吹柳絮更纷纷。",
        "若无存志，宁为凤求凰。",
        "不怕慢，就怕停。",
        "小胜靠智，大胜靠德。",
        "一年之计在于春，一日之计在于晨。",
        "千里之行，始于足下。",
        "十年树木，百年树人。",
        "明日复明日，明日何其多。",
        "合抱之木，生于毫末；九层之台，起于垒土。",
        "不积跬步，无以至千里。",
        "人谁无过，过而能改，善莫大焉。",
        "填词场上笑声扬，平步青云伴君旁。",
        "路遥知马力，日久见人心。",
        "在天愿作比翼鸟，在地愿为连理枝。",
        "海内存知己，天涯若比邻。",
        "天道酬勤，奋发图强。",
        "日出而作，日落而息。"
    ],
    "小吉": [
        "不经一番寒彻骨，怎得梅花扑鼻香。",
        "千里之行始于足下。",
        "天道酬勤。",
        "志不强者智不达。",
        "行百里者半九十。",
        "小心驶得万年船。",
        "正当浮云独去闲，细看花煮兼扁舟。",
        "千里之行，始于足下。",
        "小胜靠智，大胜靠德。",
        "不怕慢，就怕停。",
        "滴水穿石，绳锯木断。",
        "艰难困苦，玉汝于成。",
        "千里之墙，行百里者半。",
        "磨刀不误砍柴工。",
        "千里之行，始于足下。",
        "心态决定命运，选择改变人生。",
        "千淘万漉，吹尽狂沙始到金。",
        "有志者事竟成，破釜沉舟百二秦关终属楚。",
        "千力之主，夕阳西下，一道能青。",
        "路虽远行则将至，事虽难做则必成。",
        "千里之行始于足下。",
        "千里之行，始于足下。",
        "一通百通，八面玲珑。",
        "有志者事竟成，百折不挠，方见天日。",
        "一日三秋，浮云富贵轻。",
        "闲云潭影日悠悠，閒云潭影浮空秀。",
        "千里不行，行百里者半。",
        "小事多看常有吉，小心开路脚跟前。",
        "三更灯火五更鸡，正是男儿立志时。",
        "阴阳鞠镕几多年，哪个英雄到岸",
        "山无陵，江水为竭，冬雷震震，夏雨雪，天地合，乃敢与君绝。",
        "天道酬勤，奋斗是也。"
    ],
    "末吉": [
        "人无远虑，必有近忧。",
        "尘世茫茫无尽，人生碌碌争先。",
        "空把光阴暗度，枉为豪气争权。",
        "人生若只如初见，何事秋风悲画扇。",
        "不怕慢，就怕停。",
        "失败是成功之母。",
        "千里之行，始于足下。",
        "不积跬步，无以至千里。",
        "小心驶得万年船。",
        "千里之行，始于足下。",
        "不怕慢，就怕停。",
        "不积跬步，无以至千里。",
        "有志者事竟成。",
        "小心驶得万年船。",
        "千里之行，始于足下。",
        "不怕慢，就怕停。",
        "千里放舟任逍遥，惜乎倾城值几何。",
        "前事不忘，后事之师。",
        "一失足成千古恨。",
        "小心翼翼，前方万路开。",
        "若知今日，何必当初。",
        "成则为王败则为寇。",
        "夜明月起夜沉沉，良宵岂幻想凡云。",
        "绳锯木断，水滴石穿。",
        "小心驶得万年船。",
        "长风破浪会有时，直挂云帆济沧海。",
        "失之东隅，收之桑榆。",
        "千愁万思，日落西山。",
        "有志者事竟成，破釜沉舟百二秦关终属楚。",
        "明月清风，欲送别千里忧怨。",
        "不积跬步，无以至千里。",
        "千里长征，一步一步来。"
    ]
}

MONOPOLY_MAP = {
    "total_blocks": 200,
    "blocks": {
        "0": {"type": "首都", "name": "北京", "description": "每次经过可获得200金币", "region": "直辖市"},
        "1": {"type": "直辖市", "name": "天津", "description": "天津煎饼果子，来了就得吃", "region": "直辖市"},
        "2": {"type": "省会", "name": "石家庄", "description": "河北的省会，离北京很近", "region": "省会"},
        "3": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},
        "4": {"type": "地级市", "name": "保定", "description": "历史文化名城，直隶总督府所在地", "region": "地级市"},
        "5": {"type": "县城", "name": "雄安新区", "description": "未来之城，正在崛起", "region": "县城"},
        "6": {"type": "县城", "name": "唐山", "description": "工业城市，曾经的地震遗址", "region": "县城"},
        "7": {"type": "机遇", "name": "命运转盘", "description": "触发随机事件", "region": "机遇"},
        "8": {"type": "省会", "name": "太原", "description": "山西的省会，煤老板的故乡", "region": "省会"},
        "9": {"type": "地级市", "name": "大同", "description": "云冈石窟，佛教艺术的瑰宝", "region": "地级市"},
        "10": {"type": "县城", "name": "平遥古城", "description": "保存完好的明清古城", "region": "县城"},
        "11": {"type": "县城", "name": "五台山", "description": "佛教圣地，香火旺盛", "region": "县城"},
        "12": {"type": "机遇", "name": "命运转盘", "description": "触发随机事件", "region": "机遇"},
        "13": {"type": "省会", "name": "呼和浩特", "description": "内蒙古的省会，草原上的城市", "region": "省会"},
        "14": {"type": "地级市", "name": "包头", "description": "钢铁之城，工业重镇", "region": "地级市"},
        "15": {"type": "县城", "name": "鄂尔多斯", "description": "富得流油的城市，煤炭资源丰富", "region": "县城"},
        "16": {"type": "县城", "name": "呼伦贝尔", "description": "大草原，适合避暑", "region": "县城"},
        "17": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},
        "18": {"type": "省会", "name": "沈阳", "description": "东北的工业中心，清朝发源地", "region": "省会"},
        "19": {"type": "地级市", "name": "大连", "description": "海滨城市，浪漫之都", "region": "地级市"},
        "20": {"type": "县城", "name": "鞍山", "description": "钢铁之城，温泉胜地", "region": "县城"},
        "21": {"type": "县城", "name": "抚顺", "description": "煤都，雷锋的第二故乡", "region": "县城"},
        "22": {"type": "机遇", "name": "命运转盘", "description": "触发随机事件", "region": "机遇"},
        "23": {"type": "省会", "name": "长春", "description": "汽车工业之城，电影之城", "region": "省会"},
        "24": {"type": "地级市", "name": "吉林市", "description": "雾凇之都，冰雪之城", "region": "地级市"},
        "25": {"type": "县城", "name": "延边", "description": "朝鲜族自治州，美食天堂", "region": "县城"},
        "26": {"type": "县城", "name": "白城", "description": "草原湿地，生态旅游胜地", "region": "县城"},
        "27": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},
        "28": {"type": "省会", "name": "哈尔滨", "description": "冰城，俄罗斯风情浓厚", "region": "省会"},
        "29": {"type": "地级市", "name": "牡丹江", "description": "雪乡所在地，冬季旅游胜地", "region": "地级市"},
        "30": {"type": "县城", "name": "伊春", "description": "森林城市，空气清新", "region": "县城"},
        "31": {"type": "县城", "name": "大庆", "description": "石油之城，工业重镇", "region": "县城"},
        "32": {"type": "机遇", "name": "命运转盘", "description": "触发随机事件", "region": "机遇"},
        "33": {"type": "省会", "name": "济南", "description": "泉城，趵突泉天下第一泉", "region": "省会"},
        "34": {"type": "地级市", "name": "青岛", "description": "海滨城市，啤酒之都", "region": "地级市"},
        "35": {"type": "县城", "name": "烟台", "description": "葡萄酒之乡，海滨度假胜地", "region": "县城"},
        "36": {"type": "县城", "name": "威海", "description": "最干净的城市之一，适合养老", "region": "县城"},
        "37": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},
        "38": {"type": "省会", "name": "南京", "description": "六朝古都，历史底蕴深厚", "region": "省会"},
        "39": {"type": "地级市", "name": "苏州", "description": "园林之城，江南水乡", "region": "地级市"},
        "40": {"type": "县城", "name": "无锡", "description": "太湖明珠，鱼米之乡", "region": "县城"},
        "41": {"type": "县城", "name": "常州", "description": "恐龙园所在地，欢乐之城", "region": "县城"},
        "42": {"type": "机遇", "name": "命运转盘", "description": "触发随机事件", "region": "机遇"},
        "43": {"type": "省会", "name": "杭州", "description": "人间天堂，西湖美景", "region": "省会"},
        "44": {"type": "地级市", "name": "宁波", "description": "港口城市，经济发达", "region": "地级市"},
        "45": {"type": "县城", "name": "温州", "description": "民营经济之都，商人遍天下", "region": "县城"},
        "46": {"type": "县城", "name": "绍兴", "description": "鲁迅故乡，黄酒之都", "region": "县城"},
        "47": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},
        "48": {"type": "省会", "name": "福州", "description": "有福之州，三坊七巷", "region": "省会"},
        "49": {"type": "地级市", "name": "厦门", "description": "海滨城市，鼓浪屿闻名遐迩", "region": "地级市"},
        # Group 13: 50-53
        "50": {"type": "省会", "name": "郑州", "description": "中原古都，传说与美食并存，让人流连忘返", "region": "省会"},
        "51": {"type": "地级市", "name": "洛阳", "description": "牡丹花开的季节，古韵犹存的历史名城", "region": "地级市"},
        "52": {"type": "县城", "name": "开封", "description": "古风遗韵，包罗万象的美食诱惑", "region": "县城"},
        "53": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 14: 54-57
        "54": {"type": "省会", "name": "武汉", "description": "江城魅力，热干面香味四溢", "region": "省会"},
        "55": {"type": "地级市", "name": "十堰", "description": "山水之间，诗意盎然的汽车之城", "region": "地级市"},
        "56": {"type": "地级市", "name": "宜昌", "description": "三峡畔的明珠，风光旖旎", "region": "地级市"},
        "57": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 15: 58-61
        "58": {"type": "省会", "name": "长沙", "description": "星城夜色迷人，辣味十足", "region": "省会"},
        "59": {"type": "地级市", "name": "株洲", "description": "工业与文化交汇的创新之城", "region": "地级市"},
        "60": {"type": "县城", "name": "衡阳", "description": "历史悠久，风情万种的小城", "region": "县城"},
        "61": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 16: 62-65
        "62": {"type": "省会", "name": "南昌", "description": "英雄城中藏着诗与远方", "region": "省会"},
        "63": {"type": "地级市", "name": "九江", "description": "鄱阳湖畔，渔歌互答", "region": "地级市"},
        "64": {"type": "县城", "name": "赣州", "description": "客家文化浓郁，山水画卷般美丽", "region": "县城"},
        "65": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 17: 66-69
        "66": {"type": "地级市", "name": "泉州", "description": "海上丝路起点，美食与古迹共舞", "region": "地级市"},
        "67": {"type": "县城", "name": "漳州", "description": "浪漫海风拂面，甜蜜得来不易", "region": "县城"},
        "68": {"type": "县城", "name": "莆田", "description": "福地宝岛旁的小城，古今传奇", "region": "县城"},
        "69": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 18: 70-73
        "70": {"type": "省会", "name": "海口", "description": "热带风情，椰风海韵扑面而来", "region": "省会"},
        "71": {"type": "地级市", "name": "三亚", "description": "沙滩度假胜地，阳光与海水的浪漫相遇", "region": "地级市"},
        "72": {"type": "县城", "name": "儋州", "description": "椰林轻拂中感受浓浓岛韵", "region": "县城"},
        "73": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 19: 74-77
        "74": {"type": "地级市", "name": "攀枝花", "description": "山城新意，钢铁与彩虹并存", "region": "地级市"},
        "75": {"type": "县城", "name": "德阳", "description": "吃辣有理，热情满满的小城", "region": "县城"},
        "76": {"type": "地级市", "name": "乐山", "description": "大佛守望下的美食诱惑", "region": "地级市"},
        "77": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 20: 78-81
        "78": {"type": "县城", "name": "泸州", "description": "老酒香浓，水路风光无限", "region": "县城"},
        "79": {"type": "地级市", "name": "宜宾", "description": "长江之畔，醇酒飘香", "region": "地级市"},
        "80": {"type": "县城", "name": "内江", "description": "川渝腹地隐秘的小城，低调而迷人", "region": "县城"},
        "81": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 21: 82-85
        "82": {"type": "省会", "name": "贵阳", "description": "山城风情，云雾缭绕间别有韵味", "region": "省会"},
        "83": {"type": "地级市", "name": "遵义", "description": "红色基因与美食交织的热土", "region": "地级市"},
        "84": {"type": "县城", "name": "安顺", "description": "喀斯特地貌下的神秘美景", "region": "县城"},
        "85": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 22: 86-89
        "86": {"type": "县城", "name": "大理", "description": "洱海边的慢生活，诗意与浪漫并存", "region": "县城"},
        "87": {"type": "地级市", "name": "丽江", "description": "古镇风情，石板路上诉说着故事", "region": "地级市"},
        "88": {"type": "县城", "name": "西双版纳", "description": "热带雨林的神秘色彩，充满原始魅力", "region": "县城"},
        "89": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 23: 90-93
        "90": {"type": "省会", "name": "拉萨", "description": "雪域高原的心脏，虔诚与传奇同行", "region": "省会"},
        "91": {"type": "地级市", "name": "日喀则", "description": "大昭寺前的转经筒，岁月静好", "region": "地级市"},
        "92": {"type": "县城", "name": "林芝", "description": "桃花源般的仙境，让人心醉神迷", "region": "县城"},
        "93": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 24: 94-97
        "94": {"type": "地级市", "name": "巴彦淖尔", "description": "辽阔草原上偶遇诗与远方", "region": "地级市"},
        "95": {"type": "县城", "name": "乌海", "description": "荒漠边缘的小城，别有洞天", "region": "县城"},
        "96": {"type": "地级市", "name": "赤峰", "description": "古韵悠长，草原风情扑面而来", "region": "地级市"},
        "97": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 25: 98-101
        "98": {"type": "省会", "name": "西安", "description": "千年古都，每一砖每一瓦都在诉说历史", "region": "省会"},
        "99": {"type": "地级市", "name": "咸阳", "description": "秦朝余韵犹存，历史厚重感十足", "region": "地级市"},
        "100": {"type": "县城", "name": "宝鸡", "description": "古乐悠扬，文物藏身的秘境", "region": "县城"},
        "101": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 26: 102-105
        "102": {"type": "省会", "name": "兰州", "description": "黄河畔的西北门户，一碗拉面温暖人心", "region": "省会"},
        "103": {"type": "地级市", "name": "嘉峪关", "description": "长城之端，雄关漫道真如铁", "region": "地级市"},
        "104": {"type": "县城", "name": "张掖", "description": "丹霞地貌绘出炫目的色彩", "region": "县城"},
        "105": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 27: 106-109
        "106": {"type": "省会", "name": "西宁", "description": "青海湖畔的风情万种，宁静致远", "region": "省会"},
        "107": {"type": "地级市", "name": "格尔木", "description": "戈壁深处的倔强之城", "region": "地级市"},
        "108": {"type": "县城", "name": "黄南", "description": "藏区风情与祈福共存的小镇", "region": "县城"},
        "109": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 28: 110-113
        "110": {"type": "省会", "name": "合肥", "description": "科技与传统交融，活力四射", "region": "省会"},
        "111": {"type": "地级市", "name": "芜湖", "description": "水上轻歌曼舞，美食香飘万里", "region": "地级市"},
        "112": {"type": "县城", "name": "蚌埠", "description": "湖畔风情有故事，温情缓缓流淌", "region": "县城"},
        "113": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 29: 114-117
        "114": {"type": "地级市", "name": "安庆", "description": "古韵犹存，徽派风情满城飘逸", "region": "地级市"},
        "115": {"type": "县城", "name": "马鞍山", "description": "铁与火的碰撞，铸就独特风采", "region": "县城"},
        "116": {"type": "县城", "name": "黄山", "description": "云海奇观，登临绝顶忘返凡尘", "region": "县城"},
        "117": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 30: 118-121
        "118": {"type": "地级市", "name": "南阳", "description": "古木参天，历史的深处藏着奇遇", "region": "地级市"},
        "119": {"type": "县城", "name": "商丘", "description": "古运河畔，小巷故事说不尽", "region": "县城"},
        "120": {"type": "县城", "name": "新乡", "description": "活力四射，创业激情一触即发", "region": "县城"},
        "121": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 31: 122-125
        "122": {"type": "省会", "name": "济南", "description": "泉水叮咚，趵突泉流韵动人", "region": "省会"},
        "123": {"type": "地级市", "name": "烟台", "description": "海风徐来，渔歌唱晚", "region": "地级市"},
        "124": {"type": "县城", "name": "潍坊", "description": "风筝故乡，悠闲与热闹并存", "region": "县城"},
        "125": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 32: 126-129
        "126": {"type": "地级市", "name": "临沂", "description": "红色故都外的活力拼图", "region": "地级市"},
        "127": {"type": "县城", "name": "济宁", "description": "孔孟之道余韵悠长，幽默风趣", "region": "县城"},
        "128": {"type": "县城", "name": "泰安", "description": "泰山之下，笑看风云变幻", "region": "县城"},
        "129": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 33: 130-133
        "130": {"type": "地级市", "name": "徐州", "description": "古运河畔，繁华与沧桑共存", "region": "地级市"},
        "131": {"type": "县城", "name": "常州", "description": "小桥流水人家外，多彩生活启航", "region": "县城"},
        "132": {"type": "地级市", "name": "南通", "description": "长江北岸的明珠，洋溢着新潮气息", "region": "地级市"},
        "133": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 34: 134-137
        "134": {"type": "地级市", "name": "温州", "description": "海边商贸古今交织，总有惊喜等你", "region": "地级市"},
        "135": {"type": "县城", "name": "绍兴", "description": "酒香与古韵不期而遇，浸润心田", "region": "县城"},
        "136": {"type": "县城", "name": "金华", "description": "小城故事多，幽默风趣引人入胜", "region": "县城"},
        "137": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 35: 138-141
        "138": {"type": "地级市", "name": "吉安", "description": "红色记忆与文艺情怀在此交融", "region": "地级市"},
        "139": {"type": "县城", "name": "景德镇", "description": "瓷都神韵，白瓷青花讲述千年秘辛", "region": "县城"},
        "140": {"type": "县城", "name": "萍乡", "description": "小城大爱，幽默风采令人耳目一新", "region": "县城"},
        "141": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 36: 142-145 (台湾地区)
        "142": {"type": "直辖市", "name": "台北", "description": "历史与现代交织的繁华都会", "region": "直辖市"},
        "143": {"type": "地级市", "name": "台中", "description": "温暖阳光下的创意之都，活力无限", "region": "地级市"},
        "144": {"type": "地级市", "name": "高雄", "description": "港湾城市，浪漫与开放并存", "region": "地级市"},
        "145": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 37: 146-149 (特别行政区)
        "146": {"type": "特别行政区", "name": "香港", "description": "东方之珠，璀璨夜景闪耀繁华", "region": "特别行政区"},
        "147": {"type": "特别行政区", "name": "澳门", "description": "魅力十足的小赌怡情，别样风光", "region": "特别行政区"},
        "148": {"type": "地级市", "name": "佛山", "description": "武术与陶艺齐飞，美食与工艺共鸣", "region": "地级市"},
        "149": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 38: 150-153 (新疆部分)
        "150": {"type": "省会", "name": "乌鲁木齐", "description": "西域风情浓厚，市场与美食齐放异彩", "region": "省会"},
        "151": {"type": "地级市", "name": "喀什", "description": "古丝路的驿站，神秘与热情共存", "region": "地级市"},
        "152": {"type": "县城", "name": "哈密", "description": "瓜果飘香中透出丝丝异域风情", "region": "县城"},
        "153": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 39: 154-157
        "154": {"type": "地级市", "name": "吐鲁番", "description": "火焰山下，奇观连连眼花缭乱", "region": "地级市"},
        "155": {"type": "县城", "name": "伊宁", "description": "繁星点点的边陲小镇，别具风味", "region": "县城"},
        "156": {"type": "地级市", "name": "克拉玛依", "description": "油城魅影，黑金闪耀独特风采", "region": "地级市"},
        "157": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 40: 158-161
        "158": {"type": "县城", "name": "武威", "description": "边疆小城，历史与传说交织", "region": "县城"},
        "159": {"type": "地级市", "name": "酒泉", "description": "长城脚下，月亮与硝烟共诉衷肠", "region": "地级市"},
        "160": {"type": "县城", "name": "庆阳", "description": "古道边的小镇，笑看云卷云舒", "region": "县城"},
        "161": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 41: 162-165
        "162": {"type": "地级市", "name": "海宁", "description": "小商品城外的宁静港湾，别有洞天", "region": "地级市"},
        "163": {"type": "县城", "name": "嘉兴", "description": "水乡风情浓郁，细雨轻拂心田", "region": "县城"},
        "164": {"type": "县城", "name": "舟山", "description": "渔火点点中流淌着海的传说", "region": "县城"},
        "165": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 42: 166-169
        "166": {"type": "地级市", "name": "连云港", "description": "黄海之滨，浪漫与务实并行", "region": "地级市"},
        "167": {"type": "县城", "name": "常熟", "description": "江南水乡里，小巷深深见风情", "region": "县城"},
        "168": {"type": "县城", "name": "泰州", "description": "古韵新风交汇处，幽默故事不断", "region": "县城"},
        "169": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 43: 170-173
        "170": {"type": "地级市", "name": "东莞", "description": "制造业名城外，时尚与创意齐飞", "region": "地级市"},
        "171": {"type": "县城", "name": "惠州", "description": "山海之间，慢生活与甜蜜邂逅", "region": "县城"},
        "172": {"type": "县城", "name": "汕头", "description": "潮汕文化浓烈，美食与海韵齐放", "region": "县城"},
        "173": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 44: 174-177
        "174": {"type": "县城", "name": "自贡", "description": "盐都旧梦今犹在，小巷笑谈间尽显幽默", "region": "县城"},
        "175": {"type": "地级市", "name": "遂宁", "description": "川西腹地的温情城市，总有惊喜隐现", "region": "地级市"},
        "176": {"type": "县城", "name": "眉山", "description": "诗意闲适中，火锅香气荡漾", "region": "县城"},
        "177": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 45: 178-181 (来自山东的新篇章)
        "178": {"type": "地级市", "name": "德州", "description": "麦香四溢，幽默风趣的古城印记", "region": "地级市"},
        "179": {"type": "县城", "name": "聊城", "description": "运河之畔，故事与笑谈相伴", "region": "县城"},
        "180": {"type": "县城", "name": "滨州", "description": "海风与田园共同谱写的轻快旋律", "region": "县城"},
        "181": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 46: 182-185 (东北风情)
        "182": {"type": "地级市", "name": "营口", "description": "港口风情浓，海韵与故事漫溢", "region": "地级市"},
        "183": {"type": "县城", "name": "盘锦", "description": "芦苇荡里，油画般的田园风光", "region": "县城"},
        "184": {"type": "县城", "name": "阜新", "description": "老工业基地焕发新生，幽默中透着坚韧", "region": "县城"},
        "185": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 47: 186-189 (山西风光)
        "186": {"type": "省会", "name": "太原", "description": "古韵与现代交融，煤香中透出诗情", "region": "省会"},
        "187": {"type": "地级市", "name": "临汾", "description": "黄土高坡上的传奇与幽默并存", "region": "地级市"},
        "188": {"type": "县城", "name": "运城", "description": "盐湖风情，历史回眸间笑看风云", "region": "县城"},
        "189": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 48: 190-193 (山西续篇)
        "190": {"type": "地级市", "name": "长治", "description": "群山环绕，幽默与韵味同在", "region": "地级市"},
        "191": {"type": "县城", "name": "晋城", "description": "古色古香的小城，总能引发微笑", "region": "县城"},
        "192": {"type": "县城", "name": "朔州", "description": "北国风光中，悄然藏着逸趣横生", "region": "县城"},
        "193": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 49: 194-197 (河北韵味)
        "194": {"type": "县城", "name": "唐山", "description": "钢铁与海风并存，笑看兴衰百态", "region": "县城"},
        "195": {"type": "地级市", "name": "邯郸", "description": "历史厚重，幽默中透出坚韧的魅力", "region": "地级市"},
        "196": {"type": "县城", "name": "衡水", "description": "水利与风情同行，质朴中见真章", "region": "县城"},
        "197": {"type": "机遇", "name": "机遇空间", "description": "触发随机事件", "region": "机遇"},

        # Group 50: 198-199 (终点归程)
        "198": {"type": "县城", "name": "塘沽", "description": "海边渔村韵味十足，浓缩咸湿风情", "region": "县城"},
        "199": {"type": "地级市", "name": "沧州", "description": "曾经是海上丝绸之路的起点", "region": "地级市"}
    },
    "default_block": {"type": "机遇", "name": "命运空间", "description": "触发随机事件", "region": "机遇"}
}

MAP_TYPE_SYMBOLS = {
    "特别行政区": "🏬",
    "首都": "🏯",
    "直辖市": "🏣",
    "省会": "🏫",
    "地级市": "🏢",
    "县城": "🏡",
    "空地": "⬜",
    "机遇": "🌠",
}

# 区域的升级倍率
UPGRADE_MULTIPLIER_OF_THE_AREA = {
    "特别行政区": 5.0,
    "直辖市": 3.0,
    "省会": 2.0,
    "地级市": 1.5,
    "县城": 1.0,
    "其他": 1.0
}

# 区域的租金倍率
RENT_MULTIPLIER_OF_THE_AREA = {
    "特别行政区": 5.0,
    "直辖市": 3.0,
    "省会": 2.0,
    "地级市": 1.5,
    "县城": 1.0,
    "其他": 1.0
}

# 区域的基本价格
BASE_PRICE_OF_THE_AREA = {
    "特别行政区": 10.0,
    "直辖市": 5.0,
    "省会": 3.0,
    "地级市": 2.0,
    "县城": 1.0,
    "其他": 1.0
}

RANDOM_EVENTS = {
    "good_events": [
        {
            "id": "treasure",
            "name": "发现宝藏",
            "description": "你发现了一个古老的宝箱",
            "effect": {
                "exp": 100,
                "consumable": 2,
                "weapon": 1,
            }
        },
        {
            "id": "treasure",
            "name": "发现宝藏",
            "description": "你发现了一个精美的宝箱",
            "effect": {
                "exp": 600,
                "weapon": 1,
                "armor": 1,
                "consumable": 4
            }
        },
        {
            "id": "treasure",
            "name": "发现宝藏",
            "description": "你发现了一个会哭的宝箱",
            "effect": {
                "gold": 500,
                "exp": 100,
                "weapon": 1,
                "consumable": 2
            }
        },
        {
            "id": "lottery",
            "name": "中奖啦",
            "description": "你买的彩票中奖了",
            "effect": {
                "gold": 1000
            }
        },
        {
            "id": "found_job",
            "name": "找到工作",
            "description": "你找到了一个高薪工作，打工使你快乐！",
            "effect": {
                "gold": 3000,
                "exp": 2000
            }
        },
        {
            "id": "found_silver_mine",
            "name": "发现银矿",
            "description": "你发现了一座金矿，获得了大量金矿资源，化身黄金矿工了家人们！",
            "effect": {
                "gold": 1600,
                "exp": 400
            }
        },
        {
            "id": "birthday_gift",
            "name": "生日礼物",
            "description": "朋友送给你一份精美的生日礼物，有朋友真好！",
            "effect": {
                "gold": 666,
                "consumable": 5
            }
        },
        {
            "id": "inherited_money",
            "name": "继承财富",
            "description": "你继承了一笔家族遗产，谁还不是个富二代了🆒",
            "effect": {
                "gold": 3000
            }
        },
        {
            "id": "found_gem",
            "name": "发现宝石",
            "description": "在探险中你发现了一颗宝石，卖了不少钱",
            "effect": {
                "gold": 2020,
                "exp": 360
            }
        },
        {
            "id": "business_success",
            "name": "生意成功",
            "description": "你的生意取得了成功，利润不菲",
            "effect": {
                "gold": 2800,
                "exp": 200
            }
        },
        {
            "id": "bonus",
            "name": "年终奖金",
            "description": "冒险家协会发年终奖了，你看着沉甸甸的钱袋，开心的笑了出来",
            "effect": {
                "gold": 3600
            }
        },
        {
            "id": "surprise_cash",
            "name": "意外现金",
            "description": "你在路边的电线杆下面见到了十块钱！",
            "effect": {
                "gold": 10
            }
        },
        {
            "id": "volunteer_reward",
            "name": "志愿奖励",
            "description": "你参与“是兄弟就来砍我”的志愿者活动，得到了一大笔钱，但是你是被砍的那个。",
            "effect": {
                "gold": 5000,
                "exp": 400,
                "hp": -500
            }
        },
        {
            "id": "spring",
            "name": "治疗泉水",
            "description": "偶遇治疗泉水，喝了一口，感觉精神好多了",
            "effect": {
                "exp": 80,
                "hp": 200
            }
        },
        {
            "id": "royal_grant",
            "name": "王室赐予",
            "description": "沼泽地的怪物入侵，你奋力搏杀，国王很赞赏你的英勇，赐予了你一把武器！",
            "effect": {
                "weapon": 1
            }
        },
        {
            "id": "stock_market_gain",
            "name": "股市获利",
            "description": "你的股票投资获得了显著回报，大赚一笔！",
            "effect": {
                "gold": 4000,
                "exp": 130
            }
        },
        {
            "id": "fortune_cookie",
            "name": "幸运饼干",
            "description": "你在餐馆里吃到了一张幸运饼干，获得奖金",
            "effect": {
                "gold": 500,
                "exp": 20
            }
        }
    ],
    "bad_events": [
        {
            "id": "tax",
            "name": "缴税",
            "description": "需要缴纳一些税款，记得申报专项扣除",
            "effect": {
                "gold": -1200
            }
        },
        {
            "id": "robbery",
            "name": "被偷窃",
            "description": "你的钱包被偷了,真是可恶！",
            "effect": {
                "gold": -3000
            }
        },
        {
            "id": "beaten",
            "name": "正义的被刺",
            "description": "有个阴暗的家伙偷偷给了你的腰子一刀，等你反应过来的时候他已经不见了，甚至偷走了你的钱包！",
            "effect": {
                "gold": -1000,
                "hp": -20
            }
        },
        {
            "id": "fall_ill",
            "name": "生病",
            "description": "你突然生病，需要支付医疗费用，我作证，这不是新冠肺炎",
            "effect": {
                "gold": -250,
                "hp": -30
            }
        },
        {
            "id": "job_lost",
            "name": "失业",
            "description": "因为经济不景气，你失去了工作，大环境不好啊~",
            "effect": {
                "gold": -250
            }
        },
        {
            "id": "natural_disaster",
            "name": "自然灾害",
            "description": "你遭遇了一场自然灾害，财产受损，天灾总数难以避免的...",
            "effect": {
                "gold": -500
            }
        },
        {
            "id": "theft",
            "name": "盗窃",
            "description": "你遭遇了扒手，损失了一些贵重物品，小偷果然最可恶了啊啊啊啊！",
            "effect": {
                "gold": -350,
                "lost_item": 1
            }
        },
        {
            "id": "legal_fine",
            "name": "法律罚款",
            "description": "你带着武器出席贵族舞会，违反了王国规定，你需要支付罚款。等待，误入白虎堂？",
            "effect": {
                "gold": -800
            }
        },
        {
            "id": "scam",
            "name": "诈骗",
            "description": "你被诈骗，损失了部分资金。兄弟，建议你赶紧下载国家反诈中心app",
            "effect": {
                "gold": -1000
            }
        }
    ]
}

# 全部鱼类
FISH_ITEMS = [
    ['海龙王', '我有时候真的会怕它打我一巴掌', 4500, 5],
    ['海龟', '可以拿来炖海龟汤，听说有个同名的推理游戏？', 800, 3],
    ['蓝鲸', '布什戈门，你说你用一根破木棍子把这玩意钓上来了？', 6000, 6],
    ['虎鲸', '虽然但是，虎鲸看起来真的很像一只巨型的奶牛猫，等等？你怎么把它钓上来的？', 6000, 6],
    ['海鲈', '清淡海鲈', 130, 2],
    ['大剑鲷鱼', '鲜活的鲷鱼(但愿任天堂不要来告我)', 100, 1],
    ['带鱼', '它简直长的离谱', 120, 2],
    ['翡翠螺', '相当漂亮，会是不错的装饰品', 75, 1],
    ['珍珠螺', '看起来很漂亮，可是它到底是怎么咬钩的？有人知道吗？', 140, 2],
    ['彩色珊瑚鱼', '色彩斑斓珊瑚鱼', 500, 3],
    ['鲨鱼', '听说鲨鱼的皮肤会用来排泄，所以它的肉肯定不好吃，当然我是猜的。', 600, 3],
    ['小丑鱼', '一条小丑鱼', 50, 1],
    ['海星', '只是一只普通的海星而已，等等，它是不是粉色的？？？？', 230, 2],
    ['海绵', '这块海绵居然还打着领带，难不成它也会做美味蟹黄堡？', 240, 2],
    ['石头', '为什么你会钓上来一块石头？从自己身上找找原因吧，孩子', 10, 1],
    ['鲫鱼', '普通的鲫鱼', 70, 1],
    ['鲈鱼', '适合清蒸', 100, 1],
    ['青鱼', '清爽的青鱼', 200, 2],
    ['鲍鱼', '这就拿去做佛跳墙', 800, 3],
    ['手枪虾', '兄弟，我劝你不要用手抓它', 500, 3],
    ['海参', '听说这玩意可以用屁股吃饭，真的假的？', 2000, 4],
    ['海胆', '新鲜海胆(这个世界上真的有人会吃海胆吗？)', 300, 2],
    ['海蜇', '清凉爽口的海蜇', 70, 1],
    ['比目鱼', '有谁记得鲁迅小时候的对子：“独角兽，比目鱼”', 120, 2],
    ['梭子蟹', '活梭子蟹', 400, 3],
    ['蛏子', '赶海的时候很容易搞到的小玩意', 90, 1],
    ['虾米', '小虾米就不要来侮辱我的鱼饵了', 50, 1],
    ['帝王蟹', '我儿蟹蟹有大帝之姿', 900, 3],
    ['鳗鱼', '香糯鳗鱼', 250, 2],
    ['海鳗', '长条海鳗', 280, 2],
    ['中华鲟', '牢底坐穿鱼', 600, 3],
    ['毛蟹', '毛茸茸毛蟹', 450, 3],
    ['石斑鱼', '周星驰的配音(bushi)', 320, 2],
    ['金枪鱼', '好吃！爱吃！！', 450, 3],
    ['大比目', '完全就是比目鱼啊，只是大了一些而已', 310, 3],
    ['海马', '听说海马都是父亲带孩子，就要男妈妈(bushi', 400, 3],
    ['海雀', '彩色海雀，好看捏~', 160, 2],
    ['琵琶虾', '弯曲琵琶虾', 130, 2],
    ['水母', '透明的水母，看起来就像是一只塑料袋', 75, 1],
    ['银鲹', '闪亮银鲹(这字儿到底怎么读？)', 100, 1],
    ['金鲳', '金色鲳鱼(ps:我没吃过)', 500, 3],
    ['龙虾', '它看起来似乎是用钳子夹住了你的鱼饵...', 85, 1],
    ['墨鱼', '有话好好说，别喷我一身', 500, 3],
    ['章鱼', '你老实跟我说，你跟克总什么关系？', 400, 3],
    ['珍珠贝', '光滑珍珠贝', 250, 2],
    ['紫菜', '新鲜的紫菜，听说烧汤很不错！', 10, 1],
    ['海螺', '为什么不问问神奇海螺呢？', 40, 1],
    ['海胆卵', '珍贵的海胆卵，虽然但是它到底有什么用？', 900, 3],
    ['海蛇', '一条可爱的海蛇，但是我有点怕它，你呢？', 290, 2],
    ['海马草', '这TM是鱼？', 500, 3],
    ['红珊瑚', '珊瑚中的红色品种', 750, 3],
    ['蓝珊瑚', '珊瑚中的蓝色品种', 800, 3],
    ['绿珊瑚', '珊瑚中的绿色品种', 700, 3],
    ['海狮', '别看它长得憨厚，其实会跳舞哦！', 300, 2],
    ['珊瑚虫', '彩色小虫，派对上的亮点', 150, 2],
    ['海葵', '会吐泡泡的花朵', 200, 2],
    ['海龙', '传说中的水中霸主', 5000, 5],
    ['双髻鲨', '拥有两顶小帽子的鲨鱼', 400, 3],
    ['灯笼鱼', '夜晚的水中小灯笼', 250, 2],
    ['河豚', '他要是一直鼓着，你就拿他刷鞋，很好用！', 350, 2],
    ['海象', '听说海象的牙很不错，但是你为什么能用鱼竿把它给钓上来？', 600, 3],
    ['螃蟹', '横行霸道的小甲壳', 120, 2],
    ['海牛', '如果你现在穿着狼人套装的话，它可能会被吓晕过去', 1000, 3],
    ['飞鱼', '它喊着勇气啊、羁绊啊什么的就从水里飞出来撞到了你的鱼钩...', 220, 2],
    ['氧气罐', '这一定是某个可怜的家伙留下的', 180, 2],
    ['海带', '多吃海带，对身体有好处', 60, 1],
    ['三叉戟', '海神的三叉戟，孩子，去称霸海洋吧！！！', 5000, 5],
    ['魔鬼鱼', '你把它翻过来，看看它是不是在笑', 1700, 4],
    ['一箱财宝', '里面装着阿兹特克的金币，你数了数，一共881枚，还有一枚在哪里呢？', 8810, 6],
    ['跳动的心脏', '没准这就是戴维琼斯的', 7777, 6],
    ['金色义腿', '打开看看，里面或许装着朗姆酒', 2200, 4],
    ['罗盘', '或许它可以带你去你梦想的任何地方', 6666, 6],
    ['瓶子', '看起来是个普通的瓶子，等等，瓶子里好像装着一艘黑色大船！', 6666, 6],
    ['一包花生', '我想猴子和鹦鹉会喜欢的', 400, 3],
    ['巨大的黑色触手', '快跑！是克拉肯！！！', 3333, 5],
    ['会哭的箱子', '获取你得把它放在船身外侧，它的泪水随时可以灌满甲板', 3000, 4]
]

# 商店常驻物品
SHOP_ITEMS = [
    ['面包', 'consumable', '闻起来香香的', 25, 1, {'hp': 50}],
    ['药水', 'consumable', '出门必备的小药水', 50, 1, {'hp': 100}],
    ['急救包', 'consumable', '出事儿了就得靠它', 150, 2, {'hp': 300}],
    ['治疗卷轴', 'consumable', '麻瓜总是很难理解卷轴上的符文到底是怎么发挥作用的', 200, 3, {'hp': 400}],
    ['原素瓶', 'consumable', '不死人的果粒橙', 500, 4, {'hp': 1000}],
    ['杰克的酒', 'consumable', '卡塔利纳的杰克·巴尔多赠予的酒，非常好喝！', 1000, 5, {'hp': 2000}],
    ['女神的祝福', 'consumable', '来自太阳长女葛温德林的祝福', 2000, 6, {'hp': 9999}, 6],
    ['木制鱼竿', 'fishing_rod', '非常普通的木制鱼竿', 1000, 1, {'lucky': 0.5, 'gold_bonus': 0.3, 'exp_bonus': 0.3, 'durability': 100}],
    ['铁制鱼竿', 'fishing_rod', '铁制的鱼竿，很耐用', 3000, 1, {'lucky': 0.5, 'gold_bonus': 0.3, 'exp_bonus': 0.6, 'durability': 500}],
    ['金制鱼竿', 'fishing_rod', '纯金打造的鱼竿，会让你变得非常幸运', 8000, 1, {'lucky': 0.9, 'gold_bonus': 0.9, 'exp_bonus': 0.9, 'durability': 1000}],
]
