import asyncio
import json
import logging
import os
import secrets
from pathlib import Path
from urllib.parse import parse_qsl
import hashlib
import hmac

from aiohttp import web
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatMemberStatus
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
    FSInputFile,
)
from aiogram.exceptions import TelegramBadRequest

from database import (
    init_db,
    create_user,
    get_user,
    set_language,
    get_language,
    add_channel,
    get_channels,
    delete_channel,
    create_post,
    get_posts,
)


# =========================================================
# CONFIG
# =========================================================

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

WEB_APP_URL = os.getenv(
    "WEB_APP_URL",
    "https://telegrampublisherbot.onrender.com/"
)

PORT = int(os.getenv("PORT", "10000"))

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"
UPLOAD_DIR = BASE_DIR / "uploads"

UPLOAD_DIR.mkdir(exist_ok=True)


if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# =========================================================
# BOT
# =========================================================

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

dp = Dispatcher()


# =========================================================
# TRANSLATIONS
# =========================================================

TEXTS = {
    "ar": {
        "welcome_title": "⚡ <b>Telegram Publisher</b>",
        "welcome": (
            "مرحبًا بك في منصة النشر الاحترافية.\n\n"
            "يمكنك من خلالها إدارة قنواتك وإنشاء المنشورات "
            "ونشر الصور والفيديوهات والملفات والروابط."
        ),
        "choose_language": "🌐 اختر لغة البوت:",
        "language_saved": "✅ تم اختيار اللغة العربية.",
        "english_saved": "✅ English selected.",
        "open_panel": "⚡ فتح لوحة التحكم",
        "channels": "📢 قنواتي",
        "add_channel": "➕ إضافة قناة",
        "help": "ℹ️ المساعدة",
        "no_channels": (
            "ليس لديك أي قناة مرتبطة حتى الآن.\n\n"
            "استخدم /addchannel لإضافة قناة."
        ),
        "channel_list": "📢 <b>قنواتك:</b>\n\n",
        "add_channel_help": (
            "➕ <b>إضافة قناة</b>\n\n"
            "1. أضف البوت إلى قناتك كمسؤول.\n"
            "2. امنحه صلاحية نشر الرسائل.\n"
            "3. أرسل اسم القناة بهذا الشكل:\n\n"
            "<code>@yourchannel</code>"
        ),
        "channel_added": "✅ تم إضافة القناة بنجاح:\n<b>{}</b>",
        "channel_not_found": (
            "❌ لم أتمكن من الوصول إلى القناة.\n\n"
            "تأكد أن البوت موجود في القناة كمسؤول "
            "وأن اسم القناة صحيح."
        ),
        "not_admin": (
            "❌ البوت ليس لديه صلاحية الإدارة في هذه القناة."
        ),
        "channel_deleted": "🗑️ تم حذف القناة.",
        "help_text": (
            "ℹ️ <b>طريقة الاستخدام</b>\n\n"
            "• أضف قناتك باستخدام /addchannel\n"
            "• افتح لوحة التحكم\n"
            "• اختر القناة\n"
            "• اكتب المنشور\n"
            "• ارفع صورة أو فيديو أو ملف\n"
            "• أضف الروابط والأزرار\n"
            "• عاين المنشور\n"
            "• اضغط نشر 🚀"
        ),
        "language": "🌐 تغيير اللغة",
        "select_language": "اختر اللغة:",
    },

    "en": {
        "welcome_title": "⚡ <b>Telegram Publisher</b>",
        "welcome": (
            "Welcome to the professional publishing platform.\n\n"
            "Manage your channels, create posts and publish "
            "photos, videos, files and links."
        ),
        "choose_language": "🌐 Choose your language:",
        "language_saved": "✅ Arabic selected.",
        "english_saved": "✅ English selected.",
        "open_panel": "⚡ Open Dashboard",
        "channels": "📢 My Channels",
        "add_channel": "➕ Add Channel",
        "help": "ℹ️ Help",
        "no_channels": (
            "You don't have any connected channels yet.\n\n"
            "Use /addchannel to add a channel."
        ),
        "channel_list": "📢 <b>Your channels:</b>\n\n",
        "add_channel_help": (
            "➕ <b>Add Channel</b>\n\n"
            "1. Add the bot to your channel as an administrator.\n"
            "2. Give it permission to post messages.\n"
            "3. Send the channel username like this:\n\n"
            "<code>@yourchannel</code>"
        ),
        "channel_added": "✅ Channel added successfully:\n<b>{}</b>",
        "channel_not_found": (
            "❌ I couldn't access this channel.\n\n"
            "Make sure the bot is an administrator "
            "and the username is correct."
        ),
        "not_admin": (
            "❌ The bot does not have administrator permissions "
            "in this channel."
        ),
        "channel_deleted": "🗑️ Channel deleted.",
        "help_text": (
            "ℹ️ <b>How to use</b>\n\n"
            "• Add your channel with /addchannel\n"
            "• Open the dashboard\n"
            "• Choose your channel\n"
            "• Write your post\n"
            "• Upload photo, video or file\n"
            "• Add links and buttons\n"
            "• Preview your post\n"
            "• Press Publish 🚀"
        ),
        "language": "🌐 Change language",
        "select_language": "Choose language:",
    }
}


