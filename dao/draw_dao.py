from typing import Optional
from sqlalchemy.orm import Session
from model.draw import Draw
from schema.draw_schema import DrawCreate, DrawFilter, DrawUpdate


class DrawDao:

    @staticmethod
    def insert(db: Session, draw_create: DrawCreate) -> Draw:
        draw = Draw(**draw_create.model_dump())
        db.add(draw)
        db.flush()
        db.refresh(draw)
        return draw

    @staticmethod
    def get_by_draw_id(db: Session, draw_id: int) -> Optional[Draw]:
        return db.query(Draw).filter(Draw.id == draw_id).first()

    @staticmethod
    def query_draw_list(db: Session, draw_filter: DrawFilter) -> list[Draw]:
        query = db.query(Draw).order_by(Draw.id.desc())
        if draw_filter.id:
            query = query.filter(Draw.id == draw_filter.id)

        if draw_filter.status:
            query = query.filter(Draw.status == draw_filter.status)

        return query.all()

    @staticmethod
    def update(db: Session, draw: Draw, draw_update: DrawUpdate) -> Optional[Draw]:
        for field, value in draw_update.model_dump(exclude_unset=True).items():
            setattr(draw, field, value)
        return draw
