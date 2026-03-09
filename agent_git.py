import os
import asyncio
import feedparser
from telegram import Bot
from google import genai

# --- DEBUG PRINTING ---
print(f"DEBUG: TELEGRAM_TOKEN exists: {bool(os.environ.get('TELEGRAM_TOKEN'))}")
print(f"DEBUG: CHAT_ID exists: {bool(os.environ.get('CHAT_ID'))}")
print(f"DEBUG: GEMINI_KEY exists: {bool(os.environ.get('GEMINI_KEY'))}")

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

FEEDS = {
    "AI Tools": "https://www.artificialintelligence-news.com/feed/",
    "IT Market": "https://techcrunch.com/category/business/feed/",
    "Tech Jobs": "https://remoteok.com/remote-jobs.rss",
    "India Tech": "https://economictimes.indiatimes.com/tech/rssfeeds/1335720.cms"
}

async def run_agent():
    # If keys are missing, stop immediately so we see the error in logs
    if not TELEGRAM_TOKEN or not GEMINI_KEY:
        print("❌ CRITICAL ERROR: API Keys are missing from Environment!")
        return

    bot = Bot(token=TELEGRAM_TOKEN)
    
    # Use the aio client for async
    client = genai.Client(api_key=GEMINI_KEY).aio
    
    print("🚀 Sending Header...")
    await bot.send_message(chat_id=CHAT_ID, text="<b>🌍 GLOBAL & INDIA TECH BRIEFING</b>", parse_mode="HTML")
    await asyncio.sleep(5)

    for category, url in FEEDS.items():
        try:
            print(f"📡 Fetching {category}...")
            feed = feedparser.parse(url)
            stories = feed.entries[:3]
            context = "\n".join([f"Title: {s.title}\nLink: {s.link}" for s in stories]) if stories else "General tech trends."

            print(f"🤖 AI working on {category}...")
            response = await client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=f"Summarize these {category} updates for a developer: {context}"
            )
            
            msg = f"<b>📍 {category}</b>\n{response.text.replace('<', '&lt;').replace('>', '&gt;')}"
            await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML")
            print(f"✅ {category} sent!")
            await asyncio.sleep(10) # Safe delay

        except Exception as e:
            print(f"❌ Error in {category}: {e}")

if __name__ == "__main__":
    asyncio.run(run_agent())
