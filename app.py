from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import HTTP routes from hsrv.py
from routes import *
from utils import flatbed
from utils.conn import close_all_pools

# CORS Configuration
origins = [
    "*"
    # "https://parda.af",  # Add your production frontend URL here
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield  # App is running
    await close_all_pools()


# Create FastAPI app
app = FastAPI(
    lifespan=lifespan,
    title="pardaBase API",
    description="Backend for pardaBase curtains admin system App",
    version="1.1.0",
    docs_url="/api/docs",  # Custom Swagger UI path
    redoc_url="/api/redoc",  # Custom ReDoc path
    openapi_url="/api/openapi.json"  # Custom OpenAPI spec URL
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of origins that are allowed to make requests
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Mount HTTP routes
routers = [
    login_router,
    dashboard_router,
    product_router,
    roll_router,
    bill_router,
    misc_router,
    entity_router,
    supplier_router,
    purchase_router,
    expense_router,
    print_router,
    telegram_router,
    payment_router,
    earning_router,
    report_router,
    search_router,
    sync_router,
    user_router,
    pardaaf_router,
]

for r in routers:
    app.include_router(r)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    endpoint = request.url.path
    method = request.method
    error_message = str(exc)

    await flatbed('exception', f"Unhandled error at {method} {endpoint}: {error_message}")

    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


# Run the application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
