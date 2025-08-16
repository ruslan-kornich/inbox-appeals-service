from datetime import timedelta
from pydantic import BaseModel, Field

class JWTSettings(BaseModel):
    secret_key: str  = Field(env="JWT_SECRET", default="CHANGE_ME")
    algorithm:  str  = "HS256"
    access_token_expires:  timedelta = timedelta(minutes=15)
    refresh_token_expires: timedelta = timedelta(days=7)

settings = JWTSettings()
