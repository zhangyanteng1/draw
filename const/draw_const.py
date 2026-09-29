class DrawConst:

    """抽奖状态枚举"""
    NOT_STARTED = 1   # 未开始
    IN_PROGRESS = 2   # 进行中
    ENDED = 3         # 已结束
    OFFLINE = 4       # 已下线

    """ 未抽中奖品sku 谢谢惠顾 """
    # 此 sku 对应数据库中预置的「谢谢参与」奖品记录，为固定种子（提前生成、固定不变）。
    # 若重建种子数据，需保证该奖品记录的 prize_sku 与本常量保持一致，否则未中奖判断会静默失效。
    NOT_WIN_PRIZE_SKU = "P4-260723-QD67"

    """领取状态枚举"""
    PENDING = 0  # 未领取
    CLAIMED = 1  # 已领取
    EXPIRED = 2  # 已过期

    """ 抽中状态 """
    DRAW_WIN = 1      # 抽中
    DRAW_LOSE = 0     # 未抽中


