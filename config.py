import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    APP_NAME = os.environ.get('APP_NAME') or 'Flask Cookbook'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'password'
