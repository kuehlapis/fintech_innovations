# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from controllers.analyse_controller import router as analyse_router
from controllers.auth_controller import router as auth_router
from controllers.dashboard_controller import router as dashboard_router
from controllers.portfolio_controller import router as portfolio_router
from controllers.transactions_controller import router as transactions_router

app = FastAPI(title="OneWealth")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(portfolio_router, prefix="/api")
app.include_router(transactions_router, prefix="/api")
app.include_router(analyse_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}