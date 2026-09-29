from sqlalchemy.orm import Session
from dao.draw_dao import DrawDao
from dao.draw_prize_dao import DrawPrizeDao
from dao.prize_dao import PrizeDao
from exceptions.exceptions import BusinessError
from schema.draw_prize_schema import DrawPrizeCreateList, DrawPrizeReq, DrawPrizeUpdateList, DrawPrizeConfig, \
    DrawPrizesConfigList


class DrawPrizeService:

    @staticmethod
    def save_draw_prize(db: Session, draw_prize_create_list: DrawPrizeCreateList, user_id: int):
        draw_id = draw_prize_create_list.draw_id
        if not draw_id:
            raise BusinessError("未关联抽奖活动")

        draw_prize_list = DrawPrizeService.check_draw_prize(db, draw_id,
                                                            draw_prize_create_list.draw_prize_list,
                                                            op_id=user_id)

        if draw_prize_list:
            DrawPrizeDao.batch_upsert(db, draw_prize_list)
            db.commit()

    @staticmethod
    def update_draw_prize(db: Session, draw_prize_update_list: DrawPrizeUpdateList, user_id: int):
        draw_id = draw_prize_update_list.draw_id

        if not draw_id:
            raise BusinessError("未关联抽奖活动")

        draw_prize_list = DrawPrizeService.check_draw_prize(db, draw_id,
                                                            draw_prize_update_list.draw_prize_list,
                                                            up_id=user_id)

        if draw_prize_list:
            DrawPrizeDao.batch_upsert(db, draw_prize_list)
            db.commit()

    @staticmethod
    def check_draw_prize(db: Session, draw_id: int, draw_prize_list: list[DrawPrizeReq],
                         op_id: int = None, up_id: int = None) -> list[DrawPrizeReq]:

        # 判断抽奖活动是否存在
        draw = DrawDao.get_by_draw_id(db, draw_id)
        if not draw:
            raise BusinessError("抽奖活动不存在")

        if not draw_prize_list or len(draw_prize_list) <= 0:
            raise BusinessError("奖品不能为空")

        # 新增时根据draw_id判断是否已有正在进行中的活动
        if op_id:
            draw_prizes = DrawPrizeDao.get_by_draw_id(db, draw_id)
            if draw.status == 2 and draw_prizes:
                raise BusinessError(f"{draw.draw_name}该进行中的活动已关联奖品")

        # 新增：进行中的活动不能修改
        if up_id:
            if draw.status == 2:
                raise BusinessError("该活动正在进行中不能修改")

        is_guaranteed_count = 0

        probability_count = 0

        prize_list = []

        # 判断关联的奖品sku是否存在
        for draw_prize in draw_prize_list:

            # 如果创建 设置创建人和设置奖品id
            if op_id:
                # 设置创建人
                draw_prize.op_id = op_id
                # 设置奖品id
                draw_prize.draw_id = draw_id

            # 如果更新，设置更新人id
            if up_id:
                draw_prize.up_id = up_id
                # 更新需要过滤传过来下架的商品,  更新的逻辑：用户下架奖品不调用接口，由前端将状态置为2做提交
                if draw_prize.draw_prize_status == 2:
                    continue

            prize = PrizeDao.get_by_sku(db, draw_prize.prize_sku)

            if not prize:
                raise BusinessError(f"{draw_prize.prize_name}({draw_prize.prize_sku})奖品不存在")

            if prize.remaining_stock <= 0:
                raise BusinessError(f"{draw_prize.prize_name}({draw_prize.prize_sku})奖品可用库存不足")

            if draw_prize.prize_inventory <= 0:
                raise BusinessError(f"{draw_prize.prize_name}({draw_prize.prize_sku})没有设置奖品库存")

            if draw_prize.prize_inventory > prize.remaining_stock:
                raise BusinessError(f"{draw_prize.prize_name}({draw_prize.prize_sku})奖品库存大于可用库存")

            if draw_prize.prize_sku in prize_list:
                raise BusinessError("包含重复的奖品")

            # 判断设置的已消耗库存不能大于奖品库存
            if draw_prize.reduce_inventory and draw_prize.reduce_inventory > draw_prize.prize_inventory:
                raise BusinessError("已消耗库存不能大于奖品库存")

            # 允许为0，永远抽不中
            if draw_prize.probability is None:
                raise BusinessError("奖品概率不能为空")

            if draw_prize.is_guaranteed == 1:
                is_guaranteed_count += 1

            # 兜底奖品不算概率
            if draw_prize.is_guaranteed != 1:
                probability_count += draw_prize.probability

                prize_list.append(draw_prize.prize_sku)

        if len(prize_list) > 6:
            raise BusinessError("奖品不能大于6个")

        if is_guaranteed_count < 1:
            raise BusinessError("没有配置兜底奖品")

        if is_guaranteed_count > 1:
            raise BusinessError("兜底商品只能包含一个")

        if probability_count != 10000:
            raise BusinessError("分配的概率总和必须为10000")

        return draw_prize_list



