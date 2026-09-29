import logging

from cache.script_cache import ScriptCache
from db.session import create_session
from service.draw_service import DrawService
from tool.date_utils import DateUtils
from tool.logging_config import setup_root_logging, setup_script_logging, setup_service_logging

logger = logging.getLogger(__name__)


class DrawJobReconcile:

    @staticmethod
    def draw_reconcile():
        now_time = DateUtils.get_current_datetime()
        logger.info(f"draw reconcile job start {now_time}")

        key = "draw_reconcile"
        if not ScriptCache().acquire_task_lock(key):
            logger.info(f"任务正在运行中: {key} {now_time}")
            return

        db = create_session()
        try:
            result = DrawService.reconcile_draw_stock(db)
            logger.info(f"draw reconcile job end. result={result}")
        except Exception as e:
            logger.error(f"draw reconcile error: {e}")
        finally:
            ScriptCache().delete_task_lock(key)
            db.close()

    @staticmethod
    def run():
        DrawJobReconcile.draw_reconcile()


if __name__ == '__main__':
    setup_root_logging()
    setup_script_logging()
    setup_service_logging()
    # 复用调度入口的包裹逻辑, 保证直接跑文件也注入 trace_id
    from script.main import run_once
    run_once("draw_reconcile_task")
