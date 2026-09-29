import random
import copy
from typing import Optional

from schema.draw_prize_schema import DrawPrizeConfig


class DrawUtils:
    """
    抽奖逻辑工具类
    """

    def __init__(self, prizes_config, draw_counter=0, guarantee_count=5):
        """
        初始化抽奖系统
        :param prizes_config: 奖项配置列表，格式示例：
            [
                {"id": "1", "draw_name": "一等奖", "probability": 1, "stock": 1, "is_guaranteed": 0},
                {"id": "2", "draw_name": "二等奖", "probability": 5, "stock": 1, "is_guaranteed": 0},
                {"id": "3", "draw_name": "三等奖", "probability": 20, "stock": 1, "is_guaranteed": 0},
                {"id": "4", "draw_name": "谢谢参与", "probability": 74, "stock": 1, "is_guaranteed": 1}
            ]
        :param guarantee_count: 硬保底次数（抽多少次未中奖时，必中一个库存充足的奖项）
        """
        self.prizes = copy.deepcopy(prizes_config)  # 原始配置（用于重置）
        self.current_prizes = copy.deepcopy(prizes_config)  # 当前运行时数据
        self.guarantee_count = guarantee_count
        self.draw_counter = draw_counter  # 记录当前连续未中奖（或未中大奖）的次数

    def _get_available_prizes(self):
        """获取当前库存大于0的奖项列表"""
        return [p for p in self.current_prizes if p['stock'] > 0]

    def _calculate_total_weight(self, available):
        """计算可用奖项的总权重"""
        return sum(p['probability'] for p in available)

    def _force_guarantee(self):
        """
        保底逻辑：优先寻找"谢谢参与"或权重最大的低价值奖项作为保底奖品。
        如果没有保底奖品，则返回 None（表示奖池已空）。
        """
        available = self._get_available_prizes()
        if not available:
            return None

        # is_guaranteed=1为兜底奖品
        for p in available:
            if p['is_guaranteed'] == 1:
                return p

    def draw(self) -> Optional[DrawPrizeConfig]:
        """
        执行一次抽奖
        :return: dict 中奖结果，包含 id, name, probability, stock 等字段；若奖池为空返回 None
        """

        # 冗余代码注释
        # self.draw_counter += 1

        # ---------- 第一步：硬保底触发 ----------
        # 如果达到了保底次数（比如抽了5次还没中过任何奖），强制命中兜底
        if self.draw_counter >= self.guarantee_count:
            guarantee_prize = self._force_guarantee()
            if guarantee_prize and guarantee_prize['stock'] > 0:
                # 保底命中
                result = guarantee_prize.copy()
                return DrawPrizeConfig.model_validate(result)
            else:
                # 连保底奖都没库存了，说明奖池彻底空了
                return None

        # ---------- 第二步：常规权重随机抽取 ----------
        available = self._get_available_prizes()
        if not available:
            return None  # 所有奖品抽完了

        total_weight = self._calculate_total_weight(available)
        # 生成一个 [0, total_weight) 之间的随机浮点数
        rand_val = random.random() * total_weight

        # 遍历奖项，计算累积权重，判断随机数落在哪个区间
        cumulative = 0
        for prize in available:
            cumulative += prize['probability']
            if rand_val <= cumulative:
                # 命中该奖项
                result = prize.copy()
                return DrawPrizeConfig.model_validate(result)

        # 理论上不会走到这里，但防御性编程
        return None


# if __name__ == "__main__":
#     # 1. 配置奖项（权重总和不必等于100，系统自动按比例计算）
#     config = [
#         {"id": "1", "draw_name": "星巴克复古白绿系列马克杯350ml", "probability": 5, "stock": 10, "is_guaranteed": 0},
#         {"id": "2", "draw_name": "阿迪达斯SUPERSTAR II经典贝壳头板鞋", "probability": 5, "stock": 10, "is_guaranteed": 0},
#         {"id": "3", "draw_name": "巴黎圣日尔曼26/27赛季主场球衣", "probability": 5, "stock": 10, "is_guaranteed": 0},
#         {"id": "4", "draw_name": "iphone17 薰衣草紫色 256G", "probability": 1, "stock": 10, "is_guaranteed": 0},
#         {"id": "5", "draw_name": "HUAWEI Pura X Max", "probability": 1, "stock": 10, "is_guaranteed": 0},
#         {"id": "6", "draw_name": "谢谢惠顾", "probability": 83, "stock": 1000, "is_guaranteed": 0},
#         {"id": "7", "draw_name": "10元红包", "probability": 0, "stock": 1000, "is_guaranteed": 1}
#     ]
#
#     # 2. 初始化系统，设置硬保底为 10 次
#     draw = DrawUtils(prizes_config=config, draw_counter=5, guarantee_count=5)
#
#     draw_prize = draw.draw()
#     print(draw_prize)
#     print(draw_prize.draw_name)
