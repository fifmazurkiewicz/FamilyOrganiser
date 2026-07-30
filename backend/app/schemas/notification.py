import uuid
from datetime import datetime

from pydantic import BaseModel, computed_field


class NotificationResponse(BaseModel):
    id: uuid.UUID
    title: str
    body: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}

    @computed_field  # type: ignore[prop-decorator]
    @property
    def message(self) -> str:
        return self.body
