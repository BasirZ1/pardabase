from contextlib import asynccontextmanager

from fastapi import FastAPI

# Import HTTP routes from hsrv.py
from hsrv import router as http_router
from utils.conn import close_all_pools


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield  # App is running
    await close_all_pools()

# Create FastAPI app
app = FastAPI(lifespan=lifespan)

# Mount HTTP routes
app.include_router(http_router)

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
