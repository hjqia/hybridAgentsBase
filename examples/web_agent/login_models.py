from pydantic import BaseModel, Field

class LoginResult(BaseModel):
    success: bool = Field(description="Whether the login was successful")
    message: str = Field(default="No message provided", description="A message about the login status")
