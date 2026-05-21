from pydantic import BaseModel, Field


class BrevoAttachment(BaseModel):
    """Attachment for Brevo email (content as base64)."""

    name: str
    content: str  # base64-encoded


class BrevoEmailPayload(BaseModel):
    """Payload for sending email via Brevo API."""

    sender: dict  # {"name": str, "email": str}
    to: list[dict]  # [{"email": str, "name": Optional[str]}]
    replyTo: dict | None = None
    subject: str
    htmlContent: str | None = None
    textContent: str | None = None
    attachment: list[BrevoAttachment] | None = None

    model_config = {"populate_by_name": True}


class EmailResponse(BaseModel):
    status: str = Field(default="success", description="The status of the response")
    msg: str = Field(
        default="Email retrieved successfully", description="The status of the response"
    )
    messageId: str = Field(description="The message ID")
    # data: ContactForm = Field(description="The contact details")
