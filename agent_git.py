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
    print("🤖 Researching...")
    
    # 1. Send Header
    await bot.send_message(chat_id=CHAT_ID, text="<b>🌍 GLOBAL & INDIA TECH BRIEFING</b>", parse_mode="HTML")
    await asyncio.sleep(2) # Short pause after header

    for category, url in FEEDS.items():
        try:
            print(f"📡 Fetching {category}...")
            feed = feedparser.parse(url)
            stories = feed.entries[:3]
            
            # If feed is slow or empty, provide fallback context
            if not stories:
                raw_context = f"No specific recent news for {category}. Summarize the general 2026 outlook for this sector in India/Global."
            else:
                raw_context = "\n".join([f"Title: {s.title}\nLink: {s.link}" for s in stories])
            
            # 3. AI Summary
            response = await generate_ai_summary(category, raw_context)
            
            # 4. Clean and Send
            clean_text = response.text.replace('<', '&lt;').replace('>', '&gt;')
            msg = f"<b>📍 {category}</b>\n{clean_text}"
            
            await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML")
            print(f"✅ Sent {category}")
            
            # INCREASE THIS SLEEP: Give Telegram 5-7 seconds to process each category
            await asyncio.sleep(7) 
            
        except Exception as e:
            print(f"❌ Error in {category}: {e}")
            # Even if it fails, wait before the next one
            await asyncio.sleep(2)

    print("✅ All briefings processed!"))

if __name__ == "__main__":

    asyncio.run(send_briefing())
