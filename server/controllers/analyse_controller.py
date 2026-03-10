from fastapi import APIRouter

from services.analysis_service import AnalysisService

router = APIRouter(prefix="/analyse", tags=["analyse"])
analysis_service = AnalysisService()


@router.post("/run/{user_id}")
async def run_analysis(user_id: str, query: str = ""):
    return await analysis_service.run_and_persist(user_id=user_id, raw_text=query)


@router.get("/history/{user_id}")
def get_history(user_id: str):
    return {"runs": analysis_service.get_history(user_id)}


@router.get("/latest/{user_id}")
def get_latest(user_id: str):
    return {"latest": analysis_service.get_latest(user_id)}