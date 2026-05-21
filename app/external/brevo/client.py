from fastapi import HTTPException
from app.core.settings import get_settings
from app.external._request import InternalRequestClient
from app.external.brevo.schemas import BrevoEmailPayload, EmailResponse
import httpx

settings = get_settings()


class BrevoClient:
    """
    Brevo client to send emails

    Args:
        InternalRequestClient (_type_): _description_
    """

    def __init__(self):
        self.base_url = settings.BREVO_URL
        self.api_key = settings.BREVO_API
        self.default_sender_name = settings.DEFAULT_SENDER_NAME
        self.default_sender_email = settings.DEFAULT_SENDER_EMAIL
        self.client = InternalRequestClient(base_url=settings.BREVO_URL)

    async def send_email(self, payload: BrevoEmailPayload):
        url = f"{self.base_url}/smtp/email"
        headers = {
            "accept": "application/json",
            "api-key": self.api_key,
            "content-type": "application/json",
        }

        # Convert payload to dict (using the same structure expected by Brevo)
        data = payload.model_dump(by_alias=True, exclude_none=True)

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                resp_data = response.json()
                return EmailResponse(**resp_data)
            except httpx.HTTPStatusError as e:
                # logger.error(
                #     f"Brevo API error {e.response.status_code}: {e.response.text}"
                # )
                raise HTTPException(
                    status_code=502,
                    detail=f"Email service error: {e.response.status_code}, {e.response.text}",
                )
            except Exception as e:
                # logger.error(f"Unexpected error sending email via Brevo: {str(e)}")
                raise HTTPException(
                    status_code=500, detail=f"Failed to send email {str(e)}"
                )
