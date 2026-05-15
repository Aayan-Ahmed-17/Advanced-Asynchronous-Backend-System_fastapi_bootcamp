import asyncio
from app.dependencies.security import get_password_hash, verify_password, create_access_token

async def test():
    password = "secret_password"
    hashed = get_password_hash(password)
    print(f"Hashed: {hashed}")
    print(f"Verify Correct: {verify_password(password, hashed)}")
    
    token = create_access_token(data={"sub": "user@example.com"})
    print(f"Access Token: {token}")

if __name__ == "__main__":
    asyncio.run(test())
