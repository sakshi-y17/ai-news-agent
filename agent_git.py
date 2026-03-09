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
    # This is the most widely supported model ID for the new SDK
    model_id = "gemini-1.5-flash" 
    prompt = f"Summarize these {category} updates for a developer in 3 bullets: {context}"
    try:
        response = await asyncio.wait_for(
            client.models.generate_content(model=model_id, contents=prompt),
            timeout=40
        )
        return response.text if response else "No summary generated."
    except Exception as e:
        # If it still fails, the log will tell us exactly why
        print(f"DEBUG: Attempted model {model_id} - Error: {e}")
        return f"⚠️ AI Error: {str(e)}"
        
async def main():
    if not all([TOKEN, CHAT_ID, KEY]):
        print("❌ ERROR: Missing Secrets!")
        return

    bot = Bot(token=TOKEN)
    async with genai.Client(api_key=KEY, http_options={'api_version': 'v1'}) as client:
        
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



