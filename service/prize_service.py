import random
import string

from sqlalchemy.orm import Session

from dao.prize_dao import PrizeDao
from exceptions.exceptions import BusinessError
from schema.prize_schema import PrizeCreate, PrizeUpdate
from tool.date_utils import DateUtils


class PrizeService:

    @staticmethod
    def generate_sku(prize_type: int) -> str:
        date_part = DateUtils.get_current_datetime().strftime('%y%m%d')
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"P{prize_type}-{date_part}-{random_part}"

    @staticmethod
    def save_prize(db: Session, prize_create: PrizeCreate, user_id: int):
        if not prize_create.prize_name:
            raise BusinessError("奖品名称不能为空")

        if not prize_create.prize_type:
            raise BusinessError("奖品类型不能为空")

        if not prize_create.prize_sku:
            prize_create.prize_sku = PrizeService.generate_sku(prize_create.prize_type)
        else:
            existing = PrizeDao.get_by_sku(db, prize_create.prize_sku)
            if existing:
                raise BusinessError("奖品SKU已存在")

        if not prize_create.description:
            raise BusinessError("商品描述不能为空")

        if prize_create.remaining_stock and prize_create.remaining_stock > prize_create.total_stock:
            raise BusinessError("剩余库存不能大于总库存")

        # remaining_stock可用库存没传 默认等于total_stock总库存
        if not prize_create.remaining_stock:
            prize_create.remaining_stock = prize_create.total_stock

        prize_create.op_id = user_id
        PrizeDao.insert(db, prize_create)
        db.commit()

    @staticmethod
    def update_prize(db: Session, prize_id: int, prize_update: PrizeUpdate, user_id: int):
        prize = PrizeDao.get_by_id(db, prize_id)
        if not prize:
            raise BusinessError("奖品不存在")

        prize_update.up_id = user_id
        PrizeDao.update(db, prize, prize_update)
        db.commit()

    @staticmethod
    def delete_prize(db: Session, prize_id: int):
        prize = PrizeDao.get_by_id(db, prize_id)
        if not prize:
            raise BusinessError("奖品不存在")
        PrizeDao.delete(db, prize)
        db.commit()
