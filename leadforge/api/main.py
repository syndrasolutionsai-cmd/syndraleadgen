from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from leadforge.api.routes import auth, clients, campaigns, review, analytics

app = FastAPI(title="LeadForge API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(campaigns.router)
app.include_router(review.router)
app.include_router(analytics.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
