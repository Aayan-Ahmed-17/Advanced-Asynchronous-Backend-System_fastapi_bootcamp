import httpx
import asyncio
import time

BASE_URL = "http://127.0.0.1:8000"

async def test_auth_flow():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # 1. Register
        email = f"test_{int(time.time())}@example.com"
        password = "strongpassword123"
        print(f"--- Testing Registration for {email} ---")
        reg_response = await client.post("/auth/register", json={"email": email, "password": password})
        print(f"Status: {reg_response.status_code}")
        print(f"Response: {reg_response.json()}")

        # 2. Login
        print("\n--- Testing Login ---")
        login_response = await client.post("/auth/login", json={"email": email, "password": password})
        print(f"Status: {login_response.status_code}")
        tokens = login_response.json()
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        print(f"Tokens received: {'Yes' if access_token and refresh_token else 'No'}")

        # 3. Refresh Token
        print("\n--- Testing Token Refresh ---")
        refresh_response = await client.post(f"/auth/refresh?refresh_token={refresh_token}")
        print(f"Status: {refresh_response.status_code}")
        print(f"New Access Token received: {'Yes' if refresh_response.json().get('access_token') else 'No'}")

        # 4. Logout (Blacklist)
        print("\n--- Testing Logout ---")
        logout_response = await client.post("/auth/logout", headers={"Authorization": f"Bearer {access_token}"})
        print(f"Status: {logout_response.status_code}")
        print(f"Response: {logout_response.json()}")

if __name__ == "__main__":
    asyncio.run(test_auth_flow())
