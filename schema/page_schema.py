from pydantic import BaseModel


class PageModel(BaseModel):
    """分页"""
    page: int = 1
    page_size: int = 10


class Total(BaseModel):
    """数据总数"""
    total: int = 0
