from dotenv import load_dotenv
import os

load_dotenv(override=True)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    PAYMENT_MERCHANT_ID = os.environ["PAYMENT_MERCHANT_ID"]
    PAYMENT_SECURITY_TOKEN = os.environ["PAYMENT_SECURITY_TOKEN"]
    PAYMENT_API_URL = os.environ["PAYMENT_API_URL"]
    PORT = os.environ.get("FLASK_PORT", 5000)


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    DEBUG = False
