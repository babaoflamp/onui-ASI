import asyncio
from playwright.async_api import async_playwright
import os


async def login_and_capture():
    base_url = "http://localhost:9002"
    credentials = {"username": "mediazen@mediazen.co.kr", "password": "mz1234!@"}

    os.makedirs("screenshots_auth", exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        await page.set_viewport_size({"width": 1280, "height": 800})

        try:
            # 1. Go to landing page
            print(f"Navigating to {base_url}...")
            await page.goto(base_url)

            # 2. Open login modal
            print("Opening login modal...")
            await page.evaluate("openAuthModal('login')")

            # 3. Fill and submit login form
            print("Filling login form...")
            await page.fill(
                '#login-form input[name="username"]', credentials["username"]
            )
            await page.fill(
                '#login-form input[name="password"]', credentials["password"]
            )
            await page.click('#login-form button[type="submit"]')

            # 4. Wait for navigation to dashboard
            print("Waiting for redirection to dashboard...")
            await page.wait_for_url(f"{base_url}/dashboard", timeout=15000)
            print("Login successful.")

            # 5. Capture authenticated pages
            auth_pages = [
                "/dashboard",
                "/mypage",
                "/learning-progress",
                "/speechpro-practice",
                "/onui-beats",
                "/video-learning",
            ]

            for i, route in enumerate(auth_pages, 1):
                url = f"{base_url}{route}"
                filename = f"screenshots_auth/auth_{i}.png"
                print(f"Capturing {url} -> {filename}")
                await page.goto(url, wait_until="networkidle")
                await asyncio.sleep(2)
                await page.screenshot(path=filename)

        except Exception as e:
            print(f"Error: {e}")
            await page.screenshot(path="screenshots_auth/error_state.png")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(login_and_capture())
