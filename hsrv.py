import os
import tempfile
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Form, Header, File, UploadFile, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse

from Models import TokenValidationRequest, AuthRequest, ChangePasswordRequest, NewAdminRequest, RemoveProductRequest, \
    UpdateRollRequest, AddExpenseRequest, RemoveRollRequest, RemoveBillRequest
from utils import flatbed, check_username_password_admins, get_admins_data, check_admins_token, \
    search_recent_activities_list, update_admins_password, add_new_admin_ps, insert_new_product, \
    get_image_for_product, search_products_list, update_product, get_product_and_roll_ps, remove_product_ps, \
    remember_admins_action, update_roll_quantity_ps, add_expense_ps, insert_new_roll, update_roll, \
    search_rolls_for_product, get_sample_image_for_roll, remove_roll_ps, insert_new_bill, \
    update_bill, get_bill_ps, remove_bill_ps
from utils.hasher import hash_password

router = APIRouter()
load_dotenv(override=True)


@router.get("/")
async def index():
    return "Legacy Route Error"


@router.post("/is-token-valid")
async def is_token_valid(request: TokenValidationRequest):
    try:
        check_status = check_admins_token(1, request.loginToken)
        return JSONResponse(content={"check_result": check_status})

    except Exception as e:
        flatbed('exception', f"in is_token_valid {e}")
        return "Error", 500


@router.post("/auth")
async def auth(request: AuthRequest):
    try:
        if not request.username or not request.password:
            return JSONResponse(content={'result': False}, status_code=400)

        check_result = check_username_password_admins(request.username, request.password)

        if check_result:
            login_token, full_name, level = get_admins_data(request.username)
            return JSONResponse(content={
                'result': check_result,
                'loginToken': login_token,
                'fullName': full_name,
                "level": level
            })
        else:
            return JSONResponse(content={"result": False})
    except Exception as e:
        flatbed('exception', f"in auth {e}")
        return "Error", 500


