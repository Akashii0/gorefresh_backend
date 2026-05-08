import logging
from typing import Optional, Tuple

import cloudinary
from cloudinary import uploader, utils
from fastapi import HTTPException, UploadFile
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.settings import get_settings

# globals
settings = get_settings()

# Configure logger
logger = logging.getLogger("cloudinary")
logger.setLevel(logging.INFO)


class CloudinaryService:
    def __init__(self):
        self.configure()

    def configure(self):
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True,
            timeout=30,  # 30-second timeout
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    async def upload_image(
        self,
        file: UploadFile,
        folder: str,
        public_id: Optional[str] = None,
        transformations: Optional[list] = None,
    ) -> Tuple[str, str]:
        """Upload image with retry logic and return (url, public_id)"""
        try:
            transformations = transformations or [
                {"width": 800, "height": 800, "crop": "fill", "quality": "auto"},
                {"fetch_format": "auto"},
            ]

            result = uploader.upload(
                file.file,
                folder=f"sahara/{folder}",
                public_id=public_id,
                transformation=transformations,
                resource_type="auto",
                invalidate=True,
            )
            return result["secure_url"], result["public_id"]
        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            raise HTTPException(500, "Image upload failed")

    @retry(stop=stop_after_attempt(3))
    async def delete_image(self, public_id: str) -> bool:
        """Delete image with retry logic"""
        try:
            result = uploader.destroy(public_id, invalidate=True)
            return result.get("result") == "ok"
        except Exception as e:
            logger.error(f"Deletion failed: {str(e)}")
            raise HTTPException(500, "Image deletion failed")

    def generate_thumbnail_url(self, public_id: str, width=300, height=300) -> str:
        """Generate transformed URL without re-uploading"""
        return utils.cloudinary_url(
            public_id,
            transformation=[
                {"width": width, "height": height, "crop": "fill"},
                {"quality": "auto"},
            ],
        )[0]
