# ChatGPT on WeChat: 游戏娱乐插件介绍

欢迎来到 **ChatGPT on WeChat** 的游戏娱乐插件！这个插件为用户提供了丰富多彩的游戏体验，包括钓鱼、大富翁模式、经济系统和等级系统。无论你是喜欢休闲游戏还是寻求娱乐，这里都有适合你的活动。

## 更新日志

**V0.2.3 (2025-01-12)**
- 添加充值功能
- 添加下注功能
- 打怪练级和大富翁分解为两个行为：外出、冒险
- 添加多种道具
- 添加多种怪场景和怪物
- 数值平衡

**V0.2.2 (2024-12-01)**
- 修复一系列绑定ID导致的bug
- 修复装备伤害重叠的bug

**V0.2.1 (2024-11-25)**
- 重构用户系统为ID绑定机制
- 修复强制攻击装备显示异常
- 修复大富翁租金计算问题

**V0.2.0 (2024-11-20)**
- 将外出探险模式更新为大富翁模式
- 新增多人互动功能
- 优化游戏币获取机制


## 如何开始

1. **安装插件**：在微信中搜索并添加 ChatGPT on WeChat 插件。
   ```
   #installp git@github.com:Sakura7301/game.git
   ```
2. **配置插件**：请务必在 ChatGPT on WeChat 的配置文件中设置 `hot_reload = true`，以确保插件能够正常运行。
3. **配置管理员**: 程序运行之后你需要修改`plugins/game/data/config.json`文件中的`admins`字段来将管理员的微信昵称添加进去，例如：
   ```json
   {
     "admins": ["小明", "小红"]
   }
   ```
4. **开始游戏**：参见游戏指令说明文档，开始游戏吧。

---

## 🎮 游戏指令说明文档

欢迎来到游戏世界！本游戏支持丰富的指令操作，涵盖基础功能、物品管理、冒险玩法、社交互动等多个方面。通过使用这些指令，你可以探索游戏的无限可能性！

---

### 📖 目录

1. [基础指令](#基础指令)
2. [物品相关指令](#物品相关指令)
3. [交易相关指令](#交易相关指令)
4. [冒险相关指令](#冒险相关指令)
5. [地产相关指令](#地产相关指令)
6. [社交系统指令](#社交系统指令)
7. [其他功能指令](#其他功能指令)
8. [管理员功能指令](#管理员功能指令)
9. [使用示例](#使用示例)

---

### 基础指令

基础指令是玩家日常操作的核心功能，用于注册账号、查看状态、每日签到等。

| 指令         | 功能描述                 |
|--------------|--------------------------|
| 📝 **注册**   | 注册新玩家，开始游戏冒险 |
| 📊 **状态**   | 查看当前玩家状态信息     |
| 📅 **签到**   | 每日签到领取金币奖励     |

---

### 物品相关指令

物品相关指令用于管理游戏中的物品，包括查看商店、购买、使用和赠送物品等。

| 指令                                      | 功能描述                           |
|-------------------------------------------|------------------------------------|
| 🏪 **商店**                               | 查看商店中的物品列表               |
| 💰 **购买 [物品名]**                      | 购买指定物品                       |
| 🎒 **背包**                               | 查看玩家背包中的物品               |
| ⚔️ **装备 [物品名]**                      | 装备指定物品                       |
| 🎁 **赠送 [@用户] [物品名] [数量]**       | 向其他玩家赠送指定物品             |
| 💊 **使用 [物品名]**                      | 使用背包中的消耗品                 |

---

### 交易相关指令

交易相关指令用于出售物品、批量处理背包物品以及参与下注玩法。

| 指令                                     | 功能描述                           |
|------------------------------------------|------------------------------------|
| 💸 **出售 [物品名] [数量]**              | 出售指定物品，售价为原价的 80%     |
| 📦 **批量出售 [类型]**                   | 批量出售背包中指定类型的物品       |
| 🎲 **下注 [大/小/顺子/豹子] 数额**          | 参与下注玩法，根据押注类型进行赌局 |

---

### 冒险相关指令

冒险相关指令是游戏的核心玩法之一，包括钓鱼、冒险、打怪升级等。

| 指令                     | 功能描述                           |
|--------------------------|------------------------------------|
| 🎣 **钓鱼**              | 进行钓鱼获取金币或其他道具         |
| 📖 **图鉴**              | 查看钓鱼获得的鱼类图鉴             |
| 🌄 **外出**              | 外出探索，开始大富翁游戏           |
| 🤺 **冒险**              | 进行冒险，打怪升级                 |
| 👊 **攻击 [@用户]**       | 攻击其他玩家，触发战斗             |
| 🗺️ **地图**              | 查看游戏地图，了解地形与位置         |

---

### 地产相关指令

地产相关指令用于管理玩家的地产系统，包括购买、升级地块等。

| 指令                     | 功能描述                           |
|--------------------------|------------------------------------|
| 🏠 **我的地产**          | 查看玩家当前拥有的地产             |
| 🏘️ **购买地块**          | 购买新的地块                       |
| 🏘️ **升级地块**          | 升级已有地块，提高收益             |

---

### 社交系统指令

社交系统指令用于与其他玩家互动，包括求婚、赠送物品、解除婚姻关系等。

| 指令                     | 功能描述                           |
|--------------------------|------------------------------------|
| 💕 **求婚 [@用户]**       | 向指定玩家求婚                     |
| 💑 **同意求婚**           | 同意求婚请求，建立婚姻关系         |
| 💔 **拒绝求婚**           | 拒绝求婚请求                       |
| ⚡️ **离婚**              | 解除婚姻关系                       |

---

### 其他功能指令

其他功能指令包括排行榜、提醒设置等实用工具。

| 指令                     | 功能描述                           |
|--------------------------|------------------------------------|
| 🏆 **排行榜 [类型]**      | 查看指定类型的排行榜               |
| 🔔 **提醒 [内容]**        | 设置提醒事项                       |
| 🗑️ **删除提醒**           | 删除已设置的提醒                   |

---

### 管理员功能指令

管理员功能指令仅限管理员使用，用于管理游戏系统，包括开关机、充值、设置定时任务等。

| 指令                                      | 功能描述                           |
|-------------------------------------------|------------------------------------|
| 🔧 **开机**                               | 开启游戏系统                       |
| 🔧 **关机**                               | 关闭游戏系统                       |
| 💴 **充值 [@用户] 数额**                  | 为指定用户充值金币                 |
| ⏰ **定时 [开机/关机] [时间] [每天]**     | 设置系统定时任务                   |
| 📋 **查看定时**                           | 查看当前设置的定时任务             |
| ❌ **取消定时 [开机/关机] [时间]**        | 取消指定的定时任务                 |
| 🗑️ **清空定时**                           | 清空所有定时任务                   |

---

### 使用示例

以下是一些常见指令的使用示例：

1. **注册新玩家**
```
注册
```

2. **每日签到**
```
签到
```

3. **购买物品**
```
购买 钓鱼竿
```

4. **赠送物品**
```
赠送 @小明 钓鱼竿 1
```

5. **冒险打怪**
```
冒险
```

6. **攻击其他玩家**
```
攻击 @小红
```

7. **查看排行榜**
```
排行榜 冒险
排行榜 等级
```

8. **管理员充值**
```
充值 @玩家A 1000
```

---


#### 结语

无论你是想放松心情，还是享受竞技乐趣，**ChatGPT on WeChat** 的游戏娱乐插件都能为你提供无尽的欢乐。快来加入我们，开启你的游戏之旅吧！

祝你游戏愉快！ 🎮
