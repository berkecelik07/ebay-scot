import os
import json
import smtplib
import requests
import schedule
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime
import anthropic

# ============================================================
# AYARLAR — Buraya kendi bilgilerini gir
# ============================================================
GMAIL_ADRES     = os.environ.get("GMAIL_ADRES", "senin@gmail.com")
GMAIL_SIFRE     = os.environ.get("GMAIL_SIFRE", "")        # App Password (aşağıda açıklandı)
ALICI_ADRES     = os.environ.get("ALICI_ADRES", "senin@gmail.com")
ANTHROPIC_KEY   = os.environ.get("ANTHROPIC_API_KEY", "")
ONAY_URL        = os.environ.get("ONAY_URL", "http://localhost:5000") # Railway URL gelince değişir

KATEGORILER = [
    "Tools & Hardware",
    "Home & Garden",
    "Sports & Outdoors",
    "Automotive Parts",
    "Office Supplies",
    "Health & Beauty",
]

MIN_KAR_ORANI = 0.40   # %40 minimum kâr
# ============================================================

client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

def urun_ara(kategori):
    """Claude AI ile düşük rekabetli ürün ara"""
    print(f"[{datetime.now().strftime('%H:%M')}] {kategori} kategorisi araştırılıyor...")

    prompt = f"""You are an eBay dropshipping expert. Find 2 specific low-competition product opportunities in "{kategori}" that can be sourced from AliExpress.

Return ONLY a valid JSON array with 2 objects. No markdown, no backticks.
Each object:
{{
  "title": "specific product name",
  "aliexpress_search": "exact search term to find it on AliExpress",
  "source_cost_usd": 4.50,
  "ebay_sell_price_usd": 14.99,
  "profit_margin_pct": 70,
  "competition_level": "Low",
  "competition_reason": "one sentence why competition is low",
  "demand_score": 8,
  "category": "{kategori}",
  "ebay_title": "optimized eBay listing title max 80 chars",
  "ebay_description": "3 paragraph product description in HTML"
}}

Be very specific. Example: "Adjustable Laptop Stand Aluminum Foldable 6 Angles" not just "laptop stand".
Source cost must be realistic AliExpress wholesale price.
Profit margin must be at least 40%."""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.content[0].text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)

def aliexpress_fotograf_indir(arama_terimi, urun_basligi):
    """AliExpress'ten ürün fotoğrafı URL'si bul"""
    # AliExpress affiliate API ile gerçek entegrasyon
    # Şimdilik placeholder URL döndürüyor
    # Gerçek API: https://portals.aliexpress.com/affiportals/web/portals.htm
    
    arama = arama_terimi.replace(" ", "+")
    
    # Gerçek implementasyon için AliExpress Affiliate API:
    # affiliate_key = os.environ.get("ALIEXPRESS_AFFILIATE_KEY")
    # api_url = f"https://api.aliexpress.com/search?q={arama}&key={affiliate_key}"
    
    # Şimdilik ürünün placeholder görsel linki
    placeholder = f"https://via.placeholder.com/400x400/1a1a2e/00bcd4?text={arama_terimi.replace(' ', '+')[:20]}"
    return placeholder

