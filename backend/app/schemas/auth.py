from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)
    avatar: str | None = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str | None = Field(None, min_length=8, max_length=128)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
