from fastapi import FastAPI

# Import HTTP routes from hsrv.py
from hsrv import router as http_router

# Create FastAPI app
app = FastAPI()

# Mount HTTP routes
app.include_router(http_router)

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
