from fastapi import FastAPI, status
from app.router import product
from fastapi.middleware.cors import CORSMiddleware


def create_application():
    app = FastAPI(
        title="E-commerce",
        description="Backend for e-commerce",
        version="0.0.1",
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