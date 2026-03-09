import os
import asyncio
import feedparser
from telegram import Bot
from google import genai
from google.genai import types

# --- ENV LOAD ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
KEY = os.environ.get("GEMINI_KEY")

FEEDS = {
    "AI Tools": "https://www.artificialintelligence-news.com/feed/",
    "IT Market": "https://techcrunch.com/category/business/feed/",
    "Tech Jobs": "https://remoteok.com/remote-jobs.rss",
    "India Tech": "https://economictimes.indiatimes.com/tech/rssfeeds/1335720.cms"
}

async def get_summary(client, category, context):
    """Summarizes with a 30-second timeout to prevent hanging."""
    prompt = f"Summarize these {category} updates for a developer in 3 bullets: {context}"
    try:
        # Using a timeout to ensure GitHub doesn't wait forever
        response = await asyncio.wait_for(
            client.models.generate_content(model="gemini-2.5-flash", contents=prompt),
            timeout=30
        )
        return response.text if response else "No summary generated."
    except asyncio.TimeoutError:
        return "⚠️ AI Timeout: News was too long or server was slow."
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"

async def main():
    if not all([TOKEN, CHAT_ID, KEY]):
        print("❌ ERROR: Missing Secrets! Check your GitHub Settings.")
        return

    bot = Bot(token=TOKEN)
    # Using the 'aio' client correctly within a context manager
    async with genai.Client(api_key=KEY).aio as client:
        
        print("📡 Sending Header...")
        await bot.send_message(chat_id=CHAT_ID, text="<b>🌍 GLOBAL & INDIA TECH BRIEFING</b>", parse_mode="HTML")
        await asyncio.sleep(2)

        for name, url in FEEDS.items():
            print(f"🔍 Processing: {name}...")
            try:
                # 1. Fetch Feed
                data = feedparser.parse(url)
                stories = data.entries[:3]
                context = "\n".join([f"- {s.title}" for s in stories]) if stories else "No news today."
                
                # 2. Get AI Summary
                summary = await get_summary(client, name, context)
                
                # 3. Clean and Format
                final_msg = f"<b>📍 {name}</b>\n{summary.replace('<', '&lt;').replace('>', '&gt;')}"
                
                # 4. Send to Telegram
                await bot.send_message(chat_id=CHAT_ID, text=final_msg, parse_mode="HTML")
                print(f"✅ Successfully sent: {name}")
                
                # 5. Crucial: Wait 10 seconds to avoid Telegram rate limits
                await asyncio.sleep(10)

            except Exception as e:
                print(f"❌ Failed {name}: {e}")
                continue

    print("🏁 Full Process Complete.")

if __name__ == "__main__":
    asyncio.run(main())
