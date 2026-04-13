from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import logging
import asyncio

router = APIRouter()
logger = logging.getLogger(__name__)

DATA_PATH = "data/roleplay-scenarios.json"

class ChatRequest(BaseModel):
    scenario_id: str
    messages: List[dict]  # [{"role": "user/assistant", "content": "..."}]

def load_scenarios():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("/roleplay", response_class=HTMLResponse)
async def roleplay_page(request: Request):
    return request.app.state.templates.TemplateResponse(request, "ai-roleplay.html")

@router.get("/api/roleplay/scenarios")
async def get_scenarios():
    return load_scenarios()

@router.post("/api/roleplay/chat")
async def roleplay_chat(request: Request, payload: ChatRequest):
    scenarios = load_scenarios()
    scenario = next((s for s in scenarios if s["id"] == payload.scenario_id), None)
    
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # LLM 프롬프트 구성
    system_prompt = f"""
    당신은 한국어 학습 도우미 '오누이'입니다. 현재 상황은 '{scenario['title']}'이며, 당신의 역할은 '{scenario['persona']}'입니다.
    학습자가 자연스럽게 한국어를 연습할 수 있도록 도와주세요.
    
    지침:
    1. 반드시 한국어로만 답변하세요.
    2. 학습자의 수준({scenario['level']})에 맞춰 너무 어렵지 않은 단어를 사용하세요.
    3. 학습자가 대화를 이어갈 수 있도록 질문을 포함하세요.
    4. 학습자가 잘못된 표현을 쓰면 아주 친절하게 짧게 교정해 줄 수도 있습니다.
    5. 현재 상황의 목표들({', '.join(scenario['goals'])})을 달성할 수 있도록 유도하세요.
    6. 대화 도중 관련 한국 문화(예: 식사 예절, 높임말 관습 등)를 자연스럽게 언급하며 팁을 주면 좋습니다.
    """

    messages = [{"role": "system", "content": system_prompt}] + payload.messages

    # LLM 호출 (main.py의 설정을 활용)
    backend = (request.app.state.model_backend or "").strip().lower()

    try:
        if backend == "gemini":
            # Gemini API 호출 로직
            try:
                import google.generativeai as genai
            except ImportError:
                raise RuntimeError("Gemini 패키지(google.generativeai)가 설치되어 있지 않습니다.")

            if not request.app.state.gemini_model:
                raise RuntimeError("GEMINI_MODEL 설정이 필요합니다.")

            model = genai.GenerativeModel(request.app.state.gemini_model)

            # 대화 형식 변환 (Gemini용)
            history = []
            for msg in messages[1:-1]:
                role = "user" if msg["role"] == "user" else "model"
                history.append({"role": role, "parts": [msg["content"]]})

            chat = model.start_chat(history=history)
            response = chat.send_message(messages[-1]["content"])
            ai_message = response.text

        elif backend == "ollama":
            # Ollama 호출 로직 (간략화)
            import requests
            ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
            model = request.app.state.ollama_model or os.getenv("OLLAMA_MODEL")
            if not model:
                raise RuntimeError("OLLAMA_MODEL 설정이 필요합니다.")

            url = f"{ollama_url}/v1/chat/completions"
            resp = requests.post(url, json={
                "model": model,
                "messages": messages,
                "temperature": 0.7
            }, timeout=30)

            if resp.status_code != 200:
                raise RuntimeError(f"Ollama 응답 상태 코드: {resp.status_code} - {resp.text}")

            ai_message = resp.json().get("choices", [])[0].get("message", {}).get("content", "")

        elif backend == "openai":
            openai_client = request.app.state.openai_client
            openai_model = request.app.state.openai_model
            if not openai_client:
                raise RuntimeError("OpenAI 클라이언트가 초기화되지 않았습니다. OPENAI_API_KEY를 확인하세요.")
            if not openai_model:
                raise RuntimeError("OPENAI_MODEL 설정이 필요합니다.")

            response = openai_client.chat.completions.create(
                model=openai_model,
                messages=[
                    {"role": "system", "content": "당신은 한국어 학습 도우미입니다."},
                    *messages[1:]
                ],
                temperature=0.7,
                max_tokens=1000
            )
            ai_message = response.choices[0].message.content

        else:
            raise RuntimeError(f"지원되지 않는 AI 백엔드입니다: '{backend}'. set MODEL_BACKEND to 'ollama', 'openai', or 'gemini'.")

        return {"message": ai_message}

    except Exception as e:
        logger.error(f"Roleplay chat error (backend={backend}): {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "backend": backend})

@router.post("/api/roleplay/evaluate")
async def roleplay_evaluate(request: Request, payload: ChatRequest):
    scenarios = load_scenarios()
    scenario = next((s for s in scenarios if s["id"] == payload.scenario_id), None)
    
    # 전체 대화 내용을 바탕으로 평가 프롬프트 구성
    chat_log = "\n".join([f"{m['role']}: {m['content']}" for m in payload.messages])
    
    eval_prompt = f"""
    다음은 '{scenario['title']}' 상황에서의 한국어 대화 기록입니다. 
    학습자의 한국어 능력을 평가하고 개선점을 알려주세요.
    
    대화 기록:
    {chat_log}
    
    평가 기준:
    1. 목표 달성도: {', '.join(scenario['goals'])}
    2. 어휘 사용: {', '.join(scenario['keywords'])} 사용 여부
    3. 문법 및 자연스러움
    
    결과는 반드시 JSON 형식으로 반환하세요.
    형식: {{"score": 0~100, "feedback": "전체 총평", "strengths": ["장점1", "장점2"], "improvements": ["개선점1", "개선점2"]}}
    """

    # LLM 호출하여 평가 결과 생성
    # (chat API와 유사한 구조로 호출)
    # ... (생략 가능, 구현 시 추가)
    
    return {"status": "success", "result": "Evaluation placeholder"}
