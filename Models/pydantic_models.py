# Define the data structure for incoming requests
from typing import Optional

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


class RemoveUserRequest(BaseModel):
    loginToken: str
    usernameToRemove: str
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


class UpdateBillStatusRequest(BaseModel):
    loginToken: str
    username: str
    billCode: str
    status: str


class UpdateBillTailorRequest(BaseModel):
    loginToken: str
    username: str
    billCode: str
    tailor: str


class AddPaymentBillRequest(BaseModel):
    loginToken: str
    username: str
    billCode: str
    amount: int


class AddExpenseRequest(BaseModel):
    loginToken: str
    username: str
    categoryIndex: int
    description: str
    amount: int


class AddOnlineOrderRequest(BaseModel):
    api: str

    # Contact Info
    firstName: str
    lastName: Optional[str] = None
    phone: str
    email: Optional[str] = None

    # Shipping Info
    country: str
    address: str
    city: str
    state: str
    zipCode: Optional[str] = None

    # Payment
    paymentMethod: str

    # Cart
    cartItems: str  # If you're sending as JSON string
    totalAmount: int

    # Notes
    notes: Optional[str] = None
