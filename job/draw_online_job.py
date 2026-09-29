import logging

from cache.script_cache import ScriptCache
from const.draw_const import DrawConst
from db.session import create_session
from exceptions.exceptions import BusinessError
from service.draw_service import DrawService
from tool.date_utils import DateUtils

logger = logging.getLogger(__name__)


class DrawJobOnline:

    @staticmethod
    def draw_online():
        now_time = DateUtils.get_current_datetime()
        logger.info(f"draw online job start. {now_time}")

        key = "draw_online"
        if not ScriptCache().acquire_task_lock(key):
            logger.info(f"任务正在运行中: {key} {now_time}")
            return

        db = create_session()
        try:
            task_list = DrawService.draw_list(db, DrawConst.NOT_STARTED)

            if not task_list or len(task_list) <= 0:
                logger.info(f"没有待处理的任务: {key} {now_time}")
                return

            for v in task_list:
                cur_date = DateUtils.get_current_datetime()
                if v.offline_time > cur_date >= v.start_time:
                    try:
                        DrawService.draw_online(db, v.id)
                        logger.info(f"活动id: {v.id} 活动名称: {v.draw_name} "
                                    f"start_time: {v.start_time} offline_time: {v.offline_time} 更新为上线")
                    except BusinessError as e:
                        logger.error(f"update draw online task error: {str(e)}")
                        continue

            logger.info("draw online job end.")
        except Exception as e:
            logger.error(f"get online error: {str(e)}")
        finally:
            ScriptCache().delete_task_lock(key)
            db.close()

    @staticmethod
    def run():
        DrawJobOnline.draw_online()
