from typing import Any

from job.draw_offline_job import DrawJobOffline
from job.draw_online_job import DrawJobOnline
from job.draw_reconcile_job import DrawJobReconcile


def job_route() -> dict[str, Any]:
    return {
        "draw_online_task": DrawJobOnline.run,
        "draw_offline_task": DrawJobOffline.run,
        "draw_reconcile_task": DrawJobReconcile.run,
    }
