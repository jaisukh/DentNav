from contextlib import asynccontextmanager

import braintrust
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.analysis import router as analysis_router
from app.api.v1.auth import router as auth_router
from app.api.v1.questionnaire import router as questionnaire_router
from app.config import settings
from app.db.session import engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.braintrust_api_key:
        braintrust.init_logger(
            project_id="ba5e81e6-1dd0-4aaa-ad2a-94ead1fc5bb6",
            api_key=settings.braintrust_api_key,
        )
    yield
    await engine.dispose()


app = FastAPI(title="DentNav Backend API", version="0.1.0", lifespan=lifespan)

_default_origins = [
    "http://localhost:3000",
    "https://dentnav.vercel.app",
    "https://dentnav-production.up.railway.app",
]
_allow_origins = list(dict.fromkeys([*_default_origins, *settings.cors_origins]))

_cors_kwargs = {
    "allow_origins": _allow_origins,
    "allow_origin_regex": settings.cors_origin_regex_effective,
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
    "expose_headers": ["X-Removed-Stale-Questionnaire"],
}
app.add_middleware(CORSMiddleware, **_cors_kwargs)


@app.get("/health")
async def health() -> dict[str, bool]:
    return {"ok": True}



app.include_router(questionnaire_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
