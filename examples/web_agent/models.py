from pydantic import BaseModel, Field

class WebFormResult(BaseModel):
    success: bool = Field(description="Whether the form was successfully submitted")
    message: str = Field(description="The response message from the website")
    data_submitted: dict = Field(description="The data that was submitted in the form")
