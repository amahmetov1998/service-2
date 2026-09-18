from pydantic import BaseModel, ConfigDict


class Message(BaseModel):
    message: dict
