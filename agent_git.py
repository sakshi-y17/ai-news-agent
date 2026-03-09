import os
import feedparser
import asyncio
from telegram import Bot
from google import genai

# --- CONFIGURATION (Loading from Secrets) ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

FEEDS = {
    "AI Tools": "https://www.artificialintelligence-news.com/feed/",
    "IT Market": "https://techcrunch.com/category/business/feed/",
    "Tech Jobs": "https://remoteok.com/remote-jobs.rss",
    "India Tech": "https://economictimes.indiatimes.com/tech/rssfeeds/1335720.cms"
}

bot = Bot(token=TELEGRAM_TOKEN)
ai_client = genai.Client(api_key=GEMINI_KEY).aio

async def generate_ai_summary(category, raw_context):
    india_instruction = "Focus on Indian IT hubs and startups." if category == "India Tech" else ""
    prompt = f"Summarize these {category} updates for a developer. {india_instruction} Max 3 bullet points. Context: {raw_context}"
    return await ai_client.models.generate_content(model="gemini-2.5-flash", contents=prompt)

async def send_briefing():
    await bot.send_message(chat_id=CHAT_ID, text="<b>🌍 GLOBAL & INDIA TECH BRIEFING</b>", parse_mode="HTML")
    for category, url in FEEDS.items():
        try:
            feed = feedparser.parse(url)
            stories = feed.entries[:3]
            raw_context = "\n".join([f"Title: {s.title}\nLink: {s.link}" for s in stories]) if stories else "General tech trends."
            response = await generate_ai_summary(category, raw_context)
            msg = f"<b>📍 {category}</b>\n{response.text.replace('<', '&lt;').replace('>', '&gt;')}"
            await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(send_briefing())