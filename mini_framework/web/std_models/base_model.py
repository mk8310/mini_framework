from datetime import datetime, date

from pydantic import BaseModel

def json_datetime_encoder(v):
    if not v:
        return v
    if isinstance(v, datetime):
        return v.strftime("%Y-%m-%d %H:%M:%S.%f")
    if isinstance(v, date):
        return v.strftime("%Y-%m-%d")
    return v

class BaseViewModel(BaseModel):
    class Config:
        json_encoders = {
            datetime: json_datetime_encoder,
            date: json_datetime_encoder,
        }