from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.routers import permission
from app.routers import category
from app.routers import products
from app.routers import auth
from app.routers import reviews
from tests import test_endpoints
from .log import log_middleware


app = FastAPI(
    title="FastAPI Ernesto Khachatyryan ", 
    description="Магазин мужской одежды"
)

origins = [
    "http://localhost:8000"
]


app.middleware("http")(log_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
        "localhost:8000",
        "127.0.0.1:8000",
        "127.0.0.1:8000/docs",
        "futuredomain.com",  # будущий домен
        "*.futuredomain.com",  # поддомены
    ],
)


@app.get("/")
async def welcome() -> dict:
    return {"message": "Добро пожаловать в магазин Ernesto Khachatyryan"}


app.include_router(category.router)
app.include_router(products.router)
app.include_router(auth.router)
app.include_router(permission.router)
app.include_router(reviews.router)
app.include_router(test_endpoints.router)
