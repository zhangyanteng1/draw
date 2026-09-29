import logging
from collections import namedtuple
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from cache.draw_cache import DrawCache
from const.draw_cache_key import DrawCacheKey
from const.draw_const import DrawConst
from dao.draw_dao import DrawDao
from dao.draw_prize_dao import DrawPrizeDao
from dao.prize_dao import PrizeDao
from dao.user_dao import UserDao
from dao.user_draw_dao import UserDrawDao
from dao.user_draw_log_dao import UserDrawLogDao
from dao.user_draw_prize_dao import UserDrawPrizeDao
from exceptions.exceptions import BusinessError
from model.draw import Draw
from model.draw_prize import DrawPrize
from model.user_draw import UserDraw
from model.user_draw_log import UserDrawLog
from model.user_draw_prize import UserDrawPrize
from schema.draw_prize_schema import DrawPrizeConfig, DrawPrizesConfigList
from schema.draw_schema import DrawCreate, DrawUpdate, DrawFilter
from schema.user_draw_log_schema import UserDrawLogFilter
from schema.user_draw_schema import UserDrawFilter, UserDrawAdd
from tool.date_utils import DateUtils
from tool.draw_utils import DrawUtils
from tool.string_utils import StringUtils

# 预占结果: reserved=是否成功预占(供异常时回滚), stock_key=预占的Redis键, result=最终结果(可能已降级)
PrizeReservation = namedtuple("PrizeReservation", ["reserved", "stock_key", "result"])

logger = logging.getLogger(__name__)


