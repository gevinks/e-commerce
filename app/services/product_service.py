from sqlalchemy.orm import Session
from app.models.product import ProductCreate, ProductResponse, ProductUpdate
from app.database.models import Product
from sqlalchemy.exc import SQLAlchemyError, DatabaseError
from typing import Optional, List
from app.services.product_service_errors import *


class ProductService:

    def __init__(self, db_session: Session):
        self.db = db_session

    def create_product(self, product_data: ProductCreate) -> ProductResponse:
        try:
            new_product = Product(
                name=product_data.name,
                price=product_data.price,
                description=product_data.description,
                stock_quantity=product_data.stock_quantity
            )

            self.db.add(new_product)
            self.db.commit()
            self.db.refresh(new_product)

            self._handle_post_creation_logic(new_product)
            
            return self._convert_to_response(new_product)
        
        except ProductServiceError as pse:
            raise pse
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(f"Database Operation failed: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ProductServiceError(f"Unexcpected error during product creation: {str(e)}")

    
    def get_products(
            self,
            skip:int = 0,
            limit:int = 0,
            active_only:bool = True,
            search_term:Optional[str] = None
    ) -> List[ProductResponse]:
        
        try:
            query = self.db.query(Product)

            if (active_only):
                query = query.filter(Product.is_active == True)

            if (search_term):
                search_pattern = f"%{search_term}%"
                query = query.filter(
                    (Product.name.ilike(search_pattern)) |
                    (Product.description.ilike(search_pattern))
                )
            
            safe_limit = min(limit, 100)

            products = query.offset(skip).limit(safe_limit).all()

            return [self._convert_to_response(product) for product in products]
        
        except SQLAlchemyError as sqe:
            raise DatabaseError(f"Failed to retrieve products: {str(sqe)}")
        
    def get_product_by_id(
            self,
            product_id:int,
            active_only:bool = True,
    ) -> ProductResponse:
        try:
            query = self.db.query(Product).filter(Product.id == product_id)

            if (active_only):
                query = query.filter(Product.is_active == True)

            product = query.first()

            if not product:
                if active_only:
                    raise ProductNotFoundError(f"Active product with {product_id} not found")
                else:
                    raise ProductNotFoundError(f"Product with {product_id} not found")
                
            return self._convert_to_response(product)
        
        except ProductNotFoundError as e:
            raise
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to retrieve product from db: {str(e)}")
        
    def update_product(
            self,
            product_id:int,
            product_data:ProductUpdate,
    ) -> ProductResponse:
        
        try:
            existing_product = self.db.query(Product).filter(Product.id == product_id).first()

            if not existing_product:
                raise ProductNotFoundError(f"Product with product id {product_id} not found")
            
            update_data = product_data.model_dump(exclude_unset=True)

            if not update_data:
                return self._convert_to_response(existing_product)
            
            self._validate_product_update_rules(existing_product, update_data)

            for field, value in update_data.items():
                setattr(existing_product, field, value)

            self.db.commit()
            self.db.refresh(existing_product)

            return self._convert_to_response(existing_product)

        except (ProductNotFoundError, ProductServiceError):
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to update product: {str(e)}")
        
    def delete_product(
            self,
            product_id:int,
            soft_delete: bool = True
    ):
        try:
            existing_product = self.db.query(Product).filter(Product.id == product_id).first()

            if not existing_product:
                raise ProductNotFoundError(f"Product with id:{product_id} not found")
            
            self._validate_product_deletion_rules(existing_product)

            if soft_delete:
                existing_product.is_active = False
                self.db.commit()
                self.db.refresh(existing_product)

                return {
                    "message": f"Product '{existing_product.name}' soft deleted successfully.",
                    "product_id": {product_id},
                    "deletion_type": "soft",
                    "recoverable": True,
                    "product_name": existing_product.name
                }

            else:
                product_name = existing_product.name
                self.db.delete(existing_product)
                self.db.commit()

                return {
                    "message": f"Product '{product_name}' soft deleted successfully.",
                    "product_id": {product_id},
                    "deletion_type": "hard",
                    "recoverable": False,
                    "product_name": product_name
                }

        except (ProductNotFoundError, ProductDeletionError):
            raise
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to delete product: {str(e)}")
        
    def update_product_stock(
            self,
            product_id:int,
            stock_adjustment:int
    ) -> ProductResponse:
        try:
            product = self.db.query(Product).filter(Product.id == product_id).first()

            if not product:
                raise ProductNotFoundError(f"Product with id:{product_id} not found")
            
            new_stock = product.stock_quantity + stock_adjustment

            if new_stock < 0:
                raise InvalidStockOperationError(
                    f"Cannot reduce stock by {abs(stock_adjustment)}."
                    f"Current stock number: {product.stock_quantity}."
                )
            
            if new_stock > 100000:
                raise InvalidStockOperationError(
                    f"Cannot increase stock by {abs(stock_adjustment)}."
                    f"Stock adjustment too high."
                )

            product.stock_quantity = new_stock
            self.db.commit()
            self.db.refresh(product)

            return self._convert_to_response(product)
        
        except (InvalidStockOperationError, ProductNotFoundError):
            raise
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to update product stock with id {product_id}: {str(e)}")
        
    def _validate_product_creation_rules(
            self,
            product_data:ProductCreate
    ) -> None:
        
        reserved_names = ["admin", "system", "test", "demo", "null", "undefined"]

        if product_data.name.lower() in reserved_names:
            raise ProductServiceError(
                f"Product name '{product_data.name}' is reserved and cannot be used"
            )
        if product_data.price < 0.01:
            raise ProductServiceError(
                "Product price must be greater than 0.01"
            )
        
        if product_data.price > 100000:
            raise ProductServiceError(
                "Product price exceeds mas limit"
            )
        
        existing_product = self.db.query(Product).filter(
            Product.name.ilike(product_data.name),
            Product.is_active == True
            ).first()
        
        if existing_product:
            raise ProductService(
                f"An active product with name '{product_data.name}' already exists."
            )
        
    def _validate_product_update_rules(
            self,
            existing_product: Product,
            update_data: dict
    ) -> None:
        
        if "price" in update_data:
            new_price = update_data["price"]
            if new_price < existing_product*0.5:
                raise ProductServiceError(
                    f"Price reduction is greater than 50%."
                    f"Exceeds 50% limit. Requires approval"
                )
            
        if "name" in update_data:
            reserved_name = ["admin", "system", "test", "demo"]
            if update_data["name"].lower() in reserved_name:
                raise ProductServiceError(
                    f"Cannot change product name to '{update_data["name"]}'"
                )
            
    def _validate_product_deletion_rules(self, product: Product) -> None:

        if product.stock_quantity > 0:
            raise ProductDeletionError(
                f"Cannot delete product '{product.name}' with remaining stocks"
                f"Clear inventory first or use stock adjustments."
            )
        
    def _handle_post_creation_logic(self, product:Product) -> None:
        print(f"Product created: '{product.name}' (ID: {product.id}) at {product.price}")

    def _convert_to_response(self, product:Product) -> ProductResponse:
        return ProductResponse(
            id=product.id,
            name=product.name,
            price=product.price,
            description=product.description,
            stock_quantity=product.description,
            is_active=product.is_active,
            created_at=product.created_at,
            updated_at=product.updated_at
        )