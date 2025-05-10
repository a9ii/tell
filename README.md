

# 🤖 Anonymous Message Bot for Telegram

A Telegram bot that receives anonymous messages via private chat and posts them to a designated channel. It supports emoji-based reactions (❤️ / 😂 / 😢), stores interaction data in JSON, and ensures only channel followers can send messages.

---

## ✨ Features

- **Anonymous Submissions:** Users send text messages privately; the bot reposts them anonymously in a public channel.
- **Admin Forwarding:** Each submission is forwarded to the admin with the sender's identity (for moderation).
- **Emoji Reactions:** Messages include three interactive emojis with counters (❤️ / 😂 / 😢).
- **One Vote per User:** Each user can react once per message; reactions can be changed.
- **JSON Persistence:** All reactions and votes are saved in a local JSON file.
- **Subscription Check:** Only users who follow the target channel can send messages.
- **Simple Interaction:** Commands are minimal; message content must be plain text.

---

## 📦 Requirements

- Python 3.8+
- `pyTelegramBotAPI` (aka `telebot`)

Install dependencies with:

```bash
pip install pyTelegramBotAPI
````

---

## ⚙️ Configuration

Edit the following variables at the top of `bot.py`:

```python
BOT_TOKEN = os.getenv("BOT_TOKEN", "<YOUR_TOKEN>")
ADMIN_ID = 123456789                 # Telegram user ID of the admin
TARGET_CHANNEL_ID = -1001234567890  # Must include -100 prefix
REACTION_FILE = Path("reactions.json")
```

Ensure your bot is:

* Added to the channel as an **admin**.
* Granted permission to **post messages** and **read channel member status**.

You may use a `.env` file or environment variables for `BOT_TOKEN`.

---

## 🚀 Running the Bot

```bash
python bot.py
```

The bot will continuously poll for messages and handle incoming data.

---

## 🧾 Supported Commands

| Command  | Description                                         |
| -------- | --------------------------------------------------- |
| `/start` | Welcome message with usage instructions             |
| `/id`    | Returns user ID (in private) or group ID (in group) |

---

## 🧠 Reaction Data Format

All message reactions are saved in a structured JSON file like this:

```json
{
  "chat_id:message_id": {
    "counts": {
      "heart": 5,
      "laugh": 2,
      "cry": 1
    },
    "users": {
      "123456789": "heart",
      "987654321": "laugh"
    }
  }
}
```

This ensures durability across bot restarts and enables per-user tracking.

---

## 🛡️ Privacy & Limitations

* Only **plain text** messages are supported (to ensure anonymity and prevent media leaks).
* Admins can identify the sender but users remain anonymous to the public.
* Designed with privacy, simplicity, and student communities in mind (e.g. MIS departments).

---

## 🤝 Contributing

Pull requests and suggestions are welcome!

---



> ❤️ If you find this project helpful, consider starring it on GitHub!

```


