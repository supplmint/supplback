from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import re

load_dotenv()

from app.routes import health, api

app = FastAPI(title="Health App Backend")

# CORS configuration
# FastAPI doesn't support regex in allow_origins, so we'll use a function
def is_allowed_origin(origin: str) -> bool:
    allowed_patterns = [
        r"^http://localhost:5173$",
        r"^https://.*\.web\.app$",
        r"^https://.*\.firebaseapp\.com$",
    ]
    return any(re.match(pattern, origin) for pattern in allowed_patterns)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.(web\.app|firebaseapp\.com)|http://localhost:5173",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router)
app.include_router(api.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Health App Backend"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port)

