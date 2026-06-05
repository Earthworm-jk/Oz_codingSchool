# 📑 4일차 USER API 설계 (Real User & Auth API Design)
## 프로젝트명: 흉부 X-Ray AI 진단 서비스 (Chest X-Ray AI Diagnosis Service)

본 문서는 **흉부 X-Ray AI 진단 서비스**의 실전 프로덕션 레벨 User 및 인증/인가(Auth) API 설계안입니다. 
기존의 2일차 연습용 API(임시 리스트 및 `/practice_api` 기반)와 달리, 데이터베이스(DB) 모델 및 JWT 인증 기법(HttpOnly Cookie 포함)을 고려하여 설계하였으며, 사용자 요구사항 정의서(URD)에 부합하는 명세입니다.

---

## 🔗 API 목록 (Table of Contents)

| 연관 요구사항 | API 이름 | 메서드 | 엔드포인트 | 인증 필요 | 설명 |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **[REQ-USER-001]** | [1. 회원가입 API](#1-회원가입-api) | `POST` | `/api/v1/users/signup` | N | 내/외국인 맞춤형 회원 가입 |
| **[REQ-USER-010]** | [2. 이메일 중복 확인 API](#2-이메일-중복-확인-api) | `GET` | `/api/v1/users/check-email` | N | 이메일 규격 및 중복 여부 확인 |
| **[REQ-USER-002]** | [3. 로그인 API](#3-로그인-api) | `POST` | `/api/v1/users/login` | N | Access/Refresh Token 발급 |
| **[REQ-USER-003]** | [4. 로그아웃 API](#4-로그아웃-api) | `POST` | `/api/v1/users/logout` | Y | 리프레시 토큰 및 세션 폐기 |
| **[NFR-USER-001]** | [5. 토큰 재발급 (Refresh) API](#5-토큰-재발급-refresh-api) | `POST` | `/api/v1/users/refresh` | N (Cookie) | 만료된 Access Token 재발급 |
| **[REQ-USER-006]** | [6. 내 정보 조회 API](#6-내-정보-조회-api) | `GET` | `/api/v1/users/me` | Y | 로그인 회원의 마이페이지 데이터 |
| **[REQ-USER-007]** | [7. 내 정보 수정 API](#7-내-정보-수정-api) | `PATCH` | `/api/v1/users/me` | Y | 부서, 전화번호 Partial 수정 |
| **[REQ-USER-008]** | [8. 비밀번호 변경 API](#8-비밀번호-변경-api) | `PATCH` | `/api/v1/users/me/password` | Y | 마이페이지 비밀번호 검증 및 변경 |
| **[REQ-USER-009]** | [9. 회원 탈퇴 API](#9-회원-탈퇴-api) | `DELETE` | `/api/v1/users/me` | Y | 연관 데이터베이스 Hard Delete 처리 |

### 🛠️ 관리자(Admin) 전용 API 후보
| 연관 요구사항 | API 이름 | 메서드 | 엔드포인트 | 인증 필요 | 설명 |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **[REQ-USER-004]** | [10. 전체 회원 목록 조회 API](#10-전체-회원-목록-조회-api) | `GET` | `/api/v1/admin/users` | Y (Admin) | 검색 및 필터링 적용 목록 조회 |
| **[REQ-USER-005]** | [11. 회원 권한 변경 API](#11-회원-권한-변경-api) | `PATCH` | `/api/v1/admin/users/role` | Y (Admin) | 가입 승인대기자 및 권한 변경 |

---

## 1. 회원가입 API

### 1.1 API 개요
* **설명**: 사내 구성원(개발진, 의료진, 연구진)을 신규 가입시킵니다. 국적별(내국인/외국인) 성명 규칙 제약, 사번 검증, 비밀번호 유효성 검증을 거칩니다. (기존 practice API의 `validate_nationality_names`, `validate_password`, `validate_employee_number` 검증 로직을 재사용 및 확장)
* **엔드포인트**: `/api/v1/users/signup`
* **메서드**: `POST`
* **인증 필요**: N

### 1.2 요청(Request)
* **Headers**: `Content-Type: application/json`
* **본문 예시 (내국인)**:
```json
{
  "email": "doctor.kim@example.com",
  "nationality": "korean",
  "last_name": "김",
  "first_name": "민수",
  "middle_name": null,
  "department": "med",
  "gender": "male",
  "phone_number": "01012345678",
  "password": "Password123!",
  "employee_number": "20260001"
}
```
* **본문 예시 (외국인)**:
```json
{
  "email": "smith.john@example.com",
  "nationality": "foreigner",
  "last_name": "Smith",
  "first_name": "John",
  "middle_name": "Fitzgerald",
  "department": "res",
  "gender": "male",
  "phone_number": "01098765432",
  "password": "SecurePassword123!",
  "employee_number": "20260002"
}
```
* **요청 바디 필드 스키마**:

| 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| email | string | Y | 이메일 주소 (중복 불가, 최대 30자) |
| nationality | string | Y | 회원 국적 구분 (`korean` 또는 `foreigner`) |
| last_name | string | N | 성 (내국인 필수 / 외국인 선택 사항, 최대 20자) |
| first_name | string | Y | 이름 (내국인 성명 결합 2~10자 / 외국인 필수 1~20자) |
| middle_name | string | N | 미들네임 (내국인 입력 불가 / 외국인 선택 사항, 최대 20자) |
| department | string | Y | 소속 부서 (`dev`: 개발팀, `med`: 의료진, `res`: 연구진) |
| gender | string | Y | 성별 (`male`: 남성, `female`: 여성) |
| phone_number | string | Y | 휴대폰 번호 (숫자만 저장) |
| password | string | Y | 비밀번호 (8~20자, 대소문자/숫자/특수문자 1개 이상씩 포함) |
| employee_number | string | Y | 사번 (8자리 숫자 포맷, 중복 불가) |

### 1.3 응답(Response)
* **성공 (201 Created)**:
```json
{
  "id": 1,
  "email": "doctor.kim@example.com",
  "nationality": "korean",
  "last_name": "김",
  "first_name": "민수",
  "middle_name": null,
  "department": "med",
  "gender": "male",
  "phone_number": "01012345678",
  "employee_number": "20260001",
  "role": "pending",
  "is_active": true
}
```
* **실패 (400 Bad Request)**:
  * `내국인은 성(last_name)이 필수입니다.`
  * `내국인은 미들네임(middle_name)을 입력할 수 없습니다.`
  * `내국인 성명의 총 길이는 최소 2글자 이상, 최대 10글자 이하여야 합니다.`
  * `사번은 8자리 숫자여야 합니다.`
  * `이미 가입된 사번입니다.`

---

## 2. 이메일 중복 확인 API

### 2.1 API 개요
* **설명**: 회원가입 전 이메일 입력값의 정규 포맷 준수 여부 및 DB 내 기존 가입 이메일과의 중복을 검사합니다. (기존 practice API의 `validate_email` 로직 재사용)
* **엔드포인트**: `/api/v1/users/check-email`
* **메서드**: `GET`
* **인증 필요**: N

### 2.2 요청(Request)
* **쿼리 파라미터**:

| 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| email | string | Y | 검사 대상 이메일 주소 |

### 2.3 응답(Response)
* **성공 (200 OK)**:
```json
{
  "message": "사용 가능한 이메일입니다."
}
```
* **실패 (400 Bad Request)**:
```json
{
  "detail": "이미 등록된 이메일입니다."
}
```

---

## 3. 로그인 API

### 3.1 API 개요
* **설명**: 이메일과 비밀번호로 로그인하며, JWT Access Token(JSON Response)과 Refresh Token(HttpOnly Secure Cookie)을 발급받습니다.
* **엔드포인트**: `/api/v1/users/login`
* **메서드**: `POST`
* **인증 필요**: N

### 3.2 요청(Request)
* **Headers**: `Content-Type: application/x-www-form-urlencoded`
* **본문 필드(Form Data)**:

| 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| username | string | Y | 로그인 대상 이메일 주소 |
| password | string | Y | 비밀번호 |

### 3.3 응답(Response)
* **성공 (200 OK)**:
  * Response Header에 `Set-Cookie`를 통해 JWT Refresh Token이 브라우저 쿠키 저장소로 바로 세팅됩니다.
* **Response Headers**:
```http
Set-Cookie: refresh_token=eyJhbGciOiJIUz...; Path=/api/v1/users/refresh; HttpOnly; Secure; SameSite=Strict
```
* **Response Body**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```
* **실패 (401 Unauthorized)**:
```json
{
  "detail": "이메일 또는 비밀번호가 일치하지 않습니다."
}
```

---

## 4. 로그아웃 API

### 4.1 API 개요
* **설명**: 현재 사용자의 토큰 세션을 무효화 처리하고 쿠키를 파기합니다.
* **엔드포인트**: `/api/v1/users/logout`
* **메서드**: `POST`
* **인증 필요**: Y (Access Token 헤더 탑재 필요)

### 4.2 요청(Request)
* **Headers**: `Authorization: Bearer <Access Token>`

### 4.3 응답(Response)
* **성공 (200 OK)**:
  * Refresh Token 쿠키를 만료(Max-Age=0) 시키는 헤더를 반환합니다.
```json
{
  "message": "로그아웃 되었습니다."
}
```

---

## 5. 토큰 재발급 (Refresh) API

### 5.1 API 개요
* **설명**: Access Token 만료 시, HttpOnly Refresh Token 쿠키를 사용하여 새로운 Access Token을 갱신 발급받습니다.
* **엔드포인트**: `/api/v1/users/refresh`
* **메서드**: `POST`
* **인증 필요**: N (HttpOnly 쿠키 자체 인증)

### 5.2 요청(Request)
* **Request Headers**: `Cookie: refresh_token=<Token 값>`

### 5.3 응답(Response)
* **성공 (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```
* **실패 (401 Unauthorized)**:
```json
{
  "detail": "리프레시 토큰이 만료되었습니다. 다시 로그인 하십시오."
}
```

---

## 6. 내 정보 조회 API

### 6.1 API 개요
* **설명**: 현재 로그인한 사용자의 정보를 조회합니다. (마이페이지용)
* **엔드포인트**: `/api/v1/users/me`
* **메서드**: `GET`
* **인증 필요**: Y

### 6.2 요청(Request)
* **Headers**: `Authorization: Bearer <Access Token>`

### 6.3 응답(Response)
* **성공 (200 OK)**:
```json
{
  "id": 1,
  "email": "doctor.kim@example.com",
  "nationality": "korean",
  "last_name": "김",
  "first_name": "민수",
  "middle_name": null,
  "department": "med",
  "gender": "male",
  "phone_number": "01012345678",
  "employee_number": "20260001",
  "role": "staff",
  "is_active": true
}
```

---

## 7. 내 정보 수정 API

### 7.1 API 개요
* **설명**: 마이페이지 내부에서 회원의 부서 및 전화번호 정보를 부분 수정합니다.
* **엔드포인트**: `/api/v1/users/me`
* **메서드**: `PATCH`
* **인증 필요**: Y

### 7.2 요청(Request)
* **Headers**: `Authorization: Bearer <Access Token>`, `Content-Type: application/json`
* **본문 예시**:
```json
{
  "department": "dev",
  "phone_number": "01087654321"
}
```
* **본문 필드 설명**:

| 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| department | string | N | 변경 소속 부서 (`dev`, `med`, `res`) |
| phone_number | string | N | 변경 휴대폰 번호 (숫자 포맷 검증 규칙 재적용) |

### 7.3 응답(Response)
* **성공 (200 OK)**:
```json
{
  "id": 1,
  "email": "doctor.kim@example.com",
  "nationality": "korean",
  "last_name": "김",
  "first_name": "민수",
  "middle_name": null,
  "department": "dev",
  "gender": "male",
  "phone_number": "01087654321",
  "employee_number": "20260001",
  "role": "staff",
  "is_active": true
}
```

---

## 8. 비밀번호 변경 API

### 8.1 API 개요
* **설명**: 마이페이지 내에서 기존 비밀번호를 검증하고 새로운 비밀번호를 설정합니다. (기존 practice API의 `validate_password` 로직을 사용하여 새 비밀번호 복잡성 검증)
* **엔드포인트**: `/api/v1/users/me/password`
* **메서드**: `PATCH`
* **인증 필요**: Y

### 8.2 요청(Request)
* **Headers**: `Authorization: Bearer <Access Token>`, `Content-Type: application/json`
* **본문 예시**:
```json
{
  "current_password": "Password123!",
  "new_password": "NewSecurePassword777!"
}
```

### 8.3 응답(Response)
* **성공 (200 OK)**:
```json
{
  "message": "비밀번호가 변경되었습니다."
}
```
* **실패 (400 Bad Request)**:
```json
{
  "detail": "기존 비밀번호가 올바르지 않습니다."
}
```

---

## 9. 회원 탈퇴 API

### 9.1 API 개요
* **설명**: 로그인한 사용자가 회원 탈퇴를 수행합니다. DB 연관 정보(진료 기록, 진단 이력 등)가 Hard Delete 처리됩니다.
* **엔드포인트**: `/api/v1/users/me`
* **메서드**: `DELETE`
* **인증 필요**: Y

### 9.2 요청(Request)
* **Headers**: `Authorization: Bearer <Access Token>`

### 9.3 응답(Response)
* **성공 (200 OK)**:
```json
{
  "message": "회원 탈퇴 처리가 완료되었습니다."
}
```

---

## 🛠️ 관리자 전용 API 후보 (Admin Candidate APIs)

### 10. 전체 회원 목록 조회 API

#### 10.1 API 개요
* **설명**: Admin 역할을 보유한 최고 관리자가 전체 사내 구성원 리스트를 조회합니다. 이메일/이름 매칭 검색 기능과 부서별 필터링 기능이 제공됩니다.
* **엔드포인트**: `/api/v1/admin/users`
* **메서드**: `GET`
* **인증 필요**: Y (Admin 권한 필수)

#### 10.2 요청(Request)
* **Headers**: `Authorization: Bearer <Access Token>`
* **쿼리 파라미터**:

| 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| query | string | N | 검색어 (이메일 혹은 성명 검색) |
| department | string | N | 부서 필터 (`dev`, `med`, `res`) |

#### 10.3 응답(Response)
* **성공 (200 OK)**:
```json
[
  {
    "id": 1,
    "email": "doctor.kim@example.com",
    "nationality": "korean",
    "last_name": "김",
    "first_name": "민수",
    "middle_name": null,
    "department": "med",
    "gender": "male",
    "phone_number": "01012345678",
    "employee_number": "20260001",
    "role": "staff",
    "is_active": true
  }
]
```

---

### 11. 회원 권한 변경 API

#### 11.1 API 개요
* **설명**: Admin 관리자가 특정 회원의 역할(대기자, 일반스태프, 어드민)을 강제로 변경하여 승인 또는 권한 수정을 수행합니다.
* **엔드포인트**: `/api/v1/admin/users/role`
* **메서드**: `PATCH`
* **인증 필요**: Y (Admin 권한 필수)

#### 11.2 요청(Request)
* **Headers**: `Authorization: Bearer <Access Token>`, `Content-Type: application/json`
* **본문 예시**:
```json
{
  "user_id": 2,
  "new_role": "staff"
}
```
* **본문 필드 설명**:

| 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| user_id | integer | Y | 대상 회원의 고유 식별 번호 (ID) |
| new_role | string | Y | 변경할 권한명 (`pending`: 승인대기, `staff`: 일반회원, `admin`: 관리자) |

#### 11.3 응답(Response)
* **성공 (200 OK)**:
```json
{
  "message": "권한이 변경되었습니다."
}
```

---

## 💡 기존 Practice API 검증 및 구현 로직 차용 계획

본 실전 API 구현 시, 기존 2일차 practice API에서 개발 및 검증된 핵심 유효성 검사 로직을 그대로 재사용(차용)하여 개발 효율성과 정밀도를 극대화합니다.

### 1. 성명 및 국적별 제약조건 검증 (`validate_nationality_names`)
* **내국인 (`korean`)**:
  * 성(`last_name`)과 이름(`first_name`) 필수 체크.
  * 미들네임(`middle_name`) 입력 차단 (입력 시 `400 Bad Request` 에러).
  * 성+이름의 공백 제외 결합 길이가 **2자 이상 10자 이하**인지 검증.
* **외국인 (`foreigner`)**:
  * 이름(`first_name`) 필수 체크 (길이 1~20자).
  * 성(`last_name`) 및 미들네임(`middle_name`)은 선택적 허용 (입력 시 각 최대 20자).

### 2. 이메일 형식 및 고유성 검증 (`validate_email`)
* **이메일 형식 정규표현식**: `^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$` 패턴 매칭 수행.
* **이메일 최대 길이**: 30자 초과 방지.
* **이메일 중복 체크**: DB 저장 정보 조회 시 중복된 이메일 등록을 원천 차단 (`400 Bad Request`).

### 3. 비밀번호 복잡성 검증 (`validate_password`)
* **길이 제한**: 최소 8자 이상, 최대 20자 이하.
* **복잡성 조건 (각 1개 이상 필수 포함)**:
  * 대문자 1개 이상 (`any(c.isupper() for c in password)`)
  * 소문자 1개 이상 (`any(c.islower() for c in password)`)
  * 숫자 1개 이상 (`any(c.isdigit() for c in password)`)
  * 특수문자 1개 이상 (`[!@#$%^&*(),.?":{}|<>\-_+=\[\]\\/;`~']` 패턴)

### 4. 사번 유효성 및 중복 검증 (`validate_employee_number`)
* **사번 패턴**: **8자리 숫자** 포맷 (`^\d{8}$`) 강제화.
* **중복 체크**: 동일 사번 가입 차단.

### 5. Swagger 테스트 및 PR 리뷰 연계
* **Swagger 테스트**: FastAPI의 자동 생성 인터랙티브 문서 환경을 구성하여 API 기능별 작동과 오류 응답을 검증합니다.
* **PR 리뷰**: 구현 완료 후 브랜치 병합 전 실전 코드를 바탕으로 한 상호 코드 리뷰 및 피드백을 진행합니다.

