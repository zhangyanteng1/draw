from sqlalchemy import update, bindparam, insert
from sqlalchemy.orm import Session
from model.draw_prize import DrawPrize
from schema.draw_prize_schema import DrawPrizeReq, DrawPrizeUpdate


class DrawPrizeDao:

    @staticmethod
    def batch_upsert(db: Session, draw_prize_list: list[DrawPrizeReq]) -> int:
        insert_list = [p.model_dump(exclude={'id'}) for p in draw_prize_list if not p.id]
        update_list = [p.model_dump() for p in draw_prize_list if p.id]

        count = 0

        if insert_list:
            db.execute(insert(DrawPrize), insert_list)
            count += len(insert_list)

        if update_list:
            stmt = (
                update(DrawPrize)
                .where(DrawPrize.id == bindparam('id'))
                .values({
                    DrawPrize.prize_name: bindparam('prize_name'),
                    DrawPrize.prize_sku: bindparam('prize_sku'),
                    DrawPrize.prize_type: bindparam('prize_type'),
                    DrawPrize.is_guaranteed: bindparam('is_guaranteed'),
                    DrawPrize.prize_price: bindparam('prize_price'),
                    DrawPrize.prize_inventory: bindparam('prize_inventory'),
                    DrawPrize.draw_prize_status: bindparam('draw_prize_status'),
                    DrawPrize.reduce_inventory: bindparam('reduce_inventory'),
                    DrawPrize.prize_picture: bindparam('prize_picture'),
                    DrawPrize.probability: bindparam('probability'),
                    DrawPrize.up_id: bindparam('up_id'),
                })
            )
            result = db.execute(stmt, update_list, execution_options={"synchronize_session": False})
            count += result.rowcount

        return count

    @staticmethod
    def get_by_draw_id(db: Session, draw_id: int) -> list[DrawPrize]:
        return db.query(DrawPrize).filter(DrawPrize.draw_id == draw_id).all()

    @staticmethod
    def get_by_draw_prize(db: Session, draw_id: int, prize_sku: str) -> DrawPrize:
        query = db.query(DrawPrize).filter(DrawPrize.draw_id == draw_id
                                           ).filter(DrawPrize.prize_sku == prize_sku)

        return query.first()

    @staticmethod
    def update(db: Session, draw_prize: DrawPrize, draw_prize_update: DrawPrizeUpdate) -> DrawPrize:
        for field, value in draw_prize_update.model_dump(exclude_unset=True).items():
            setattr(draw_prize, field, value)
        return draw_prize

    @staticmethod
    def reduce_inventory_atomic(db: Session, draw_id: int, prize_sku: str) -> int:
        """原子条件扣减已消耗库存: 仅当 prize_inventory - reduce_inventory > 0 时 +1。返回影响行数"""
        stmt = (
            update(DrawPrize)
            .where(DrawPrize.draw_id == draw_id)
            .where(DrawPrize.prize_sku == prize_sku)
            .where(DrawPrize.prize_inventory - DrawPrize.reduce_inventory > 0)
            .values(reduce_inventory=DrawPrize.reduce_inventory + 1)
        )
        result = db.execute(stmt, execution_options={"synchronize_session": False})
        return result.rowcount

    @staticmethod
    def restore_inventory_atomic(db: Session, draw_id: int, prize_sku: str) -> int:
        """回滚已消耗库存: reduce_inventory - 1 (仅当 >0)。返回影响行数"""
        stmt = (
            update(DrawPrize)
            .where(DrawPrize.draw_id == draw_id)
            .where(DrawPrize.prize_sku == prize_sku)
            .where(DrawPrize.reduce_inventory > 0)
            .values(reduce_inventory=DrawPrize.reduce_inventory - 1)
        )
        result = db.execute(stmt, execution_options={"synchronize_session": False})
        return result.rowcount

