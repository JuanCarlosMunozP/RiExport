from email_validator import EmailNotValidError
from pydantic import BaseModel, field_validator, validate_email


class Token(BaseModel):
    welcome_message: str
    message: str
    access_token:str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class LoginRequest(BaseModel):

    email: str
    password: str

    @field_validator("email")
    def validate_email(cls,v):
        if any(c.isupper() for c in v):
            raise ValueError("Email must be in lowercase letter only")

        try:
            validate_email(v)
            return v
        except EmailNotValidError:
            raise ValueError("Invalid email format")

    @field_validator("password")
    def validate_password_field(cls,v):
        from schemas.user import validate_password
        return validate_password(v)

    class Config:
        json_schema_extra = {
            "example":{
                "email":"your.email@example.com",
                "password":"your_password"
            }
        }

class ForgotPasswordRequest(BaseModel):

    email:str 

    @field_validator("email")
    def validate_email(cls,v):
        if any(c.isupper() for c in v):
            raise ValueError("Email must be in lowercase letter only")

        try:
            validate_email(v)
            return v
        except EmailNotValidError:
            raise ValueError("Invalid email format")


class ResetPasswordRequest(BaseModel):

    token:str
    new_password:str

    @field_validator("new_password")
    def validate_new_password(cls,v):
        from schemas.user import validate_password
        return validate_password(v)

class PasswordResetResponse(BaseModel):

    message: str
    reset_token:str

class PasswordResetSuccessResponse(BaseModel):
    message:str
        
        
