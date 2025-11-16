from app.main import app
from fastapi import status

@app.get('/health')
def health_check():
    return {
        "status_code": status.HTTP_200_OK,
        "status": "OK",
        "message": "E-commerce API is running smoothly."
    }
