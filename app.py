from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import HTTP routes from hsrv.py
from hsrv import router as http_router
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
app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of origins that are allowed to make requests
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Mount HTTP routes
app.include_router(http_router)

# Run the application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
