from app.main import app
from fastapi import APIRouter

router = APIRouter(
    prefix= "/products",
    tags= ["products"],
    responses= {
        404: {
            "description": "Not Found"
        },
        500: {
            "description": "Internal Server Error"
        }
    }
)

@router.get("/")
def get_products():
    pass

@router.get("/{product_id}")
def get_product_by_id():
    pass

@router.post("/")
def create_product():
    pass

@router.put("/{product_id}")
def modify_product():
    pass

@router.patch("/{product_id}/stock")
def update_product_stock():
    pass

@router.delete("/{product_id}")
def delete_product():
    pass
