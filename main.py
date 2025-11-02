"""Main entry point for the FastAPI server."""

import uvicorn

from nes.api import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
