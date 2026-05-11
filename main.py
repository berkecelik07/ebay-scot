import os
import json
import smtplib
import requests
import schedule
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

GMAIL_ADDRESS    = os.environ.get("GMAIL_ADDRESS", "")
GMAIL_PASSWORD   = os.environ.get("GMAIL_PASSWORD", "")
RECIPIENT_EMAIL  = os.environ.get("RECIPIENT_EMAIL", "")
ANTHROPIC_KEY    = os.environ.get("ANTHROPIC_API_KEY", "").strip()

CATEGORIES = [
    "Tools & Hardware",
    "Home & Garden",
    "Sports & Outdoors",
    "Automotive Parts",
    "Office Supplies",
    "Health & Beauty",
]

MIN_PROFIT_MARGIN = 0.40

def claude_api(prompt):
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 1500,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=60
        )
        print(f"HTTP STATUS: {response.status_code}")
        data = response.json()
        print(f"API KEYS: {list(data.keys())}")
        print(f"API RESPONSE: {str(data)[:500]}")

        if "error" in data:
            raise Exception(f"API error: {data['error']['message']}")

        if "content" not in data:
            raise Exception(f"No content in response: {data}")

        text = data["content"][0]["text"].strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return text
    except requests.exceptions.Timeout:
        raise Exception("API timeout")
    except Exception as e:
        raise Exception(f"claude_api failed: {str(e)}")

def search_products(category):
    print(f"[{datetime.now().strftime('%H:%M')}] Searching {category}...")
    prompt = f"""Find 2 low-competition eBay dropshipping products in "{category}" sourceable from AliExpress.

Return ONLY a JSON array, no markdown, no explanation:
[
  {{
    "title": "specific product name",
    "aliexpress_search": "search term",
    "source_cost_usd": 4.50,
    "ebay_sell_price_usd": 14.99,
    "profit_margin_pct": 70,
    "competition_level": "Low",
    "competition_reason": "why competition is low",
    "demand_score": 8,
    "category": "{category}",
    "ebay_title": "eBay listing title max 80 chars",
    "ebay_description": "product description 3 paragraphs"
  }}
]"""
    text = claude_api(prompt)
    return json.loads(text)

def build_email(products):
    product_html = ""
    for u in products:
        aliexpress_link = f"https://www.aliexpress.com/wholesale?SearchText={u['aliexpress_search'].replace(' ', '+')}"
        product_html += f"""
        <div style="background:#1e1e2e;border:1px solid #333;border-radius:16px;padding:24px;margin-bottom:24px;">
            <span style="background:#0d3b4f;color:#00bcd4;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:bold;">
                🟢 {u['competition_level']} Competition — {u['category']}
            </span>
            <h2 style="color:#fff;font-size:16px;margin:12px 0 8px 0;">{u['title']}</h2>
            <p style="color:#888;font-size:13px;font-style:italic;margin:0 0 16px 0;">"{u['competition_reason']}"</p>
            <div style="display:flex;gap:12px;margin-bottom:16px;">
                <div style="flex:1;background:#111;border-radius:12px;padding:12px;text-align:center;">
                    <p style="color:#888;font-size:11px;margin:0 0 4px 0;">AliExpress</p>
                    <p style="color:#fff;font-size:18px;font-weight:bold;margin:0;">${u['source_cost_usd']:.2f}</p>
                </div>
                <div style="flex:1;background:#111;border-radius:12px;padding:12px;text-align:center;">
                    <p style="color:#888;font-size:11px;margin:0 0 4px 0;">eBay Price</p>
                    <p style="color:#00bcd4;font-size:18px;font-weight:bold;margin:0;">${u['ebay_sell_price_usd']:.2f}</p>
                </div>
                <div style="flex:1;background:#0d3b1e;border-radius:12px;padding:12px;text-align:center;">
                    <p style="color:#4caf50;font-size:11px;margin:0 0 4px 0;">Profit</p>
                    <p style="color:#4caf50;font-size:18px;font-weight:bold;margin:0;">{u['profit_margin_pct']}%</p>
                </div>
            </div>
            <p style="color:#888;font-size:12px;margin:0 0 12px 0;">Demand: {'⭐' * u['demand_score']} ({u['demand_score']}/10)</p>
            <a href="{aliexpress_link}" style="display:inline-block;background:#e8581c;color:#fff;padding:10px 20px;border-radius:8px;text-decoration:none;font-size:13px;font-weight:bold;">
                🛒 View on AliExpress
            </a>
        </div>"""

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="background:#0a0a0f;font-family:Arial,sans-serif;padding:24px;margin:0;">
<div style="max-width:600px;margin:0 auto;">
    <div style="text-align:center;margin-bottom:32px;">
        <h1 style="color:#00bcd4;font-size:28px;margin:0;">eBay<span style="color:#fff;">Scout</span></h1>
        <p style="color:#888;font-size:13px;">{datetime.now().strftime('%d %B %Y')} - Daily Opportunity Report</p>
    </div>
    <div style="background:#1a1a2e;border:1px solid #00bcd4;border-radius:16px;padding:16px;margin-bottom:24px;text-align:center;">
        <p style="color:#00bcd4;margin:0;">🤖 AI found <strong>{len(products)} opportunities</strong> today!</p>
    </div>
    {product_html}
</div></body></html>"""

def send_email(products):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"eBayScout - {len(products)} New Opportunities! ({datetime.now().strftime('%d/%m')})"
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = RECIPIENT_EMAIL
    msg.attach(MIMEText(build_email(products), "html"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())
        print(f"✅ Email sent: {RECIPIENT_EMAIL}")
    except Exception as e:
        print(f"❌ Email error: {e}")

def daily_research():
    print(f"\n{'='*40}")
    print(f"[{datetime.now().strftime('%d/%m/%Y %H:%M')}] Research started")
    print(f"API KEY first 10 chars: {ANTHROPIC_KEY[:10]}...")

    all_products = []
    for category in CATEGORIES:
        try:
            products = search_products(category)
            for u in products:
                margin = (u['ebay_sell_price_usd'] - u['source_cost_usd']) / u['ebay_sell_price_usd']
                if margin >= MIN_PROFIT_MARGIN:
                    all_products.append(u)
            time.sleep(2)
        except Exception as e:
            print(f"❌ {category} error: {e}")

    print(f"✅ {len(all_products)} opportunities found")
    if all_products:
        all_products.sort(key=lambda x: x['profit_margin_pct'], reverse=True)
        send_email(all_products[:6])

if __name__ == "__main__":
    print("eBayScout started!")
    daily_research()
    schedule.every().day.at("09:00").do(daily_research)
    while True:
        schedule.run_pending()
        time.sleep(60)
