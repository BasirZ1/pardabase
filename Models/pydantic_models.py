# Define the data structure for incoming requests
from pydantic import BaseModel


class TokenValidationRequest(BaseModel):
    loginToken: str


class AuthRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    loginToken: str
    username: str
    oldPassword: str
    newPassword: str


class NewAdminRequest(BaseModel):
    loginToken: str
    fullName: str
    username: str
    password: str
    level: int
