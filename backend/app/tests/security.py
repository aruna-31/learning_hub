from dotenv import load_dotenv
load_dotenv()
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime,timedelta
import os


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password):
    return pwd_context.hash(password)
def verify_password(password,hashed):
    return pwd_context.verify(password,hashed)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
def create_access_token(data):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=60)

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
print("SECRET_KEY =", SECRET_KEY)
print("ALGORITHM =", ALGORITHM)