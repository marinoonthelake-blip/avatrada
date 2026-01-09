from fastapi import APIRouter
from celery.result import AsyncResult
from celery_worker.tasks import run_backtest
from src.core.celery_app import celery_app

router = APIRouter(prefix="/backtest", tags=["Backtesting"])

@router.post("/start")
async def start_backtest(strategy: str, days: int = 30):
    task = run_backtest.delay(strategy, days)
    return {"task_id": task.id, "status": "SUBMITTED"}

@router.get("/status/{task_id}")
async def get_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)

    response = {
        "task_id": task_id,
        "status": task_result.state,
        "result": task_result.result if task_result.ready() else None
    }

    if task_result.state == 'PROGRESS':
        response["progress"] = task_result.info.get('progress', 0)

    return response
