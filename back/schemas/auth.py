from enum import Enum
from typing import Optional
import re 

from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel, field_validator

def validate_password(password:str) -> str:
    regex = r"[A-Za-z!@$%^&*(),.?\":{}|<>]"

    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if not regex:
        raise ValueError("Password must contain at least one uppercase letter, one lowercase letter, one digit, one special character.")
    return password


def validate_username(name:str) -> str:

    if re.search(r"\d",name):
        raise ValueError("Name can't contain numbers")
    if not name.replace(" ","").isalpha():
        raise ValueError("Name can only contain letters and spaces")
    return name


class UserBase(BaseModel):
    username: str
    email:str 
    password: str
    role:Enum

    @field_validator("email")
    def validate_email(cls,v):
        if any(c.isupper() for c in v):
            raise ValueError("Email must be in lowercase letters only")
        try:
            validate_email(v, check_deliverability=False)
            return v
        except EmailNotValidError as e:
            # email-validator 2.x rejects .local even without DNS
            if "special-use or reserved" in str(e).lower() and "@" in v:
                local_part, _, domain = v.partition("@")
                if local_part and "." in domain:
                    return v
            raise ValueError("Invalid email format")

class UserCreate(UserBase):
    username: str
    email:str
    password:str
    role: str

    @field_validator("password")
    def validate_password_field(cls,v):
        return validate_password(v)
    


class UserResponse(BaseModel):
    welcome_message: str | None = None
    username: str
    email:str
    id:int

    class Config:
        from_attributes = True


class User(UserResponse):
    username:str

    class Config:
        from_attributes = True


class TokenPair(BaseModel):
    access_token:str
    refresh_token:str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token:str

