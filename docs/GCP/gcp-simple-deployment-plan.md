# GCP 빠른 배포 (Simple Cloud Run) 계획

이 계획은 기존 `DEPLOYMENT.md` 가이드를 기반으로 프로젝트를 Google Cloud Run에 빠르고 간단하게 배포하기 위한 절차를 설명합니다. 이 배포 방식은 MVP 테스트 및 단일 인스턴스 환경에 적합합니다.

## 1단계: 사전 요구사항 확인 및 환경 설정

1. **GCP 프로젝트 생성 및 설정**
   - Google Cloud Console에서 새 프로젝트를 생성하거나 기존 프로젝트를 선택합니다.
   - 로컬에서 프로젝트 ID 환경 변수 설정: `export PROJECT_ID="your-project-id"`
   - GCP CLI 초기화: `gcloud config set project $PROJECT_ID`
2. **필수 API 활성화**
   - Cloud Build, Cloud Run, Container Registry API를 활성화합니다.
   ```bash
   gcloud services enable \
     cloudbuild.googleapis.com \
     run.googleapis.com \
     containerregistry.googleapis.com
   ```

## 2단계: Docker 이미지 빌드 및 푸시

1. **도커 이미지 로컬 빌드**
   ```bash
   docker build -t gcr.io/$PROJECT_ID/onui-korean:latest .
   ```
2. **GCP Container Registry로 푸시**
   - GCR 인증 및 이미지 푸시를 진행합니다.
   ```bash
   docker push gcr.io/$PROJECT_ID/onui-korean:latest
   ```

## 3단계: Cloud Run 서비스 배포

1. **컨테이너 배포 실행**
   - 푸시된 이미지를 사용하여 Cloud Run에 배포합니다. 외부 접근을 허용하고 기본 리소스를 할당합니다.
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

## 4단계: 환경 변수 구성 (.env 적용)

1. **필수 환경 변수 설정**
   - `.env.production` 등을 참고하여 Cloud Run 서비스에 환경 변수를 주입합니다.
   ```bash
   gcloud run services update onui-korean \
     --region asia-northeast1 \
     --update-env-vars MODEL_BACKEND=ollama,SECRET_KEY=your-secret-key,OPENAI_API_KEY=your-key
   ```
   *(참고: 운영 환경에서는 보안을 위해 GCP Secret Manager 사용을 권장합니다.)*

## 5단계: 배포 확인 및 마무리

1. **배포된 서비스 URL 확인 및 접속 테스트**
   ```bash
   gcloud run services describe onui-korean \
     --region asia-northeast1 \
     --format 'value(status.url)'
   ```
2. **로그 확인**
   - 배포 후 애플리케이션 시작 로그를 확인하여 정상 동작을 검증합니다.
   ```bash
   gcloud run services logs read onui-korean --region asia-northeast1 --limit 50
   ```
3. **리소스 최적화 (선택)**
   - 초기 비용 절감을 위해 최소 인스턴스를 0으로 유지하고 필요시 메모리/CPU를 조정합니다.