def t(language, key):
    language = language if language in TEXTS else "ar"
    return TEXTS[language].get(key, key)


# =========================================================
# LANGUAGE KEYBOARD
# =========================================================

def language_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🇸🇦 العربية",
                    callback_data="lang_ar"
                ),
                InlineKeyboardButton(
                    text="🇬🇧 English",
                    callback_data="lang_en"
                )
            ]
        ]
    )


# =========================================================
# MAIN KEYBOARD
# =========================================================

def main_keyboard(language):
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=t(language, "open_panel"),
                    web_app=WebAppInfo(url=WEB_APP_URL)
                )
            ],
            [
                KeyboardButton(text=t(language, "channels")),
                KeyboardButton(text=t(language, "add_channel"))
            ],
            [
                KeyboardButton(text=t(language, "help")),
                KeyboardButton(text=t(language, "language"))
            ]
        ],
        resize_keyboard=True,
        is_persistent=True
    )


# =========================================================
# START
# =========================================================

@dp.message(CommandStart())
async def start_handler(message: Message):

    user = get_user(message.from_user.id)

    if not user:
        create_user(
            message.from_user.id,
            "ar"
        )

        await message.answer(
            "🌐 <b>Choose your language / اختر اللغة</b>",
            reply_markup=language_keyboard()
        )

        return

    language = user["language"]

    await message.answer(
        f"{t(language, 'welcome_title')}\n\n"
        f"{t(language, 'welcome')}",
        reply_markup=main_keyboard(language)
    )


# =========================================================
# LANGUAGE CALLBACK
# =========================================================

@dp.callback_query(F.data.startswith("lang_"))
async def language_callback(callback: CallbackQuery):

    language = callback.data.replace("lang_", "")

    if language not in ("ar", "en"):
        await callback.answer()
        return

    set_language(
        callback.from_user.id,
        language
    )

    await callback.message.delete()

    if language == "ar":
        text = (
            f"{t(language, 'welcome_title')}\n\n"
            f"{t(language, 'language_saved')}\n\n"
            f"{t(language, 'welcome')}"
        )
    else:
        text = (
            f"{t(language, 'welcome_title')}\n\n"
            f"{t(language, 'english_saved')}\n\n"
            f"{t(language, 'welcome')}"
        )

    await callback.message.answer(
        text,
        reply_markup=main_keyboard(language)
    )

    await callback.answer()


# =========================================================
# LANGUAGE BUTTON
# =========================================================

@dp.message(F.text.in_(["🌐 تغيير اللغة", "🌐 Change language"]))
async def change_language(message: Message):

    await message.answer(
        "🌐 اختر اللغة / Choose language:",
        reply_markup=language_keyboard()
    )


# =========================================================
# HELP
# =========================================================

@dp.message(F.text.in_(["ℹ️ المساعدة", "ℹ️ Help"]))
async def help_handler(message: Message):

    language = get_language(
        message.from_user.id
    )

    await message.answer(
        t(language, "help_text")
    )


# =========================================================
# ADD CHANNEL
# =========================================================

@dp.message(Command("addchannel"))
@dp.message(F.text.in_(["➕ إضافة قناة", "➕ Add Channel"]))
async def add_channel_handler(message: Message):

    language = get_language(
        message.from_user.id
    )

    await message.answer(
        t(language, "add_channel_help")
    )


