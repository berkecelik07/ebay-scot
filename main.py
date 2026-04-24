import os
import json
import smtplib
import requests
import schedule
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

GMAIL_ADRES   = os.environ.get("GMAIL_ADRES", "")
GMAIL_SIFRE   = os.environ.get("GMAIL_SIFRE", "")
ALICI_ADRES   = os.environ.get("ALICI_ADRES", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

KATEGORILER = [
    "Tools & Hardware",
    "Home & Garden",
    "Sports & Outdoors",
    "Automotive Parts",
    "Office Supplies",
    "Health & Beauty",
]

MIN_KAR_ORANI = 0.40

def claude_api(prompt):
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-opus-4-5",
            "max_tokens": 1500,
            "messages": [{"role": "user", "content": prompt}]
        },
        timeout=60
    )
    data = response.json()
    text = data["content"][0]["text"].strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return text

def urun_ara(kategori):
    print(f"[{datetime.now().strftime('%H:%M')}] {kategori} arastiriliyor...")
    prompt = f"""You are an eBay dropshipping expert. Find 2 specific low-competition product opportunities in "{kategori}" that can be sourced from AliExpress.

Return ONLY a valid JSON array with 2 objects. No markdown, no backticks, no explanation.
Each object:
{{
  "title": "specific product name",
  "aliexpress_search": "exact search term",
  "source_cost_usd": 4.50,
  "ebay_sell_price_usd": 14.99,
  "profit_margin_pct": 70,
  "competition_level": "Low",
  "competition_reason": "one sentence why competition is low",
  "demand_score": 8,
  "category": "{kategori}",
  "ebay_title": "optimized eBay title max 80 chars",
  "ebay_description": "3 paragraph product description"
}}"""
    text = claude_api(prompt)
    return json.loads(text)

def email_hazirla(urunler):
    urun_html = ""
    for i, u in enumerate(urunler):
        aliexpress_link = f"https://www.aliexpress.com/wholesale?SearchText={u['aliexpress_search'].replace(' ', '+')}"
        urun_html += f"""
        <div style="background:#1e1e2e;border:1px solid #333;border-radius:16px;padding:24px;margin-bottom:24px;">
            <div style="margin-bottom:12px;">
                <span style="background:#0d3b4f;color:#00bcd4;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:bold;">
                    🟢 {u['competition_level']} Rekabet
                </span>
                <span style="color:#888;font-size:12px;margin-left:8px;">{u['category']}</span>
            </div>
            <h2 style="color:#fff;font-size:16px;margin:0 0 8px 0;">{u['title']}</h2>
            <p style="color:#888;font-size:13px;font-style:italic;margin:0 0 16px 0;">"{u['competition_reason']}"</p>
            <div style="display:flex;gap:12px;margin-bottom:16px;">
                <div style="flex:1;background:#111;border-radius:12px;padding:12px;text-align:center;">
                    <p style="color:#888;font-size:11px;margin:0 0 4px 0;">AliExpress</p>
                    <p style="color:#fff;font-size:18px;font-weight:bold;margin:0;">${u['source_cost_usd']:.2f}</p>
                </div>
                <div style="flex:1;background:#111;border-radius:12px;padding:12px;text-align:center;">
                    <p style="color:#888;font-size:11px;margin:0 0 4px 0;">eBay Fiyati</p>
                    <p style="color:#00bcd4;font-size:18px;font-weight:bold;margin:0;">${u['ebay_sell_price_usd']:.2f}</p>
                </div>
                <div style="flex:1;background:#0d3b1e;border-radius:12px;padding:12px;text-align:center;">
                    <p style="color:#4caf50;font-size:11px;margin:0 0 4px 0;">Kar</p>
                    <p style="color:#4caf50;font-size:18px;font-weight:bold;margin:0;">%{u['profit_margin_pct']}</p>
                </div>
            </div>
            <p style="color:#888;font-size:12px;margin:0 0 8px 0;">Talep: {'⭐' * u['demand_score']} ({u['demand_score']}/10)</p>
            <a href="{aliexpress_link}" style="display:inline-block;background:#e8581c;color:#fff;padding:10px 20px;border-radius:8px;text-decoration:none;font-size:13px;font-weight:bold;">
                🛒 AliExpress'te Gor
            </a>
        </div>
        """

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="background:#0a0a0f;font-family:Arial,sans-serif;padding:24px;margin:0;">
<div style="max-width:600px;margin:0 auto;">
    <div style="text-align:center;margin-bottom:32px;">
        <h1 style="color:#00bcd4;font-size:28px;margin:0;">eBay<span style="color:#fff;">Scout</span></h1>
        <p style="color:#888;font-size:13px;">{datetime.now().strftime('%d %B %Y')} - Gunluk Firsat Raporu</p>
    </div>
    <div style="background:#1a1a2e;border:1px solid #00bcd4;border-radius:16px;padding:16px;margin-bottom:24px;text-align:center;">
        <p style="color:#00bcd4;margin:0;">🤖 AI bugun <strong>{len(urunler)} firsat</strong> buldu!</p>
    </div>
    {urun_html}
</div>
</body></html>"""

def email_gonder(urunler):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"eBayScout - {len(urunler)} Yeni Firsat! ({datetime.now().strftime('%d/%m')})"
    msg["From"] = GMAIL_ADRES
    msg["To"] = ALICI_ADRES
    msg.attach(MIMEText(email_hazirla(urunler), "html"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADRES, GMAIL_SIFRE)
            server.sendmail(GMAIL_ADRES, ALICI_ADRES, msg.as_string())
        print(f"✅ Email gonderildi: {ALICI_ADRES}")
    except Exception as e:
        print(f"❌ Email hatasi: {e}")

def gunluk_arastirma():
    print(f"\n{'='*40}")
    print(f"[{datetime.now().strftime('%d/%m/%Y %H:%M')}] Arastirma basladi")
    tum_urunler = []
    for kategori in KATEGORILER:
        try:
            urunler = urun_ara(kategori)
            for u in urunler:
                kar = (u['ebay_sell_price_usd'] - u['source_cost_usd']) / u['ebay_sell_price_usd']
                if kar >= MIN_KAR_ORANI:
                    tum_urunler.append(u)
            time.sleep(2)
        except Exception as e:
            print(f"❌ {kategori} hatasi: {e}")

    print(f"✅ {len(tum_urunler)} firsat bulundu")
    if tum_urunler:
        tum_urunler.sort(key=lambda x: x['profit_margin_pct'], reverse=True)
        email_gonder(tum_urunler[:6])

if __name__ == "__main__":
    print("eBayScout basladi!")
    gunluk_arastirma()
    schedule.every().day.at("09:00").do(gunluk_arastirma)
    while True:
        schedule.run_pending()
        time.sleep(60)
