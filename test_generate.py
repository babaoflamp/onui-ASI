
import requests

def test_generate():
    url = "http://localhost:9002/api/generate-content"
    data = {
        "topic": "식당에서 주문하기",
        "level": "초급",
        "backend": "gemini"
    }
    try:
        response = requests.post(url, data=data, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_generate()