# =========================================================
# RECEIVE CHANNEL USERNAME
# =========================================================

@dp.message(F.text.startswith("@"))
async def channel_username_handler(message: Message):

    username = message.text.strip()

    if " " in username or len(username) < 2:
        return

    language = get_language(
        message.from_user.id
    )

    try:

        chat = await bot.get_chat(username)

        if chat.type != "channel":

            await message.answer(
                "❌ هذا ليس Channel."
            )

            return

        me = await bot.get_me()

        member = await bot.get_chat_member(
            chat_id=chat.id,
            user_id=me.id
        )

        if member.status not in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        ):

            await message.answer(
                t(language, "not_admin")
            )

            return

        add_channel(
            telegram_id=message.from_user.id,
            channel_id=str(chat.id),
            username=(
                f"@{chat.username}"
                if chat.username
                else username
            ),
            title=chat.title or ""
        )

        await message.answer(
            t(language, "channel_added").format(
                chat.title or username
            ),
            reply_markup=main_keyboard(language)
        )

    except Exception as e:

        logger.exception(
            "Channel verification failed: %s",
            e
        )

        await message.answer(
            t(language, "channel_not_found")
        )


# =========================================================
# MY CHANNELS
# =========================================================

@dp.message(F.text.in_(["📢 قنواتي", "📢 My Channels"]))
async def my_channels_handler(message: Message):

    language = get_language(
        message.from_user.id
    )

    channels = get_channels(
        message.from_user.id
    )

    if not channels:

        await message.answer(
            t(language, "no_channels")
        )

        return

    text = t(language, "channel_list")

    buttons = []

    for channel in channels:

        username = channel["username"]

        if not username:
            username = channel["title"]

        text += f"• <b>{username}</b>\n"

        buttons.append([
            InlineKeyboardButton(
                text=f"🗑️ {username}",
                callback_data=(
                    f"delete_channel:{channel['channel_id']}"
                )
            )
        ])

    await message.answer(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=buttons
        )
    )


# =========================================================
# DELETE CHANNEL
# =========================================================

@dp.callback_query(F.data.startswith("delete_channel:"))
async def delete_channel_callback(
    callback: CallbackQuery
):

    channel_id = callback.data.split(
        "delete_channel:",
        1
    )[1]

    delete_channel(
        callback.from_user.id,
        channel_id
    )

    language = get_language(
        callback.from_user.id
    )

    await callback.message.edit_text(
        t(language, "channel_deleted")
    )

    await callback.answer()


# =========================================================
# TELEGRAM WEB APP AUTH
# =========================================================

