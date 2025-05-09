from fastapi import APIRouter
from api.db.database import Database

router = APIRouter(prefix="/plants", tags=["plants"])


@router.get("/", summary="Get all plant species")
async def get_all_plants():
    query = """
        SELECT id, scientific_name, common_name, description, care_tips, image_url
        FROM plant_species
        ORDER BY id
    """
    rows = await Database.fetch_all(query)
    return [dict(row) for row in rows]
