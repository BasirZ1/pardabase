import os
import re
import tempfile
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Form, Header, File, UploadFile, Query, BackgroundTasks, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse, HTMLResponse

from Models import TokenValidationRequest, AuthRequest, ChangePasswordRequest, RemoveProductRequest, \
    UpdateRollRequest, AddExpenseRequest, RemoveRollRequest, RemoveBillRequest, UpdateBillStatusRequest, \
    UpdateBillTailorRequest, AddPaymentBillRequest, RemoveUserRequest, AddOnlineOrderRequest
from utils import flatbed, check_username_password, get_users_data, check_users_token, \
    search_recent_activities_list, update_users_password, add_new_user_ps, insert_new_product, \
    get_image_for_product, search_products_list, update_product, get_product_and_roll_ps, remove_product_ps, \
    remember_users_action, update_roll_quantity_ps, add_expense_ps, insert_new_roll, update_roll, \
    search_rolls_for_product, get_sample_image_for_roll, remove_roll_ps, insert_new_bill, \
    update_bill, get_bill_ps, remove_bill_ps, search_bills_list, update_bill_status_ps, set_current_db, make_bill_dic, \
    make_product_dic, make_roll_dic, update_bill_tailor_ps, add_payment_bill_ps, get_users_list_ps, \
    get_image_for_user, remove_user_ps, generate_token, update_user, search_bills_list_filtered, \
    search_expenses_list_filtered, make_expense_dic, search_products_list_filtered, insert_new_online_order, \
    subscribe_newsletter_ps, send_mail_html, unsubscribe_newsletter_ps, confirm_email_newsletter_ps
from utils.hasher import hash_password

router = APIRouter()
load_dotenv(override=True)


async def set_db_from_header(tenant: str = Header(None)):
    """Dependency to extract tenant and set the current database."""
    if not tenant:
        raise HTTPException(status_code=400, detail="Missing tenant header")

    set_current_db(tenant)  # Just sets the DB, no return needed


@router.get("/")
async def index():
    return "Legacy Route Error"


@router.post("/is-token-valid")
async def is_token_valid(request: TokenValidationRequest, _: None = Depends(set_db_from_header)):
    try:
        check_status = await check_users_token(1, request.loginToken)
        return JSONResponse(content={"check_result": check_status})

    except Exception as e:
        await flatbed('exception', f"in is_token_valid {e}")
        return "Error", 500


@router.post("/auth")
async def auth(request: AuthRequest, _: None = Depends(set_db_from_header)):
    try:
        if not request.username or not request.password:
            return JSONResponse(content={'result': False}, status_code=400)

        check_result = await check_username_password(request.username, request.password)

        if check_result:
            data = await get_users_data(request.username)
            return JSONResponse(content={
                'result': check_result,
                'loginToken': data['login_token'],
                'fullName': data['full_name'],
                "level": data['level']
            })
        else:
            return JSONResponse(content={"result": False})
    except Exception as e:
        await flatbed('exception', f"in auth {e}")
        return "Error", 500


@router.post("/get-dashboard-data")
async def get_dashboard_data(request: TokenValidationRequest, _: None = Depends(set_db_from_header)):
    try:
        check_status = await check_users_token(1, request.loginToken)
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
        await flatbed('exception', f"Error in get-dashboard-data: {str(e)}")
        return "Error"


@router.get("/recent-activities-list-get")
async def get_recent_activity(loginToken: str, _date: int, _: None = Depends(set_db_from_header)):
    """
    Retrieve a list of recent activities.
    """
    try:
        check_status = await check_users_token(3, loginToken)
        if not check_status:
            return "Access denied", 401

        recent_activity_data = await search_recent_activities_list(_date)
        recent_activities_list = get_formatted_recent_activities_list(recent_activity_data)
        if recent_activities_list:
            return JSONResponse(content=recent_activities_list, status_code=200)
        else:
            return "not found", 404
    except Exception as e:
        await flatbed("exception", f"in get_recent_activity {e}")
        return "Error", 500