class DrawService:

    @staticmethod
    def save_draw(db: Session, draw_create: DrawCreate, user_id: int):
        if StringUtils.is_none(draw_create.draw_name):
            raise BusinessError("抽奖名称不能为空")

        DrawService.check_draw_date(draw_create.start_time, draw_create.offline_time)

        draw_create.op_id = user_id

        DrawDao.insert(db, draw_create)
        db.commit()

    @staticmethod
    def update_draw(db: Session, draw_id: int, draw_update: DrawUpdate, user_id: int):
        draw = DrawDao.get_by_draw_id(db, draw_id)
        if not draw:
            raise BusinessError("抽奖活动不存在")

        if StringUtils.is_none(draw_update.draw_name):
            raise BusinessError("抽奖名称不能为空")

        # 传了开始时间 或 下线时间时 对时间做校验
        if draw_update.start_time or draw_update.offline_time:
            DrawService.check_draw_date(draw_update.start_time, draw_update.offline_time)

        draw_update.up_id = user_id

        DrawDao.update(db, draw, draw_update)
        db.commit()

    @staticmethod
    def draw_offline(db: Session, draw_id: int, user_id: int = None):
        draw = DrawDao.get_by_draw_id(db, draw_id)
        if not draw:
            raise BusinessError("抽奖活动不存在")
        draw_update = DrawUpdate(
            status=DrawConst.OFFLINE,
            up_id=user_id
        )

        DrawDao.update(db, draw, draw_update)
        db.commit()

    @staticmethod
    def draw_online(db: Session, draw_id: int, user_id: int = None):
        draw = DrawDao.get_by_draw_id(db, draw_id)
        if not draw:
            logger.error(f"活动id: {draw_id} 抽奖活动不存在")
            raise BusinessError("抽奖活动不存在")
        if draw.status == DrawConst.ENDED:
            logger.error(f"活动id: {draw.id} 活动名称: {draw.draw_name} "
                         f"start_time: {draw.start_time} offline_time: {draw.offline_time} 已结束活动不能上线")
            raise BusinessError("已结束活动不能上线")
        now_time = DateUtils.get_current_datetime()
        if draw.offline_time < now_time:
            logger.error(f"活动id: {draw.id} 活动名称: {draw.draw_name} "
                         f"offline_time: {draw.offline_time} now_time: {now_time} 抽奖活动已结束")
            raise BusinessError("抽奖活动已结束")

        # 新增 未关联奖品不允许上线
        draw_prize = DrawPrizeDao.get_by_draw_id(db, draw_id)
        if not draw_prize:
            logger.error(f"活动id: {draw.id} 活动名称: {draw.draw_name} 该抽奖活动未关联奖品")
            raise BusinessError("该抽奖活动未关联奖品")

        draw_update = DrawUpdate(
            status=DrawConst.IN_PROGRESS,
            up_id=user_id
        )

        DrawDao.update(db, draw, draw_update)
        db.commit()

        # 上线时初始化奖品 Redis 库存(幂等: 仅当 key 不存在时设置)
        ttl = max(int((draw.offline_time - now_time).total_seconds()), 1)
        DrawService.init_draw_prize_stock(draw_id, draw_prize, ttl)

    @staticmethod
    def draw_list(db: Session, status: int) -> Optional[list[Draw]]:
        if status:
            draw_filter = DrawFilter(
                status=status
            )
            return DrawDao.query_draw_list(db, draw_filter=draw_filter)
        return None

    @staticmethod
    def check_draw_date(start_time: datetime, offline_time: datetime):
        if not start_time:
            raise BusinessError("抽奖开始时间不能为空")

        if not offline_time:
            raise BusinessError("抽奖下线时间不能为空")

        start_time = DateUtils.datetime_to_timestamp(start_time)
        offline_time = DateUtils.datetime_to_timestamp(offline_time)

        now_timestamp = DateUtils.get_current_timestamp()

        if offline_time < now_timestamp:
            raise BusinessError("抽奖结束时间不能小于当前时间")

        if start_time >= offline_time:
            raise BusinessError("抽奖下线时间不能早于开始时间")

    # 抽奖逻辑
    @staticmethod
    def draw_get(db: Session, draw_id: int, user_id: int) -> Optional[DrawPrizeConfig]:

        # 并发控制, 不允许连续重复抽取
        draw_cache = DrawCache()
        draw_lock_key = DrawCacheKey.draw_cache_lock % (str(draw_id), str(user_id))
        if not draw_cache.acquire_user_draw_lock(key=draw_lock_key):
            raise BusinessError("操作太快,请勿重复抽取")

        reserved = False
        stock_key = None

        try:
            # reserved = False
            # stock_key = None

            # 校验活动
            draw_prize_list = DrawService.check_draw(db, draw_id)

            # 校验用户资格
            user_draw = DrawService.check_user_qualification(db, user_id, draw_id)

            # 获取用户最近5次抽奖记录, 连续5次抽不中需要走兜底
            draw_counter = DrawService.get_user_draw_log_five(db, user_id, draw_id)

            # 进行抽奖
            result = DrawService.draw(draw_prize_list, draw_counter)
            if result is None:
                # 奖池已空(所有奖品库存耗尽)
                raise BusinessError("奖池已抽完,感谢参与")

            # 预占库存(三层: Redis + draw_prize + 全局), 抢不到则降级谢谢参与
            reserved, stock_key, result = DrawService.reserve_prize_stock(
                draw_cache, db, draw_id, draw_prize_list, result
            )

            # 写入抽奖日志(此时 result 已最终确定)
            user_draw_log = DrawService.save_user_draw_log(db, user_id, draw_id, result)
            if not user_draw_log:
                logger.error("抽奖日志写入异常")
                db.rollback()
                if reserved:
                    draw_cache.release_stock(stock_key)
                raise RuntimeError("抽奖日志写入异常")

            # 抽中真实奖品: 写获奖记录(库存已在预占阶段扣减)
            if result.prize_sku != DrawConst.NOT_WIN_PRIZE_SKU:
                DrawService.save_user_draw_prize(db, user_draw_log, result)

            # 记录已使用抽奖次数
            DrawService.update_user_draw_used_times(db, user_draw)

            db.commit()
            return result
        except BusinessError:
            # 业务校验异常(次数已用完/活动已下线/奖池已空/操作太快等)交由全局处理器返回友好提示
            db.rollback()
            if reserved:
                draw_cache.release_stock(stock_key)
            raise
        except Exception as e:
            # 内部异常: 记录后上抛, 走全局处理器返回"服务器内部错误"
            logger.error(f"抽奖出现错误: {str(e)}", exc_info=True)
            db.rollback()
            if reserved:
                draw_cache.release_stock(stock_key)
            raise
        finally:
            # 无论成功/失败/异常, 抽奖结束都释放锁
            draw_cache.delete_user_draw_lock(draw_lock_key)

    @staticmethod
    def check_draw(db: Session, draw_id: int) -> list[DrawPrize]:

        # 校验抽奖活动是否存在
        draw = DrawDao.get_by_draw_id(db, draw_id)

        # 获取当前时间
        now_time = DateUtils.get_current_datetime()

        if not draw:
            raise BusinessError("抽奖活动不存在")

        if draw.status != DrawConst.IN_PROGRESS or draw.offline_time <= now_time:
            raise BusinessError("抽奖活动未开始或已下线")

        # 查询奖品
        draw_prize_list = DrawPrizeDao.get_by_draw_id(db, draw_id)

        if not draw_prize_list:
            raise BusinessError("没有配置抽奖奖品")

        return draw_prize_list

    @staticmethod
    def check_user_qualification(db: Session, user_id: int, draw_id: int) -> Optional[UserDraw]:

        # 查询用户
        user = UserDao.get_by_user_id(db, user_id)
        if not user:
            raise BusinessError("用户不存在")

        # 查询用户抽奖资格和次数
        user_draw_filter = UserDrawFilter(
            user_id=user_id,
            draw_id=draw_id
        )
        user_draw = UserDrawDao.get_by_user_draw(db, user_draw_filter)

        if not user_draw:
            raise BusinessError("无抽奖资格")

        if user_draw.total_quota <= user_draw.used_times:
            raise BusinessError("抽奖次数已用完")

        return user_draw

    @staticmethod
    def get_user_draw_log_five(db: Session, user_id: int, draw_id: int) -> int:
        # 获取用户近5次抽奖记录
        user_draw_log_filter = UserDrawLogFilter(
            user_id=user_id,
            draw_id=draw_id,
            page=1,
            page_size=5
        )
        # is_win = False
        draw_counter = 0

        user_draw_log_list, total = UserDrawLogDao.query_user_draw_list(db, user_draw_log_filter)

        # 取用户最近5次的抽奖记录， 如果记录数小于5次直接跳过
        if user_draw_log_list and total >= 5:
            for user_draw_log in user_draw_log_list:

                # is_win=1代表抽中, 近5次抽中记录包含获奖记录就终止不走兜底
                if user_draw_log.is_win == DrawConst.DRAW_WIN:
                    draw_counter = 0
                    return draw_counter
                draw_counter += 1

        return draw_counter

    @staticmethod
    def draw(draw_prize_list: list[DrawPrize], draw_counter: int) -> Optional[DrawPrizeConfig]:
        # 进行抽奖
        prizes_config = []

        for item in draw_prize_list:
            draw_prize_config = DrawPrizeConfig.model_validate(item).model_dump()
            # 计算可用库存
            stock = item.prize_inventory - item.reduce_inventory
            if stock <= 0:
                draw_prize_config['stock'] = 0
            else:
                draw_prize_config['stock'] = stock

            prizes_config.append(draw_prize_config)

        draw_utils = DrawUtils(prizes_config=prizes_config, draw_counter=draw_counter)

        # 获取抽奖结果
        result = draw_utils.draw()

        return result

    @staticmethod
    def init_draw_prize_stock(draw_id: int, draw_prize_list: list[DrawPrize], ttl: int):
        """上线时把每个真实奖品的可用库存写入 Redis(谢谢参与不预占, 跳过)"""
        draw_cache = DrawCache()
        for draw_prize in draw_prize_list:
            if draw_prize.prize_sku == DrawConst.NOT_WIN_PRIZE_SKU:
                continue
            stock = draw_prize.prize_inventory - draw_prize.reduce_inventory
            if stock < 0:
                stock = 0
            stock_key = DrawCacheKey.draw_prize_stock % (str(draw_id), draw_prize.prize_sku)
            draw_cache.init_stock(stock_key, stock, ex=ttl)

    @staticmethod
    def get_prize_available_stock(draw_prize_list: list[DrawPrize], prize_sku: str) -> int:
        """从已加载的奖品配置中取某 sku 的当前可用库存(供 Redis 自愈兜底值)"""
        for draw_prize in draw_prize_list:
            if draw_prize.prize_sku == prize_sku:
                stock = draw_prize.prize_inventory - draw_prize.reduce_inventory
                return stock if stock > 0 else 0
        return 0

    @staticmethod
    def build_not_win_result(draw_prize_list: list[DrawPrize]) -> DrawPrizeConfig:
        """降级: 构造谢谢参与结果"""
        for draw_prize in draw_prize_list:
            if draw_prize.prize_sku == DrawConst.NOT_WIN_PRIZE_SKU:
                return DrawPrizeConfig.model_validate(draw_prize)
        return DrawPrizeConfig(prize_sku=DrawConst.NOT_WIN_PRIZE_SKU, draw_name="谢谢参与")

    @staticmethod
    def reserve_prize_stock(draw_cache: DrawCache, db: Session, draw_id: int,
                            draw_prize_list: list[DrawPrize], result: DrawPrizeConfig) -> PrizeReservation:
        """
        三层预占库存: Redis -> draw_prize -> 全局 remaining_stock。
        全部成功: reserved=True, 携带 stock_key 供异常时回滚。
        任一层抢不到: 回退已扣减层并降级为谢谢参与, reserved=False。
        (谢谢参与视为无限, 不预占)
        """
        # 谢谢参与视为无限, 不预占
        if result.prize_sku == DrawConst.NOT_WIN_PRIZE_SKU:
            return PrizeReservation(False, None, result)

        stock_key = DrawCacheKey.draw_prize_stock % (str(draw_id), result.prize_sku)
        db_available = DrawService.get_prize_available_stock(draw_prize_list, result.prize_sku)
        not_win_result = DrawService.build_not_win_result(draw_prize_list)

        # 第一层: Redis 预占
        if not draw_cache.reserve_stock(stock_key, db_available):
            logger.info(f"奖品预占失败, 降级谢谢参与: draw_id={draw_id} sku={result.prize_sku}")
            return PrizeReservation(False, None, not_win_result)

        # 第二层: draw_prize 原子扣减
        if not DrawService.update_draw_prize_reduce_inventory(db, result.prize_sku, draw_id):
            draw_cache.release_stock(stock_key)
            logger.warning(f"draw_prize 库存扣减失败, 降级谢谢参与: draw_id={draw_id} sku={result.prize_sku}")
            return PrizeReservation(False, None, not_win_result)

        # 第三层: 全局 remaining_stock 原子扣减(跨活动共享sku的最终权威)
        if not DrawService.update_prize_remaining_stock(db, result.prize_sku):
            DrawService.restore_draw_prize_inventory(db, result.prize_sku, draw_id)
            draw_cache.release_stock(stock_key)
            logger.warning(f"全局库存耗尽, 降级谢谢参与: draw_id={draw_id} sku={result.prize_sku}")
            return PrizeReservation(False, None, not_win_result)

        return PrizeReservation(True, stock_key, result)

    @staticmethod
    def save_user_draw_log(db: Session, user_id: int, draw_id: int, result: DrawPrizeConfig) -> UserDrawLog:
        user_draw_log = UserDrawLog()
        user_draw_log.user_id = user_id
        user_draw_log.draw_id = draw_id
        user_draw_log.draw_time = DateUtils.get_current_datetime()
        user_draw_log.prize_name = result.draw_name
        user_draw_log.prize_sku = result.prize_sku

        if result.prize_sku != DrawConst.NOT_WIN_PRIZE_SKU:
            user_draw_log.is_win = 1

        return UserDrawLogDao.insert(db, user_draw_log)

    @staticmethod
    def save_user_draw_prize(db: Session, user_draw_log: UserDrawLog, result: DrawPrizeConfig):
        user_draw_prize = UserDrawPrize()

        user_draw_prize.user_id = user_draw_log.user_id
        user_draw_prize.draw_id = user_draw_log.draw_id

        user_draw_prize.draw_prize_id = result.id
        user_draw_prize.prize_sku = user_draw_log.prize_sku

        user_draw_prize.status = DrawConst.CLAIMED
        user_draw_prize.draw_time = user_draw_log.draw_time

        # 当前业务场景抽中会立即发放, 领取时间暂时为抽奖时间
        user_draw_prize.claim_time = user_draw_log.draw_time

        # 过期时间同抽奖活动时间
        draw = DrawDao.get_by_draw_id(db, user_draw_log.draw_id)
        user_draw_prize.expire_time = draw.offline_time

        UserDrawPrizeDao.insert(db, user_draw_prize)

    @staticmethod
    def update_user_draw_used_times(db: Session, user_draw: UserDraw):

        if user_draw:
            used_times = user_draw.used_times + 1

            user_draw_add = UserDrawAdd(
                user_id=user_draw.user_id,
                draw_id=user_draw.draw_id,
                total_quota=user_draw.total_quota,
                used_times=used_times
            )
            UserDrawDao.update(db, user_draw, user_draw_add)

    @staticmethod
    def update_draw_prize_reduce_inventory(db: Session, prize_sku_id: str, draw_id: int) -> bool:
        """原子条件扣减 draw_prize 已消耗库存; 仅当有可用库存时成功。返回是否扣减成功"""
        rowcount = DrawPrizeDao.reduce_inventory_atomic(db, draw_id, prize_sku_id)
        return rowcount > 0

    @staticmethod
    def restore_draw_prize_inventory(db: Session, prize_sku_id: str, draw_id: int):
        """回滚 draw_prize 已消耗库存(全局库存不足时的补偿)"""
        DrawPrizeDao.restore_inventory_atomic(db, draw_id, prize_sku_id)

    @staticmethod
    def update_prize_remaining_stock(db: Session, prize_sku_id: str) -> bool:
        """原子条件扣减全局奖品剩余库存(不会为负); 库存已耗尽返回 False"""
        rowcount = PrizeDao.reduce_remaining_stock_atomic(db, prize_sku_id)
        if rowcount == 0:
            logger.warning(f"全局奖品剩余库存已耗尽: sku={prize_sku_id}")
        return rowcount > 0

    @staticmethod
    def reconcile_draw_stock(db: Session) -> dict:
        """
        对账: 对齐「进行中活动」的 Redis 库存计数器与 DB 可用库存。
        漂移来源是崩溃/网络导致的 Redis 与 DB 跨存储非原子扣减, 二者无法进同一事务, 只能事后修复。
        修复采用 DELETE 而非写值: 删除后由抽奖自愈逻辑在下一次抽奖时用 DB 权威值重建, 方向无关、无竞态。
        key 缺失不视为漂移(自愈兜底, 功能正确), 仅记录日志便于排查。
        :return: {"checked": 检查的奖品key数, "drifted": 发现的漂移数, "fixed": 成功修复数}
        """
        checked = 0
        drifted = 0
        fixed = 0

        draw_cache = DrawCache()

        # 仅对进行中的活动对账
        draw_list = DrawDao.query_draw_list(db, DrawFilter(status=DrawConst.IN_PROGRESS))
        if not draw_list:
            return {"checked": 0, "drifted": 0, "fixed": 0}

        for draw in draw_list:
            draw_prize_list = DrawPrizeDao.get_by_draw_id(db, draw.id)
            if not draw_prize_list:
                continue

            for draw_prize in draw_prize_list:
                # 谢谢参与不预占库存, 跳过
                if draw_prize.prize_sku == DrawConst.NOT_WIN_PRIZE_SKU:
                    continue

                db_available = draw_prize.prize_inventory - draw_prize.reduce_inventory
                if db_available < 0:
                    db_available = 0

                stock_key = DrawCacheKey.draw_prize_stock % (str(draw.id), draw_prize.prize_sku)
                redis_stock = draw_cache.get_stock(stock_key)
                checked += 1

                # key 缺失: 抽奖自愈会用 DB 值重建, 不算漂移
                if redis_stock is None:
                    logger.info(f"对账: Redis 库存 key 缺失, 交由抽奖自愈重建 "
                                f"draw_id={draw.id} sku={draw_prize.prize_sku} db_available={db_available}")
                    continue

                if redis_stock != db_available:
                    drifted += 1
                    logger.warning(f"对账发现库存漂移: draw_id={draw.id} sku={draw_prize.prize_sku} "
                                   f"redis={redis_stock} db={db_available} 差值={db_available - redis_stock}")
                    if draw_cache.delete_stock(stock_key):
                        fixed += 1
                        logger.info(f"对账已修复(删除 key 交由自愈重建): draw_id={draw.id} sku={draw_prize.prize_sku}")
                    else:
                        logger.error(f"对账修复失败: draw_id={draw.id} sku={draw_prize.prize_sku}")

        return {"checked": checked, "drifted": drifted, "fixed": fixed}
