import logging

from fastapi import APIRouter, Depends, HTTPException, status
from schemas.product import ProductCreate, ProductResponse
from db.session import get_db
from models.product import Product,TypeProduct

from sqlalchemy.orm import Session

router = APIRouter()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@router.post("/create-product",response_model=ProductResponse,status_code=status.HTTP_201_CREATED)
def create_product(payload:ProductCreate,db:Session = Depends(get_db)) -> Product:
    product = Product(
        name=payload.name,
        presentation=payload.presentation,
        stock=payload.stock,
        type=payload.type
    )
    db.add(product)
    db.commit()
    logger.info("Producto creado exitosmente")
    db.refresh(product)
    return product

@router.get("/list-products",response_model=ProductResponse,status_code=status.HTTP_200_OK)
def list_products(skip: int=0,limit: int=20,db:Session = Depends(get_db)):
    return db.query(ProductResponse).offset(skip).limit(limit).all()

@router.get("/{product_id}",response_model=ProductResponse,status_code=status.HTTP_200_OK)
def get_product(product_id:int,db:Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404,detail="Product not found")
    return product

@router.put("/{product_id}",response_model=ProductResponse,status_code=status.HTTP_200_OK)
def update_product(product_id:int,data:ProductResponse,db:Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404,detail="Product not found")
    product.name = data.name
    db.commit()
    logger.info("Producto actualizado exitosamente.")
    return product

@router.delete("/{product_id}",response_model=ProductResponse,status_code=status.HTTP_200_OK)
def delete_product(product_id:int,db:Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id)
    if not product:
        raise HTTPException(status_code=404,detail="Product not Found")
    db.delete(product)
    db.commit()
    logger.info("Producto eliminado exitosamente")
    
