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

_scenarios_cache: list | None = None

def load_scenarios():
    global _scenarios_cache
    if _scenarios_cache is not None:
        return _scenarios_cache
    if not os.path.exists(DATA_PATH):
        _scenarios_cache = []
        return _scenarios_cache
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        _scenarios_cache = json.load(f)
    return _scenarios_cache

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

    # 역사 인물 롤플레이 프롬프트 구성
    era = scenario.get("era", "")
    speaking_style = scenario.get("speaking_style", "")
    topics = scenario.get("topics", [])

    system_prompt = f"""당신은 한국 역사 인물 '{scenario['persona']}'입니다.
시대: {era}
말투: {speaking_style}
주요 주제: {', '.join(topics)}

역할극 지침:
1. 반드시 한국어로만 답변하세요. 절대 영어로 답하지 마세요.
2. '{scenario['persona']}'의 성격, 시대적 배경, 말투를 일관되게 유지하세요.
3. 학습자 수준({scenario['level']})에 맞게 어휘를 조절하세요.
4. 답변은 반드시 2~3문장 이내로 짧고 간결하게 하세요. 절대 길게 설명하지 마세요.
5. 마지막 문장은 학습자에게 짧은 질문으로 끝내세요.
6. 학습 목표({', '.join(scenario['goals'])})를 자연스럽게 달성할 수 있도록 유도하세요.
7. 학습자가 잘못된 표현을 쓰면 인물의 캐릭터를 유지하며 한 문장으로만 교정해주세요."""

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

            model = genai.GenerativeModel(
                request.app.state.gemini_model,
                generation_config={"max_output_tokens": 200, "temperature": 0.7},
            )

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
                "temperature": 0.7,
                "max_tokens": 200,
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
                max_tokens=200,
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
