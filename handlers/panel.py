from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from config import ADMIN_ID


async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ شما ادمین نیستید.")
        return

    keyboard = [

        [
            InlineKeyboardButton("📊 آمار", callback_data="stats"),
            InlineKeyboardButton("👥 کاربران", callback_data="users")
        ],

        [
            InlineKeyboardButton("🧠 حافظه", callback_data="memory"),
            InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")
        ],

        [
            InlineKeyboardButton("⭐ VIP", callback_data="vip"),
            InlineKeyboardButton("🚫 Ban", callback_data="ban")
        ],

        [
            InlineKeyboardButton("⚙ تنظیمات", callback_data="settings"),
            InlineKeyboardButton("📜 لاگ‌ها", callback_data="logs")
        ]

    ]

    await update.message.reply_text(
        "🤖 پنل مدیریت AI Telegram",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
