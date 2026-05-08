from typing import Annotated

from fastapi import Depends

from app.Admin import models, selectors

CurrentAdmin = Annotated[models.Admin, Depends(selectors.get_current_admin)]
