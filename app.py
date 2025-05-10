#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت الرسائل المجهولة – نشر إلى قناة مع تفاعل واحد لكل مستخدم وتخزين JSON
──────────────────────────────────────────────────────────────────────────
• يستقبل رسائل نصيّة في الخاص ويعيد نشرها مجهولة في القناة.
• يوجِّه الأصل إلى الأدمن لرؤية المُرسِل.
• يضيف أزرار تفاعل ❤️ / 😂 / 😢 بعدّادات تُحفَظ في ملف JSON.
• كل مستخدم له صوت واحد لكل رسالة؛ يمكنه استبداله.
• يقبل الرسائل فقط من متابعي القناة.
• ‎/id يعيد: في الخاص → مُعرّف المستخدم • في المجموعات → مُعرّف المجموعة.
"""

from __future__ import annotations
import os
import json
import logging
from pathlib import Path
from typing import Dict

import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException

# ─────────────── الإعدادات ───────────────
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "<YOUR_TOKEN>") 
ADMIN_ID: int = <Admin_ID>
TARGET_CHANNEL_ID: int = -100<ID>      # ⚠️ تأكّد من البادئة -100
REACTION_FILE: Path = Path("reactions.json")   # ملف تخزين التفاعلات
# ──────────────────────────────────────────

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)

# ─────────────── تحميل التفاعلات ───────────────
if REACTION_FILE.exists():
    with REACTION_FILE.open(encoding="utf-8") as f:
        reaction_data: Dict[str, Dict] = json.load(f)
else:
    reaction_data = {}                         # { "chat:msg": {counts:{}, users:{}} }

def save_reactions() -> None:
    """حفظ القاموس إلى JSON (يُستدعى بعد كل تعديل)."""
    try:
        with REACTION_FILE.open("w", encoding="utf-8") as f:
            json.dump(reaction_data, f, ensure_ascii=False, indent=2)
    except Exception:
        logging.exception("تعذّر حفظ ملف التفاعلات")


# ─────────────── أدوات مساعدة ───────────────
def msg_key(chat_id: int, msg_id: int) -> str:
    return f"{chat_id}:{msg_id}"

def init_entry(chat_id: int, msg_id: int) -> None:
    key = msg_key(chat_id, msg_id)
    if key not in reaction_data:
        reaction_data[key] = {
            "counts": {"heart": 0, "laugh": 0, "cry": 0},
            "users": {}  # {user_id: "heart"/"laugh"/"cry"}
        }

def build_keyboard(chat_id: int, msg_id: int) -> types.InlineKeyboardMarkup:
    entry = reaction_data.get(msg_key(chat_id, msg_id), {})
    counts = entry.get("counts", {"heart": 0, "laugh": 0, "cry": 0})
    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        types.InlineKeyboardButton(f"❤️ {counts['heart']}", callback_data=f"heart|{chat_id}|{msg_id}"),
        types.InlineKeyboardButton(f"😂 {counts['laugh']}", callback_data=f"laugh|{chat_id}|{msg_id}"),
        types.InlineKeyboardButton(f"😭 {counts['cry']}", callback_data=f"cry|{chat_id}|{msg_id}"),
    )
    return kb

def is_channel_member(user_id: int) -> bool:
    """
    يتحقّق من متابعة المستخدم للقناة.
    إذا لم تكن للبوت صلاحية `getChatMember` (CHAT_ADMIN_REQUIRED) نعدّ المستخدم متابعًا
    حفاظًا على استمرارية الخدمة، ويمكنك تغيير السلوك بسهولة.
    """
    try:
        member = bot.get_chat_member(TARGET_CHANNEL_ID, user_id)
        return member.status not in ("left", "kicked")
    except ApiTelegramException as e:
        if "CHAT_ADMIN_REQUIRED" in str(e):
            logging.warning("⚠️ البوت ليس مشرفًا أو لا يملك صلاحية رؤية الأعضاء؛ سيتم تجاوز فحص الاشتراك.")
            return True  # تجاوز الفحص عند غياب الصلاحية
        logging.warning("ApiTelegramException في فحص العضوية: %s", e)
        return False
    except Exception as e:
        logging.warning("خطأ غير متوقّع في فحص العضوية: %s", e)
        return False


# ─────────────── أوامر البوت ───────────────
@bot.message_handler(commands=["start"])
def cmd_start(m: types.Message) -> None:
    bot.send_message(
        m.chat.id,
        (
            "👋 أهلاً ومرحبًا بك!\n"
            "• أرسل رسالتك هنا، وسننشرها في الكروب بسرّيّة تامّة.\n"
            "✨ استمتع بحريّة التعبير!"
        ),
    )

@bot.message_handler(commands=["id"])
def cmd_id(m: types.Message) -> None:
    if m.chat.type in ("group", "supergroup"):
        bot.reply_to(m, f"🆔 معرّف هذه المجموعة: <code>{m.chat.id}</code>")
    else:
        bot.reply_to(m, f"🆔 معرّفك الشخصي: <code>{m.from_user.id}</code>")


# ─────────────── استقبال الرسائل الخاصة ───────────────
@bot.message_handler(func=lambda msg: msg.chat.type == "private", content_types=["text"])
def private_handler(m: types.Message) -> None:
    # التحقّق من الاشتراك
    if not is_channel_member(m.from_user.id):
        bot.reply_to(m, "⚠️ ولك حبيبي، إنت مو من نظم المعلومات شتسوي هنا؟ 😂 هذا البوت مخصص للناس الفاهمة بس، طلاب نظم المعلومات. روح دورلك غير مكان ✋")
        return

    # توجيه الأصل للأدمن
    try:
        bot.forward_message(ADMIN_ID, m.chat.id, m.message_id)
    except Exception:
        logging.exception("تعذّر توجيه الرسالة للأدمن")

    # نشر مجهول في القناة
    sent = bot.send_message(
        TARGET_CHANNEL_ID,
        f"📩 <b>رسالة مجهولة:</b>\n{m.text}",
        reply_markup=build_keyboard(TARGET_CHANNEL_ID, 0),  # مؤقّت
        disable_web_page_preview=True,
    )

    # إعداد التفاعل
    init_entry(sent.chat.id, sent.message_id)
    bot.edit_message_reply_markup(
        sent.chat.id,
        sent.message_id,
        reply_markup=build_keyboard(sent.chat.id, sent.message_id),
    )
    save_reactions()

    bot.reply_to(m, "✅ تم نشر رسالتك بسرّيّة.!")


# ─────────────── التفاعلات ───────────────
@bot.callback_query_handler(func=lambda c: c.data.split("|", 1)[0] in ("heart", "laugh", "cry"))
def reaction_handler(call: types.CallbackQuery) -> None:
    action, cid, mid = call.data.split("|")
    chat_id, msg_id = int(cid), int(mid)
    user_id = call.from_user.id

    init_entry(chat_id, msg_id)
    entry = reaction_data[msg_key(chat_id, msg_id)]
    counts, users = entry["counts"], entry["users"]

    prev = users.get(str(user_id))
    if prev == action:                       # ضغط نفس الرمز مجدّدًا
        bot.answer_callback_query(call.id, "💡 سبق أن اخترت هذا الرمز.")
        return

    if prev:                                 # تغيير الرأي
        counts[prev] = max(0, counts[prev] - 1)
    counts[action] += 1
    users[str(user_id)] = action
    save_reactions()

    try:
        bot.edit_message_reply_markup(chat_id, msg_id, reply_markup=build_keyboard(chat_id, msg_id))
    except ApiTelegramException:
        pass

    bot.answer_callback_query(call.id, "✅ تم تسجيل تفاعلك.")

# ─────────────── محتوى غير مدعوم ───────────────
@bot.message_handler(func=lambda _: True, content_types=["audio", "document", "photo",
                                                         "video", "sticker", "voice"])
def unsupported(m: types.Message) -> None:
    if m.chat.type == "private":
        bot.reply_to(m, "⚠️ يدعم البوت الرسائل النصّيّة فقط للنشر المجهول.")

# ─────────────── التشغيل ───────────────
if __name__ == "__main__":
    logging.info("🚀 Bot is running…")
    bot.infinity_polling(
        timeout=20,
        long_polling_timeout=20,
        allowed_updates=["message", "callback_query"],
    )
