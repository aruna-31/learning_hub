from app.security import hash_password, verify_password, create_access_token

password = "aruna123"

hashed = hash_password(password)

print(hashed)

print(verify_password(password, hashed))

token = create_access_token({"sub": "aruna@gmail.com"})

print(token)