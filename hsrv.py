import re
import tempfile
from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Form, File, UploadFile, Query, BackgroundTasks, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse, HTMLResponse

from Models import AuthRequest, ChangePasswordRequest, CodeRequest, \
    UpdateRollRequest, AddExpenseRequest, UpdateBillStatusRequest, \
    UpdateBillTailorRequest, AddPaymentBillRequest, RemoveUserRequest, AddOnlineOrderRequest, RefreshTokenRequest
from helpers import classify_image_upload, get_formatted_search_results_list, \
    get_formatted_expenses_list, get_formatted_rolls_list, get_formatted_recent_activities_list, \
    get_formatted_users_list
from helpers.general import delete_temp_file
from utils import verify_jwt_user, set_current_db, send_mail_html, create_jwt_token, \
    set_db_from_tenant, create_refresh_token, verify_refresh_token
from db import insert_new_product, update_product, insert_new_roll, update_roll, insert_new_bill, \
    update_bill, insert_new_user, update_user, check_username_password, get_users_data, \
    search_recent_activities_list, update_users_password, search_products_list, get_product_and_roll_ps, \
    remember_users_action, remove_user_ps, search_bills_list_filtered, search_expenses_list_filtered, \
    search_products_list_filtered, insert_new_online_order, subscribe_newsletter_ps, remove_product_ps, \
    remove_roll_ps, remove_bill_ps, update_bill_tailor_ps, update_roll_quantity_ps, update_bill_status_ps, \
    add_payment_bill_ps, unsubscribe_newsletter_ps, get_bill_ps, get_users_list_ps, \
    get_dashboard_data_ps, search_rolls_for_product, search_bills_list, confirm_email_newsletter_ps, \
    handle_image_update, get_sample_image_for_roll, get_image_for_user, get_image_for_product, insert_new_expense, \
    update_expense
from utils.hasher import hash_password

router = APIRouter()
load_dotenv(override=True)


@router.get("/")
async def index():
    return "Legacy Route Error"


@router.post("/is-token-valid", summary="check if user authentication is valid")
async def is_token_valid(
        _: dict = Depends(verify_jwt_user(required_level=1))
):
    return JSONResponse(content={"result": True}, status_code=200)


@router.post("/refresh-token")
async def refresh_token(request: RefreshTokenRequest):
    user_data = await verify_refresh_token(request.refreshToken)

    data = await get_users_data(user_data['username'])

    user_id = data["user_id"]
    full_name = data["full_name"]
    level = data["level"]
    image_url = data["image_url"]

    # Create new access and refresh tokens
    new_access_token = create_jwt_token(
        sub=user_id,
        username=user_data['username'],
        full_name=full_name,
        level=level,
        tenant=user_data['tenant'],
        image_url=image_url
    )

    new_refresh_token = create_refresh_token(
        sub=user_id,
        username=user_data['username'],
        full_name=full_name,
        level=level,
        tenant=user_data['tenant'],
        image_url=image_url
    )

    return JSONResponse(content={
        "accessToken": new_access_token,
        "refreshToken": new_refresh_token,
        "fullName": full_name,
        "level": level,
        "imageUrl": image_url
    }, status_code=200)


@router.post("/login")
async def login(
        request: AuthRequest
):
    await set_db_from_tenant(request.tenant)

    check_result = await check_username_password(request.username, request.password)

    if check_result:
        data = await get_users_data(request.username)

        user_id = data["user_id"]
        full_name = data["full_name"]
        level = data["level"]
        image_url = data["image_url"]

        access_token = create_jwt_token(user_id, request.username, full_name, level,
                                        request.tenant, image_url)
        _refresh_token = create_refresh_token(user_id, request.username, full_name, level,
                                              request.tenant, image_url)

        return JSONResponse(content={
            "accessToken": access_token,
            "refreshToken": _refresh_token,
            "fullName": full_name,
            "level": level,
            "imageUrl": image_url
        }, status_code=200)
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")


@router.post("/get-dashboard-data")
async def get_dashboard_data(
        _: dict = Depends(verify_jwt_user(required_level=1))
):
    data = await get_dashboard_data_ps()
    # Fetch data for the dashboard
    return JSONResponse(content=data, status_code=200)


