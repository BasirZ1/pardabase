from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Form, UploadFile, File, Depends
from fastapi.responses import JSONResponse

from Models import RemoveRequest, UpdateRollRequest, UpdateCutFabricTXStatusRequest, CommentRequest
from db import insert_new_roll, handle_image_update, remember_users_action, update_roll, remove_roll_ps, \
    archive_roll_ps, add_roll_quantity_ps, add_cut_fabric_tx, search_rolls_for_product, \
    get_cutting_history_list_for_roll_ps, get_cutting_history_list_ps, update_cut_fabric_tx_status_ps, \
    search_rolls_for_purchase_item, get_drafts_list_ps
from helpers import classify_image_upload, get_formatted_rolls_list, format_cut_fabric_records
from utils import verify_jwt_user, flatbed

router = APIRouter()
load_dotenv(override=True)


@router.post("/add-or-edit-roll")
async def add_or_edit_roll(
        codeToEdit: Optional[str] = Form(None),
        productCode: str = Form(...),
        purchaseItemId: Optional[int] = Form(None),
        quantity: int = Form(...),
        color: Optional[str] = Form(None),
        image: Optional[UploadFile] = File(None),
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    image_status, image_data = await classify_image_upload(image)

    if codeToEdit is None:
        # CREATE NEW
        code = await insert_new_roll(productCode, purchaseItemId, quantity, color)
        if not code:
            return JSONResponse(content={
                "result": False
            })
        await handle_image_update("roll", user_data['tenant'], code, image_status, image_data)
        await remember_users_action(user_data['user_id'], f"Roll Added: {productCode}{code}")
    else:
        code = await update_roll(codeToEdit, quantity, color)
        if not code:
            return JSONResponse(content={
                "result": False
            })
        await handle_image_update("roll", user_data['tenant'], code, image_status, image_data)
        await remember_users_action(user_data['user_id'], f"Roll updated: {productCode}{code}")

    return JSONResponse(content={
        "result": True,
        "code": code
    })


@router.get("/rolls-for-product-get")
async def get_rolls_for_product(
        code: str,
        _: dict = Depends(verify_jwt_user(required_level=1))
):
    """
    Retrieve a list of rolls based on product code.
    """
    rolls_data = await search_rolls_for_product(code)
    rolls_list = get_formatted_rolls_list(rolls_data)
    return JSONResponse(content=rolls_list, status_code=200)


@router.get("/rolls-for-purchase-item-get")
async def get_rolls_for_purchase_item(
        purchaseItemId: int,
        _: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Retrieve a list of rolls based on purchase item id.
    """
    rolls_data = await search_rolls_for_purchase_item(purchaseItemId)
    rolls_list = get_formatted_rolls_list(rolls_data)
    return JSONResponse(content=rolls_list, status_code=200)


@router.get("/drafts-list-get")
async def get_drafts_list(
        _: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Retrieve a list of drafts.
    """
    drafts_data = await get_drafts_list_ps()
    drafts_list = format_cut_fabric_records(drafts_data)

    return JSONResponse(content=drafts_list, status_code=200)


@router.get("/cutting-history-list-get")
async def get_cutting_history_list(
        status: str,
        date: int,
        _: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Retrieve a list of cutting history.
    """
    history_data = await get_cutting_history_list_ps(status, date)
    history_list = format_cut_fabric_records(
        history_data,
        extra={
            "reviewedBy": "reviewed_by",
            "reviewedAt": "reviewed_at"
        }
    )

    return JSONResponse(content=history_list, status_code=200)


@router.get("/roll-cutting-history-list-get")
async def get_roll_cutting_history_list(
        code: str,
        _: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Retrieve a list of cutting history based on roll.
    """
    history_data = await get_cutting_history_list_for_roll_ps(code)
    history_list = format_cut_fabric_records(
        history_data,
        extra={
            "reviewedBy": "reviewed_by",
            "reviewedAt": "reviewed_at"
        }
    )

    return JSONResponse(content=history_list, status_code=200)


@router.post("/add_comment_for_subtract")
async def add_comment_for_subtract(
        request: CommentRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=1))
):
    """
    Endpoint to add comment for subtracting a roll's quantity.
    """
    result = await add_cut_fabric_tx(request.code, request.quantity, user_data['user_id'],
                                     "draft", None, request.comment)
    await remember_users_action(user_data['user_id'], f"wants to cut fabric: "
                                                      f"{request.code} {request.quantity / 100}m")
    return JSONResponse(content={"result": result}, status_code=200)


@router.post("/update-cut-fabric-tx-status")
async def update_cut_fabric_tx_status(
        request: UpdateCutFabricTXStatusRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Endpoint to update a cut_fabric transaction's status.
    """
    result = await update_cut_fabric_tx_status_ps(request.id, request.newStatus, user_data['user_id'])
    await remember_users_action(user_data['user_id'], f"Cut draft status updated: "
                                                      f"{request.id} {request.newStatus}")
    return JSONResponse(content={"result": result}, status_code=200)


@router.post("/update-roll-quantity")
async def update_roll_quantity(
        request: UpdateRollRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Endpoint to update a roll's quantity.
    """
    qty = request.quantity
    if request.action == "add":
        result = await add_cut_fabric_tx(request.code, qty, user_data['user_id'], status='adjustment',
                                         comment=request.comment, bill_code=request.reference)
    elif request.action == "subtract":
        result = await add_cut_fabric_tx(request.code, -qty, user_data['user_id'], status='adjustment',
                                         comment=request.comment, bill_code=request.reference)
    elif request.action == "cut":
        result = await add_cut_fabric_tx(request.code, qty, user_data['user_id'],
                                         comment=request.comment, bill_code=request.reference)
    else:
        result = False
    await remember_users_action(user_data['user_id'], f"Roll quantity updated: "
                                                      f"{request.code} {request.action} {qty / 100}m")
    return JSONResponse(content={"result": result}, status_code=200)


@router.post("/remove-roll")
async def remove_roll(
        request: RemoveRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Endpoint to either remove or archive a roll.
    """
    if request.mode == "remove":
        result = await remove_roll_ps(request.code)
        action_desc = f"Roll removed with history: {request.code}"
        await handle_image_update("roll", user_data['tenant'], request.code, "remove", None)
    elif request.mode == "archive":
        result = await archive_roll_ps(request.code)
        action_desc = f"Roll removed: {request.code}"
    else:
        await flatbed("debug", f"invalid mode {request.mode}")
        return JSONResponse(content={"error": "Invalid mode"}, status_code=400)

    if result:
        await remember_users_action(user_data['user_id'], action_desc)

    return JSONResponse(content={"result": result}, status_code=200)
