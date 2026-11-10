from pydantic import BaseModel, EmailStr, Field


class AccountCreate(BaseModel):
    email: EmailStr = Field(max_length=320)
    password: str = Field(min_length=12, max_length=128)


class AccountResponse(BaseModel):
    id: int
    email: str
    onboarding_status: str