@router.get("/users-list-get")
async def get_users_list(loginToken: str, _: None = Depends(set_db_from_header)):
    """
    Retrieve a list of users.
    """
    try:
        check_status = await check_users_token(3, loginToken)
        if not check_status:
            return "Access denied", 401

        users_data = await get_users_list_ps()
        users_list = get_formatted_users_list(users_data)
        if users_list:
            return JSONResponse(content=users_list, status_code=200)
        else:
            return "not found", 404
    except Exception as e:
        await flatbed("exception", f"in get_users_list: {e}")
        return "Error", 500


@router.post("/change-password")
async def change_password(request: ChangePasswordRequest, _: None = Depends(set_db_from_header)):
    """
    Endpoint to change password for Admin accounts.
    """
    try:
        login_token = request.loginToken
        check_status = await check_users_token(1, login_token)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        username = request.username
        old_password = request.oldPassword
        new_password = request.newPassword

        check_old_password = await check_username_password(username, old_password)
        if check_old_password is False:
            return "Failure", 401

        await update_users_password(username, hash_password(new_password))
        return "Success", 200

    except Exception as e:
        await flatbed('exception', f"in change password {e}")
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
        image: Optional[UploadFile] = File(None),
        _: None = Depends(set_db_from_header)
):
    try:
        # Validate authorization header
        if not Authorization.startswith("Bearer "):
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        login_token = Authorization.split(" ")[1]  # Extract token after "Bearer"
        check_status = await check_users_token(3, login_token)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        # Read each image file's content (all files are required
        image_data = await image.read() if image is not None else None

        if codeToEdit is None:
            # Insert registration data and images into the database
            result = await insert_new_product(image_data, name, categoryIndex, cost, price, description)
            if result:
                await remember_users_action(username, f"Product Added: {result}")
                return JSONResponse(content={
                    "code": result,
                    "name": name,
                })
            return "Failure", 500

        result = await update_product(codeToEdit, image_data, name, categoryIndex, cost, price, description)
        if result:
            await remember_users_action(username, f"Product updated: {codeToEdit}")
            return JSONResponse(content={
                "code": codeToEdit,
                "name": name,
            })
        return "Failure", 500

    except Exception as e:
        # Log the exception for debugging
        await flatbed("exception", f"in add_or_edit_product: {e}")
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
        _: None = Depends(set_db_from_header)
):
    try:
        # Validate authorization header
        if not Authorization.startswith("Bearer "):
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        login_token = Authorization.split(" ")[1]  # Extract token after "Bearer"
        check_status = await check_users_token(3, login_token)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        # Read image data only if an image is uploaded
        image_data = await image.read() if image else None

        if codeToEdit is None:
            # Insert registration data and images into the database
            code = await insert_new_roll(productCode, quantity, color, image_data)
            if code:
                await remember_users_action(username, f"Roll Added: {code}")
                return JSONResponse(content={
                    "code": code
                })
            return "Failure", 500

        code = update_roll(codeToEdit, productCode, quantity, color, image_data)
        if code:
            await remember_users_action(username, f"Roll updated: {code}")
            return JSONResponse(content={
                "code": code
            })
        return "Failure", 500

    except Exception as e:
        # Log the exception for debugging
        await flatbed("exception", f"in add_or_edit_roll: {e}")
        return "Error submitting data", 500  # Error response


@router.post("/add-or-edit-bill")
async def add_or_edit_bill(
        Authorization: str = Header(None),
        username: str = Form(...),
        codeToEdit: Optional[str] = Form(None),
        billDate: Optional[str] = Form(None),
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
        installation: Optional[str] = Form(None),
        _: None = Depends(set_db_from_header)
):
    try:
        # Validate authorization header
        if not Authorization.startswith("Bearer "):
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        login_token = Authorization.split(" ")[1]  # Extract token after "Bearer"
        check_status = await check_users_token(2, login_token)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        if codeToEdit is None:
            # Insert registration data and images into the database
            code = await insert_new_bill(billDate, dueDate, customerName, customerNumber, price, paid, remaining,
                                         fabrics, parts, status, salesman, tailor, additionalData, installation)
            if code:
                await remember_users_action(username, f"Bill Added: {code}")
                return JSONResponse(content={
                    "code": code,
                    "name": customerName
                })
            return "Failure", 500

        code = await update_bill(codeToEdit, dueDate, customerName, customerNumber, price, paid, remaining,
                                 fabrics, parts, additionalData, installation)
        if code:
            await remember_users_action(username, f"Bill updated: {code}")
            return JSONResponse(content={
                "code": code,
                "name": customerName
            })
        return "Failure", 500

    except Exception as e:
        # Log the exception for debugging
        await flatbed("exception", f"in add_or_edit_bill: {e}")
        return "Error submitting data", 500  # Error response


