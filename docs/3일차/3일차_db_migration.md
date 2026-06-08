# 3일차 DB 모델 및 Alembic 마이그레이션 정리

## 작업 목적

ERD를 기준으로 SQLAlchemy ORM 모델을 작성하고, Alembic migration 파일을 통해 실제 데이터베이스 스키마를 생성할 수 있도록 준비했습니다.

이번 프로젝트에서 `users`는 환자가 아니라 서비스에 로그인하는 의료진/직원 계정으로 해석합니다. `patients`는 의료진/직원이 관리하는 환자 정보입니다.

## 작성한 모델 파일

| 테이블 | 모델 파일 | 설명 |
| --- | --- | --- |
| `users` | `app/models/users.py` | 의료진/직원 사용자 계정 |
| `patients` | `app/models/patients.py` | 환자 기본 정보 |
| `medical_records` | `app/models/medical_records.py` | 환자의 진료 기록 |
| `xray_images` | `app/models/xray_images.py` | X-ray 이미지 정보 |
| `ai_analysis_results` | `app/models/ai_analysis_results.py` | AI 분석 결과 |

## 반영한 관계

| 관계 | 설명 |
| --- | --- |
| `patients.id` -> `medical_records.patient_id` | 환자 1명은 여러 진료 기록을 가질 수 있음 |
| `medical_records.id` -> `xray_images.record_id` | 진료 기록 1개는 여러 X-ray 이미지를 가질 수 있음 |
| `medical_records.id` -> `ai_analysis_results.record_id` | 진료 기록 1개는 여러 AI 분석 결과를 가질 수 있음 |
| `users.id` -> `xray_images.uploader_id` | 의료진/직원 사용자가 X-ray 이미지를 업로드함 |

## 팀 확장 필드 반영

ERD의 `users` 기본 구조에 더해, 팀에서 회원가입 UI/API 확장 방향으로 합의한 필드를 추가했습니다.

| 필드 | 이유 |
| --- | --- |
| `nationality` | 내국인/외국인 구분 |
| `first_name`, `last_name`, `middle_name` | 이름 구조 분리 |
| `employee_number` | 사번 기반 중복 가입 방지 |

`password_confirm`은 DB 저장 대상이 아니라 요청 검증용 값이므로 모델에 포함하지 않았습니다.

## Alembic 설정

`alembic/env.py`는 다음 흐름으로 모델 정보를 읽습니다.

```python
from app.core.db.databases import Base, DATABASE_URL
from app import models

target_metadata = Base.metadata
```

따라서 `app/models/__init__.py`에서 모든 모델을 import하도록 연결했습니다.

## 생성된 Migration 파일

```text
alembic/versions/539d910b57d8_create_medical_schema.py
```

이 migration 파일은 다음 테이블을 생성합니다.

```text
users
patients
medical_records
xray_images
ai_analysis_results
```

## 실행한 검증

모델 metadata 인식 확인:

```bash
uv run python -c "from app.core.db.databases import Base; import app.models; print(sorted(Base.metadata.tables.keys()))"
```

확인 결과:

```text
['ai_analysis_results', 'medical_records', 'patients', 'users', 'xray_images']
```

DB 접속 없이 Alembic SQL 생성 확인:

```bash
uv run alembic upgrade head --sql
```

확인 결과:

```text
CREATE TABLE users ...
CREATE TABLE patients ...
CREATE TABLE medical_records ...
CREATE TABLE ai_analysis_results ...
CREATE TABLE xray_images ...
```

## 실제 DB 적용 결과

Aiven MySQL의 `ai_health` 데이터베이스에 아래 명령어로 migration을 적용했습니다.

```bash
uv run alembic upgrade head
```

적용 후 Alembic 현재 revision을 확인했습니다.

```bash
uv run alembic current
```

확인 결과:

```text
539d910b57d8 (head)
```

DB에 생성된 테이블:

```text
users
patients
medical_records
xray_images
ai_analysis_results
alembic_version
```

확인된 외래키 관계:

```text
medical_records.patient_id -> patients.id
xray_images.record_id -> medical_records.id
xray_images.uploader_id -> users.id
ai_analysis_results.record_id -> medical_records.id
```

`.env`에는 Aiven 접속 정보를 입력하되, DB 비밀번호가 포함되므로 GitHub에 업로드하지 않습니다.

## DB Viewer 캡처

Aiven MySQL의 `ai_health` 데이터베이스에 접속하여 DB Viewer에서 다음 항목을 확인했습니다.

- `users`, `patients`, `medical_records`, `xray_images`, `ai_analysis_results` 테이블 생성
- `alembic_version` 테이블 생성
- `users` 테이블 컬럼 생성
- `medical_records`, `xray_images`, `ai_analysis_results`의 FK 컬럼 생성

![DB Viewer 테이블 확인](../media/3일차_db_viewer_tables.png)