def email_hazirla(urunler):
    """HTML email şablonu oluştur"""
    
    urun_html = ""
    for i, u in enumerate(urunler):
        kar = u['ebay_sell_price_usd'] - u['source_cost_usd']
        onay_link = f"{ONAY_URL}/onayla/{i}"
        reddet_link = f"{ONAY_URL}/reddet/{i}"
        aliexpress_link = f"https://www.aliexpress.com/wholesale?SearchText={u['aliexpress_search'].replace(' ', '+')}"

        urun_html += f"""
        <div style="background:#1e1e2e; border:1px solid #333; border-radius:16px; padding:24px; margin-bottom:24px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                <span style="background:#0d3b4f; color:#00bcd4; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:bold;">
                    🟢 {u['competition_level']} Rekabet
                </span>
                <span style="color:#888; font-size:12px;">{u['category']}</span>
            </div>

            <h2 style="color:#ffffff; font-size:16px; margin:0 0 8px 0;">{u['title']}</h2>
            <p style="color:#888; font-size:13px; font-style:italic; margin:0 0 16px 0;">"{u['competition_reason']}"</p>

            <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; margin-bottom:16px;">
                <div style="background:#111; border-radius:12px; padding:12px; text-align:center;">
                    <p style="color:#888; font-size:11px; margin:0 0 4px 0;">AliExpress</p>
                    <p style="color:#ffffff; font-size:18px; font-weight:bold; margin:0;">${u['source_cost_usd']:.2f}</p>
                </div>
                <div style="background:#111; border-radius:12px; padding:12px; text-align:center;">
                    <p style="color:#888; font-size:11px; margin:0 0 4px 0;">eBay Fiyatı</p>
                    <p style="color:#00bcd4; font-size:18px; font-weight:bold; margin:0;">${u['ebay_sell_price_usd']:.2f}</p>
                </div>
                <div style="background:#0d3b1e; border-radius:12px; padding:12px; text-align:center;">
                    <p style="color:#4caf50; font-size:11px; margin:0 0 4px 0;">Kâr</p>
                    <p style="color:#4caf50; font-size:18px; font-weight:bold; margin:0;">%{u['profit_margin_pct']}</p>
                </div>
            </div>

            <div style="margin-bottom:16px;">
                <p style="color:#888; font-size:11px; margin:0 0 4px 0;">Talep Skoru</p>
                <div style="display:flex; gap:4px;">
                    {''.join(['<div style="width:16px; height:8px; border-radius:2px; background:#00bcd4;"></div>' if j < u['demand_score'] else '<div style="width:16px; height:8px; border-radius:2px; background:#333;"></div>' for j in range(10)])}
                    <span style="color:#888; font-size:11px; margin-left:8px;">{u['demand_score']}/10</span>
                </div>
            </div>

            <a href="{aliexpress_link}" style="display:inline-block; background:#e8581c; color:#fff; padding:10px 20px; border-radius:8px; text-decoration:none; font-size:13px; margin-bottom:12px;">
                🛒 AliExpress'te Gör
            </a>

            <div style="display:flex; gap:12px;">
                <a href="{onay_link}" style="flex:1; display:block; background:#1b5e20; color:#4caf50; padding:14px; border-radius:12px; text-decoration:none; font-size:14px; font-weight:bold; text-align:center; border:1px solid #2e7d32;">
                    ✅ Onayla ve eBay'e Listele
                </a>
                <a href="{reddet_link}" style="display:block; background:#1a1a1a; color:#888; padding:14px 20px; border-radius:12px; text-decoration:none; font-size:14px; text-align:center; border:1px solid #333;">
                    ❌ Reddet
                </a>
            </div>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="background:#0a0a0f; font-family:'Segoe UI', Arial, sans-serif; padding:24px; margin:0;">
        <div style="max-width:600px; margin:0 auto;">

            <div style="text-align:center; margin-bottom:32px;">
                <h1 style="color:#00bcd4; font-size:28px; margin:0;">eBay<span style="color:#ffffff;">Scout</span></h1>
                <p style="color:#888; font-size:13px; margin:8px 0 0 0;">
                    {datetime.now().strftime('%d %B %Y')} · Günlük Fırsat Raporu
                </p>
            </div>

            <div style="background:#1a1a2e; border:1px solid #00bcd4; border-radius:16px; padding:16px; margin-bottom:24px; text-align:center;">
                <p style="color:#00bcd4; margin:0; font-size:14px;">
                    🤖 AI bugün <strong>{len(urunler)} fırsat</strong> buldu — Onayla ve eBay'e otomatik listele!
                </p>
            </div>

            {urun_html}

            <p style="color:#444; font-size:11px; text-align:center; margin-top:24px;">
                Bu email eBayScout tarafından otomatik gönderilmiştir.
            </p>
        </div>
    </body>
    </html>
    """
    return html

def email_gonder(urunler):
    """Gmail üzerinden email gönder"""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🛍 eBayScout — {len(urunler)} Yeni Fırsat Bulundu! ({datetime.now().strftime('%d/%m')})"
    msg["From"] = GMAIL_ADRES
    msg["To"] = ALICI_ADRES

    html = email_hazirla(urunler)
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADRES, GMAIL_SIFRE)
            server.sendmail(GMAIL_ADRES, ALICI_ADRES, msg.as_string())
        print(f"[{datetime.now().strftime('%H:%M')}] ✅ Email gönderildi: {ALICI_ADRES}")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M')}] ❌ Email hatası: {e}")

def gunluk_arastirma():
    """Her gün çalışan ana fonksiyon"""
    print(f"\n{'='*50}")
    print(f"[{datetime.now().strftime('%d/%m/%Y %H:%M')}] Günlük araştırma başladı")
    print(f"{'='*50}")

    tum_urunler = []

    for kategori in KATEGORILER:
        try:
            urunler = urun_ara(kategori)
            # Sadece min kâr oranını geçenleri al
            for u in urunler:
                kar_orani = (u['ebay_sell_price_usd'] - u['source_cost_usd']) / u['ebay_sell_price_usd']
                if kar_orani >= MIN_KAR_ORANI:
                    tum_urunler.append(u)
            time.sleep(2)  # API rate limit için bekle
        except Exception as e:
            print(f"❌ {kategori} hatası: {e}")

    print(f"\n✅ Toplam {len(tum_urunler)} fırsat bulundu")

    if tum_urunler:
        # En iyi 6 ürünü seç (kâr oranına göre)
        tum_urunler.sort(key=lambda x: x['profit_margin_pct'], reverse=True)
        en_iyi = tum_urunler[:6]
        email_gonder(en_iyi)
    else:
        print("Bu gün uygun fırsat bulunamadı.")

# ============================================================
# ZAMANLAYICI
# ============================================================
if __name__ == "__main__":
    print("eBayScout başlatıldı!")
    print(f"Kategoriler: {', '.join(KATEGORILER)}")
    print(f"Minimum kâr: %{int(MIN_KAR_ORANI*100)}")
    print("Her sabah 09:00'da araştırma yapılacak\n")

    # Hemen bir kez çalıştır (test için)
    gunluk_arastirma()

    # Her sabah 09:00'da çalış
    schedule.every().day.at("09:00").do(gunluk_arastirma)

    while True:
        schedule.run_pending()
        time.sleep(60)
