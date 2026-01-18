from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.products import Product as ProductModel
from app.models.categories import Category as CategoryModel
from app.schemas import Product as ProductSchema, ProductCreate
from app.db_depends import get_async_db


router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductSchema])
async def get_all_products(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех активных товаров.
    """
    result = await db.scalars(select(ProductModel).where(ProductModel.is_active == True))
    return result.all()


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Создаёт новый товар.
    """
    result = await db.scalars(
        select(CategoryModel).where(CategoryModel.id == product.category_id,
                                    CategoryModel.is_active == True)
    )
    category = result.first()
    if not category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Category not found or inactive")
    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


@router.get("/category/{category_id}", response_model=list[ProductSchema])
async def get_products_by_category(category_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список активных товаров в указанной категории по её ID.
    """
    result = await db.scalars(
        select(CategoryModel).where(CategoryModel.id == category_id,
                                    CategoryModel.is_active == True)
    )
    category = result.first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Category not found or inactive")
    result = await db.scalars(
        select(ProductModel).where(ProductModel.category_id == category_id,
                                   ProductModel.is_active == True)
    )
    return result.all()


@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    result = await db.scalars(
        select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True)
    )
    product = result.first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Product not found or inactive")
    return product


@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(product_id: int, product: ProductCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Обновляет товар по его ID.
    """
    result = await db.scalars(
        select(ProductModel).where(ProductModel.id == product_id)
    )
    db_product = result.first()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    result = await db.scalars(
        select(CategoryModel).where(CategoryModel.id == product.category_id,
                                    CategoryModel.is_active == True)
    )
    category = result.first()
    if not category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Category not found or inactive")
    db.execute(
        update(ProductModel).where(ProductModel.id == product_id).values(**product.model_dump())
    )
    await db.commit()
    await db.refresh(db_product)
    return db_product


@router.delete("/{product_id}")
async def delete_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Удаляет товар по его ID (логическое удаление).
    """
    result = await db.scalars(
        select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True)
    )
    product = result.first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Product not found or inactive")
    db.execute(
        update(ProductModel).where(ProductModel.id == product_id).values(is_active=False)
    )
    await db.commit()
    return {"status": "success", "message": "Product marked as inactive"}
