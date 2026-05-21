from typing import Any

from app.common.exceptions import BadRequest
from app.core.settings import get_settings
from app.external._request import InternalRequestClient
from app.external.paystack.schemas import (
    PaystackInitTransactionResponse,
    PaystackVerifyTransactionResponse,
)

# Globals
settings = get_settings()


class InternalPaystackClient:
    """
    Paystack client for async requests
    """

    def __init__(self):
        self.base_url = settings.PAYSTACK_URL
        self.api_key = settings.PAYSTACK_API_KEY
        self.client = InternalRequestClient(base_url=settings.PAYSTACK_URL)

    async def init_transaction(
        self,
        amount: float,
        email: str,
        callback_url: str,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Initialize a transaction with Paystack

        Args:
            amount: Amount in naira (will be converted to kobo)
            email: Customer's email address
            callback_url: URL to redirect to after payment
            metadata: Additional data to attach to the transaction

        Returns:
            PaystackInitTransactionResponse object containing transaction details

        Raises:
            HTTPException: If the Paystack API request fails
        """
        url = f"{self.base_url}/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "amount": int(amount),
            "email": email,
            "callback_url": callback_url,
        }

        if metadata:
            data["metadata"] = metadata

        try:
            response = await self.client.post(endpoint=url, json=data, headers=headers)
            response.raise_for_status()
            return PaystackInitTransactionResponse(**response.json())
        except Exception as e:
            # Log error
            raise BadRequest(f"Failed to initialize Paystack transaction: {str(e)}")

    async def verify_transaction(self, reference: str):
        """
        Verify a transaction with Paystack

        Args:
            reference: The Paystack transaction reference

        Returns:
            PaystackVerifyTransactionResponse object containing transaction details

        Raises:
            Exception: If the Paystack API request fails
        """
        url = f"{self.base_url}/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = await self.client.get(endpoint=url, headers=headers)
            response.raise_for_status()
            return PaystackVerifyTransactionResponse(**response.json())
        except Exception as e:
            # Log error
            raise BadRequest(f"Failed to verify Paystack transaction: {str(e)}")
