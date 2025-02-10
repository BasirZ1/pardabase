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


class RemoveProductRequest(BaseModel):
    loginToken: str
    code: str
    username: str


class RemoveRollRequest(BaseModel):
    loginToken: str
    rollCode: str
    username: str


class RemoveBillRequest(BaseModel):
    loginToken: str
    billCode: str
    username: str


class UpdateRollRequest(BaseModel):
    loginToken: str
    username: str
    rollCode: str
    quantity: int
    action: str


class AddExpenseRequest(BaseModel):
    loginToken: str
    username: str
    categoryIndex: int
    description: str
    amount: int
