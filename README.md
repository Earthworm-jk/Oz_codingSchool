# AI Health Web Assignment

FastAPI 기반 AI 헬스케어 웹 서비스 팀 프로젝트입니다.  
직원 회원가입/승인, 환자 관리, 진료 기록 등록, 흉부 X-ray 기반 폐렴 예측, Grad-CAM 결과 확인, Docker/Redis 기반 AI worker 분리까지 단계별 미션을 수행했습니다.

## 프로젝트 개요

이 프로젝트는 병원 내부 직원이 환자와 진료 기록을 관리하고, 업로드된 흉부 X-ray 이미지를 AI 모델로 분석하여 폐렴 여부와 Grad-CAM heatmap을 확인하는 웹 서비스입니다.

주요 기능은 다음과 같습니다.

- 직원 회원가입, 로그인, 내 정보 조회/수정/삭제
- 첫 가입자 자동 관리자 지정 및 이후 가입자 승인 대기 처리
- 관리자 회원 목록 조회 및 권한 변경
- 환자 등록, 조회, 수정, 삭제
- 진료 기록 등록 및 X-ray 이미지 업로드
- 폐렴 예측 요청, 예측 결과 저장, 결과 조회
- 여러 예측 결과 비교 UI
- Redis queue와 별도 AI worker를 이용한 예측 작업 분리
- Docker Compose 기반 FastAPI, MySQL, Redis, AI worker 실행

## 기술 스택

- Backend: FastAPI, SQLAlchemy ORM, Alembic
- Database: MySQL
- Auth: JWT, passlib bcrypt
- AI Worker: Python, PyTorch, Redis queue
- Frontend: 프로젝트 템플릿의 정적 HTML/CSS/JavaScript
- Infra: Docker, Docker Compose, Nginx, AWS EC2 선택 배포 검증
- Collaboration: GitHub Flow 변형 전략, `dev` 중심 PR 병합

## 실행 방법

로컬 개발 환경에서는 `.env`를 작성한 뒤 아래 명령으로 실행합니다.

```bash
uv run alembic upgrade head
uv run fastapi run app/main.py
```

Docker 환경에서는 `.env` 작성 후 아래 명령으로 실행합니다.

```bash
docker compose up -d --build
```

실행 후 접속 경로:

- Frontend: `http://localhost:8000/`
- Swagger UI: `http://localhost:8000/docs`
- Healthcheck: `http://localhost:8000/healthcheck`

## 환경 변수 예시

실제 비밀번호와 SECRET_KEY는 `.env`에만 작성하고 GitHub에는 올리지 않습니다.

```env
DB_HOST=mysql
DB_PORT=3306
DB_USER=ai_health
DB_PASSWORD=password1234
DB_ROOT_PASSWORD=password1234
DB_NAME=ai_health

SECRET_KEY=change-me-to-random-secret-key

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_URL=redis://redis:6379/0
```

## 심사용 테스트 계정

새 DB에서 실행하는 경우 첫 번째 회원가입 사용자는 자동으로 `admin` 권한을 받습니다.  
따라서 아래 관리자 계정을 먼저 회원가입한 뒤 로그인하면 회원 관리 화면에 접근할 수 있습니다.

| 구분 | 이메일 | 비밀번호 | 비고 |
| --- | --- | --- | --- |
| 관리자 | `testadmin@example.com` | 별도 제출 채널로 전달 | fresh DB에서 첫 가입 시 자동 admin |
| 일반 사용자 | `teststaff@example.com` | 별도 제출 채널로 전달 | 가입 후 관리자 승인 필요 |

공개 저장소에는 테스트 계정의 실제 비밀번호를 작성하지 않습니다.  
심사용 비밀번호는 LMS 제출 코멘트, 비공개 노션 문서 등 별도 채널로 전달합니다.

회원가입 입력 예시:

```json
{
  "email": "testadmin@example.com",
  "password": "<별도 전달 비밀번호>",
  "nationality": "korean",
  "last_name": "테스트",
  "first_name": "관리자",
  "middle_name": null,
  "employee_number": "90000001",
  "phone_number": "01090000001",
  "gender": "male",
  "department": "developer"
}
```

