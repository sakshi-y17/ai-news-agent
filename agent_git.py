import os
import feedparser
import asyncio
from telegram import Bot
from google import genai

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

FEEDS = {
    "AI Tools": "https://www.artificialintelligence-news.com/feed/",
    "IT Market": "https://techcrunch.com/category/business/feed/",
    "Tech Jobs": "https://remoteok.com/remote-jobs.rss",
    "India Tech": "https://economictimes.indiatimes.com/tech/rssfeeds/1335720.cms"
}

# Initialize
bot = Bot(token=TELEGRAM_TOKEN)
ai_client = genai.Client(api_key=GEMINI_KEY).aio

async def generate_ai_summary(category, raw_context):
    india_instruction = "Focus heavily on Indian IT hubs like Bangalore, Pune, and startups." if category == "India Tech" else ""
    prompt = f"""
    Summarize these {category} updates for a developer.
    {india_instruction}
    STRICT RULE: Maximum 3 bullet points. Under 150 words.
    Context: {raw_context}
    """
    response = await ai_client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response

async def send_briefing():
    print("🤖 Starting Research...")
    
    # Send Header
    await bot.send_message(chat_id=CHAT_ID, text="<b>🌍 GLOBAL & INDIA TECH BRIEFING</b>", parse_mode="HTML")
    await asyncio.sleep(2)

    for category, url in FEEDS.items():
        try:
            print(f"📡 Fetching {category}...")
            feed = feedparser.parse(url)
            stories = feed.entries[:3]
            
            if not stories:
                raw_context = f"No recent news for {category}. Summarize 2026 tech trends."
            else:
                raw_context = "\n".join([f"Title: {s.title}\nLink: {s.link}" for s in stories])
            
            response = await generate_ai_summary(category, raw_context)
            clean_text = response.text.replace('<', '&lt;').replace('>', '&gt;')
            
            msg = f"<b>📍 {category}</b>\n{clean_text}"
            await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML")
            
            print(f"✅ Sent {category}")
            # The 7-second sleep to prevent Telegram spam blocks
            await asyncio.sleep(7) 
            
        except Exception as e:
            print(f"❌ Error in {category}: {e}")

    print("✅ All briefings processed!")

if __name__ == "__main__":
    asyncio.run(send_briefing())
