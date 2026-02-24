import os
from dotenv import load_dotenv

# Load .env for local development
load_dotenv()

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Courtmate")
    ENV: str = os.getenv("ENV", "development")

    DATABASE_URL: str = os.getenv("DATABASE_URL")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 60)
    )

    def validate(self):
        """Validate required production environment variables"""
        required_vars = {
            "DATABASE_URL": self.DATABASE_URL,
            "JWT_SECRET_KEY": self.JWT_SECRET_KEY,
        }

        missing = [key for key, value in required_vars.items() if not value]

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

settings = Settings()

# Only enforce strict validation in production
if settings.ENV == "production":
    settings.validate()