```json
{
  "email": "teststaff@example.com",
  "password": "<별도 전달 비밀번호>",
  "nationality": "korean",
  "last_name": "테스트",
  "first_name": "직원",
  "middle_name": null,
  "employee_number": "90000002",
  "phone_number": "01090000002",
  "gender": "female",
  "department": "medical team"
}
```

## 프로젝트 과정 총정리

### 1. Team Rule 정의

프로젝트 초반에 팀 협업 규칙을 먼저 정리했습니다.  
브랜치 네이밍, 커밋 메시지, PR 작성 방식, 리뷰어 지정 방식, 충돌 발생 시 공유 방식 등을 정하고 `docs/1일차/1일차_team_rules.md`에 기록했습니다.

초보자가 많은 팀이었기 때문에 복잡한 규칙보다는 “작업 전 브랜치 확인, 작업 후 push, PR에서 변경 내용 공유, 리뷰 후 merge” 흐름을 반복하는 방식으로 진행했습니다.

### 2. 사용자 요구사항 정의

초기에는 제공된 미션 요구사항을 읽고 API 요구사항을 해석하는 것부터 시작했습니다.  
이후 실제 템플릿의 방향이 “환자가 직접 가입하는 서비스”가 아니라 “직원이 환자 정보를 관리하는 서비스”에 가깝다는 점을 확인하고, 직원 계정과 환자/진료 기록을 분리해서 이해했습니다.

작성한 주요 요구사항 문서:

- `docs/4일차/4일차_USER_API_설계.md`
- `docs/5일차/5일차_PATIENT_RECORD_API_요구사항정의서.md`
- `docs/6일차/6일차_폐렴예측_API_설계.md`

### 3. API 명세서 작성

Swagger UI와 요구사항 문서를 함께 보면서 API 명세를 정리했습니다.

주요 API 범위:

- Practice API: 회원 목록 조회, 상세 조회, 등록, 수정, 삭제
- User API: 회원가입, 로그인, 로그아웃, 내 정보 조회/수정/삭제, 관리자 권한 변경
- Patient API: 환자 등록, 목록 조회, 상세 조회, 수정, 삭제
- Medical Record API: 진료 기록 등록, 조회, 수정, 삭제
- Pneumonia API: 폐렴 예측 요청, 예측 결과 조회, 결과 비교

API 응답에서는 비밀번호 원문이 노출되지 않도록 하고, 인증이 필요한 API는 JWT Bearer token을 사용했습니다.

### 4. Git & GitHub Branch 전략 구성

팀은 GitHub Flow를 변형해 사용했습니다.

기본 흐름:

```text
main
  ↓
dev
  ↓
feature/*
```

작업자는 `dev`에서 feature 브랜치를 만들고, 기능 구현 후 PR을 생성했습니다.  
리뷰어가 Swagger, 프론트 화면, 코드 변경 범위를 확인한 뒤 `dev`에 merge했습니다.  
주요 단계가 안정화되면 `dev`를 `main`에 병합하는 방식으로 진행했습니다.

### 5. 프로젝트 세팅

프로젝트 템플릿 구조를 먼저 분석했습니다.

주요 구조:

- `app/main.py`: FastAPI 앱 생성, 라우터 등록, 정적 파일 서빙
- `app/apis/`: API router
- `app/models/`: SQLAlchemy ORM 모델
- `app/schemas/`: Pydantic 요청/응답 스키마
- `app/core/`: DB, 설정, 인증, Redis 연결
- `static/`: 프론트엔드 템플릿
- `worker/`: AI worker 코드
- `alembic/`: DB 마이그레이션 관리

초기에는 템플릿 이해를 돕기 위해 프로젝트 가이드 문서와 미션별 설명 문서를 작성했습니다.

### 6. API 및 AI 워커 코드 작성 후 Branch 전략을 통한 코드 병합

각 기능은 feature 브랜치에서 구현하고 PR 리뷰 후 `dev`에 병합했습니다.

진행한 주요 구현:

