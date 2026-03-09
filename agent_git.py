import os
import feedparser
import asyncio
from telegram import Bot
from google import genai

# --- CONFIG ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

FEEDS = {
    "AI Tools": "https://www.artificialintelligence-news.com/feed/",
    "IT Market": "https://techcrunch.com/category/business/feed/",
    "Tech Jobs": "https://remoteok.com/remote-jobs.rss",
    "India Tech": "https://economictimes.indiatimes.com/tech/rssfeeds/1335720.cms"
}

# Use a context manager for the client to ensure it stays open
async def run_agent():
    async with genai.Client(api_key=GEMINI_KEY).aio as ai_client:
        bot = Bot(token=TELEGRAM_TOKEN)
        
        print("🚀 Sending Header...")
        await bot.send_message(chat_id=CHAT_ID, text="<b>🌍 GLOBAL & INDIA TECH BRIEFING</b>", parse_mode="HTML")
        await asyncio.sleep(3)

        for category, url in FEEDS.items():
            try:
                print(f"📡 Processing {category}...")
                feed = feedparser.parse(url)
                stories = feed.entries[:3]
                
                context = "No new stories found. Summarize general tech trends for 2026."
                if stories:
                    context = "\n".join([f"Title: {s.title}\nLink: {s.link}" for s in stories])

                prompt = f"Summarize these {category} updates for a developer (max 3 bullets): {context}"
                
                # Await the AI response
                response = await ai_client.models.generate_content(
                    model="gemini-2.5-flash", 
                    contents=prompt
                )
                
                if response and response.text:
                    clean_text = response.text.replace('<', '&lt;').replace('>', '&gt;')
                    msg = f"<b>📍 {category}</b>\n{clean_text}"
                    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML")
                    print(f"✅ {category} sent!")
                else:
                    print(f"⚠️ {category} returned no text from AI.")

                # Wait 10 seconds between categories to avoid Telegram rate limits
                await asyncio.sleep(10)

            except Exception as e:
                print(f"❌ Error in {category}: {e}")

if __name__ == "__main__":
    asyncio.run(run_agent())
