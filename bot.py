```python
import os
import asyncio
import logging
from html import escape
from aiohttp import web

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv


# =========================================================
# SETTINGS
# =========================================================

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL_ID = os.getenv("CHANNEL_ID")
PORT = int(os.getenv("PORT", "10000"))


if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing")

if not ADMIN_ID:
    raise ValueError("ADMIN_ID is missing")

if not CHANNEL_ID:
    raise ValueError("CHANNEL_ID is missing")


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


# =========================================================
# BOT
# =========================================================

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    ),
)

dp = Dispatcher()


# =========================================================
# USER DRAFTS
# =========================================================

drafts = {}


# =========================================================
# KEYBOARDS
# =========================================================

def preview_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 نشر في القناة",
                    callback_data="publish",
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ إلغاء",
                    callback_data="cancel",
                )
            ],
        ]
    )


def main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ إنشاء منشور",
                    callback_data="new_post",
                )
            ]
        ]
    )


# =========================================================
# ACCESS CONTROL
# =========================================================

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


# =========================================================
# START
# =========================================================

@dp.message(CommandStart())
async def start_handler(message: Message):

    if not is_admin(message.from_user.id):
        await message.answer(
            "⛔ <b>غير مسموح</b>\n\n"
            "هذا البوت مخصص للإدارة فقط."
        )
        return

    await message.answer(
        "👋 <b>مرحبًا بك في بوت النشر</b>\n\n"
        "من هنا تستطيع إنشاء منشورات ونشرها في القناة.",
        reply_markup=main_keyboard(),
    )


# =========================================================
# NEW POST
# =========================================================

@dp.callback_query(F.data == "new_post")
async def new_post_handler(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ غير مسموح",
            show_alert=True,
        )
        return

    drafts.pop(callback.from_user.id, None)

    await callback.message.answer(
        "📝 <b>أرسل المنشور الآن</b>\n\n"
        "يمكنك إرسال:\n"
        "• نص فقط\n"
        "• صورة مع وصف\n"
        "• فيديو مع وصف\n\n"
        "بعد الإرسال سأعرض لك المعاينة قبل النشر.\n\n"
        "لإلغاء العملية أرسل:\n"
        "<code>/cancel</code>"
    )

    await callback.answer()


# =========================================================
# CANCEL COMMAND
# =========================================================

@dp.message(F.text == "/cancel")
async def cancel_command(message: Message):

    if not is_admin(message.from_user.id):
        return

    drafts.pop(message.from_user.id, None)

    await message.answer(
        "❌ تم إلغاء المنشور.",
        reply_markup=main_keyboard(),
    )


# =========================================================
# RECEIVE TEXT
# =========================================================

@dp.message(F.text)
async def receive_text(message: Message):

    if not is_admin(message.from_user.id):
        return

    if message.text.startswith("/"):
        return

    drafts[message.from_user.id] = {
        "type": "text",
        "text": message.text,
    }

    await message.answer(
        "👀 <b>معاينة المنشور:</b>\n\n"
        f"{escape(message.text)}",
        reply_markup=preview_keyboard(),
    )


# =========================================================
# RECEIVE PHOTO
# =========================================================

@dp.message(F.photo)
async def receive_photo(message: Message):

    if not is_admin(message.from_user.id):
        return

    photo = message.photo[-1]
    caption = message.caption or ""

    drafts[message.from_user.id] = {
        "type": "photo",
        "file_id": photo.file_id,
        "caption": caption,
    }

    preview_caption = (
        "👀 <b>معاينة المنشور:</b>\n\n"
        f"{escape(caption)}"
        if caption
        else "👀 <b>معاينة المنشور</b>"
    )

    await message.answer_photo(
        photo=photo.file_id,
        caption=preview_caption,
        reply_markup=preview_keyboard(),
    )


# =========================================================
# RECEIVE VIDEO
# =========================================================

@dp.message(F.video)
async def receive_video(message: Message):

    if not is_admin(message.from_user.id):
        return

    video = message.video
    caption = message.caption or ""

    drafts[message.from_user.id] = {
        "type": "video",
        "file_id": video.file_id,
        "caption": caption,
    }

    preview_caption = (
        "👀 <b>معاينة المنشور:</b>\n\n"
        f"{escape(caption)}"
        if caption
        else "👀 <b>معاينة المنشور</b>"
    )

    await message.answer_video(
        video=video.file_id,
        caption=preview_caption,
        reply_markup=preview_keyboard(),
    )


# =========================================================
# PUBLISH
# =========================================================

@dp.callback_query(F.data == "publish")
async def publish_handler(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ غير مسموح",
            show_alert=True,
        )
        return

    user_id = callback.from_user.id
    post = drafts.get(user_id)

    if not post:
        await callback.answer(
            "⚠️ لا يوجد منشور للنشر.",
            show_alert=True,
        )
        return

    try:

        if post["type"] == "text":

            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=post["text"],
            )

        elif post["type"] == "photo":

            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=post["file_id"],
                caption=post["caption"] or None,
            )

        elif post["type"] == "video":

            await bot.send_video(
                chat_id=CHANNEL_ID,
                video=post["file_id"],
                caption=post["caption"] or None,
            )

        drafts.pop(user_id, None)

        await callback.message.answer(
            "✅ <b>تم نشر المنشور بنجاح!</b>\n\n"
            f"📢 القناة: <code>{escape(str(CHANNEL_ID))}</code>",
            reply_markup=main_keyboard(),
        )

        await callback.answer("تم النشر ✅")

    except Exception as e:

        logger.exception("Publishing error")

        await callback.message.answer(
            "❌ <b>حدث خطأ أثناء النشر.</b>\n\n"
            f"<code>{escape(str(e))}</code>"
        )

        await callback.answer("حدث خطأ ❌")


# =========================================================
# CANCEL BUTTON
# =========================================================

@dp.callback_query(F.data == "cancel")
async def cancel_handler(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ غير مسموح",
            show_alert=True,
        )
        return

    drafts.pop(callback.from_user.id, None)

    await callback.message.answer(
        "❌ تم إلغاء المنشور.",
        reply_markup=main_keyboard(),
    )

    await callback.answer()


# =========================================================
# UNKNOWN CONTENT
# =========================================================

@dp.message()
async def unknown_message(message: Message):

    if not is_admin(message.from_user.id):
        return

    await message.answer(
        "⚠️ هذا النوع من الملفات غير مدعوم حاليًا.\n\n"
        "أرسل نصًا أو صورة أو فيديو."
    )


# =========================================================
# HEALTH SERVER FOR RENDER
# =========================================================

async def health_check(request):
    return web.Response(
        text="Telegram Publisher Bot is running."
    )


async def start_health_server():

    app = web.Application()

    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)

    runner = web.AppRunner(app)

    await runner.setup()

    site = web.TCPSite(
        runner,
        host="0.0.0.0",
        port=PORT,
    )

    await site.start()

    logger.info(
        f"Health server started on port {PORT}"
    )

    return runner


# =========================================================
# MAIN
# =========================================================

async def main():

    logger.info("Bot is starting...")

    health_runner = await start_health_server()

    try:
        await dp.start_polling(bot)

    finally:
        await health_runner.cleanup()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
```