@router.post("/add-or-edit-user")
async def add_or_edit_user(
        Authorization: str = Header(None),
        username: str = Form(...),
        usernameToEdit: Optional[str] = Form(None),
        fullName: str = Form(...),
        usernameChange: str = Form(...),
        password: Optional[str] = Form(None),
        level: int = Form(...),
        image: Optional[UploadFile] = File(None),
        _: None = Depends(set_db_from_header)
):
    try:
        # Validate authorization header
        if not Authorization.startswith("Bearer "):
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        login_token = Authorization.split(" ")[1]  # Extract token after "Bearer"
        check_status = await check_users_token(3, login_token)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        # Read image data only if an image is uploaded
        image_data = await image.read() if image else None

        if usernameToEdit is None:
            if password is None:
                return JSONResponse(content={"error": "Password is missing"}, status_code=403)
            token = generate_token(username)
            # Insert registration data and images into the database
            result = await add_new_user_ps(token, fullName, usernameChange, password, level, image_data)
            if result:
                await remember_users_action(username, f"User added: {usernameChange}")
                return "Success", 200
            return "Failure", 500

        result = await update_user(usernameToEdit, fullName, usernameChange, level, password, image_data)
        if result:
            await remember_users_action(username, f"user updated: {usernameChange}")
            return "Success", 200
        return "Failure", 500

    except Exception as e:
        # Log the exception for debugging
        await flatbed("exception", f"in add_or_edit_user: {e}")
        return "Error submitting data", 500  # Error response


