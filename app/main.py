from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

from app.routes import health, api

app = FastAPI(title="Health App Backend")

# CORS configuration - allow all Firebase domains and localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://suppl-f09d8.web.app",
        "https://suppl-f09d8.firebaseapp.com",
    ],
    allow_origin_regex=r"https://.*\.(web\.app|firebaseapp\.com|firebasestorage\.app)",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router)
app.include_router(api.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Health App Backend", "status": "ok"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port)