@router.post("/get-dashboard-data")
async def get_dashboard_data(request: TokenValidationRequest):
    try:
        check_status = check_admins_token(1, request.loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        # Fetch data for the dashboard
        return JSONResponse(content={
            "totalBills": 404,
            "billsCompleted": 404,
            "billsPending": 404,
            "totalProducts": 404
        })

    except Exception as e:
        flatbed('exception', f"Error in get-dashboard-data: {str(e)}")
        return "Error"


@router.get("/recent-activities-list-get")
async def get_recent_activity(loginToken: str, date: int):
    """
    Retrieve a list of recent activities.
    """
    try:
        check_status = check_admins_token(3, loginToken)
        if not check_status:
            return "Access denied", 401

        recent_activity_data = search_recent_activities_list(date)
        recent_activities_list = get_formatted_recent_activities_list(recent_activity_data)
        if recent_activities_list:
            return JSONResponse(content=recent_activities_list, status_code=200)
        else:
            return "not found", 404
    except Exception as e:
        flatbed("exception", f"in get_recent_activity {e}")
        return "Error", 500


@router.post("/change-password")
async def change_password(request: ChangePasswordRequest):
    """
    Endpoint to change password for Admin accounts.
    """
    try:
        login_token = request.loginToken
        check_status = check_admins_token(1, login_token)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        username = request.username
        old_password = request.oldPassword
        new_password = request.newPassword

        check_old_password = check_username_password_admins(username, old_password)
        if check_old_password is False:
            return "Failure", 401

        update_admins_password(username, hash_password(new_password))
        return "Success", 200

    except Exception as e:
        flatbed('exception', f"in change password {e}")
        return "Error", 500


@router.post("/add-new-admin")
async def add_new_admin(request: NewAdminRequest):
    """
    Endpoint to add new admin to system.
    """
    try:
        login_token = request.loginToken
        check_status = check_admins_token(5, login_token)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        full_name = request.fullName
        username = request.username
        password = request.password
        level = request.level

        result = add_new_admin_ps(login_token, full_name, username, password, level)
        if result is False:
            return "Failure", 401
        return JSONResponse("Success", status_code=200)
    except Exception as e:
        flatbed('exception', f"in add_new_admin {e}")
        return "Error", 500


@router.post("/add-or-edit-product")
async def add_or_edit_product(
        Authorization: str = Header(None),
        username: str = Form(...),
        codeToEdit: Optional[str] = Form(None),
        name: str = Form(...),
        categoryIndex: int = Form(...),
        cost: int = Form(...),
        price: int = Form(...),
        description: Optional[str] = Form(None),
        image: UploadFile = File(...),
):
    try:
        # Validate authorization header
        if not Authorization.startswith("Bearer "):
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        login_token = Authorization.split(" ")[1]  # Extract token after "Bearer"
        check_status = check_admins_token(3, login_token)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        # Read each image file's content (all files are required)
        image_data = await image.read()
        if codeToEdit is None:
            # Insert registration data and images into the database
            result = insert_new_product(image_data, name, categoryIndex, cost, price, description)
            if result:
                remember_admins_action(username, f"Product Added: {result}")
                return JSONResponse(content={
                    "code": result,
                    "name": name,
                })
            return "Failure", 500

        result = update_product(codeToEdit, image_data, name, categoryIndex, cost, price, description)
        if result:
            remember_admins_action(username, f"Product updated: {codeToEdit}")
            return JSONResponse(content={
                "code": codeToEdit,
                "name": name,
            })
        return "Failure", 500

    except Exception as e:
        # Log the exception for debugging
        flatbed("exception", f"in add_or_edit_product: {e}")
        return "Error submitting data", 500  # Error response


@router.post("/add-or-edit-roll")
async def add_or_edit_roll(
        Authorization: str = Header(None),
        username: str = Form(...),
        codeToEdit: Optional[str] = Form(None),
        productCode: Optional[str] = Form(None),
        quantity: int = Form(...),
        color: Optional[str] = Form(None),
        image: Optional[UploadFile] = File(None),
):
    try:
        # Validate authorization header
        if not Authorization.startswith("Bearer "):
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        login_token = Authorization.split(" ")[1]  # Extract token after "Bearer"
        check_status = check_admins_token(3, login_token)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        # Read image data only if an image is uploaded
        image_data = await image.read() if image else None

        if codeToEdit is None:
            # Insert registration data and images into the database
            code = insert_new_roll(productCode, quantity, color, image_data)
            if code:
                remember_admins_action(username, f"Roll Added: {code}")
                return JSONResponse(content={
                    "code": code
                })
            return "Failure", 500

        code = update_roll(codeToEdit, productCode, quantity, color, image_data)
        if code:
            remember_admins_action(username, f"Roll updated: {code}")
            return JSONResponse(content={
                "code": code
            })
        return "Failure", 500

    except Exception as e:
        # Log the exception for debugging
        flatbed("exception", f"in add_or_edit_roll: {e}")
        return "Error submitting data", 500  # Error response


@router.post("/add-or-edit-bill")
async def add_or_edit_bill(
        Authorization: str = Header(None),
        username: str = Form(...),
        codeToEdit: Optional[str] = Form(None),
        billDate: str = Form(...),
        dueDate: Optional[str] = Form(None),
        customerName: Optional[str] = Form(None),
        customerNumber: Optional[str] = Form(None),
        price: Optional[int] = Form(None),
        paid: Optional[int] = Form(None),
        remaining: Optional[int] = Form(None),
        fabrics: Optional[str] = Form(None),
        parts: Optional[str] = Form(None),
        status: Optional[str] = Form(None),
        salesman: Optional[str] = Form(None),
        tailor: Optional[str] = Form(None),
        additionalData: Optional[str] = Form(None),
        installation: Optional[str] = Form(None)
):
    try:
        # Validate authorization header
        if not Authorization.startswith("Bearer "):
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        login_token = Authorization.split(" ")[1]  # Extract token after "Bearer"
        check_status = check_admins_token(2, login_token)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        if codeToEdit is None:
            # Insert registration data and images into the database
            code = insert_new_bill(billDate, dueDate, customerName, customerNumber, price, paid, remaining,
                                   fabrics, parts, status, salesman, tailor, additionalData, installation)
            if code:
                remember_admins_action(username, f"Bill Added: {code}")
                return JSONResponse(content={
                    "code": code,
                    "name": customerName
                })
            return "Failure", 500

        code = update_bill(codeToEdit, billDate, dueDate, customerName, customerNumber, price, paid, remaining,
                           fabrics, parts, status, salesman, tailor, additionalData, installation)
        if code:
            remember_admins_action(username, f"Bill updated: {code}")
            return JSONResponse(content={
                "code": code,
                "name": customerName
            })
        return "Failure", 500

    except Exception as e:
        # Log the exception for debugging
        flatbed("exception", f"in add_or_edit_bill: {e}")
        return "Error submitting data", 500  # Error response


@router.get("/products-list-get")
async def get_products_list(
        loginToken: str,
        searchQuery: str,
        searchByIndex: int,
):
    """
    Retrieve a list of products based on search query.
    """
    try:
        check_status = check_admins_token(1, loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        products_data = search_products_list(searchQuery, searchByIndex)
        products_list = get_formatted_products_list(products_data)
        if products_list:
            return JSONResponse(content=products_list, status_code=200)
        else:
            return "not found", 404
    except Exception as e:
        flatbed("exception", f"in get_products_list {e}")
        return "Error", 500


@router.get("/rolls-for-product-get")
async def get_rolls_for_product(
        loginToken: str,
        productCode: str
):
    """
    Retrieve a list of rolls based on product code.
    """
    try:
        check_status = check_admins_token(1, loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        rolls_data = search_rolls_for_product(productCode)
        rolls_list = get_formatted_rolls_list(rolls_data)
        if rolls_list:
            return JSONResponse(content=rolls_list, status_code=200)
        else:
            return "not found", 404
    except Exception as e:
        flatbed("exception", f"in get_rolls_for_product {e}")
        return "Error", 500


@router.get("/product-image-get")
async def get_product_image(
        loginToken: str = Query(...),
        code: str = Query(...),
        background_tasks: BackgroundTasks = None
):
    """
    Endpoint to get product's image by code.
    """
    try:
        check_status = check_admins_token(1, loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        # Get the agent image data
        product_image = get_image_for_product(code)

        if product_image:
            # Create a temporary file to store the image data
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(product_image)
                temp_file_path = temp_file.name

            # Schedule the file for deletion after the response is sent
            background_tasks.add_task(delete_temp_file, temp_file_path)
            # Return the image file response
            return FileResponse(temp_file_path, media_type="image/jpeg")
        else:
            # Return a message indicating the image is not found with HTTP status code 404
            return "Image not found", 404

    except Exception as e:
        flatbed('exception', f"in get_product_image: {e}")
        return "Error", 500


@router.get("/roll-sample-image-get")
async def get_roll_sample_image(
        loginToken: str = Query(...),
        code: str = Query(...),
        background_tasks: BackgroundTasks = None
):
    """
    Endpoint to get roll's image by code.
    """
    try:
        check_status = check_admins_token(1, loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        # Get the agent image data
        sample_image = get_sample_image_for_roll(code)

        if sample_image:
            # Create a temporary file to store the image data
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(sample_image)
                temp_file_path = temp_file.name

            # Schedule the file for deletion after the response is sent
            background_tasks.add_task(delete_temp_file, temp_file_path)
            # Return the image file response
            return FileResponse(temp_file_path, media_type="image/jpeg")
        else:
            # Return a message indicating the image is not found with HTTP status code 404
            return "Image not found", 404

    except Exception as e:
        flatbed('exception', f"in get_roll_sample_image: {e}")
        return "Error", 500


@router.get("/product-and-roll-get")
async def get_product_and_roll(
        loginToken: str,
        code: str
):
    """
    Retrieve a product and roll based on code.
    """
    try:
        check_status = check_admins_token(1, loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        product = get_product_and_roll_ps(code)
        if product:
            return JSONResponse(content=product, status_code=200)
        else:
            return "not found", 404
    except Exception as e:
        flatbed("exception", f"in get_product_and_roll {e}")
        return "Error", 500


@router.get("/bill-get")
async def get_bill(
        loginToken: str,
        code: str
):
    """
    Retrieve a bill based on code.
    """
    try:
        check_status = check_admins_token(1, loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        data = get_bill_ps(code)
        if data:
            bill = {
                "billCode": data[0],
                "billDate": data[1],
                "dueDate": data[2],
                "customerName": data[3],
                "customerNumber": data[4],
                "price": data[5],
                "paid": data[6],
                "remaining": data[7],
                "fabrics": data[8],
                "parts": data[9],
                "status": data[10],
                "salesman": data[11],
                "tailor": data[12],
                "additionalData": data[13],
                "installation": data[14]
            }
            return JSONResponse(content=bill, status_code=200)
        else:
            return "not found", 404
    except Exception as e:
        flatbed("exception", f"in get_bill {e}")
        return "Error", 500


@router.post("/remove-product")
async def remove_product(request: RemoveProductRequest):
    """
    Endpoint to remove a product.
    """
    try:
        check_status = check_admins_token(3, request.loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        remove_product_ps(request.code)
        remember_admins_action(request.username, f"Product removed: {request.code}")
        return JSONResponse("Success", status_code=200)
    except Exception as e:
        flatbed('exception', f"in remove_product: {e}")
        return "Error", 500


@router.post("/remove-roll")
async def remove_roll(request: RemoveRollRequest):
    """
    Endpoint to remove a roll.
    """
    try:
        check_status = check_admins_token(3, request.loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        remove_roll_ps(request.rollCode)
        remember_admins_action(request.username, f"Roll removed: {request.rollCode}")
        return JSONResponse("Success", status_code=200)
    except Exception as e:
        flatbed('exception', f"in remove_roll: {e}")
        return "Error", 500


@router.post("/remove-bill")
async def remove_bill(request: RemoveBillRequest):
    """
    Endpoint to remove a bill.
    """
    try:
        check_status = check_admins_token(3, request.loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        remove_bill_ps(request.billCode)
        remember_admins_action(request.username, f"Bill removed: {request.rollCode}")
        return JSONResponse("Success", status_code=200)
    except Exception as e:
        flatbed('exception', f"in remove_bill: {e}")
        return "Error", 500


@router.post("/update-roll-quantity")
async def update_roll_quantity(request: UpdateRollRequest):
    """
    Endpoint to update a roll's quantity.
    """
    try:
        check_status = check_admins_token(3, request.loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        update_roll_quantity_ps(request.rollCode, request.quantity, request.action)
        remember_admins_action(request.username, f"Roll quantity updated: "
                                                 f"{request.rollCode} {request.action} {request.quantity}")
        return JSONResponse("Success", status_code=200)
    except Exception as e:
        flatbed('exception', f"in update_roll_quantity: {e}")
        return "Error", 500


@router.post("/add-expense")
async def add_expense(request: AddExpenseRequest):
    """
    Endpoint to add an expense.
    """
    try:
        check_status = check_admins_token(3, request.loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        expense_id = add_expense_ps(request.categoryIndex, request.description, request.amount)
        if expense_id:
            remember_admins_action(request.username, f"Added Expense: Desc: {request.description}")
            return JSONResponse(content={
                "description": request.description,
                "amount": request.amount
            })
        return "Failure", 500
    except Exception as e:
        flatbed('exception', f"in add_expense: {e}")
        return "Error", 500


#  Helper Functions
def get_formatted_recent_activities_list(recent_activity_data):
    """
    Helper function to format recent activities data into JSON-compatible objects.

    Parameters:
    - logs_data: Raw data fetched from the database.

    Returns:
    - A list of formatted recent activities dictionaries.
    """
    recent_activity_list = []
    if recent_activity_data:
        for data in recent_activity_data:
            activity = {
                "id": data[0],
                "date": data[1].strftime('%Y-%m-%d %H:%M:%S') if isinstance(data[1], datetime) else data[1],
                "username": data[2],
                "action": data[3],
            }
            recent_activity_list.append(activity)
    return recent_activity_list


def get_formatted_products_list(products_data):
    """
    Helper function to format products data into JSON-compatible objects.

    Parameters:
    - products_data: Raw data fetched from the database.

    Returns:
    - A list of formatted products dictionaries.
    """
    products_list = []
    if products_data:
        for data in products_data:
            product = {
                "code": data[0],
                "name": data[1],
                "categoryIndex": data[2],
                "quantityInCm": data[3],
                "costPerMetre": data[4],
                "pricePerMetre": data[5],
                "description": data[6]
            }
            products_list.append(product)
    return products_list


def get_formatted_rolls_list(rolls_data):
    """
    Helper function to format rolls data into JSON-compatible objects.

    Parameters:
    - rolls_data: Raw data fetched from the database.

    Returns:
    - A list of formatted rolls dictionaries.
    """
    rolls_list = []
    if rolls_data:
        for data in rolls_data:
            roll = {
                "productCode": data[0],
                "rollCode": data[1],
                "quantityInCm": data[2],
                "colorLetter": data[3]
            }
            rolls_list.append(roll)
    return rolls_list


def delete_temp_file(file_path: str):
    """
    Deletes the specified temporary file.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        # Log the error if file deletion fails
        flatbed('exception', f"In delete temp file {file_path}: {e}")


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(router, host='127.0.0.1', port=8000)
