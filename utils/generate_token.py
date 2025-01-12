import base64
import hashlib
import hmac


def generate_token(username):
    # Generate and store a new token
    secret_key = "123@pardabase"
    # Encode the user data and secret key as bytes
    user_data_bytes = username.encode('utf-8')
    secret_key_bytes = secret_key.encode('utf-8')
    token_bytes = hmac.new(secret_key_bytes, user_data_bytes, hashlib.sha256).digest()
    login_token = base64.urlsafe_b64encode(token_bytes).decode('utf-8')
    return login_token
