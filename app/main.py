from fastapi import FastAPI, status

app = FastAPI()

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