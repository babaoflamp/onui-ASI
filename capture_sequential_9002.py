import asyncio
from playwright.async_api import async_playwright
import os


async def capture_sequential_9002():
    routes = [
        "/",
        "/video-learning",
        "/onui-beats",
        "/voice-call",
        "/onui-messenger",
        "/content-generation",
        "/daily-expression",
        "/folktales",
        "/signup",
        "/login",
        "/mypage",
        "/learning-progress",
        "/dashboard",
        "/speechpro-practice",
        "/roleplay",
        "/sitemap",
        "/stt-api-test",
        "/api-test",
        "/change-password",
        "/admin/login",
        "/admin",
        "/admin/dashboard",
        "/admin/users",
        "/admin/api",
        "/admin/system",
        "/admin/logs",
        "/admin/settings",
    ]

    base_url = "http://localhost:9002"
    os.makedirs("screenshots_9002", exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1280, "height": 800})

        for i, route in enumerate(routes, 1):
            url = f"{base_url}{route}"
            filename = f"screenshots_9002/{i}.png"
            print(f"[{i}/27] Capturing {url} -> {filename}")
            try:
                # 9002 포트의 경우 리다이렉션이나 로딩 시간이 필요할 수 있으므로 타임아웃 넉넉히 설정
                await page.goto(url, wait_until="networkidle", timeout=15000)
                await asyncio.sleep(1.5)  # UI 렌더링을 위해 약간의 대기
                await page.screenshot(path=filename)
            except Exception as e:
                print(f"Failed to capture {url}: {e}")
                # 실패 시 빈 화면이라도 찍어두거나 넘어가기
                try:
                    await page.screenshot(path=filename)
                except:
                    pass

        await browser.close()


if __name__ == "__main__":
    asyncio.run(capture_sequential_9002())
