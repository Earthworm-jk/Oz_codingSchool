import urllib.request
import json
import urllib.error

BASE_URL = "http://127.0.0.1:8000/practice_api"

def make_request(path, method="GET", body=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    data = json.dumps(body).encode("utf-8") if body is not None else None
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))

# 1. Test GET /users
code, data = make_request("/users")
print("1. GET /users Status:", code)
print("1. GET /users Count:", len(data))

# 2. Test GET /users/1
code, data = make_request("/users/1")
print("2. GET /users/1 Status:", code)
print("2. GET /users/1 Name:", data.get("last_name") + data.get("first_name"), "Nationality:", data.get("nationality"))

# 3. Test POST with invalid Korean Name (has middle name)
invalid_korean = {
    "nationality": "korean",
    "last_name": "김",
    "first_name": "철수",
    "middle_name": "John",
    "age": 20,
    "email": "chulsoo@example.com",
    "password": "Password123!",
    "employee_number": "20240004"
}
code, data = make_request("/users", "POST", invalid_korean)
print("3. POST invalid Korean Status:", code, "Detail:", data.get("detail"))

# 4. Test POST with valid foreigner (optional last name, has middle name)
valid_foreigner = {
    "nationality": "foreigner",
    "last_name": None,
    "first_name": "Alex",
    "middle_name": "David",
    "age": 22,
    "email": "alex@example.com",
    "password": "Password123!",
    "employee_number": "20240005"
}
code, data = make_request("/users", "POST", valid_foreigner)
print("4. POST valid foreigner Status:", code, "First Name:", data.get("first_name"), "Middle Name:", data.get("middle_name"), "Last Name:", data.get("last_name"))

# 5. Test POST with valid Korean
valid_korean = {
    "nationality": "korean",
    "last_name": "이",
    "first_name": "영희",
    "middle_name": None,
    "age": 25,
    "email": "younghee@example.com",
    "password": "Password123!",
    "employee_number": "20240006"
}
code, data = make_request("/users", "POST", valid_korean)
print("5. POST valid Korean Status:", code, "Full Name:", data.get("last_name") + data.get("first_name"), "New ID:", data.get("id"))
