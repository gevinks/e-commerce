from app.main import app

@app.get("/products")
def get_products():
    pass

@app.get("/products/{product_id}")
def get_product_from_id(product_id: int):
    pass

@app.post("/products")
def post_product(request):
    pass

@app.put("/products/{product_id}")
