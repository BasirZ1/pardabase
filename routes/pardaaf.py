from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse

from Models import AddOnlineOrderRequest
from db import insert_new_online_order, subscribe_newsletter_ps, confirm_email_newsletter_ps, unsubscribe_newsletter_ps, \
    get_fx_current_rate
from utils import send_mail_html, set_current_db, verify_jwt_user

router = APIRouter()
load_dotenv(override=True)


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
        await send_mail_html("Confirm your subscription", email, html_content, text_content, include_unsubscribe=True, token=result)

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
        text_content: str,
        custom_sender: Optional[str] = None,
        user_data: dict = Depends(verify_jwt_user(required_level=5))
):
    """
    Endpoint to let me send mail for testing.
    """
    # check_status = await check_users_token(5, loginToken)
    # if not check_status:
    #     return JSONResponse(content={"error": "Access denied"}, status_code=401)
    result = await send_mail_html(subject, email, html_content, text_content, custom_sender=custom_sender)
    return JSONResponse(content={"result": result})


@router.get("/fx/latest")
async def get_fx_latest(
        quoteCurrency: str,
        baseCurrency: Optional[str] = None
        # user_data: dict = Depends(verify_jwt_user(required_level=1))
):
    """
    Endpoint to get rate for a currency pair.
    """
    main_db = "pardaaf_main"
    set_current_db(main_db)
    data = await get_fx_current_rate(quoteCurrency, baseCurrency)
    return JSONResponse(content=data)
