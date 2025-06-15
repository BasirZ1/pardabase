# Define the data structure for incoming requests
from typing import Optional

from pydantic import BaseModel


class RefreshTokenRequest(BaseModel):
    refreshToken: Optional[str] = None


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


class RemoveExpenseRequest(BaseModel):
    expenseId: str


class UpdateRollRequest(BaseModel):
    code: str
    quantity: int
    action: str


class UpdateBillStatusRequest(BaseModel):
    code: str
    status: str


class UpdateBillTailorRequest(BaseModel):
    code: str
    tailor: str


class AddPaymentBillRequest(BaseModel):
    code: str
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
