from fastapi import APIRouter, Request, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import google.generativeai as genai
import os
import io
import logging
import base64
from PIL import Image

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/vision-learning", response_class=HTMLResponse)
async def vision_page(request: Request):
    return request.app.state.templates.TemplateResponse("vision-learning.html", {"request": request})

@router.post("/api/vision/analyze")
async def analyze_image(request: Request, file: UploadFile = File(...)):
    if not request.app.state.openai_api_key and not os.getenv("GEMINI_API_KEY"):
         raise HTTPException(status_code=500, detail="API Key not configured")

    try:
        # 이미지 읽기 및 검증
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # JPEG로 변환 (Gemini 지원 형식)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Gemini 호출 준비
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel(request.app.state.gemini_model)

        prompt = """
        이미지 속에서 가장 핵심적인 사물 하나를 식별해서 한국어 학습 콘텐츠를 만들어주세요.
        결과는 반드시 다음 JSON 형식으로만 답변하세요:
        {
            "word": "사물 이름 (한국어)",
            "english": "Object name (English)",
            "pronunciation": "발음 (로마자 표기)",
            "description": "사물에 대한 짧은 설명",
            "examples": [
                {"ko": "한국어 예문 1", "en": "English Translation 1"},
                {"ko": "한국어 예문 2", "en": "English Translation 2"},
                {"ko": "한국어 예문 3", "en": "English Translation 3"}
            ]
        }
        학습자가 배우기 좋은 실생활 예문으로 구성해 주세요.
        """

        # 이미지 데이터를 Gemini 형식으로 변환
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_data = img_byte_arr.getvalue()

        # Gemini 멀티모달 호출
        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": img_data}
        ])

        # JSON 파싱
        try:
            import re
            json_text = response.text
            # 마크다운 제거
            json_text = re.sub(r'```json\s*|\s*```', '', json_text).strip()
            import json
            result = json.loads(json_text)
            return result
        except Exception as e:
            logger.error(f"Failed to parse Gemini vision response: {e}")
            return JSONResponse(status_code=500, content={"error": "결과 분석 실패", "raw": response.text})

    except Exception as e:
        logger.error(f"Vision analyze error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
