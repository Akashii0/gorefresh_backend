from app.core.settings import get_settings
from app.Admin import models

# Globals
settings = get_settings()


async def format_admin(admin: models.Admin):
    """
    Format admin obj to dict
    """
    return {
        "id": admin.id,
        "pfp_url": admin.pfp_url,
        "first_name": admin.first_name,
        "last_name": admin.last_name,
        "email": admin.email,
        "phone": admin.phone,
        "is_active": admin.is_active,
        "last_login": admin.last_login,
        "updated_at": admin.updated_at,
        "created_at": admin.created_at,
    }


async def format_admin_summary(admin: models.Admin):
    """
    Formats the admin obj to dict
    """
    return {
        "id": admin.id,
        "pfp_url": admin.pfp_url,
        "full_name": f"{admin.first_name} {admin.last_name}",
    }
