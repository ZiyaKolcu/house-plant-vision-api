from fastapi import APIRouter, HTTPException
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


@router.get("/{common_name}")
async def get_plant_by_common_name(common_name: str):
    query = """
        SELECT id, scientific_name, common_name, description, care_tips, image_url
        FROM plant_species
        WHERE LOWER(common_name) = LOWER(%s)
    """
    row = await Database.fetchrow(query, common_name)

    if not row:
        raise HTTPException(status_code=404, detail="Plant not found")

    return dict(row)


@router.get("/id/{plant_id}")
async def get_plant_by_id(plant_id: int):
    query = """
        SELECT id, scientific_name, common_name, description, care_tips, image_url
        FROM plant_species
        WHERE id = %s
    """
    plant = await Database.fetchrow(query, plant_id)

    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    return plant
