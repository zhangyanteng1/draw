import logging

from cache.script_cache import ScriptCache
from const.draw_const import DrawConst
from db.session import create_session
from exceptions.exceptions import BusinessError
from service.draw_service import DrawService
from tool.date_utils import DateUtils
from tool.logging_config import setup_root_logging, setup_service_logging, setup_script_logging

logger = logging.getLogger(__name__)


class DrawJobOffline:

    @staticmethod
    def draw_offline():
        now_time = DateUtils.get_current_datetime()
        logger.info(f"draw offline job start. {now_time}")

        key = "draw_offline"
        if not ScriptCache().acquire_task_lock(key):
            logger.info(f"任务正在运行中: {key} {now_time}")
            return

        db = create_session()
        try:
            task_list = DrawService.draw_list(db, DrawConst.IN_PROGRESS)

            if not task_list or len(task_list) <= 0:
                logger.info(f"没有待处理的任务: {key} {now_time}")
                return

            for v in task_list:
                # 重新获取当前时间防止数据量过大存在时差
                cur_date = DateUtils.get_current_datetime()
                if cur_date >= v.offline_time:
                    try:
                        DrawService.draw_offline(db, v.id)
                        logger.info(f"活动id: {v.id} 活动名称: {v.draw_name} "
                                    f"start_time: {v.start_time} offline_time: {v.offline_time} 更新为下线")
                    except BusinessError as e:
                        logger.error(f"update draw offline task error: {e}")
                        continue

            logger.info("draw offline job end.")
        except Exception as e:
            logger.error(f"get offline error: {e}")
        finally:
            ScriptCache().delete_task_lock(key)
            db.close()

    @staticmethod
    def run():
        DrawJobOffline.draw_offline()


if __name__ == '__main__':
    setup_root_logging()
    setup_script_logging()
    setup_service_logging()
    # 复用调度入口的包裹逻辑, 保证直接跑文件也注入 trace_id
    from script.main import run_once
    run_once("draw_offline_task")
