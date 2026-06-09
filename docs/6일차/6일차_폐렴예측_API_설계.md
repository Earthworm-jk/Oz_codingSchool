# 📑 6일차 AI 폐렴 예측 API 설계 (Pneumonia Prediction API Design)
## 프로젝트명: 흉부 X-Ray AI 진단 서비스 (Chest X-Ray AI Diagnosis Service)

본 문서는 **흉부 X-Ray AI 진단 서비스**의 6일차 AI 폐렴 예측 API 설계안입니다.
작성한 PyTorch CNN 모델(`worker/model.py`)을 활용하여, 저장된 진료 기록의 X-Ray 이미지를 기반으로 폐렴 여부를 예측하고 분석 결과를 관리하는 API 명세입니다.

---

## 🔗 API 목록 (Table of Contents)

| 연관 요구사항 | API 이름 | 메서드 | 엔드포인트 | 인증 필요 | 설명 |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **[REQ-PNEU-001]** | [1. AI 폐렴 예측 실행 API](#1-ai-폐렴-예측-실행-api) | `POST` | `/api/v1/pneumonia/predict/{record_id}` | Y | 특정 진료 기록의 X-Ray 분석 및 DB 저장 |
| **[REQ-PNEU-002]** | [2. AI 폐렴 예측 결과 조회 API](#2-ai-폐렴-예측-결과-조회-api) | `GET` | `/api/v1/pneumonia/results/{record_id}` | Y | 특정 진료 기록의 기존 분석 결과 단건 조회 |
| **[REQ-PNEU-003]** | [3. AI 폐렴 즉시 예측 API (업로드)](#3-ai-폐렴-즉시-예측-api-업로드) | `POST` | `/api/v1/pneumonia/predict/upload` | Y | 이미지 업로드 즉시 폐렴 분석 및 반환 (DB 저장 안 함) |

---

## 1. AI 폐렴 예측 실행 API

### 1.1 API 개요
* **설명**: 특정 진료 기록 ID(`record_id`)에 등록된 X-Ray 이미지 파일을 로드하여 `SimpleCNN` 모델로 분석을 수행합니다. 분석된 폐렴 여부와 확신도(Confidence) 등의 결과는 `ai_analysis_results` 테이블에 저장하고 반환합니다.
* **엔드포인트**: `/api/v1/pneumonia/predict/{record_id}`
* **메서드**: `POST`
* **인증 필요**: Y (의료진/직원 사용자)

### 1.2 요청(Request)
* **경로 파라미터**:

| 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| record_id | integer | Y | AI 분석을 수행할 진료 기록 ID |

### 1.3 응답(Response)
* **성공 (200 OK)**:
```json
{
  "id": 1,
  "record_id": 12,
  "is_pneumonia": true,
  "confidence": 98.45,
  "heatmap_url": "/media/heatmap/record_12.png",
  "ai_model": "SimpleCNN",
  "created_at": "2026-06-08T16:50:00",
  "updated_at": "2026-06-08T16:50:00"
}
```

* **실패 (404 Not Found)**:
  * `진료 기록 ID가 존재하지 않습니다.`
  * `진료 기록에 등록된 X-Ray 이미지가 없습니다.`
  * `X-Ray 이미지 파일이 서버에 존재하지 않습니다.`

---

## 2. AI 폐렴 예측 결과 조회 API

### 2.1 API 개요
* **설명**: 특정 진료 기록 ID(`record_id`)에 대해 이미 생성되어 있는 AI 분석 결과를 조회합니다.
* **엔드포인트**: `/api/v1/pneumonia/results/{record_id}`
* **메서드**: `GET`
* **인증 필요**: Y (내부 사용자 전체)

### 2.2 요청(Request)
* **경로 파라미터**:

| 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| record_id | integer | Y | 기존 분석 결과를 조회할 진료 기록 ID |

### 2.3 응답(Response)
* **성공 (200 OK)**:
```json
{
  "id": 1,
  "record_id": 12,
  "is_pneumonia": true,
  "confidence": 98.45,
  "heatmap_url": "/media/heatmap/record_12.png",
  "ai_model": "SimpleCNN",
  "created_at": "2026-06-08T16:50:00",
  "updated_at": "2026-06-08T16:50:00"
}
```

* **실패 (404 Not Found)**:
  * `진료 기록 ID가 존재하지 않습니다.`
  * `해당 진료 기록에 대한 AI 분석 결과가 존재하지 않습니다.`

---

## 3. AI 폐렴 즉시 예측 API (업로드)

### 3.1 API 개요
* **설명**: 흉부 X-Ray 이미지 파일을 직접 업로드하여 DB 저장 과정 없이 실시간으로 AI 폐렴 분석 결과를 리턴받아 화면에 표시합니다.
* **엔드포인트**: `/api/v1/pneumonia/predict/upload`
* **메서드**: `POST`
* **인증 필요**: Y (의료진/직원 사용자)

### 3.2 요청(Request)
* **Headers**: `Content-Type: multipart/form-data`
* **Body**:

| 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| file | file | Y | 폐렴 분석용 흉부 X-Ray 이미지 파일 (PNG, JPG, JPEG 등) |

### 3.3 응답(Response)
* **성공 (200 OK)**:
```json
{
  "prediction": "PNEUMONIA",
  "confidence": 98.45,
  "probability_normal": 1.55,
  "probability_pneumonia": 98.45
}
```

* **실패 (400 Bad Request)**:
  * `지원되지 않는 이미지 포맷입니다.`
  * `비어 있는 파일입니다.`
