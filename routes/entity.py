from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, APIRouter, Form
from fastapi.responses import JSONResponse

from Models import RemoveEntityRequest
from db import insert_new_entity, remember_users_action, update_entity, get_entity_details_ps, remove_entity_ps, \
    get_entities_list_ps
from helpers import get_formatted_entities_list
from utils import verify_jwt_user

router = APIRouter()
load_dotenv(override=True)


@router.post("/add-or-edit-entity")
async def add_or_edit_entity(
        idToEdit: Optional[int] = Form(None),
        name: str = Form(...),
        phone: Optional[str] = Form(None),
        address: Optional[str] = Form(None),
        notes: Optional[str] = Form(None),
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    if idToEdit is None:
        # CREATE NEW
        entity_id = await insert_new_entity(name, phone, address, notes)
        if not entity_id:
            return JSONResponse(content={
                "result": False,
                "name": name,
                "phone": phone
            })
        await remember_users_action(user_data['user_id'], f"Entity Added: {name} {phone}")
    else:
        # UPDATE OLD
        entity_id = await update_entity(idToEdit, name, phone, address, notes)
        if not entity_id:
            return JSONResponse(content={
                "result": False,
                "name": name,
                "phone": phone
            })
        await remember_users_action(user_data['user_id'], f"Entity updated: {entity_id},"
                                                          f" name: {name} phone: {phone}")
    return JSONResponse(content={
        "result": True,
        "id": entity_id,
        "name": name,
        "phone": phone
    })


@router.get("/entity-details-get")
async def get_entity_details(
        entityId: int,
        _: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Retrieve an entity's details based on entity id.
    """
    entity_details = await get_entity_details_ps(entityId)
    return JSONResponse(content=entity_details, status_code=200)


@router.get("/entities-list-get")
async def get_entities_list(
        _: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Retrieve a list of entities.
    """
    data = await get_entities_list_ps()
    entities_list = get_formatted_entities_list(data)
    return JSONResponse(content=entities_list, status_code=200)


@router.post("/remove-entity")
async def remove_entity(
        request: RemoveEntityRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Endpoint to remove an entity.
    """
    result = await remove_entity_ps(request.entityId)
    if result:
        await remember_users_action(user_data['user_id'], f"Entity removed: {request.entityId}")
    return JSONResponse(content={"result": result}, status_code=200)
