import os
import asyncio
import feedparser
from telegram import Bot
from google import genai

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
    # Updated model ID to match Google GenAI SDK requirements
    prompt = f"Summarize these {category} updates for a developer in 3 bullets: {context}"
    try:
        response = await asyncio.wait_for(
            client.models.generate_content(model="gemini-1.5-flash", contents=prompt),
            timeout=40
        )
        return response.text if response else "No summary generated."
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"

async def main():
    if not all([TOKEN, CHAT_ID, KEY]):
        print("❌ ERROR: Missing Secrets!")
        return

    bot = Bot(token=TOKEN)
    async with genai.Client(api_key=KEY).aio as client:
        
        await bot.send_message(chat_id=CHAT_ID, text="<b>🌍 GLOBAL & INDIA TECH BRIEFING</b>", parse_mode="HTML")
        await asyncio.sleep(5)

        for name, url in FEEDS.items():
            print(f"🔍 Processing: {name}...")
            try:
                data = feedparser.parse(url)
                stories = data.entries[:3]
                context = "\n".join([f"- {s.title}" for s in stories]) if stories else "No news today."
                
                summary = await get_summary(client, name, context)
                
                final_msg = f"<b>📍 {name}</b>\n{summary.replace('<', '&lt;').replace('>', '&gt;')}"
                await bot.send_message(chat_id=CHAT_ID, text=final_msg, parse_mode="HTML")
                
                print(f"✅ Successfully sent: {name}")
                # Increased wait to respect per-minute limits too
                await asyncio.sleep(15) 

            except Exception as e:
                print(f"❌ Failed {name}: {e}")

    print("🏁 Full Process Complete.")

if __name__ == "__main__":
    asyncio.run(main())

