from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from backend.services.analytics_service import AnalyticsService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

analytics_service = AnalyticsService()

@router.get("/my-weakness", response_class=HTMLResponse)
async def weakness_page(request: Request):
    return request.app.state.templates.TemplateResponse("my-weakness.html", {"request": request})

@router.get("/api/analytics/weakness")
async def get_weakness_report(request: Request):
    try:
        user = request.app.state.require_authenticated_user(request)
        report = analytics_service.get_user_weakness_report(user["id"])
        
        # 만약 AI 피드백을 추가하고 싶다면 여기서 LLM 호출 가능
        if request.query_params.get("ai_tips") == "true":
            report["ai_tips"] = await generate_ai_tips(request, report)
            
        return report
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching weakness report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def generate_ai_tips(request, report):
    """LLM을 사용하여 개인별 맞춤형 발음 교정 팁 생성"""
    if not report.get("weak_sentences") and not report.get("weak_words"):
        return "데이터가 부족하여 AI 팁을 생성할 수 없습니다."

    sentences = [s["sentence_text"] for s in report.get("weak_sentences", [])]
    words = [w["word_id"] for w in report.get("weak_words", [])]
    
    prompt = f"""
    당신은 한국어 발음 전문가입니다. 다음은 학생의 취약한 발음 데이터입니다:
    취약 문장: {', '.join(sentences)}
    취약 단어: {', '.join(words)}
    
    이 데이터를 바탕으로 학생이 특히 주의해야 할 발음 현상이나 조음 규칙에 대해 3가지 짧고 친절한 조언을 한국어로 해주세요.
    """
    
    backend = request.app.state.model_backend
    try:
        if backend == "gemini":
            import google.generativeai as genai
            model = genai.GenerativeModel(request.app.state.gemini_model)
            response = model.generate_content(prompt)
            return response.text
        elif backend == "ollama":
            import requests
            import os
            url = f"{os.getenv('OLLAMA_URL', 'http://localhost:11434')}/v1/completions"
            resp = requests.post(url, json={
                "model": request.app.state.ollama_model,
                "prompt": prompt,
                "max_tokens": 500
            }, timeout=30)
            return resp.json()["choices"][0]["text"]
        return "AI 팁을 생성할 수 없습니다."
    except Exception as e:
        logger.error(f"AI Tips error: {e}")
        return "AI 피드백 생성 중 오류가 발생했습니다."
