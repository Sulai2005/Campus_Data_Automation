"""Test login endpoint"""
import requests

# Test login
url = "http://127.0.0.1:8000/auth/login"
data = {
    "username": "admin@campus.edu",
    "password": "admin123"
}

print("Testing login endpoint...")
print(f"URL: {url}")
print(f"Data: {data}")

response = requests.post(url, data=data)

print(f"\nStatus Code: {response.status_code}")
print(f"Response: {response.json()}")

if response.status_code == 200:
    print("\n✅ LOGIN SUCCESSFUL!")
    print(f"Token: {response.json()['access_token'][:50]}...")
    print(f"Role: {response.json()['role']}")
else:
    print("\n❌ LOGIN FAILED!")
    print(f"Error: {response.json()['detail']}")
