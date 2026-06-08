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

# 6. Test PATCH /users/1 (Valid update: age and email)
update_data = {
    "age": 30,
    "email": "updated1@example.com"
}
code, data = make_request("/users/1", "PATCH", update_data)
print("6. PATCH /users/1 Status:", code, "Updated Age:", data.get("age"), "Updated Email:", data.get("email"))

# 7. Test PATCH /users/1 (Invalid update: all fields None)
code, data = make_request("/users/1", "PATCH", {})
print("7. PATCH /users/1 Empty Status:", code, "Detail:", data.get("detail"))

# 8. Test PATCH /users/1 (Invalid update: password doesn't meet conditions - no special char)
code, data = make_request("/users/1", "PATCH", {"password": "Password123"})
print("8. PATCH /users/1 Invalid PW Status:", code, "Detail:", data.get("detail"))

# 9. Test PATCH /users/1 (Invalid update: password doesn't meet conditions - no digit)
code, data = make_request("/users/1", "PATCH", {"password": "Password!"})
print("9. PATCH /users/1 Invalid PW (no digit) Status:", code, "Detail:", data.get("detail"))

# 9-1. Test PATCH /users/1 (Valid update: password meets all conditions including digit)
code, data = make_request("/users/1", "PATCH", {"password": "Password123!"})
print("9-1. PATCH /users/1 Valid PW Status:", code)

# 10. Test DELETE /users/3 (Success)
code, data = make_request("/users/3", "DELETE")
print("10. DELETE /users/3 Status:", code, "Msg:", data.get("message"))

# 11. Test GET /users (Check user 3 is deleted)
code, data = make_request("/users")
print("11. GET /users Count after delete:", len(data))

# 12. Test DELETE /users/99 (404 Not Found)
code, data = make_request("/users/99", "DELETE")
print("12. DELETE /users/99 Status:", code, "Detail:", data.get("detail"))

# 13. Test PATCH /users/1 (Valid update: change nationality to foreigner, and set middle_name and first_name)
foreigner_update = {
    "nationality": "foreigner",
    "first_name": "John",
    "middle_name": "Fitzgerald",
    "last_name": None
}
code, data = make_request("/users/1", "PATCH", foreigner_update)
print("13. PATCH /users/1 Foreigner Update Status:", code, "Nationality:", data.get("nationality"), "Middle Name:", data.get("middle_name"))

# 14. Test PATCH /users/1 (Invalid update: change nationality to korean but has middle name)
invalid_korean_update = {
    "nationality": "korean",
    "middle_name": "SomeMiddle"
}
code, data = make_request("/users/1", "PATCH", invalid_korean_update)
print("14. PATCH /users/1 Invalid Korean (has middle_name) Status:", code, "Detail:", data.get("detail"))

# 15. Test PATCH /users/1 (Attempt to modify employee_number - should NOT change)
emp_update = {
    "employee_number": "99999999",
    "age": 35
}
code, data = make_request("/users/1", "PATCH", emp_update)
print("15. PATCH /users/1 Try Update Employee Number Status:", code, "Returned Employee Number:", data.get("employee_number"))
