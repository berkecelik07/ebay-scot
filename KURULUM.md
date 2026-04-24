# eBayScout Kurulum Rehberi
## Tahmini süre: 20 dakika

---

## ADIM 1 — Gmail App Password Al (5 dakika)

Gmail'in normal şifresi çalışmaz, özel bir "App Password" lazım.

1. Gmail'e gir → sağ üstte profil fotoğrafına tıkla
2. "Manage your Google Account" seç
3. Üstte "Security" sekmesine tıkla
4. "2-Step Verification" bul ve AÇ (eğer kapalıysa)
5. Geri gel, "App passwords" ara ve tıkla
6. "Select app" → "Mail" seç
7. "Select device" → "Other" seç → "eBayScout" yaz
8. "Generate" tıkla
9. **16 haneli şifreyi kopyala** (örn: abcd efgh ijkl mnop)
   → Bunu GMAIL_SIFRE olarak kullanacaksın

---

## ADIM 2 — Anthropic API Key Al (3 dakika)

1. https://console.anthropic.com adresine git
2. Hesap oluştur (ücretsiz)
3. Sol menüde "API Keys" tıkla
4. "Create Key" tıkla
5. Çıkan anahtarı kopyala (sk-ant-... ile başlar)
   → Bunu ANTHROPIC_API_KEY olarak kullanacaksın

---

## ADIM 3 — GitHub'a Yükle (5 dakika)

1. https://github.com adresine git, hesap aç
2. "New repository" tıkla
3. İsim: "ebay-scout" → "Create repository"
4. Şu 3 dosyayı yükle (Upload files):
   - main.py
   - requirements.txt
   - railway.toml
5. "Commit changes" tıkla

---

## ADIM 4 — Railway'e Deploy Et (5 dakika)

1. https://railway.app adresine git
2. "Login with GitHub" ile gir
3. "New Project" tıkla
4. "Deploy from GitHub repo" seç
5. "ebay-scout" reposunu seç
6. Deploy başlayacak — bekle (2-3 dakika)

---

## ADIM 5 — Environment Variables Ekle (2 dakika)

Railway'de projeye tıkla → "Variables" sekmesi → şunları ekle:

| Key                  | Value                          |
|----------------------|--------------------------------|
| GMAIL_ADRES          | senin@gmail.com                |
| GMAIL_SIFRE          | (adım 1'deki 16 haneli şifre)  |
| ALICI_ADRES          | senin@gmail.com                |
| ANTHROPIC_API_KEY    | (adım 2'deki sk-ant-... key)   |

Ekledikten sonra "Deploy" tıkla.

---

## ADIM 6 — Test Et

Railway'de "Logs" sekmesine tıkla.
Şunu görmelisin:

```
eBayScout başlatıldı!
Kategoriler: Tools & Hardware, Home & Garden...
Her sabah 09:00'da araştırma yapılacak
Tools & Hardware kategorisi araştırılıyor...
✅ Email gönderildi: senin@gmail.com
```

Gmail'ini kontrol et — ilk email gelmiş olmalı! 🎉

---

## Sistem Nasıl Çalışır?

```
Her sabah 09:00
      ↓
6 kategori araştırılır
      ↓
En iyi 6 fırsat seçilir
      ↓
Gmail'ine email gelir
      ↓
"Onayla" butonuna tıklarsın
      ↓
eBay'e otomatik listelenir (eBay API bağlandıktan sonra)
```

---

## Sorun Çıkarsa

**Email gelmiyor:**
- Gmail App Password doğru girildi mi?
- 2-Factor Auth açık mı?

**API hatası:**
- Anthropic key doğru mu?
- Hesapta kredi var mı? (console.anthropic.com → Billing)

**Railway hatası:**
- Logs sekmesindeki hata mesajını bana gönder

---

## Sonraki Adımlar

- [ ] eBay API bağlantısı (otomatik listeleme)
- [ ] AliExpress Affiliate API (gerçek fotoğraflar)
- [ ] Onay/Reddet butonu aktivasyonu
- [ ] Kâr takip tablosu

Herhangi bir adımda takılırsan ekran görüntüsü at, yardım ederim!
