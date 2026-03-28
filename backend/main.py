# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mock_gstn import mock_gstn  # We will create this next

app = FastAPI(
    title="Zero-Touch GST Agentic Network",
    description="Backend orchestration for autonomous GST compliance and penalty prevention.",
    version="1.0.0"
)

# Configure CORS to allow the Next.js frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, this should be restricted to the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the Mock Government Portal routes
app.include_router(mock_gstn.router)

@app.get("/")
def health_check():
    return {"status": "Agentic Network is Live", "database_connected": True}