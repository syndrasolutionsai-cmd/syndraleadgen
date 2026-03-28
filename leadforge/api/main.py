from fastapi import FastAPI
from leadforge.api.routes import auth, clients, campaigns, review

app = FastAPI(title="LeadForge API", version="0.1.0")

app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(campaigns.router)
app.include_router(review.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
