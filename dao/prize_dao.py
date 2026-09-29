from typing import Optional

from sqlalchemy import update
from sqlalchemy.orm import Session

from model.prize import Prize
from schema.prize_schema import PrizeCreate, PrizeFilter, PrizeUpdate


class PrizeDao:

    @staticmethod
    def insert(db: Session, prize_create: PrizeCreate) -> Prize:
        prize = Prize(**prize_create.model_dump())
        db.add(prize)
        db.flush()
        db.refresh(prize)
        return prize

    @staticmethod
    def get_by_id(db: Session, prize_id: int) -> Optional[Prize]:
        return db.query(Prize).filter(Prize.id == prize_id).first()

    @staticmethod
    def get_by_sku(db: Session, prize_sku: str) -> Optional[Prize]:
        return db.query(Prize).filter(Prize.prize_sku == prize_sku).first()

    @staticmethod
    def query_list(db: Session, prize_filter: PrizeFilter) -> list[Prize]:
        query = db.query(Prize).order_by(Prize.id.desc())
        if prize_filter.id:
            query = query.filter(Prize.id == prize_filter.id)
        if prize_filter.prize_type:
            query = query.filter(Prize.prize_type == prize_filter.prize_type)
        if prize_filter.status:
            query = query.filter(Prize.status == prize_filter.status)
        if prize_filter.prize_sku:
            query = query.filter(Prize.prize_sku == prize_filter.prize_sku)
        return query.all()

    @staticmethod
    def update(db: Session, prize: Prize, prize_update: PrizeUpdate) -> Prize:
        for field, value in prize_update.model_dump(exclude_unset=True).items():
            setattr(prize, field, value)
        return prize

    @staticmethod
    def delete(db: Session, prize: Prize) -> None:
        db.delete(prize)

    @staticmethod
    def reduce_remaining_stock_atomic(db: Session, prize_sku: str) -> int:
        """原子条件扣减剩余库存: 仅当 remaining_stock > 0 时 -1, 不会为负。返回影响行数"""
        stmt = (
            update(Prize)
            .where(Prize.prize_sku == prize_sku)
            .where(Prize.remaining_stock > 0)
            .values(remaining_stock=Prize.remaining_stock - 1)
        )
        result = db.execute(stmt, execution_options={"synchronize_session": False})
        return result.rowcount


