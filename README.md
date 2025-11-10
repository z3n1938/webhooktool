# 🧰 Discord Webhook Tool

## ⚡ Features

- **Bulk & Single Message Sending**  
  Send custom messages to one or multiple webhooks instantly. Supports dynamic templates with `{{random}}` and `{{time}}`.

- **Rich Embed Builder**  
  Create fully customizable Discord embeds (title, description, fields, color, thumbnail, footer, etc.) with **real-time preview**.

- **Fake Content Generators**  
  Generate fake Discord Nitro gift codes or server invites — perfect for testing and demos.

- **Advanced Scheduler**  
  Schedule one-shot or recurring tasks (cron-style). Supports seconds, minutes, hours, and daily repeats.

- **Profile System**  
  Save and load webhook configurations, messages, and embeds for instant reuse.

- **Detailed Logging**  
  Every sent message is logged with timestamp, webhook URL, and status. Export logs as **CSV**.

- **Smart Retry Mechanism**  
  Automatically retries failed requests due to network issues or Discord rate limits.

- **Themes & UI**  
  Sleek dark mode + light mode. Full terminal color support for console lovers.

- **Cross-Platform**  
  Works flawlessly on **Windows**, **Linux**, and **macOS**.

---

## 📝 Requirements

- Python 3.8+
- `requests` – For HTTP requests to Discord
- `tkinter` – Built-in with standard Python

Install dependencies:
```bash
pip install requests tkinter
```

```markdown
## 🚀 Usage

1. **Download or clone the repo**  
   ```bash
   git clone https://github.com/yourusername/discord-webhook-tool.git
   cd discord-webhook-tool
   ```

2. **Run the tool**  
   ```bash
   python discordwebhooktool.py
   ```

3. **Add your webhook URL(s)**  
   You can paste one or multiple webhook URLs (one per line).

4. **Choose a mode**  
   - **Normal** → Send custom messages  
   - **Fake Nitro** → Generate & send fake Nitro gift codes  
   - **Fake Invite** → Generate & send fake server invites  
   - **Embed Builder** → Create and send rich Discord embeds  

5. **Set delay, template, or schedule**  
   Adjust send interval, use `{{random}}` / `{{time}}` placeholders, or create recurring tasks.

6. **Preview embeds → Hit Start**  
   See exactly how your embed will look on Discord before sending.

7. **Save profiles for future use**  
   One-click reload of webhooks, messages, embeds, and schedules.

**All logs and profiles are saved in**  
```
~/.discord_webhook_tool/
```

## ⚠️ Important Notes

- **For testing & educational purposes only**  
- **Do NOT** use real Nitro codes or spam real servers  
- **Respect Discord's ToS and rate limits**  
- The built-in retry system automatically handles temporary bans or network hiccups  

**Happy (and responsible) webhooking!** 🔔
```

Şimdi tam istediğin gibi: her başlık **##** ile, madde işaretleri temiz, kod blokları düzgün. Kopyala-yapıştır yap, README’n şahane duracak canım! 🚀✨
