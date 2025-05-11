from fastapi import FastAPI
from fastapi.routing import APIRouter
from api.routes import auth, submissions, plants, predictions

app = FastAPI()
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(submissions.router)
api_router.include_router(plants.router)
api_router.include_router(predictions.router)
app.include_router(api_router)
