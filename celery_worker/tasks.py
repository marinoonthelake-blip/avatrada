import time
from src.core.celery_app import celery_app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@celery_app.task(bind=True)
def run_backtest(self, strategy_name: str, days: int):
    """
    Simulates a long-running backtest task.
    """
    task_id = self.request.id
    logger.info(f"Starting backtest {task_id} for {strategy_name} over {days} days.")

    # Simulate processing steps
    total_steps = 5
    for i in range(total_steps):
        time.sleep(1) # Simulate CPU work
        progress = int((i + 1) / total_steps * 100)
        self.update_state(state='PROGRESS', meta={'progress': progress})
        logger.info(f"Backtest progress: {progress}%")

    return {
        "strategy": strategy_name,
        "days": days,
        "sharpe_ratio": 1.85,
        "total_return": 12.5,
        "status": "COMPLETED"
    }
