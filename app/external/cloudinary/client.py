import logging
from typing import Optional
from fastapi import HTTPException, UploadFile
import cloudinary
from cloudinary import uploader
from app.core.settings import get_settings
import asyncio
from functools import partial

settings = get_settings()
logger = logging.getLogger("cloudinary")
logger.setLevel(logging.INFO)


class ImageService:
    def __init__(self):
        self.configure()
        self.max_retries = 3
        self.base_folder = "gorefresh"

    def configure(self):
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True,
            timeout=30,
        )

    async def _execute_cloudinary_operation(self, operation, *args, **kwargs):
        """Generic retry handler for Cloudinary operations"""
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(
                    None, partial(operation, *args, **kwargs)
                )
                return result
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff

        logger.error(f"Operation failed after {self.max_retries} attempts")
        raise HTTPException(500, "Cloudinary operation failed") from last_exception

    async def upload_image(
        self,
        file: UploadFile,
        entity_type: str,  # "restaurants", "food-items", "extra-items"
        entity_id: int,
        public_id_prefix: Optional[str] = None,
    ):
        """Upload image for any entity type"""
        try:
            # Validate image type
            if not file.content_type.startswith("image/"):  # type: ignore
                raise HTTPException(400, "Only image files are allowed")

            # Read file content once
            file_content = await file.read()

            public_id = f"{public_id_prefix or entity_type}-{entity_id}"

            result = await self._execute_cloudinary_operation(
                uploader.upload,
                file_content,
                folder=f"{self.base_folder}/{entity_type}",
                public_id=public_id,
                resource_type="image",
                invalidate=True,
            )

            return result["secure_url"]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            raise HTTPException(500, "Image upload failed")

    async def delete_image(self, public_id: str) -> bool:
        """Delete image by public_id"""
        try:
            result = await self._execute_cloudinary_operation(
                uploader.destroy, public_id, invalidate=True
            )
            return result.get("result") == "ok"
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Deletion failed: {str(e)}")
            raise HTTPException(500, "Image deletion failed")
