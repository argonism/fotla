from typing import Any, Dict

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .encoder import Retriever


def start_api(retriever: Retriever, host: str = "0.0.0.0", port: int = 8000) -> None:
    app = load_fastapi_app(retriever)
    origins = [
        "http://localhost:5173",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    uvicorn.run(
        app,
        host=host,
        port=port,
    )


def load_fastapi_app(retriever: Retriever) -> FastAPI:
    app = FastAPI()
    setup_api_endpoint(app, retriever)
    return app


def setup_api_endpoint(app: FastAPI, retriever: Retriever) -> None:
    class SearchRequest(BaseModel):
        query: str
        topk: int = 100

    @app.post("/search")
    async def search(request: SearchRequest) -> Dict[str, Any]:
        result = retriever.retrieve([request.query], request.topk)
        return {"status": "success", "result": result}