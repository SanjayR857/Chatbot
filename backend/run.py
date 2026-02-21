import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",   # "filename:variable" — points to the FastAPI instance
        host="0.0.0.0",   # 0.0.0.0 = accept connections from any device on network
                          # use "127.0.0.1" to only allow your own machine
        port=8000,        # the port your API runs on
        reload=settings.DEBUG,   # reads DEBUG from .env
                                 # True  → restarts server when you save a file
                                 # False → stable, no restarts (for production)
        log_level="info", # how much logging to show: debug / info / warning / error
    )