def validate_init_data(init_data: str):

    if not init_data:
        return None

    try:

        data = dict(
            parse_qsl(
                init_data,
                keep_blank_values=True
            )
        )

        received_hash = data.pop(
            "hash",
            None
        )

        if not received_hash:
            return None

        data_check_string = "\n".join(
            f"{key}={data[key]}"
            for key in sorted(data)
        )

        secret_key = hmac.new(
            b"WebAppData",
            BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()

        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(
            calculated_hash,
            received_hash
        ):
            return None

        user_data = json.loads(
            data.get("user", "{}")
        )

        return user_data

    except Exception:

        logger.exception(
            "Mini App authentication failed"
        )

        return None


# =========================================================
# WEB API AUTH
# =========================================================

def authenticate_request(request):

    init_data = request.headers.get(
        "X-Telegram-Init-Data",
        ""
    )

    return validate_init_data(
        init_data
    )


# =========================================================
# API: CHANNELS
# =========================================================

async def api_channels(request):

    user = authenticate_request(
        request
    )

    if not user:
        return web.json_response(
            {
                "ok": False,
                "error": "Unauthorized"
            },
            status=401
        )

    telegram_id = int(
        user["id"]
    )

    channels = get_channels(
        telegram_id
    )

    result = []

    for channel in channels:

        result.append({
            "id": channel["channel_id"],
            "username": channel["username"],
            "title": channel["title"]
        })

    return web.json_response({
        "ok": True,
        "channels": result
    })


# =========================================================
# API: UPLOAD
# =========================================================

async def api_upload(request):

    user = authenticate_request(
        request
    )

    if not user:
        return web.json_response(
            {
                "ok": False,
                "error": "Unauthorized"
            },
            status=401
        )

    telegram_id = int(
        user["id"]
    )

    reader = await request.multipart()

    field = await reader.next()

    if not field:
        return web.json_response(
            {
                "ok": False,
                "error": "No file"
            },
            status=400
        )

    original_name = field.filename or "file"

    extension = Path(
        original_name
    ).suffix.lower()

    allowed = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".gif",
        ".mp4",
        ".mov",
        ".mkv",
        ".pdf",
        ".zip",
        ".rar",
        ".txt",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".mp3",
        ".m4a",
        ".ogg",
        ".wav"
    }

    if extension not in allowed:

        return web.json_response(
            {
                "ok": False,
                "error": "Unsupported file type"
            },
            status=400
        )

    random_name = (
        secrets.token_hex(16)
        + extension
    )

    file_path = UPLOAD_DIR / random_name

    size = 0
    max_size = 50 * 1024 * 1024

    with open(file_path, "wb") as f:

        while True:

            chunk = await field.read_chunk(
                size=1024 * 1024
            )

            if not chunk:
                break

            size += len(chunk)

            if size > max_size:

                try:
                    file_path.unlink()
                except Exception:
                    pass

                return web.json_response(
                    {
                        "ok": False,
                        "error": "File too large. Maximum 50 MB."
                    },
                    status=413
                )

            f.write(chunk)

    content_type = field.headers.get(
        "Content-Type",
        ""
    )

    if content_type.startswith("image/"):
        media_type = "photo"

    elif content_type.startswith("video/"):
        media_type = "video"

    elif content_type.startswith("audio/"):
        media_type = "audio"

    else:
        media_type = "document"

    return web.json_response({
        "ok": True,
        "telegram_id": telegram_id,
        "filename": original_name,
        "path": str(file_path),
        "media_type": media_type,
        "size": size
    })


# =========================================================
# BUILD INLINE BUTTONS
# =========================================================

def build_inline_keyboard(buttons):

    if not buttons:
        return None

    keyboard = []

    for button in buttons:

        text = button.get("text")

        url = button.get("url")

        if not text or not url:
            continue

        keyboard.append([
            InlineKeyboardButton(
                text=text[:64],
                url=url
            )
        ])

    if not keyboard:
        return None

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )


# =========================================================
# AUTO LINK DETECTION
# =========================================================

def normalize_buttons(buttons):

    if not isinstance(buttons, list):
        return []

    result = []

    for button in buttons:

        if not isinstance(button, dict):
            continue

        text = str(
            button.get("text", "")
        ).strip()

        url = str(
            button.get("url", "")
        ).strip()

        if not text or not url:
            continue

        if not (
            url.startswith("http://")
            or url.startswith("https://")
            or url.startswith("tg://")
        ):
            continue

        result.append({
            "text": text,
            "url": url
        })

    return result


# =========================================================
# PUBLISH POST
# =========================================================

async def publish_post(
    telegram_id,
    channel_id,
    text,
    media_type,
    media_path,
    buttons
):

    channel = get_channel(
        telegram_id,
        str(channel_id)
    )

    if not channel:
        raise RuntimeError(
            "Channel is not connected to this user"
        )

    keyboard = build_inline_keyboard(
        buttons
    )

    target = channel["channel_id"]

    text = text or ""

    if media_type == "photo":

        await bot.send_photo(
            chat_id=target,
            photo=FSInputFile(
                media_path
            ),
            caption=text[:1024] if text else None,
            reply_markup=keyboard
        )

    elif media_type == "video":

        await bot.send_video(
            chat_id=target,
            video=FSInputFile(
                media_path
            ),
            caption=text[:1024] if text else None,
            reply_markup=keyboard
        )

    elif media_type == "audio":

        await bot.send_audio(
            chat_id=target,
            audio=FSInputFile(
                media_path
            ),
            caption=text[:1024] if text else None,
            reply_markup=keyboard
        )

    else:

        if media_type == "document":

            await bot.send_document(
                chat_id=target,
                document=FSInputFile(
                    media_path
                ),
                caption=text[:1024] if text else None,
                reply_markup=keyboard
            )

        else:

            await bot.send_message(
                chat_id=target,
                text=text,
                reply_markup=keyboard
            )


# =========================================================
# API: PUBLISH
# =========================================================