@router.get("/recent-activities-list-get")
async def get_recent_activity(
        _date: int,
        _: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Retrieve a list of recent activities.
    """
    recent_activity_data = await search_recent_activities_list(_date)
    recent_activities_list = get_formatted_recent_activities_list(recent_activity_data)

    return JSONResponse(content=recent_activities_list, status_code=200)


@router.get("/users-list-get")
async def get_users_list(
        _: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Retrieve a list of users.
    """
    users_data = await get_users_list_ps()
    users_list = get_formatted_users_list(users_data)
    return JSONResponse(content=users_list, status_code=200)


@router.post("/change-password")
async def change_password(
        request: ChangePasswordRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=1))
):
    """
    Endpoint to change password for Admin accounts.
    """
    old_password = request.oldPassword
    new_password = request.newPassword

    check_old_password = await check_username_password(user_data['username'], old_password)
    if check_old_password is False:
        return JSONResponse(content={"result": False}, status_code=200)

    await update_users_password(user_data['username'], hash_password(new_password))
    return JSONResponse(content={"result": True}, status_code=200)


@router.post("/add-or-edit-product")
async def add_or_edit_product(
        codeToEdit: Optional[str] = Form(None),
        name: str = Form(...),
        categoryIndex: int = Form(...),
        cost: int = Form(...),
        price: int = Form(...),
        description: Optional[str] = Form(None),
        image: Optional[UploadFile] = File(None),
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    image_status, image_data = await classify_image_upload(image)

    if codeToEdit is None:
        # CREATE NEW
        product_code = await insert_new_product(name, categoryIndex, cost, price, description)
        if not product_code:
            return JSONResponse(content={"result": False, "code": product_code, "name": name})

        await handle_image_update("product", user_data['tenant'], product_code, image_status, image_data)
        await remember_users_action(user_data['username'], f"Product Added: {product_code}")
    else:
        # UPDATE EXISTING
        product_code = await update_product(codeToEdit, name, categoryIndex, cost, price, description)
        if not product_code:
            return JSONResponse(content={"result": False, "code": product_code, "name": name})

        await handle_image_update("product", user_data['tenant'], product_code, image_status, image_data)
        await remember_users_action(user_data['username'], f"Product updated: {product_code}")

    return JSONResponse(content={
        "result": True,
        "code": product_code,
        "name": name
    })


@router.post("/add-or-edit-roll")
async def add_or_edit_roll(
        codeToEdit: Optional[str] = Form(None),
        productCode: Optional[str] = Form(None),
        quantity: int = Form(...),
        color: Optional[str] = Form(None),
        image: Optional[UploadFile] = File(None),
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    image_status, image_data = await classify_image_upload(image)

    if codeToEdit is None:
        # CREATE NEW
        code = await insert_new_roll(productCode, quantity, color)
        if not code:
            return JSONResponse(content={
                "result": False,
                "code": f"{productCode}{code}"
            })
        await handle_image_update("roll", user_data['tenant'], code, image_status, image_data)
        await remember_users_action(user_data['username'], f"Roll Added: {productCode}{code}")
    else:
        code = await update_roll(codeToEdit, quantity, color)
        if not code:
            return JSONResponse(content={
                "result": False,
                "code": f"{productCode}{code}"
            })
        await handle_image_update("roll", user_data['tenant'], code, image_status, image_data)
        await remember_users_action(user_data['username'], f"Roll updated: {productCode}{code}")

    return JSONResponse(content={
        "result": True,
        "code": f"{productCode}{code}"
    })


@router.post("/add-or-edit-bill")
async def add_or_edit_bill(
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
        additionalData: Optional[str] = Form(None),
        installation: Optional[str] = Form(None),
        user_data: dict = Depends(verify_jwt_user(required_level=2))
):
    if codeToEdit is None:
        # CREATE NEW
        code = await insert_new_bill(billDate, dueDate, customerName, customerNumber, price, paid, remaining,
                                     fabrics, parts, user_data['username'], additionalData, installation)
        if not code:
            return JSONResponse(content={
                "result": False,
                "code": code,
                "name": customerName
            })
        await remember_users_action(user_data['username'], f"Bill Added: {code}")
    else:
        # UPDATE OLD
        code = await update_bill(codeToEdit, dueDate, customerName, customerNumber, price, paid, remaining,
                                 fabrics, parts, additionalData, installation)
        if not code:
            return JSONResponse(content={
                "result": False,
                "code": code,
                "name": customerName
            })
        await remember_users_action(user_data['username'], f"Bill updated: {code}")
    return JSONResponse(content={
        "result": True,
        "code": code,
        "name": customerName
    })


@router.post("/add-expense")
async def add_expense(
        request: AddExpenseRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Endpoint to add an expense.
    """
    expense_id = await insert_new_expense(request.categoryIndex, request.description, request.amount)
    if expense_id:
        await remember_users_action(user_data['username'], f"Added Expense: Desc: {request.description}")
        return JSONResponse(content={
            "description": request.description,
            "amount": request.amount
        })
    return "Failure", 500


@router.post("/add-or-edit-expense")
async def add_or_edit_expense(
        categoryIndex: int = Form(...),
        amount: int = Form(...),
        description: Optional[str] = Form(None),
        idToEdit: Optional[str] = Form(None),
        user_data: dict = Depends(verify_jwt_user(required_level=2))
):
    if idToEdit is None:
        # CREATE NEW
        _id = await insert_new_expense(categoryIndex, description, amount)
        if not id:
            return JSONResponse(content={
                "result": False,
                "description": description,
                "amount": amount
            })
        await remember_users_action(user_data['username'], f"Expense Added: {description} {amount}")
    else:
        # UPDATE OLD
        _id = await update_expense(idToEdit, categoryIndex, description, amount)
        if not _id:
            return JSONResponse(content={
                "result": False,
                "description": description,
                "amount": amount
            })
        await remember_users_action(user_data['username'], f"Expense updated: {_id},"
                                                           f" description: {description} amount: {amount}")
    return JSONResponse(content={
        "result": True,
        "description": description,
        "amount": amount
    })


@router.post("/add-or-edit-user")
async def add_or_edit_user(
        usernameToEdit: Optional[str] = Form(None),
        fullName: str = Form(...),
        usernameChange: str = Form(...),
        password: Optional[str] = Form(None),
        level: int = Form(...),
        image: Optional[UploadFile] = File(None),
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    image_status, image_data = await classify_image_upload(image)

    if usernameToEdit is None:
        # CREATE NEW
        if password is None:
            return JSONResponse(content={"error": "Password is missing"}, status_code=403)
        result = await insert_new_user(fullName, usernameChange, password, level)
        if not result:
            return JSONResponse(content={"result": False}, status_code=201)
        await handle_image_update("user", user_data['tenant'], usernameChange, image_status, image_data)
        await remember_users_action(user_data['username'], f"User added: {usernameChange}")
    else:
        result = await update_user(usernameToEdit, fullName, usernameChange, level, password)
        if not result:
            return JSONResponse(content={"result": False}, status_code=201)
        await handle_image_update("user", user_data['tenant'], usernameChange, image_status, image_data)
        await remember_users_action(user_data['username'], f"user updated: {usernameChange}")

    return JSONResponse(content={"result": True}, status_code=200)


@router.get("/bills-list-get")
async def get_bills_list(
        date: int,
        state: int,
        _: dict = Depends(verify_jwt_user(required_level=1))
):
    """
    Retrieve a list of bills based on date or state.
    """
    bills_data = await search_bills_list_filtered(date, state)
    bills_list = get_formatted_search_results_list(None, bills_data)
    if bills_list:
        return JSONResponse(content=bills_list, status_code=200)
    else:
        return "not found", 404


@router.get("/expenses-list-get")
async def get_expenses_list(
        date: int,
        category: int,
        _: dict = Depends(verify_jwt_user(required_level=1))
):
    """
    Retrieve a list of expenses based on date and category.
    """
    expenses_data = await search_expenses_list_filtered(date, category)
    expenses_list = get_formatted_expenses_list(expenses_data)
    return JSONResponse(content=expenses_list, status_code=200)


@router.get("/products-list-get")
async def get_products_list(
        stockCondition: int,
        category: int,
        _: dict = Depends(verify_jwt_user(required_level=1))
):
    """
    Retrieve a list of products based on date and category.
    """
    products_data = await search_products_list_filtered(stockCondition, category)
    products_list = get_formatted_search_results_list(products_data, None)
    if products_list:
        return JSONResponse(content=products_list, status_code=200)
    else:
        return "not found", 404


@router.get("/search-results-list-get")
async def get_search_results_list(
        searchQuery: str,
        _: dict = Depends(verify_jwt_user(required_level=1))
):
    """
    Smart search for products and bills based on different query formats.
    """
    search_results_list = []

    bill_code_pattern = re.fullmatch(r"(?i)b\d+", searchQuery)  # `(?i)` makes it case insensitive
    product_code_pattern = re.fullmatch(r"(?i)p\d+", searchQuery)
    roll_code_pattern = re.fullmatch(r"(?i)p\d+r\d+", searchQuery)
    phone_number_pattern = re.fullmatch(r"\+?\d{4,14}", searchQuery)  # Intl. and local formats

    if bill_code_pattern:
        # Search bill by code
        bills_data = await search_bills_list(searchQuery, 0)
        search_results_list = get_formatted_search_results_list(None, bills_data)

    elif roll_code_pattern:
        product_data = await get_product_and_roll_ps(searchQuery)
        search_results_list.append(product_data)

    elif product_code_pattern:
        # Search product by code
        products_data = await search_products_list(searchQuery, 0)
        search_results_list = get_formatted_search_results_list(products_data, None)

    elif phone_number_pattern:
        # Search bill by customer phone number
        bills_data = await search_bills_list(searchQuery, 2)
        search_results_list = get_formatted_search_results_list(None, bills_data)

    else:
        # General search (search both products and bills by name)
        products_data = await search_products_list(searchQuery, 1)
        bills_data = await search_bills_list(searchQuery, 1)
        search_results_list = get_formatted_search_results_list(products_data, bills_data)

    return JSONResponse(content=search_results_list, status_code=200)


@router.get("/search-products-list-get")
async def get_search_products_list(
        searchQuery: str,
        _: dict = Depends(verify_jwt_user(required_level=1))
):
    """
    Direct product search (code, name).
    """

    results = []
    product_code_pattern = re.fullmatch(r"(?i)p\d+", searchQuery)
    roll_code_pattern = re.fullmatch(r"(?i)p\d+r\d+", searchQuery)

    if roll_code_pattern:
        product_data = await get_product_and_roll_ps(searchQuery)
        results.append(product_data)
    elif product_code_pattern:
        products = await search_products_list(searchQuery, 0)
        results = get_formatted_search_results_list(products, None)
    else:
        # name or general string
        products = await search_products_list(searchQuery, 1)
        results = get_formatted_search_results_list(products, None)

    return JSONResponse(content=results, status_code=200)


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


@router.get("/product-image-get")
async def get_product_image(
        code: str = Query(...),
        _: dict = Depends(verify_jwt_user(required_level=1)),
        background_tasks: BackgroundTasks = None
):
    """
    Endpoint to get product's image by code.
    """
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
        return JSONResponse(content="Image not found", status_code=404)


@router.get("/user-image-get")
async def get_user_image(
        user_data: dict = Depends(verify_jwt_user(required_level=1)),
        background_tasks: BackgroundTasks = None
):
    """
    Endpoint to get user's image by username.
    """
    # Get the agent image data
    user_image = await get_image_for_user(user_data['username'])

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
        return JSONResponse(content="Image not found", status_code=404)


@router.get("/roll-sample-image-get")
async def get_roll_sample_image(
        code: str = Query(...),
        _: dict = Depends(verify_jwt_user(required_level=1)),
        background_tasks: BackgroundTasks = None
):
    """
    Endpoint to get roll's image by code.
    """
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
        return JSONResponse(content="Image not found", status_code=404)


@router.get("/product-and-roll-get")
async def get_product_and_roll(
        code: str,
        _: dict = Depends(verify_jwt_user(required_level=1))
):
    """
    Retrieve a product and roll based on code.
    """
    product = await get_product_and_roll_ps(code)
    if product:
        return JSONResponse(content=product, status_code=200)
    else:
        return "not found", 404


@router.get("/bill-get")
async def get_bill(
        code: str,
        _: dict = Depends(verify_jwt_user(required_level=1))
):
    """
    Retrieve a bill based on code.
    """
    bill = await get_bill_ps(code)

    if bill:
        return JSONResponse(content=bill, status_code=200)
    else:
        return "not found", 404


@router.post("/remove-product")
async def remove_product(
        request: CodeRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Endpoint to remove a product.
    """
    result = await remove_product_ps(request.code)
    if result:
        await handle_image_update("product", user_data['tenant'], request.code, "remove", None)
        await remember_users_action(user_data['username'], f"Product removed: {request.code}")
    return JSONResponse(content={"result": result}, status_code=200)


@router.post("/remove-roll")
async def remove_roll(
        request: CodeRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Endpoint to remove a roll.
    """
    result = await remove_roll_ps(request.code)
    if result:
        await handle_image_update("roll", user_data['tenant'], request.code, "remove", None)
        await remember_users_action(user_data['username'], f"Roll removed: {request.code}")
    return JSONResponse(content={"result": result}, status_code=200)


@router.post("/remove-user")
async def remove_user(
        request: RemoveUserRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Endpoint to remove a user.
    """
    result = await remove_user_ps(request.usernameToRemove)
    if result:
        await handle_image_update("user", user_data['tenant'], request.usernameToRemove, "remove", None)
        await remember_users_action(user_data['username'], f"User removed: {request.usernameToRemove}")
    return JSONResponse(content={"result": result}, status_code=200)


@router.post("/remove-bill")
async def remove_bill(
        request: CodeRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Endpoint to remove a bill.
    """
    result = await remove_bill_ps(request.code)
    if result:
        await remember_users_action(user_data['username'], f"Bill removed: {request.code}")
    return JSONResponse(content={"result": result}, status_code=200)


@router.post("/update-roll-quantity")
async def update_roll_quantity(
        request: UpdateRollRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=3))
):
    """
    Endpoint to update a roll's quantity.
    """
    result = await update_roll_quantity_ps(request.code, request.quantity, request.action)
    await remember_users_action(user_data['username'], f"Roll quantity updated: "
                                                       f"{request.code} {request.action} {request.quantity}")
    return JSONResponse(content={"result": result}, status_code=200)


@router.post("/update-bill-status")
async def update_bill_status(
        request: UpdateBillStatusRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=2))
):
    """
    Endpoint to update a bill's status.
    """
    result = await update_bill_status_ps(request.code, request.status)
    await remember_users_action(user_data['username'], f"Bill status updated: "
                                                       f"{request.code} {request.status}")
    return JSONResponse(content={"result": result}, status_code=200)


@router.post("/update-bill-tailor")
async def update_bill_tailor(
        request: UpdateBillTailorRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=2))
):
    """
    Endpoint to update a bill's tailor.
    """
    result = await update_bill_tailor_ps(request.code, request.tailor)
    await remember_users_action(user_data['username'], f"Bill's tailor updated: "
                                                       f"{request.code} {request.tailor}")
    return JSONResponse(content={"result": result}, status_code=200)


@router.post("/add-payment-bill")
async def add_payment_bill(
        request: AddPaymentBillRequest,
        user_data: dict = Depends(verify_jwt_user(required_level=2))
):
    """
    Endpoint to update a bill's payment.
    """
    result = await add_payment_bill_ps(request.code, request.amount)
    await remember_users_action(user_data['username'], f"Added payment to bill: "
                                                       f"{request.code} {request.amount}")
    return JSONResponse(content={"result": result}, status_code=200)


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


@router.post("/add-online-order")
async def add_online_order(request: AddOnlineOrderRequest):
    """
    Endpoint to add an online order.
    """
    set_current_db("pardaaf_db_7072")
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


@router.get("/subscribe-newsletter")
async def subscribe_newsletter(
        email: str
):
    """
    Endpoint to let users subscribe to the newsletter.
    """
    set_current_db("pardaaf_db_7072")
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
              <a href="https://parda.af">
                <img class="logo" src="https://cdn.parda.af/img/logo.png" alt="parda.af Logo" />
              </a>
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


@router.get("/unsubscribe-newsletter", response_class=HTMLResponse)
async def unsubscribe_newsletter(
        token: str
):
    """
    Endpoint to let users unsubscribe from the newsletter.
    """
    set_current_db("pardaaf_db_7072")
    if not token:
        raise HTTPException(status_code=400, detail="Invalid Method")

    result = await unsubscribe_newsletter_ps(token)
    if result:
        return f"<h3>You have been unsubscribed successfully.</h3>"

    return (f"<h3>Failed to unsubscribe.</h3>"
            f"<p> Please try again later.")


@router.get("/confirm-email-newsletter", response_class=HTMLResponse)
async def confirm_email_newsletter(
        token: str
):
    """
    Endpoint to let users confirm their email.
    """
    set_current_db("pardaaf_db_7072")
    if not token:
        raise HTTPException(status_code=400, detail="Invalid Method")

    result = await confirm_email_newsletter_ps(token)
    if result:
        return (f"<h3>Your email has been confirmed successfully.</h3>"
                f"<p>If this was an accident email unsubscribe to sales@parda.af")

    return (f"<h3>Failed to confirm your email.</h3>"
            f"<p> Please try again later.")


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
    result = await send_mail_html(subject, email, html_content, text_content)
    return JSONResponse(content={"result": result})


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(router, host='127.0.0.1', port=8000)
