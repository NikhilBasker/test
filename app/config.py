import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'my$up3r$3cur3K3y')
