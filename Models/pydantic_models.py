# Define the data structure for incoming requests
from typing import Optional

from pydantic import BaseModel


class AuthRequest(BaseModel):
    tenant: str
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    oldPassword: str
    newPassword: str


class CodeRequest(BaseModel):
    code: str


class RemoveUserRequest(BaseModel):
    usernameToRemove: str


class UpdateRollRequest(BaseModel):
    rollCode: str
    quantity: int
    action: str


class UpdateBillStatusRequest(BaseModel):
    billCode: str
    status: str


class UpdateBillTailorRequest(BaseModel):
    billCode: str
    tailor: str


class AddPaymentBillRequest(BaseModel):
    billCode: str
    amount: int


class AddExpenseRequest(BaseModel):
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
