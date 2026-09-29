import asyncio
import os
import sys
from playwright.async_api import async_playwright

async def run():
    video_dir = "/config/.gemini/antigravity/brain/50c5d83b-303c-4721-883f-1f56e36fbeb7/safehaven_raw"
    os.makedirs(video_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--window-size=1280,800"
            ]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            record_video_dir=video_dir,
            record_video_size={"width": 1280, "height": 800}
        )
        page = await context.new_page()

        print("1. Opening SafeHaven at http://127.0.0.1:8089 ...")
        await page.goto("http://127.0.0.1:8089", wait_until="networkidle")
        await asyncio.sleep(2)

        # Highlight top 112 bar and household
        print("2. Reviewing urban flooding risk for Ramesh Rao...")
        await asyncio.sleep(2)

        # Scroll checklist
        checklist = page.locator("#checklist-container")
        await checklist.scroll_into_view_if_needed()
        await asyncio.sleep(1.5)

        # Click first two checkboxes
        first_box = page.locator("#checklist-container input[type='checkbox']").first
        if await first_box.count() > 0:
            await first_box.click()
            await asyncio.sleep(1)

        # Ask Co-Pilot First query: What SafeHaven does best (Life-saving emergency directive in Kannada/English)
        print("3. Asking Co-Pilot life-saving question in chat...")
        chat_input = page.locator("#chat-input")
        await chat_input.fill("Water is rising to knee level in Sarjapur ground floor. What should my elderly father with insulin do right now?")
        await page.locator("#chat-form button").click()
        await asyncio.sleep(5)  # Wait for Gemini response

        # Switch disaster scenario to Cyclone Sagar (Udupi Coast)
        print("4. Switching to Cyclone Sagar scenario & Shekar Kunder household...")
        await page.select_option("#sel-disaster", "cyclone")
        await asyncio.sleep(1.5)
        await page.select_option("#sel-household", "HH-UDP-01")
        await asyncio.sleep(2)

        # Click 'I Need Help (Trigger SOS)' -> Automatically shifts to Shelters & Solutions!
        print("5. Clicking 'I Need Help' -> Auto-shifting to Shelters & High Ground...")
        sos_btn = page.locator(".btn-sos")
        await sos_btn.scroll_into_view_if_needed()
        await asyncio.sleep(1)
        await sos_btn.click()
        await asyncio.sleep(3)  # Transition happens

        # Inspect Nearest Shelters and Fishing Boat tracker
        print("6. Viewing Shelters, Elevation, and Vessel Tracker...")
        await asyncio.sleep(2.5)

        # Switch to Printable Emergency Card (Certificate Pass)
        print("7. Viewing beautiful Emergency Certificate Pass...")
        card_tab = page.locator(".nav-tab", has_text="Printable Emergency Card")
        await card_tab.click()
        await asyncio.sleep(3)

        # Ask second, richer prompt showing database lookup / vessel sea tracking tool call
        print("8. Asking second richer prompt in Co-Pilot chat...")
        await chat_input.fill("Check active alert details for Cyclone Sagar and list nearest cyclone relief center with capacity.")
        await page.locator("#chat-form button").click()
        await asyncio.sleep(5)

        # Switch to Responder Dashboard to see live SOS registered
        print("9. Checking District Emergency Responder Console...")
        resp_tab = page.locator(".nav-tab", has_text="Responder Dashboard")
        await resp_tab.click()
        await asyncio.sleep(3)

        print("10. Finishing recording...")
        await asyncio.sleep(2)
        await context.close()
        await browser.close()
        print("Browser closed and recording saved.")

if __name__ == "__main__":
    asyncio.run(run())
