from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str = 'ok'
    service: str = 'newspilot-review-api'
    api_version: str = 'v1'