- Practice API 5종 구현
- User API 및 관리자 승인 기능 구현
- Patient/Medical Record API 구현
- X-ray 이미지 업로드 및 media 저장
- Pneumonia prediction API 구현
- Redis queue 기반 예측 요청 분리
- AI worker에서 예측 수행 후 결과 publish/저장

처음에는 FastAPI 앱 내부에서 예측을 직접 수행하는 구조였지만, 동시 요청과 AI 모델 처리 시간을 고려해 Redis와 worker를 이용한 구조로 개선했습니다.

### 7. 아키텍처 설계 및 적용

동시성 문제를 줄이기 위해 Event-Driven Architecture를 학습하고 적용했습니다.

최종 흐름:

```text
Client
  → FastAPI
  → Redis task queue
  → AI Worker
  → Redis result channel
  → FastAPI
  → MySQL 저장
  → Client 응답
```

FastAPI는 요청 접수와 DB 저장을 담당하고, AI worker는 모델 로딩과 폐렴 예측 작업을 담당하도록 역할을 분리했습니다.  
이 구조를 통해 FastAPI 서버가 무거운 AI 추론 작업에 직접 묶이지 않도록 했습니다.

관련 문서:

- `docs/9일차/9일차_동시성문제_해결을위한_아키텍처설계.md`
- `docs/9일차/9일차_동시성문제_해결을위한_아키텍처설계.png`

### 8. 도커 인프라 관련 파일 작성

Dockerfile과 Docker Compose를 작성하여 서비스 실행 환경을 컨테이너로 분리했습니다.

구성 서비스:

- `fastapi`: FastAPI 앱 실행
- `mysql`: 데이터베이스
- `redis`: 예측 작업 queue/result 전달
- `ai-worker`: AI 모델 추론 전담 worker

Docker 관련 산출물:

- `app/Dockerfile`
- `worker/Dockerfile`
- `docker-compose.yml`
- `.dockerignore`
- `app/.dockerignore`
- `docs/8일차/8일차_docker_실행화면.md`

### 9. AWS 배포

선택 미션으로 AWS EC2 배포를 별도 브랜치에서 검증했습니다.

진행 내용:

- EC2 인스턴스 생성
- pem key로 SSH 접속
- Docker Engine, Docker Compose 설치
- EBS 용량 확장
- Docker Hub 이미지 build/push
- `docker-compose.prod.yml`, `.prod.env`, `nginx/default.conf`를 EC2로 SCP 전송
- Nginx 80번 포트 접속 확인

AWS 배포 산출물은 선택 과제 성격이므로 최종 `dev/main`에는 병합하지 않고, 별도 브랜치 `feature/aws-docker-compose-images`에 보관했습니다.

### 10. QA 진행

QA는 Swagger UI, 프론트 화면, Docker 실행 화면을 기준으로 진행했습니다.

확인한 항목:

- Swagger에서 API endpoint 노출 여부
- 회원가입/로그인/JWT 인증 동작
- 관리자 승인 전후 화면 접근 제어
- 환자 등록/조회/상세보기
- 진료 기록 등록 및 X-ray 업로드
- 폐렴 예측 결과 저장 및 조회
- Grad-CAM heatmap 표시
- 예측 결과 비교 모달
- Docker Compose 실행 및 healthcheck
- Redis worker 분리 후 예측 요청 처리

관련 문서:

- `docs/7일차/7일차_앱_실행화면.md`
- `docs/8일차/8일차_docker_실행화면.md`

## 남은 개선 가능 사항

과제 범위 내에서는 주요 기능을 완성했지만, 실제 서비스로 확장하려면 아래 항목을 더 개선할 수 있습니다.

- 관리자 계정 생성/초기화 방식을 운영 환경에 맞게 별도 seed 또는 관리 명령으로 분리
- Refresh token 저장/폐기 방식 개선
- 모델 파일과 media 파일의 저장소를 S3 같은 외부 스토리지로 분리
- 테스트 코드 보강
- 운영용 Nginx/HTTPS/도메인 설정 추가
- DB 백업 및 마이그레이션 롤백 전략 정리
