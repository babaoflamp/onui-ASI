# GCP 빠른 배포 (Simple Cloud Run) 계획서

본 계획서는 `DEPLOYMENT.md` 가이드를 기반으로 프로젝트를 Google Cloud Run에 빠르고 간단하게 배포하기 위한 절차를 설명합니다. 이 배포 방식은 단일 인스턴스 환경 및 MVP 테스트에 적합합니다. 

---

## 📌 사전 준비 및 의사 결정 요구사항 (사용자 준비 필요)

성공적인 배포를 위해 다음 항목들을 미리 결정하고 준비해 주셔야 합니다.

1. **GCP 프로젝트 준비**
   - **GCP 프로젝트 ID (`PROJECT_ID`)**: Google Cloud Console에서 배포할 프로젝트를 생성하고 해당 프로젝트의 ID를 확인해 주세요.
2. **필수 환경 변수 및 API 키 설정**
   - **AI 모델 백엔드 (`MODEL_BACKEND`)**: 사용할 AI 모델을 결정해 주세요 (예: `ollama`, `openai`, `google`).
   - **OpenAI API Key (`OPENAI_API_KEY`)**: OpenAI 모델 사용 시 발급받은 API 키가 필요합니다.
   - **Gemini API Key (`GEMINI_API_KEY`)**: 구글 Gemini 모델 사용 시 API 키가 필요합니다.
   - **애플리케이션 보안 키 (`SECRET_KEY`)**: 세션 암호화 등을 위한 보안 키(임의의 긴 문자열)를 생성해 주세요.
   - *(선택)* **Ollama URL (`OLLAMA_URL`)**: 자체 구축한 Ollama 서버를 사용할 경우 해당 서버의 URL이 필요합니다.

---

## 🚀 배포 진행 단계

### 1단계: 프로젝트 환경 설정 및 API 활성화

1. **GCP 프로젝트 설정 및 인증**
   - 터미널에서 `PROJECT_ID` 환경 변수를 설정하고 해당 프로젝트로 `gcloud` 설정을 초기화합니다.
2. **필수 GCP API 활성화**
   - 배포에 필요한 Cloud Build, Cloud Run, Container Registry API를 활성화합니다.
   ```bash
   gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com
   ```

### 2단계: Docker 이미지 빌드 및 푸시

1. **로컬 Docker 이미지 빌드**
   - 프로젝트 소스코드를 기반으로 Docker 이미지를 빌드합니다.
   ```bash
   docker build -t gcr.io/$PROJECT_ID/onui-korean:latest .
   ```
2. **GCP Container Registry 업로드**
   - 빌드된 이미지를 GCP의 컨테이너 저장소에 푸시합니다.
   ```bash
   docker push gcr.io/$PROJECT_ID/onui-korean:latest
   ```

### 3단계: Cloud Run 서비스 배포 및 구성

1. **Cloud Run 배포 실행**
   - 푸시된 이미지를 사용하여 서비스를 배포합니다 (기본 메모리 2Gi, CPU 2 할당).
   ```bash
   gcloud run deploy onui-korean \
     --image gcr.io/$PROJECT_ID/onui-korean:latest \
     --platform managed \
     --region asia-northeast1 \
     --allow-unauthenticated \
     --memory 2Gi \
     --cpu 2 \
     --max-instances 10 \
     --port 8080
   ```
2. **환경 변수(.env) 주입**
   - 사전에 준비된 API 키 및 환경 변수들을 서비스에 적용합니다.
   ```bash
   gcloud run services update onui-korean \
     --region asia-northeast1 \
     --update-env-vars MODEL_BACKEND=[선택한_모델],SECRET_KEY=[보안_키],OPENAI_API_KEY=[API_키]
   ```

### 4단계: 서비스 검증 및 모니터링

1. **배포 URL 확인**
   - 서비스가 정상적으로 배포되었는지 접속 URL을 확인합니다.
2. **로그 점검**
   - Cloud Run 로그를 확인하여 애플리케이션 시작 시 오류가 없는지 점검합니다.
3. **리소스 및 비용 최적화 (선택)**
   - 필요에 따라 초기 비용 절감을 위해 메모리/CPU를 낮추거나 최대 인스턴스 수를 제한합니다.
