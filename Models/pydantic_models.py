# Define the data structure for incoming requests
from datetime import datetime
from enum import Enum
from typing import Optional, Literal, List
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


class RemoveRequest(BaseModel):
    code: str
    mode: Literal["remove", "archive"] = "archive"


class CheckSyncRequest(BaseModel):
    key: str


class GetListsRequest(BaseModel):
    keys: List[str]


class RemovePurchaseRequest(BaseModel):
    purchaseId: int
    mode: Literal["remove", "archive"] = "archive"


class RemoveUserRequest(BaseModel):
    usernameToRemove: str


class RemoveSupplierRequest(BaseModel):
    supplierId: int


class RemoveExpenseRequest(BaseModel):
    expenseId: int


class UpdateRollRequest(BaseModel):
    code: str
    quantity: int
    action: str
    comment: Optional[str] = None


class CommentRequest(BaseModel):
    code: str
    quantity: int
    comment: str


class UpdateCutFabricTXStatusRequest(BaseModel):
    id: int
    newStatus: str


class UpdateBillStatusRequest(BaseModel):
    code: str
    status: str


class UpdateBillTailorRequest(BaseModel):
    code: str
    tailor: str
    tailorName: Optional[str] = None


class AddPaymentBillRequest(BaseModel):
    code: str
    amount: int


class GenerateReportRequest(BaseModel):
    selectedReport: str
    fromDate: str
    toDate: str


class AddExpenseRequest(BaseModel):
    categoryIndex: int
    description: str
    amount: int


class PrintJob(BaseModel):
    id: int
    file_url: str
    status: str  # PENDING or PRINTED
    created_at: datetime


class AddPrintJobRequest(BaseModel):
    fileName: str
    fileContentBase64: str  # The base64 string of the bill image/pdf


class MarkPrintedRequest(BaseModel):
    job_id: int


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


class BotState(str, Enum):
    IDLE = "idle"
    AWAITING_USERNAME = "awaiting_username"
    AWAITING_BILL_CHECK = "awaiting_bill_check"
    AWAITING_BILL_NUMBER = "awaiting_bill_number"
