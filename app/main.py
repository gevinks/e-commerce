from fastapi import FastAPI, status
from app.router import product
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings


def create_application():
    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version,
        docs_url=settings.docs_url,
        redoc_url=settings.redocs_url
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    app.include_router(
        product.router,
        prefix=settings.api_prefix
    )

    return app

app = create_application()

@app.get("/")
def read_root():
    return {
        "message": "Welcome to E-commerce App",
        "version": "0.1",
        "docs_url": "/docs",
        "redoc_url": "/redocs"
    }

@app.get("/health")
def health_check():
    return {
        "status_code": status.HTTP_200_OK,
        "status": "OK",
        "message": "E-commerce app is running fine."
    }