import argparse
import functools
import logging
import uuid

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, EVENT_JOB_MISSED
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from script.job_route import job_route
from tool.date_utils import DateUtils
from tool.logging_config import setup_root_logging, setup_script_logging, setup_service_logging, trace_id_var
from tool.yaml_utils import get_app_config


logger = logging.getLogger(__name__)

_conf = get_app_config("script")
_route = job_route()


def _wrap(func):
    """统一包裹 job 函数: 在执行体入口 set trace_id。

    ContextVar 不跨线程继承, APScheduler 线程池中执行 job 时需在此重新 set,
    使该线程后续日志(job 自身 + 调用的 service 层)带上同一 trace_id。
    统一在调度入口/手动触发处包裹, 新增 job 无需改 job 代码即自动具备链路追踪。
    trace_id 用 uuid4().hex, 与请求链路(x-request-id)格式一致。

    用 token 模式 + finally reset 清理: APScheduler 的 ThreadPoolExecutor 会复用线程,
    任务结束后若不 reset, 线程归还线程池后该 trace_id 残留, 线程被复用跑下个任务、
    在新任务 set 之前若打到日志, 会串到上一个任务的 trace_id, 链路错乱。
    """

    @functools.wraps(func)
    def inner(*args, **kwargs):
        token = trace_id_var.set(uuid.uuid4().hex)
        try:
            return func(*args, **kwargs)
        finally:
            trace_id_var.reset(token)

    return inner


# 预包裹路由: 各入口(调度器/手动触发)共用, 保证 trace_id 注入行为一致
_wrapped_route = {name: _wrap(func) for name, func in _route.items()}


# python -m script.main -o
def run_once(task_name: str):
    func = _wrapped_route.get(task_name)
    if func is None:
        logger.error(f"未找到任务: {task_name}，可用任务: {list(_wrapped_route.keys())}")
        return
    logger.info(f"手动执行任务: {task_name}")
    func()


def _on_job_event(event):
    """任务调度事件监听器: 记录每次任务运行日志(格式: 任务名 cron run 时间)"""
    job_id = event.job_id
    run_time = DateUtils.date_to_str(DateUtils.get_current_datetime(), "%Y-%m-%d %H:%M:%S")
    if event.code == EVENT_JOB_EXECUTED:
        logger.info(f"{job_id} cron run {run_time}")
    elif event.code == EVENT_JOB_ERROR:
        logger.error(f"{job_id} cron run {run_time} error", exc_info=event.exception)
    elif event.code == EVENT_JOB_MISSED:
        logger.warning(f"{job_id} cron run {run_time} missed")


def run_scheduler():
    scheduler_conf = _conf.get("scheduler")
    task_conf = _conf.get("cron")
    route = _wrapped_route

    executors = {"default": ThreadPoolExecutor(max_workers=scheduler_conf["max_workers"])}
    scheduler = BlockingScheduler(executors=executors)

    scheduler.add_listener(
        _on_job_event,
        EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_MISSED,
    )

    for key, conf in task_conf.items():
        func = route.get(key)
        if func is None:
            logger.warning("未找到任务: %s，跳过", key)
            continue
        scheduler.add_job(
            func,
            CronTrigger.from_crontab(conf["cron_expr"]),
            id=str(conf["task_id"]),
            max_instances=conf["max_instances"],
            misfire_grace_time=conf["misfire_grace_time"],
            coalesce=conf["coalesce"],
        )
        logger.info(f"注册任务: {key}, cron={conf['cron_expr']}")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")


def main():
    setup_root_logging()
    setup_script_logging()
    setup_service_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", dest="task_name", default=None, help="手动执行指定任务")
    args = parser.parse_args()

    if args.task_name:
        run_once(args.task_name)
    else:
        run_scheduler()


if __name__ == "__main__":
    main()
