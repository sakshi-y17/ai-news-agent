import os
import asyncio
import feedparser
from telegram import Bot
from google import genai

# --- CONFIG ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
KEY = os.environ.get("GEMINI_KEY")

FEEDS = {
    "AI Tools": "https://www.artificialintelligence-news.com/feed/",
    "IT Market": "https://techcrunch.com/category/business/feed/",
    "Tech Jobs": "https://remoteok.com/remote-jobs.rss",
    "India Tech": "https://economictimes.indiatimes.com/tech/rssfeeds/1335720.cms"
}

async def main():
    if not all([TOKEN, CHAT_ID, KEY]):
        print("❌ ERROR: Missing Secrets! Check GitHub Settings.")
        return

    # 1. Initialize Clients
    bot = Bot(token=TOKEN)
    # Use the .aio property directly for async calls
    client = genai.Client(api_key=KEY).aio
    
    print("🚀 Sending Header...")
    await bot.send_message(chat_id=CHAT_ID, text="<b>🌍 GLOBAL & INDIA TECH BRIEFING</b>", parse_mode="HTML")
    await asyncio.sleep(3)

    for name, url in FEEDS.items():
        print(f"🔍 Processing: {name}...")
        try:
            # Fetch News
            data = feedparser.parse(url)
            stories = data.entries[:3]
            context = "\n".join([f"- {s.title}" for s in stories]) if stories else "General tech trends."
            
            # AI Summary - Using 1.5-flash for higher quota
            prompt = f"Summarize these {name} updates for a developer in 3 bullets: {context}"
            
            print(f"🤖 Requesting AI for {name}...")
            response = await client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=prompt
            )
            
            summary = response.text if response.text else "Summary unavailable."
            
            # Send to Telegram
            final_msg = f"<b>📍 {name}</b>\n{summary.replace('<', '&lt;').replace('>', '&gt;')}"
            await bot.send_message(chat_id=CHAT_ID, text=final_msg, parse_mode="HTML")
            
            print(f"✅ Successfully sent: {name}")
            # Wait 15 seconds between categories to be safe
            await asyncio.sleep(15)

        except Exception as e:
            print(f"❌ Failed {name}: {e}")

    print("🏁 Full Process Complete.")

if __name__ == "__main__":
    asyncio.run(main())
