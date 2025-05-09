from fastapi import FastAPI
from api.routes.auth import router as auth_router
from api.routes import submissions

app = FastAPI()

app.include_router(auth_router)
app.include_router(submissions.router)
