from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GEMINI_API_KEY: str = Field(..., description="API key for Gemini")
    GEMINI_MODEL_NAME: str = Field(
        default="gemini-1.5-flash", description="Gemini model to use"
    )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