@router.get("/bills-list-get")
async def get_bills_list(
        loginToken: str,
        date: int,
        state: int,
        _: None = Depends(set_db_from_header)
):
    """
    Retrieve a list of bills based on date or state.
    """
    try:
        check_status = await check_users_token(1, loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        bills_data = await search_bills_list_filtered(date, state)
        bills_list = get_formatted_search_results_list(None, bills_data)
        if bills_list:
            return JSONResponse(content=bills_list, status_code=200)
        else:
            return "not found", 404
    except Exception as e:
        await flatbed("exception", f"in get_bills_list {e}")
        return "Error", 500


@router.get("/expenses-list-get")
async def get_expenses_list(
        loginToken: str,
        date: int,
        category: int,
        _: None = Depends(set_db_from_header)
):
    """
    Retrieve a list of expenses based on date and category.
    """
    try:
        check_status = await check_users_token(1, loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        expenses_data = await search_expenses_list_filtered(date, category)
        expenses_list = get_formatted_expenses_list(expenses_data)
        if expenses_list:
            return JSONResponse(content=expenses_list, status_code=200)
        else:
            return "not found", 404
    except Exception as e:
        await flatbed("exception", f"in get_expenses_list {e}")
        return "Error", 500


@router.get("/products-list-get")
async def get_products_list(
        loginToken: str,
        date: int,
        category: int,
        _: None = Depends(set_db_from_header)
):
    """
    Retrieve a list of products based on date and category.
    """
    try:
        check_status = await check_users_token(1, loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        products_data = await search_products_list_filtered(date, category)
        products_list = get_formatted_search_results_list(products_data, None)
        if products_list:
            return JSONResponse(content=products_list, status_code=200)
        else:
            return "not found", 404
    except Exception as e:
        await flatbed("exception", f"in get_products_list {e}")
        return "Error", 500


@router.get("/search-results-list-get")
async def get_search_results_list(
        loginToken: str,
        searchQuery: str,
        _: None = Depends(set_db_from_header)
):
    """
    Smart search for products and bills based on different query formats.
    """
    try:
        check_status = await check_users_token(1, loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        search_results_list = []

        bill_code_pattern = re.fullmatch(r"(?i)b\d+", searchQuery)  # `(?i)` makes it case insensitive
        product_code_pattern = re.fullmatch(r"(?i)p\d+", searchQuery)
        roll_code_pattern = re.fullmatch(r"(?i)p\d+r\d+", searchQuery)
        phone_number_pattern = re.fullmatch(r"\+?\d{4,14}", searchQuery)  # Intl. and local formats

        if bill_code_pattern:
            # Search bill by code
            bills_data = await search_bills_list(searchQuery, 0)
            search_results_list = get_formatted_search_results_list(None, bills_data)

        elif product_code_pattern:
            # Search product by code
            products_data = await search_products_list(searchQuery, 0)
            search_results_list = get_formatted_search_results_list(products_data, None)

        elif roll_code_pattern:
            product_data = await get_product_and_roll_ps(searchQuery)
            search_results_list.append(product_data)

        elif phone_number_pattern:
            # Search bill by customer phone number
            bills_data = await search_bills_list(searchQuery, 2)
            search_results_list = get_formatted_search_results_list(None, bills_data)

        else:
            # General search (search both products and bills by name)
            products_data = await search_products_list(searchQuery, 1)
            bills_data = await search_bills_list(searchQuery, 1)
            search_results_list = get_formatted_search_results_list(products_data, bills_data)

        if search_results_list:
            return JSONResponse(content=search_results_list, status_code=200)
        else:
            return "not found", 404

    except Exception as e:
        await flatbed("exception", f"in get_search_results_list {e}")
        return JSONResponse(content="Error", status_code=500)


@router.get("/rolls-for-product-get")
async def get_rolls_for_product(
        loginToken: str,
        productCode: str,
        _: None = Depends(set_db_from_header)
):
    """
    Retrieve a list of rolls based on product code.
    """
    try:
        check_status = check_users_token(1, loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        rolls_data = await search_rolls_for_product(productCode)
        rolls_list = get_formatted_rolls_list(rolls_data)
        if rolls_list:
            return JSONResponse(content=rolls_list, status_code=200)
        else:
            return "not found", 404
    except Exception as e:
        await flatbed("exception", f"in get_rolls_for_product {e}")
        return "Error", 500


@router.get("/product-image-get")
async def get_product_image(
        loginToken: str = Query(...),
        code: str = Query(...),
        background_tasks: BackgroundTasks = None,
        _: None = Depends(set_db_from_header)
):
    """
    Endpoint to get product's image by code.
    """
    try:
        check_status = await check_users_token(1, loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        # Get the agent image data
        product_image = await get_image_for_product(code)

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
        await flatbed('exception', f"in get_product_image: {e}")
        return "Error", 500


@router.get("/user-image-get")
async def get_user_image(
        loginToken: str = Query(...),
        username: str = Query(...),
        background_tasks: BackgroundTasks = None,
        _: None = Depends(set_db_from_header)
):
    """
    Endpoint to get user's image by username.
    """
    try:
        check_status = await check_users_token(1, loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        # Get the agent image data
        user_image = await get_image_for_user(username)

        if user_image:
            # Create a temporary file to store the image data
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(user_image)
                temp_file_path = temp_file.name

            # Schedule the file for deletion after the response is sent
            background_tasks.add_task(delete_temp_file, temp_file_path)
            # Return the image file response
            return FileResponse(temp_file_path, media_type="image/jpeg")
        else:
            # Return a message indicating the image is not found with HTTP status code 404
            return "Image not found", 404

    except Exception as e:
        await flatbed('exception', f"in get_user_image: {e}")
        return "Error", 500


@router.get("/roll-sample-image-get")
async def get_roll_sample_image(
        loginToken: str = Query(...),
        code: str = Query(...),
        background_tasks: BackgroundTasks = None,
        _: None = Depends(set_db_from_header)
):
    """
    Endpoint to get roll's image by code.
    """
    try:
        check_status = await check_users_token(1, loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        # Get the agent image data
        sample_image = await get_sample_image_for_roll(code)

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
        await flatbed('exception', f"in get_roll_sample_image: {e}")
        return "Error", 500


@router.get("/product-and-roll-get")
async def get_product_and_roll(
        loginToken: str,
        code: str,
        _: None = Depends(set_db_from_header)
):
    """
    Retrieve a product and roll based on code.
    """
    try:
        check_status = await check_users_token(1, loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        product = await get_product_and_roll_ps(code)
        if product:
            return JSONResponse(content=product, status_code=200)
        else:
            return "not found", 404
    except Exception as e:
        await flatbed("exception", f"in get_product_and_roll {e}")
        return "Error", 500


@router.get("/bill-get")
async def get_bill(
        loginToken: str,
        code: str,
        _: None = Depends(set_db_from_header)
):
    """
    Retrieve a bill based on code.
    """
    try:
        check_status = await check_users_token(1, loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        bill = await get_bill_ps(code)

        if bill:
            return JSONResponse(content=bill, status_code=200)
        else:
            return "not found", 404
    except Exception as e:
        await flatbed("exception", f"in get_bill {e}")
        return "Error", 500


@router.post("/remove-product")
async def remove_product(request: RemoveProductRequest, _: None = Depends(set_db_from_header)):
    """
    Endpoint to remove a product.
    """
    try:
        check_status = await check_users_token(3, request.loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        await remove_product_ps(request.code)
        await remember_users_action(request.username, f"Product removed: {request.code}")
        return JSONResponse("Success", status_code=200)
    except Exception as e:
        await flatbed('exception', f"in remove_product: {e}")
        return "Error", 500


@router.post("/remove-roll")
async def remove_roll(request: RemoveRollRequest, _: None = Depends(set_db_from_header)):
    """
    Endpoint to remove a roll.
    """
    try:
        check_status = await check_users_token(3, request.loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        await remove_roll_ps(request.rollCode)
        await remember_users_action(request.username, f"Roll removed: {request.rollCode}")
        return JSONResponse("Success", status_code=200)
    except Exception as e:
        await flatbed('exception', f"in remove_roll: {e}")
        return "Error", 500


@router.post("/remove-user")
async def remove_user(request: RemoveUserRequest, _: None = Depends(set_db_from_header)):
    """
    Endpoint to remove a user.
    """
    try:
        check_status = await check_users_token(3, request.loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        await remove_user_ps(request.usernameToRemove)
        await remember_users_action(request.username, f"User removed: {request.usernameToRemove}")
        return JSONResponse("Success", status_code=200)
    except Exception as e:
        await flatbed('exception', f"in remove_user: {e}")
        return "Error", 500


@router.post("/remove-bill")
async def remove_bill(request: RemoveBillRequest, _: None = Depends(set_db_from_header)):
    """
    Endpoint to remove a bill.
    """
    try:
        check_status = await check_users_token(3, request.loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        await remove_bill_ps(request.billCode)
        await remember_users_action(request.username, f"Bill removed: {request.rollCode}")
        return JSONResponse("Success", status_code=200)
    except Exception as e:
        await flatbed('exception', f"in remove_bill: {e}")
        return "Error", 500


@router.post("/update-roll-quantity")
async def update_roll_quantity(request: UpdateRollRequest, _: None = Depends(set_db_from_header)):
    """
    Endpoint to update a roll's quantity.
    """
    try:
        check_status = await check_users_token(3, request.loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        await update_roll_quantity_ps(request.rollCode, request.quantity, request.action)
        await remember_users_action(request.username, f"Roll quantity updated: "
                                                      f"{request.rollCode} {request.action} {request.quantity}")
        return JSONResponse("Success", status_code=200)
    except Exception as e:
        await flatbed('exception', f"in update_roll_quantity: {e}")
        return "Error", 500


@router.post("/update-bill-status")
async def update_bill_status(request: UpdateBillStatusRequest, _: None = Depends(set_db_from_header)):
    """
    Endpoint to update a bill's status.
    """
    try:
        check_status = await check_users_token(2, request.loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        await update_bill_status_ps(request.billCode, request.status)
        await remember_users_action(request.username, f"Bill status updated: "
                                                      f"{request.billCode} {request.status}")
        return JSONResponse("Success", status_code=200)
    except Exception as e:
        await flatbed('exception', f"in update_bill_status: {e}")
        return "Error", 500


@router.post("/update-bill-tailor")
async def update_bill_tailor(request: UpdateBillTailorRequest, _: None = Depends(set_db_from_header)):
    """
    Endpoint to update a bill's tailor.
    """
    try:
        check_status = await check_users_token(2, request.loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        await update_bill_tailor_ps(request.billCode, request.tailor)
        await remember_users_action(request.username, f"Bill's tailor updated: "
                                                      f"{request.billCode} {request.tailor}")
        return JSONResponse("Success", status_code=200)
    except Exception as e:
        await flatbed('exception', f"in update_bill_tailor: {e}")
        return "Error", 500


@router.post("/add-payment-bill")
async def add_payment_bill(request: AddPaymentBillRequest, _: None = Depends(set_db_from_header)):
    """
    Endpoint to update a bill's payment.
    """
    try:
        check_status = await check_users_token(2, request.loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        await add_payment_bill_ps(request.billCode, request.amount)
        await remember_users_action(request.username, f"Added payment to bill: "
                                                      f"{request.billCode} {request.amount}")
        return JSONResponse("Success", status_code=200)
    except Exception as e:
        await flatbed('exception', f"in add_payment_bill: {e}")
        return "Error", 500


@router.post("/add-expense")
async def add_expense(request: AddExpenseRequest, _: None = Depends(set_db_from_header)):
    """
    Endpoint to add an expense.
    """
    try:
        check_status = await check_users_token(3, request.loginToken)
        if not check_status:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        expense_id = await add_expense_ps(request.categoryIndex, request.description, request.amount)
        if expense_id:
            await remember_users_action(request.username, f"Added Expense: Desc: {request.description}")
            return JSONResponse(content={
                "description": request.description,
                "amount": request.amount
            })
        return "Failure", 500
    except Exception as e:
        await flatbed('exception', f"in add_expense: {e}")
        return "Error", 500


@router.get("/submit-request")
async def submit_request(
        currentLang: str,
        category: str,
        name: str,
        phone: str,
        email: str = Query(...),
        message: str = Query(...)
):
    """
    Endpoint to submit a request from website.
    """
    try:
        html_content = """
        Html Content Here
        """
        text_content = f"""
        Name: {name}\nPhone: {phone}\nCategory: {category}\nMessage: {message}
        Text Content Here
        """
        await send_mail_html(f"Custom order requested", "parda.af@gmail.com", html_content, text_content)
        if email is not None:
            await send_mail_html(f"Custom order requested", email, html_content, text_content)
        # Redirect to the thank-you page after email is sent
        if currentLang == "en":
            url = "https://parda.af/thank-you.html"
        elif currentLang == "fa":
            url = "https://parda.af/fa/thank-you.html"
        elif currentLang == "ps":
            url = "https://parda.af/ps/thank-you.html"
        else:
            url = "https://parda.af/thank-you.html"
        return RedirectResponse(url=url, status_code=303)

    except Exception as e:
        await flatbed('exception', f"in submit_request: {e}")
        return "Error", 500


@router.post("/add-online-order")
async def add_online_order(request: AddOnlineOrderRequest):
    """
    Endpoint to add an online order.
    """
    set_current_db("pardaaf_db_7072")
    try:
        is_from_web_app = request.api == "123456"
        if not is_from_web_app:
            return JSONResponse(content={"error": "Access denied"}, status_code=401)

        order_id = await insert_new_online_order(request.firstName, request.phone, request.country, request.address,
                                                 request.city, request.state, request.zipCode, request.paymentMethod,
                                                 request.cartItems, request.totalAmount, request.lastName,
                                                 request.email, request.notes)

        if order_id:
            html_content = """
            Html Content Here
            """
            text_content = """
            Text Content Here
            """
            await send_mail_html(f"Order Confirmed #{order_id}", "parda.af@gmail.com", html_content, text_content)
            if request.email is not None:
                await send_mail_html(f"Order Confirmed #{order_id}", request.email, html_content, text_content)
            return JSONResponse(content={
                "order_id": order_id,
                "totalAmount": request.totalAmount,
                "paymentMethod": request.paymentMethod
            })
        return JSONResponse(content={"error": "Failed to create order"}, status_code=500)
    except Exception as e:
        await flatbed('exception', f"in add_online_order: {e}")
        return JSONResponse(content={"error": "Internal server error"}, status_code=500)


@router.get("/subscribe-newsletter")
async def subscribe_newsletter(
        email: str
):
    """
    Endpoint to let users subscribe to the newsletter.
    """
    set_current_db("pardaaf_db_7072")
    try:
        result = await subscribe_newsletter_ps(email)
        if result != "failed" and result != "subscribed":
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Confirm Your Subscription</title>
  <style>
    body {{
      margin: 0;
      padding: 0;
      font-family: Arial, sans-serif;
      background-color: #f6f6f6;
    }}
    table {{
      width: 100%;
      border-spacing: 0;
    }}
    td {{
      padding: 0;
    }}
    .container {{
      width: 100%;
      max-width: 600px;
      margin: 50px auto;  /* Added top margin for spacing */
      background: #ffffff;
      padding: 40px;
      border-radius: 8px;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }}
    .logo {{
      display: block;
      max-width: 120px;
      margin: 0;
    }}
    .hero-image {{
      width: 100%;
      max-width: 180px;
      margin: 30px auto;
    }}
    .header-text {{
      font-size: 20px;
      font-weight: bold;
      color: #333;
      text-align: center;
    }}
    .sub-header-text {{
      padding: 10px 0 30px;
      color: #555;
      text-align: center;
    }}
    .btn {{
      display: block;
      padding: 12px 25px;
      background-color: #ce1e1e;
      color: white;
      text-decoration: none;
      font-size: 16px;
      border-radius: 5px;
      text-align: center;
      width: 100%;  /* Added to ensure button stays centered */
      max-width: 300px;  /* Limit button size */
      margin: 0 auto;  /* Center the button */
    }}
    .footer {{
      padding: 30px 0 0;
      font-size: 12px;
      color: #999;
      text-align: center;
    }}
    /* Mobile responsiveness */
    @media only screen and (max-width: 600px) {{
      .container {{
        padding: 20px;
      }}
      .btn {{
        padding: 10px 20px;
        font-size: 14px;
        max-width: 250px;  /* Adjust button width for smaller screens */
      }}
      .hero-image {{
        max-width: 120px;
      }}
    }}
  </style>
</head>
<body>
  <table>
    <tr>
      <td align="center">
        <table class="container">
          <!-- Logo -->
          <tr>
            <td>
              <a href="https://parda.af"><img class="logo" src="https://cdn.parda.af/img/logo.png" alt="parda.af Logo" /></a>
            </td>
          </tr>

          <!-- SVG illustration -->
          <tr>
            <td align="center">
              <img class="hero-image" src="https://cdn.parda.af/img/mailbox.webp" alt="mailbox" />
            </td>
          </tr>

          <!-- Text -->
          <tr>
            <td class="header-text">
              One last step…
            </td>
          </tr>
          <tr>
            <td class="sub-header-text">
              Please confirm your subscription to stay connected.
            </td>
          </tr>

          <!-- Confirm button -->
          <tr>
            <td>
              <a href="https://zmt.basirsoft.tech/confirm-email-newsletter?token={result}" class="btn">
                Confirm Subscription
              </a>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td class="footer">
              If you didn’t request this, you can safely ignore this email.<br />
              Sent with ❤️ from parda.af
              <br /><br />
              <small>If you have any questions, contact us at <a href="mailto:sales@parda.af">sales@parda.af</a></small>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
            text_content = f"""One last step…\n
            Please confirm your subscription to stay connected.\n
            Click the link below to confirm.\n
            https://zmt.basirsoft.tech/confirm-email-newsletter?token={result}\n\n
            If you didn’t request this, you can safely ignore this email.\n
              Sent with ❤️ from parda.af"""
            await send_mail_html("Confirm your subscription", email, html_content, text_content)

        if result == "subscribed":
            return JSONResponse(content={"result": "Already subscribed"}, status_code=200)
        elif result == "failed":
            return JSONResponse(content={"error": "Failed to subscribe"}, status_code=400)
        return JSONResponse(content={"result": result}, status_code=200)

    except Exception as e:
        await flatbed('exception', f"in subscribe_newsletter: {e}")
        return JSONResponse(content={"error": "Internal server error"}, status_code=500)


@router.get("/unsubscribe-newsletter", response_class=HTMLResponse)
async def unsubscribe_newsletter(
        token: str
):
    """
    Endpoint to let users unsubscribe from the newsletter.
    """
    set_current_db("pardaaf_db_7072")
    try:
        if not token:
            raise HTTPException(status_code=400, detail="Invalid Method")

        result = await unsubscribe_newsletter_ps(token)
        if result:
            return f"<h3>You have been unsubscribed successfully.</h3>"

        return (f"<h3>Failed to unsubscribe.</h3>"
                f"<p> Please try again later.")
    except Exception as e:
        await flatbed('exception', f"in unsubscribe_newsletter: {e}")
        return JSONResponse(content={"error": "Internal server error"}, status_code=500)


@router.get("/confirm-email-newsletter", response_class=HTMLResponse)
async def confirm_email_newsletter(
        token: str
):
    """
    Endpoint to let users confirm their email.
    """
    set_current_db("pardaaf_db_7072")
    try:
        if not token:
            raise HTTPException(status_code=400, detail="Invalid Method")

        result = await confirm_email_newsletter_ps(token)
        if result:
            return (f"<h3>Your email has been confirmed successfully.</h3>"
                    f"<p>If this was an accident email unsubscribe to sales@parda.af")

        return (f"<h3>Failed to confirm your email.</h3>"
                f"<p> Please try again later.")
    except Exception as e:
        await flatbed('exception', f"in confirm_email_newsletter: {e}")
        return JSONResponse(content={"error": "Internal server error"}, status_code=500)


@router.get("/send-html-mail")
async def send_html_mail(
        email: str,
        subject: str,
        html_content: str,
        text_content: str
):
    """
    Endpoint to let me send mail for testing.
    """
    # check_status = await check_users_token(5, loginToken)
    # if not check_status:
    #     return JSONResponse(content={"error": "Access denied"}, status_code=401)

    try:
        result = await send_mail_html(subject, email, html_content, text_content)
        return JSONResponse(content={"result": result})
    except Exception as e:
        await flatbed('exception', f"in send_mail: {e}")
        return JSONResponse(content={"error": "Internal server error"}, status_code=500)


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
                "id": data["id"],
                "date": data["date"].strftime('%Y-%m-%d %H:%M:%S') if isinstance(data["date"], datetime)
                else data["date"],
                "username": data["username"],
                "action": data["action"],
            }
            recent_activity_list.append(activity)
    return recent_activity_list


def get_formatted_expenses_list(expenses_data):
    """
    Helper function to format expenses data into JSON-compatible objects.

    Parameters:
    - expenses_data: Raw data fetched from the database.

    Returns:
    - A list of formatted expenses dictionaries.
    """
    expenses_list = []
    if expenses_data:
        for data in expenses_data:
            search_result = make_expense_dic(data)
            expenses_list.append(search_result)

    return expenses_list


def get_formatted_search_results_list(products_data, bills_data):
    """
    Helper function to format products data and bills_data into JSON-compatible objects.

    Parameters:
    - products_data: Raw data fetched from the database.
    - bills_data: Raw data fetched from the database.

    Returns:
    - A list of formatted search_results dictionaries.
    """
    search_results_list = []
    if products_data:
        for data in products_data:
            search_result = make_product_dic(data)
            search_results_list.append(search_result)

    if bills_data:
        for data in bills_data:
            search_result = make_bill_dic(data)
            search_results_list.append(search_result)

    return search_results_list


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
            roll = make_roll_dic(data)
            rolls_list.append(roll)
    return rolls_list


def get_formatted_users_list(users_data):
    """
    Helper function to format users data into JSON-compatible objects.

    Parameters:
    - users_data: Raw data fetched from the database.

    Returns:
    - A list of formatted users dictionaries.
    """
    users_list = []
    if users_data:
        for data in users_data:
            user = {
                "fullName": data["full_name"],
                "username": data["username"],
                "level": data["level"]
            }
            users_list.append(user)
    return users_list


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
