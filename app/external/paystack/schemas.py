from pydantic import BaseModel, Field


class PaystackTransactionData(BaseModel):
    """Paystack transaction data model"""

    authorization_url: str
    access_code: str
    reference: str


class PaystackInitTransactionResponse(BaseModel):
    """Paystack initialization response model"""

    status: bool
    message: str
    data: PaystackTransactionData


class PaystackVerifyTransactionData(BaseModel):
    """
    Paystack response schema for verify transaction requests
    """

    status: str = Field(description="Status of the payment")
    reference: str = Field(description="The reference for the transaction")
    amount: float = Field(description="The amount of the transaction")
    channel: str = Field(description="The method of payment")


class PaystackVerifyTransactionResponse(BaseModel):
    """Paystack transaction response model"""

    status: bool = Field(description="The status of the transaction")
    msg: str = Field(alias="message", description="The response message")
    data: PaystackVerifyTransactionData = Field(
        description="The data of the transaction", alias="data"
    )
