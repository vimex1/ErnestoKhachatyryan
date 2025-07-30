from fastapi import FastAPI
from app.routers import category
from app.routers import products

app = FastAPI()


@app.get('/')
async def welcome() -> dict:
    return {'message': 'Добро пожаловать в магазин'}

app.include_router(category.router)
app.include_router(products.router)