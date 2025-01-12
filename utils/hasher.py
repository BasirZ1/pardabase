import hashlib


def hash_password(password):
    # Convert the password to bytes and hash it using SHA-256
    return hashlib.sha256(password.encode()).hexdigest()


def check_password(stored_password_hash, provided_password):
    # Hash the provided password and compare it with the stored hash
    return stored_password_hash == hashlib.sha256(provided_password.encode()).hexdigest()