async def api_publish(request):

    user = authenticate_request(
        request
    )

    if not user:

        return web.json_response(
            {
                "ok": False,
                "error": "Unauthorized"
            },
            status=401
        )

    telegram_id = int(
        user["id"]
    )

    try:

        data = await request.json()

    except Exception:

        return web.json_response(
            {
                "ok": False,
                "error": "Invalid JSON"
            },
            status=400
        )

    channel_id = str(
        data.get("channel_id", "")
    )

    text = str(
        data.get("text", "")
    ).strip()

    media_type = data.get(
        "media_type"
    )

    media_path = data.get(
        "media_path"
    )

    buttons = normalize_buttons(
        data.get("buttons", [])
    )

    if not channel_id:

        return web.json_response(
            {
                "ok": False,
                "error": "Channel is required"
            },
            status=400
        )

    if not text and not media_path:

        return web.json_response(
            {
                "ok": False,
                "error": "Post is empty"
            },
            status=400
        )

    if media_path:

        path = Path(
            media_path
        ).resolve()

        upload_root = UPLOAD_DIR.resolve()

        if upload_root not in path.parents:

            return web.json_response(
                {
                    "ok": False,
                    "error": "Invalid media"
                },
                status=400
            )

        if not path.exists():

            return web.json_response(
                {
                    "ok": False,
                    "error": "Media file not found"
                },
                status=400
            )

        media_path = str(path)

    try:

        await publish_post(
            telegram_id=telegram_id,
            channel_id=channel_id,
            text=text,
            media_type=media_type,
            media_path=media_path,
            buttons=buttons
        )

        post_id = create_post(
            telegram_id=telegram_id,
            channel_id=channel_id,
            text=text,
            media_type=media_type,
            media_path=media_path,
            buttons=json.dumps(
                buttons,
                ensure_ascii=False
            ),
            status="published"
        )

        if media_path:

            try:
                Path(
                    media_path
                ).unlink()
            except Exception:
                pass

        return web.json_response({
            "ok": True,
            "post_id": post_id
        })

    except Exception as e:

        logger.exception(
            "Publishing failed"
        )

        return web.json_response(
            {
                "ok": False,
                "error": str(e)
            },
            status=500
        )


# =========================================================
# API: POSTS
# =========================================================

async def api_posts(request):

    user = authenticate_request(
        request
    )

    if not user:

        return web.json_response(
            {
                "ok": False,
                "error": "Unauthorized"
            },
            status=401
        )

    telegram_id = int(
        user["id"]
    )

    posts = get_posts(
        telegram_id
    )

    result = []

    for post in posts:

        result.append({
            "id": post["id"],
            "channel_id": post["channel_id"],
            "text": post["text"],
            "media_type": post["media_type"],
            "status": post["status"],
            "created_at": post["created_at"]
        })

    return web.json_response({
        "ok": True,
        "posts": result
    })


# =========================================================
# WEB PAGE
# =========================================================

async def index_handler(request):

    return web.FileResponse(
        WEB_DIR / "index.html"
    )


async def health_handler(request):

    return web.json_response({
        "status": "ok",
        "service": "Telegram Publisher"
    })


# =========================================================
# WEB SERVER
# =========================================================

async def start_web_server():

    app = web.Application(
        client_max_size=60 * 1024 * 1024
    )

    app.router.add_get(
        "/",
        index_handler
    )

    app.router.add_get(
        "/health",
        health_handler
    )

    app.router.add_get(
        "/api/channels",
        api_channels
    )

    app.router.add_post(
        "/api/upload",
        api_upload
    )

    app.router.add_post(
        "/api/publish",
        api_publish
    )

    app.router.add_get(
        "/api/posts",
        api_posts
    )

    app.router.add_static(
        "/",
        WEB_DIR,
        show_index=False
    )

    runner = web.AppRunner(
        app
    )

    await runner.setup()

    site = web.TCPSite(
        runner,
        host="0.0.0.0",
        port=PORT
    )

    await site.start()

    logger.info(
        "Web server running on port %s",
        PORT
    )

    return runner


# =========================================================
# STARTUP
# =========================================================

async def main():

    init_db()

    await start_web_server()

    logger.info(
        "Telegram Publisher Bot started"
    )

    await dp.start_polling(
        bot
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    asyncio.run(main())
