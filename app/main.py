from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from backend.middleware import TimingMiddleware
from app.routers import category
from app.routers import products
from app.routers import auth
from app.routers import permission
from app.routers import reviews


app = FastAPI()

origins = [
    "http://localhost:3000"
]

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
        "localhost:3000",
        "127.0.0.1:3000",
        "futuredomain.com",         # будущий домен
        "*.futuredomain.com",       # поддомены
    ]
)

app.add_middleware(
    HTTPSRedirectMiddleware
)

app.add_middleware(
    TimingMiddleware
)


@app.get('/')
async def welcome() -> dict:
    return {'message': 'Добро пожаловать в магазин Ernesto Khachatyryan'}


app.include_router(category.router)
app.include_router(products.router)
app.include_router(auth.router)
app.include_router(permission.router)
app.include_router(reviews.router)