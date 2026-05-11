# eBayScout

AI-powered eBay dropshipping product scout. Every morning at 09:00 it asks Claude to find low-competition products in six categories that are sourceable from AliExpress, filters them by profit margin, and emails the top opportunities as a styled HTML report.

## How it works

```
Every day at 09:00
      ↓
6 categories researched via Claude API
      ↓
Products with ≥40% profit margin kept
      ↓
Top 6 selected, sorted by margin
      ↓
HTML email sent to your Gmail
```

Categories: Tools & Hardware, Home & Garden, Sports & Outdoors, Automotive Parts, Office Supplies, Health & Beauty.

## Requirements

- Python 3.10+
- A Gmail account with 2-Step Verification enabled
- An Anthropic API key with credits

## Environment variables

| Key                 | Value                                                     |
|---------------------|-----------------------------------------------------------|
| `GMAIL_ADDRESS`     | Your Gmail address (sender)                               |
| `GMAIL_PASSWORD`    | Gmail **App Password** (16 chars, not your login password)|
| `RECIPIENT_EMAIL`   | Where reports get sent (can be the same as sender)        |
| `ANTHROPIC_API_KEY` | Anthropic console key, starts with `sk-ant-...`           |

## Local run

```bash
pip install -r requirements.txt

# PowerShell
$env:GMAIL_ADDRESS="you@gmail.com"
$env:GMAIL_PASSWORD="abcd efgh ijkl mnop"
$env:RECIPIENT_EMAIL="you@gmail.com"
$env:ANTHROPIC_API_KEY="sk-ant-..."

python main.py
```

The script runs the research immediately on startup, then sleeps until the next 09:00 trigger.

## Setup guide

### 1. Gmail App Password (~5 min)

Gmail's normal password won't work — you need a dedicated App Password.

1. Open Gmail → click your profile picture → **Manage your Google Account**
2. Go to the **Security** tab
3. Enable **2-Step Verification** if it isn't already on
4. Search for **App passwords** and open it
5. Select app → **Mail**, device → **Other** → name it `eBayScout`
6. Click **Generate** and copy the 16-character password (e.g. `abcd efgh ijkl mnop`)
7. Use it as `GMAIL_PASSWORD`

### 2. Anthropic API key (~3 min)

1. Go to <https://console.anthropic.com>
2. Create an account
3. Open **API Keys** → **Create Key**
4. Copy the key (starts with `sk-ant-...`) — use it as `ANTHROPIC_API_KEY`
5. Make sure your account has credits (Billing tab)

### 3. Push to GitHub (~5 min)

1. Create a new GitHub repo named `ebay-scout`
2. Upload `main.py`, `requirements.txt`, `railway.toml`
3. Commit

### 4. Deploy to Railway (~5 min)

1. Go to <https://railway.app> and sign in with GitHub
2. **New Project** → **Deploy from GitHub repo** → pick `ebay-scout`
3. Wait for the initial build to finish

### 5. Configure Railway variables (~2 min)

In the project's **Variables** tab, add all four keys from the table above, then redeploy.

### 6. Verify

Open the **Logs** tab — you should see:

```
eBayScout started!
[10/05/2026 09:00] Research started
[09:00] Searching Tools & Hardware...
✅ Email sent: you@gmail.com
```

Then check your inbox.

## Troubleshooting

**No email arrives**
- Confirm you used the App Password, not your Gmail login password
- Confirm 2-Step Verification is enabled

**API error in logs**
- Verify `ANTHROPIC_API_KEY` is correct
- Verify your Anthropic account has credits at console.anthropic.com → Billing

**Railway build/deploy issues**
- Check the **Logs** tab for the actual error message

## Roadmap

- [ ] eBay API integration (auto-listing)
- [ ] AliExpress Affiliate API (real product photos)
- [ ] Approve/Reject buttons in the email
- [ ] Profit tracking dashboard
