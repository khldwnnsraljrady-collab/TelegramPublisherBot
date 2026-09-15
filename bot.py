```python
import asyncio
import logging
import os
import re
from html import escape

from aiohttp import web

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ContentType
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from dotenv import load_dotenv


# =========================================================
# CONFIG
# =========================================================

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL_ID = os.getenv("CHANNEL_ID", "@razanaltifa")
PORT = int(os.getenv("PORT", "10000"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not configured.")

if not ADMIN_ID:
    raise RuntimeError("ADMIN_ID is not configured.")


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


# =========================================================
# BOT / DISPATCHER
# =========================================================

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    ),
)

dp = Dispatcher(storage=MemoryStorage())


# =========================================================
# FSM STATES
# =========================================================

class PostState(StatesGroup):
    waiting_for_post = State()


# =========================================================
# ADMIN CHECK
# =========================================================

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


# =========================================================
# MAIN MENU
# =========================================================

def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ إنشاء منشور",
                    callback_data="create_post",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📋 منشوراتي",
                    callback_data="my_posts",
                ),
                InlineKeyboardButton(
                    text="⏰ المجدولة",
                    callback_data="scheduled",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⚙️ الإعدادات",
                    callback_data="settings",
                )
            ],
        ]
    )


# =========================================================
# POST ACTIONS
# =========================================================

def post_actions() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 نشر الآن",
                    callback_data="publish_post",
                )
            ],
            [
                InlineKeyboardButton(
                    text="✏️ تعديل",
                    callback_data="edit_post",
                ),
                InlineKeyboardButton(
                    text="❌ إلغاء",
                    callback_data="cancel_post",
                ),
            ],
        ]
    )


# =========================================================
# LINK / USERNAME EXTRACTION
# =========================================================

URL_PATTERN = re.compile(
    r"https?://[^\s<>()]+",
    re.IGNORECASE,
)

USERNAME_PATTERN = re.compile(
    r"(?<![\w])@([A-Za-z0-9_]{5,32})"
)


def clean_url(url: str) -> str:
    """
    Removes punctuation accidentally attached to a URL.
    """
    return url.rstrip(".,!?;:)]}")


def username_to_url(username: str) -> str:
    return f"https://t.me/{username}"


def username_label(username: str) -> str:
    return username.lstrip("@")


def make_button_for_url(url: str) -> tuple[str, str]:
    """
    Creates a nice automatic label based on the URL.
    """

    clean = clean_url(url)

    if "t.me/" in clean.lower():
        path = clean.split("t.me/", 1)[1]
        path = path.split("?", 1)[0].strip("/")

        if path:
            return f"📢 {path}", clean

        return "📢 فتح تيليجرام", clean

    if "telegram.me/" in clean.lower():
        path = clean.split("telegram.me/", 1)[1]
        path = path.split("?", 1)[0].strip("/")

        if path:
            return f"📢 {path}", clean

        return "📢 فتح تيليجرام", clean

    if "github.com" in clean.lower():
        return "💻 GitHub", clean

    if "youtube.com" in clean.lower() or "youtu.be" in clean.lower():
        return "▶️ YouTube", clean

    if "instagram.com" in clean.lower():
        return "📸 Instagram", clean

    if "facebook.com" in clean.lower():
        return "📘 Facebook", clean

    if "x.com" in clean.lower() or "twitter.com" in clean.lower():
        return "𝕏 X", clean

    if "wa.me/" in clean.lower() or "whatsapp.com" in clean.lower():
        return "💬 WhatsApp", clean

    return "🌐 فتح الرابط", clean


def extract_buttons(text: str) -> list[tuple[str, str]]:
    """
    Detect URLs and Telegram usernames.

    Returns:
        [(button_text, url), ...]
    """

    if not text:
        return []

    buttons = []
    seen = set()

    # -----------------------------------------------------
    # 1. URLs
    # -----------------------------------------------------

    for match in URL_PATTERN.findall(text):
        url = clean_url(match)

        if url in seen:
            continue

        seen.add(url)

        label, target = make_button_for_url(url)

        buttons.append((label, target))

    # -----------------------------------------------------
    # 2. Telegram usernames
    # -----------------------------------------------------

    for match in USERNAME_PATTERN.findall(text):

        username = match

        # Don't create a second button if the username
        # already exists as a t.me URL.
        if any(
            f"t.me/{username}".lower() in url.lower()
            for _, url in buttons
        ):
            continue

        target = username_to_url(username)

        if target in seen:
            continue

        seen.add(target)

        buttons.append(
            (
                f"👤 {username}",
                target,
            )
        )

    return buttons


# =========================================================
# KEYBOARD FROM DETECTED BUTTONS
# =========================================================

def build_post_keyboard(
    buttons: list[tuple[str, str]]
) -> InlineKeyboardMarkup | None:

    if not buttons:
        return None

    rows = []

    for label, url in buttons:
        rows.append(
            [
                InlineKeyboardButton(
                    text=label,
                    url=url,
                )
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=rows
    )


# =========================================================
# DRAFT STORAGE
# =========================================================

def save_draft(
    state_data: dict,
    message: Message,
):
    """
    Converts Telegram message into a reusable draft.
    """

    content_type = message.content_type

    draft = {
        "content_type": content_type,
        "text": "",
        "file_id": None,
        "caption": "",
        "buttons": [],
    }

    # -----------------------------------------------------
    # TEXT
    # -----------------------------------------------------

    if content_type == ContentType.TEXT:

        text = message.text or ""

        draft["text"] = text
        draft["buttons"] = extract_buttons(text)

    # -----------------------------------------------------
    # PHOTO
    # -----------------------------------------------------

    elif content_type == ContentType.PHOTO:

        draft["file_id"] = message.photo[-1].file_id
        draft["caption"] = message.caption or ""
        draft["buttons"] = extract_buttons(
            message.caption or ""
        )

    # -----------------------------------------------------
    # VIDEO
    # -----------------------------------------------------

    elif content_type == ContentType.VIDEO:

        draft["file_id"] = message.video.file_id
        draft["caption"] = message.caption or ""
        draft["buttons"] = extract_buttons(
            message.caption or ""
        )

    # -----------------------------------------------------
    # DOCUMENT
    # -----------------------------------------------------

    elif content_type == ContentType.DOCUMENT:

        draft["file_id"] = message.document.file_id
        draft["caption"] = message.caption or ""
        draft["buttons"] = extract_buttons(
            message.caption or ""
        )

    # -----------------------------------------------------
    # AUDIO
    # -----------------------------------------------------

    elif content_type == ContentType.AUDIO:

        draft["file_id"] = message.audio.file_id
        draft["caption"] = message.caption or ""
        draft["buttons"] = extract_buttons(
            message.caption or ""
        )

    # -----------------------------------------------------
    # VOICE
    # -----------------------------------------------------

    elif content_type == ContentType.VOICE:

        draft["file_id"] = message.voice.file_id
        draft["caption"] = message.caption or ""
        draft["buttons"] = extract_buttons(
            message.caption or ""
        )

    # -----------------------------------------------------
    # ANIMATION / GIF
    # -----------------------------------------------------

    elif content_type == ContentType.ANIMATION:

        draft["file_id"] = message.animation.file_id
        draft["caption"] = message.caption or ""
        draft["buttons"] = extract_buttons(
            message.caption or ""
        )

    else:
        return None

    state_data["draft"] = draft

    return draft


# =========================================================
# PREVIEW TEXT
# =========================================================

def preview_info(draft: dict) -> str:

    buttons = draft.get("buttons", [])

    if buttons:
        button_text = "\n".join(
            f"• {escape(label)} → {escape(url)}"
            for label, url in buttons
        )

        button_section = (
            "\n\n🔘 <b>الأزرار المكتشفة:</b>\n"
            + button_text
        )

    else:
        button_section = (
            "\n\n🔘 <b>الأزرار:</b> لا توجد روابط أو حسابات مكتشفة."
        )

    return (
        "👀 <b>معاينة المنشور</b>\n\n"
        "سيتم نشر المحتوى كما يظهر أعلاه."
        + button_section
        + "\n\n"
        "اختر الإجراء:"
    )


# =========================================================
# START
# =========================================================

@dp.message(CommandStart())
async def start_handler(
    message: Message,
    state: FSMContext,
):

    if not is_admin(message.from_user.id):
        await message.answer(
            "⛔ <b>غير مصرح لك باستخدام هذا البوت.</b>"
        )
        return

    await state.clear()

    await message.answer(
        "🚀 <b>Telegram Publisher</b>\n\n"
        "مرحبًا بك في لوحة نشر القناة.\n\n"
        "يمكنك إنشاء منشورات تحتوي على:\n"
        "📝 نص\n"
        "🖼️ صور\n"
        "🎥 فيديو\n"
        "📎 ملفات\n"
        "🎵 صوت\n"
        "🎤 Voice\n"
        "🔗 روابط وأسماء مستخدمين\n\n"
        "سيتم اكتشاف الروابط والحسابات تلقائيًا "
        "وتحويلها إلى أزرار أسفل المنشور.",
        reply_markup=main_menu(),
    )


# =========================================================
# CREATE POST
# =========================================================

@dp.callback_query(F.data == "create_post")
async def create_post_handler(
    callback: CallbackQuery,
    state: FSMContext,
):

    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ غير مصرح", show_alert=True)
        return

    await state.set_state(PostState.waiting_for_post)

    await callback.message.edit_text(
        "➕ <b>إنشاء منشور جديد</b>\n\n"
        "أرسل الآن المنشور الذي تريد نشره.\n\n"
        "يمكن أن يكون:\n"
        "📝 نص فقط\n"
        "🖼️ صورة + نص\n"
        "🎥 فيديو + نص\n"
        "📎 ملف + نص\n"
        "🎵 صوت + نص\n"
        "🎤 Voice + نص\n"
        "🎞️ GIF + نص\n\n"
        "💡 <b>نصيحة:</b>\n"
        "ضع أي رابط أو @username داخل النص، "
        "وسأحوّله تلقائيًا إلى زر أسفل المنشور.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🏠 الرئيسية",
                        callback_data="back_home",
                    )
                ]
            ]
        ),
    )

    await callback.answer()


# =========================================================
# RECEIVE POST
# =========================================================

@dp.message(PostState.waiting_for_post)
async def receive_post_handler(
    message: Message,
    state: FSMContext,
):

    if not is_admin(message.from_user.id):
        return

    supported_types = {
        ContentType.TEXT,
        ContentType.PHOTO,
        ContentType.VIDEO,
        ContentType.DOCUMENT,
        ContentType.AUDIO,
        ContentType.VOICE,
        ContentType.ANIMATION,
    }

    if message.content_type not in supported_types:

        await message.answer(
            "⚠️ نوع المحتوى هذا غير مدعوم حاليًا.\n\n"
            "أرسل نصًا أو صورة أو فيديو أو ملفًا أو صوتًا."
        )
        return

    data = await state.get_data()

    draft = save_draft(
        data,
        message,
    )

    if not draft:
        await message.answer(
            "❌ حدث خطأ أثناء تجهيز المنشور."
        )
        return

    await state.update_data(draft=draft)

    # -----------------------------------------------------
    # Send preview content
    # -----------------------------------------------------

    keyboard = build_post_keyboard(
        draft["buttons"]
    )

    content_type = draft["content_type"]

    if content_type == ContentType.TEXT:

        await message.answer(
            draft["text"],
            reply_markup=keyboard,
        )

    elif content_type == ContentType.PHOTO:

        await message.answer_photo(
            photo=draft["file_id"],
            caption=draft["caption"] or None,
            reply_markup=keyboard,
        )

    elif content_type == ContentType.VIDEO:

        await message.answer_video(
            video=draft["file_id"],
            caption=draft["caption"] or None,
            reply_markup=keyboard,
        )

    elif content_type == ContentType.DOCUMENT:

        await message.answer_document(
            document=draft["file_id"],
            caption=draft["caption"] or None,
            reply_markup=keyboard,
        )

    elif content_type == ContentType.AUDIO:

        await message.answer_audio(
            audio=draft["file_id"],
            caption=draft["caption"] or None,
            reply_markup=keyboard,
        )

    elif content_type == ContentType.VOICE:

        await message.answer_voice(
            voice=draft["file_id"],
            caption=draft["caption"] or None,
            reply_markup=keyboard,
        )

    elif content_type == ContentType.ANIMATION:

        await message.answer_animation(
            animation=draft["file_id"],
            caption=draft["caption"] or None,
            reply_markup=keyboard,
        )

    # -----------------------------------------------------
    # Action panel
    # -----------------------------------------------------

    await message.answer(
        preview_info(draft),
        reply_markup=post_actions(),
    )


# =========================================================
# PUBLISH
# =========================================================

@dp.callback_query(F.data == "publish_post")
async def publish_handler(
    callback: CallbackQuery,
    state: FSMContext,
):

    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ غير مصرح",
            show_alert=True,
        )
        return

    data = await state.get_data()
    draft = data.get("draft")

    if not draft:
        await callback.answer(
            "⚠️ لا يوجد منشور جاهز للنشر.",
            show_alert=True,
        )
        return

    try:

        keyboard = build_post_keyboard(
            draft["buttons"]
        )

        content_type = draft["content_type"]

        # -------------------------------------------------
        # TEXT
        # -------------------------------------------------

        if content_type == ContentType.TEXT:

            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=draft["text"],
                reply_markup=keyboard,
            )

        # -------------------------------------------------
        # PHOTO
        # -------------------------------------------------

        elif content_type == ContentType.PHOTO:

            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=draft["file_id"],
                caption=draft["caption"] or None,
                reply_markup=keyboard,
            )

        # -------------------------------------------------
        # VIDEO
        # -------------------------------------------------

        elif content_type == ContentType.VIDEO:

            await bot.send_video(
                chat_id=CHANNEL_ID,
                video=draft["file_id"],
                caption=draft["caption"] or None,
                reply_markup=keyboard,
            )

        # -------------------------------------------------
        # DOCUMENT
        # -------------------------------------------------

        elif content_type == ContentType.DOCUMENT:

            await bot.send_document(
                chat_id=CHANNEL_ID,
                document=draft["file_id"],
                caption=draft["caption"] or None,
                reply_markup=keyboard,
            )

        # -------------------------------------------------
        # AUDIO
        # -------------------------------------------------

        elif content_type == ContentType.AUDIO:

            await bot.send_audio(
                chat_id=CHANNEL_ID,
                audio=draft["file_id"],
                caption=draft["caption"] or None,
                reply_markup=keyboard,
            )

        # -------------------------------------------------
        # VOICE
        # -------------------------------------------------

        elif content_type == ContentType.VOICE:

            await bot.send_voice(
                chat_id=CHANNEL_ID,
                voice=draft["file_id"],
                caption=draft["caption"] or None,
                reply_markup=keyboard,
            )

        # -------------------------------------------------
        # ANIMATION
        # -------------------------------------------------

        elif content_type == ContentType.ANIMATION:

            await bot.send_animation(
                chat_id=CHANNEL_ID,
                animation=draft["file_id"],
                caption=draft["caption"] or None,
                reply_markup=keyboard,
            )

        await state.clear()

        await callback.message.edit_text(
            "✅ <b>تم نشر المنشور بنجاح!</b>\n\n"
            f"📢 القناة: <code>{escape(str(CHANNEL_ID))}</code>\n\n"
            "يمكنك الآن إنشاء منشور جديد.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="➕ منشور جديد",
                            callback_data="create_post",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="🏠 الرئيسية",
                            callback_data="back_home",
                        )
                    ],
                ]
            ),
        )

        await callback.answer("🚀 تم النشر!")

    except Exception as e:

        logger.exception(
            "Publishing error: %s",
            e,
        )

        await callback.answer(
            "❌ فشل النشر.",
            show_alert=True,
        )

        await callback.message.answer(
            "❌ <b>حدث خطأ أثناء النشر.</b>\n\n"
            "تأكد أن البوت ما زال مشرفًا في القناة "
            "ولديه صلاحية نشر الرسائل.\n\n"
            f"<code>{escape(str(e))}</code>"
        )


# =========================================================
# EDIT POST
# =========================================================

@dp.callback_query(F.data == "edit_post")
async def edit_post_handler(
    callback: CallbackQuery,
    state: FSMContext,
):

    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ غير مصرح",
            show_alert=True,
        )
        return

    await state.set_state(PostState.waiting_for_post)

    await callback.message.answer(
        "✏️ <b>تعديل المنشور</b>\n\n"
        "أرسل المنشور الجديد بالكامل الآن.\n\n"
        "يمكنك تغيير النص أو الصورة أو الفيديو "
        "أو إضافة/حذف الروابط."
    )

    await callback.answer()


# =========================================================
# CANCEL
# =========================================================

@dp.callback_query(F.data == "cancel_post")
async def cancel_post_handler(
    callback: CallbackQuery,
    state: FSMContext,
):

    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ غير مصرح",
            show_alert=True,
        )
        return

    await state.clear()

    await callback.message.edit_text(
        "❌ <b>تم إلغاء المنشور.</b>\n\n"
        "لم يتم نشر أي شيء.",
        reply_markup=main_menu(),
    )

    await callback.answer("تم الإلغاء")


# =========================================================
# HOME
# =========================================================

@dp.callback_query(F.data == "back_home")
async def back_home_handler(
    callback: CallbackQuery,
    state: FSMContext,
):

    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ غير مصرح",
            show_alert=True,
        )
        return

    await state.clear()

    await callback.message.edit_text(
        "🚀 <b>Telegram Publisher</b>\n\n"
        "لوحة التحكم الرئيسية.",
        reply_markup=main_menu(),
    )

    await callback.answer()


# =========================================================
# MY POSTS
# =========================================================

@dp.callback_query(F.data == "my_posts")
async def my_posts_handler(
    callback: CallbackQuery,
):

    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ غير مصرح",
            show_alert=True,
        )
        return

    await callback.answer()

    await callback.message.edit_text(
        "📋 <b>منشوراتي</b>\n\n"
        "هذه الصفحة سنضيف لها لاحقًا حفظ المنشورات "
        "وإعادة استخدامها وتعديلها.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🏠 الرئيسية",
                        callback_data="back_home",
                    )
                ]
            ]
        ),
    )


# =========================================================
# SCHEDULED
# =========================================================

@dp.callback_query(F.data == "scheduled")
async def scheduled_handler(
    callback: CallbackQuery,
):

    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ غير مصرح",
            show_alert=True,
        )
        return

    await callback.answer()

    await callback.message.edit_text(
        "⏰ <b>المنشورات المجدولة</b>\n\n"
        "ميزة الجدولة ستكون في المرحلة التالية.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🏠 الرئيسية",
                        callback_data="back_home",
                    )
                ]
            ]
        ),
    )


# =========================================================
# SETTINGS
# =========================================================

@dp.callback_query(F.data == "settings")
async def settings_handler(
    callback: CallbackQuery,
):

    if not is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ غير مصرح",
            show_alert=True,
        )
        return

    await callback.answer()

    await callback.message.edit_text(
        "⚙️ <b>الإعدادات</b>\n\n"
        f"📢 القناة الحالية:\n"
        f"<code>{escape(str(CHANNEL_ID))}</code>\n\n"
        "🔘 الروابط: تلقائية\n"
        "🔐 الوصول: المدير فقط\n"
        "🌐 الوضع: عربي",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🏠 الرئيسية",
                        callback_data="back_home",
                    )
                ]
            ]
        ),
    )


# =========================================================
# HEALTH SERVER FOR RENDER
# =========================================================

async def health_handler(request):
    return web.Response(
        text="Telegram Publisher Bot is running."
    )


async def start_health_server():

    app = web.Application()

    app.router.add_get("/", health_handler)
    app.router.add_get("/health", health_handler)

    runner = web.AppRunner(app)

    await runner.setup()

    site = web.TCPSite(
        runner,
        host="0.0.0.0",
        port=PORT,
    )

    await site.start()

    logger.info(
        "Health server running on port %s",
        PORT,
    )


# =========================================================
# MAIN
# =========================================================

async def main():

    logger.info("Bot is starting...")

    await start_health_server()

    me = await bot.get_me()

    logger.info(
        "Bot connected: @%s (id=%s)",
        me.username,
        me.id,
    )

    logger.info(
        "Channel: %s",
        CHANNEL_ID,
    )

    await dp.start_polling(
        bot,
        allowed_updates=dp.resolve_used_update_types(),
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:

        logger.info(
            "Bot stopped by user."
        )
```
