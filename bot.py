# import asyncio
# import json
# import logging
# import os

# from pathlib import Path

# from dotenv import load_dotenv

# from aiogram import Bot, Dispatcher, F
# from aiogram.client.default import DefaultBotProperties
# from aiogram.enums import ParseMode, ChatMemberStatus
# from aiogram.filters import Command, CommandStart
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
# from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.types import (
#     Message,
#     CallbackQuery,
#     InlineKeyboardMarkup,
#     InlineKeyboardButton,
#     ReplyKeyboardMarkup,
#     KeyboardButton,
#     FSInputFile,
# )
# from aiogram.exceptions import TelegramBadRequest

# from database import (
#     init_db,
#     create_user,
#     get_user,
#     set_language,
#     get_language,
#     touch_user,
#     add_channel,
#     get_channels,
#     get_channel,
#     delete_channel,
#     create_post,
#     get_posts,
#     get_post,
#     update_post_text,
#     get_posts_count,
#     get_channels_count,
#     get_bot_stats,
#     get_all_users,
#     log_stat,
# )


# # =========================================================
# # CONFIG
# # =========================================================

# load_dotenv()

# BOT_TOKEN = os.getenv("BOT_TOKEN")
# ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# BASE_DIR = Path(__file__).resolve().parent
# UPLOAD_DIR = BASE_DIR / "uploads"
# UPLOAD_DIR.mkdir(exist_ok=True)

# if not BOT_TOKEN:
#     raise RuntimeError("BOT_TOKEN is missing")


# # =========================================================
# # LOGGING
# # =========================================================

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s | %(levelname)s | %(message)s"
# )

# logger = logging.getLogger(__name__)


# # =========================================================
# # BOT
# # =========================================================

# bot = Bot(
#     token=BOT_TOKEN,
#     default=DefaultBotProperties(parse_mode=ParseMode.HTML)
# )

# storage = MemoryStorage()
# dp = Dispatcher(storage=storage)


# # =========================================================
# # FSM STATES
# # =========================================================

# class PostFlow(StatesGroup):
#     choosing_channel = State()
#     waiting_text = State()
#     waiting_media = State()
#     waiting_buttons = State()
#     previewing = State()


# class ChannelFlow(StatesGroup):
#     waiting_username = State()


# class EditFlow(StatesGroup):
#     waiting_new_text = State()


# class ButtonFlow(StatesGroup):
#     waiting_text = State()
#     waiting_url = State()


# # =========================================================
# # TRANSLATIONS
# # =========================================================

# TEXTS = {
#     "ar": {
#         "main_title": "⚡ <b>Telegram Publisher</b>",
#         "welcome": (
#             "أهلاً بك 👋\n\n"
#             "أنشئ منشوراتك وانشرها لقنواتك بسهولة."
#         ),
#         "stats_line": (
#             "📢 القنوات: <b>{channels}</b>\n"
#             "📝 المنشورات: <b>{posts}</b>"
#         ),
#         "choose_language": "🌐 اختر لغة البوت:",
#         "language_saved_ar": "✅ تم اختيار اللغة العربية.",
#         "language_saved_en": "✅ English selected.",

#         "btn_create_post": "✨ إنشاء منشور",
#         "btn_my_channels": "📢 قنواتي",
#         "btn_my_posts": "📋 منشوراتي",
#         "btn_stats": "📊 الإحصائيات",
#         "btn_language": "🌐 اللغة",
#         "btn_home": "🏠 الرئيسية",
#         "btn_help": "ℹ️ المساعدة",
#         "btn_add_channel": "➕ إضافة قناة",
#         "btn_back": "◀️ رجوع",
#         "btn_cancel": "❌ إلغاء",
#         "btn_skip": "⏭️ تخطي",
#         "btn_done": "✅ تم",
#         "btn_publish": "🚀 نشر",
#         "btn_preview": "👀 معاينة",
#         "btn_edit": "✏️ تعديل النص",
#         "btn_delete": "🗑️ حذف",

#         "no_channels": (
#             "ليس لديك أي قناة.\n\n"
#             "استخدم /addchannel لإضافة قناة."
#         ),
#         "channel_list": "📢 <b>قنواتك:</b>\n\n",
#         "channel_added": "✅ تمت إضافة القناة:\n<b>{}</b>",
#         "channel_add_help": (
#             "➕ <b>إضافة قناة</b>\n\n"
#             "1. أضف البوت إلى قناتك كمسؤول.\n"
#             "2. امنحه صلاحية نشر الرسائل.\n"
#             "3. أرسل Username القناة:\n\n"
#             "<code>@yourchannel</code>"
#         ),
#         "channel_not_found": (
#             "❌ لم أتمكن من الوصول إلى القناة.\n\n"
#             "تأكد أن البوت مسؤول وأن Username صحيح."
#         ),
#         "not_admin": "❌ البوت ليس مسؤولًا في هذه القناة.",
#         "channel_deleted": "🗑️ تم حذف القناة.",
#         "confirm_delete_channel": "هل تريد حذف القناة <b>{}</b>؟",
#         "delete_confirm_yes": "🗑️ نعم، احذف",
#         "delete_confirm_no": "❌ لا",

#         "help_text": (
#             "ℹ️ <b>طريقة الاستخدام</b>\n\n"
#             "• أضف قناتك من «قنواتي»\n"
#             "• أنشئ منشوراً من «إنشاء منشور»\n"
#             "• اختر قناة → اكتب النص → أضف وسائط (اختياري)\n"
#             "• معاينة ثم نشر 🚀"
#         ),

#         "choose_channel": "📢 <b>اختر القناة:</b>",
#         "no_channel_available": "❌ لا توجد قنوات. أضف قناة أولاً.",
#         "send_post_text": (
#             "✍️ أرسل <b>نص المنشور</b> الآن.\n\n"
#             "يمكنك إرسال حتى 4096 حرف."
#         ),
#         "text_too_long": "⚠️ النص طويل جداً (الحد 4096).",
#         "text_empty": "⚠️ النص فارغ.",
#         "send_media_or_skip": (
#             "📎 أرسل <b>صورة/فيديو/ملف</b> أو اضغط «تخطي»."
#         ),
#         "media_received": "✅ تم استلام الوسائط.",
#         "buttons_info": (
#             "🔘 <b>أزرار المنشور</b>\n\n"
#             "يمكنك إضافة أزرار (نص + رابط) أو تخطي.\n\n"
#             "عند الانتهاء اضغط «تم»."
#         ),
#         "buttons_choose": "هل تريد إضافة أزرار؟",
#         "btn_add_button": "➕ إضافة زر",
#         "button_text_prompt": "أرسل نص الزر:",
#         "button_url_prompt": "أرسل رابط الزر (يبدأ بـ https://):",
#         "button_invalid_url": "⚠️ رابط غير صحيح. أرسل رابطاً يبدأ بـ https://",
#         "button_added": "✅ تم إضافة الزر.",
#         "preview_title": "👀 <b>معاينة المنشور</b>",
#         "preview_channel": "📢 القناة: <b>{}</b>",
#         "preview_text": "📝 النص:\n{}",
#         "preview_media": "📎 وسائط: {}",
#         "preview_buttons": "🔘 أزرار: {}",
#         "publish_confirm": (
#             "هل أنت متأكد من النشر؟\n\n"
#             "اضغط «🚀 نشر» للنشر في القناة."
#         ),
#         "published": "✅ تم النشر في القناة بنجاح 🚀",
#         "publish_failed": "❌ فشل النشر: {}",
#         "cancelled": "❌ تم الإلغاء.",

#         "no_posts": "📭 لا توجد منشورات.",
#         "posts_list": "📋 <b>منشوراتك:</b>\n\n",
#         "post_item": (
#             "#{id} · {media}\n"
#             "{text}"
#         ),
#         "post_view": (
#             "📋 <b>منشور #{id}</b>\n\n"
#             "📝 النص:\n{text}\n\n"
#             "{media_line}"
#             "🕐 {date}"
#         ),
#         "edit_prompt": "✏️ أرسل النص الجديد:",
#         "edit_success": "✅ تم تعديل المنشور.",
#         "edit_failed": "❌ فشل التعديل: {}",
#         "edit_no_channel": "❌ القناة غير مرتبطة.",

#         "stats_title": "📊 <b>إحصائياتك</b>",
#         "stats_body": (
#             "📢 القنوات: <b>{channels}</b>\n"
#             "📝 المنشورات: <b>{posts}</b>"
#         ),

#         "admin_title": "👑 <b>لوحة تحكم الأدمن</b>",
#         "admin_stats": (
#             "👥 <b>إجمالي المستخدمين:</b> {total}\n"
#             "🟢 <b>نشطاء 24 ساعة:</b> {a24}\n"
#             "🟢 <b>نشطاء 7 أيام:</b> {a7}\n\n"
#             "📢 <b>إجمالي القنوات:</b> {channels}\n"
#             "📝 <b>إجمالي المنشورات:</b> {posts}"
#         ),
#         "admin_users": "👥 <b>آخر المستخدمين:</b>\n\n",
#         "admin_user_row": (
#             "• <code>{tid}</code>\n"
#             "  🌐 {lang} · 🕐 {date}\n"
#         ),
#         "admin_no_access": "❌ هذا الأمر للمشرف فقط.",

#         "loading": "⏳ ...",
#     },

#     "en": {
#         "main_title": "⚡ <b>Telegram Publisher</b>",
#         "welcome": (
#             "Welcome 👋\n\n"
#             "Create and publish posts to your channels easily."
#         ),
#         "stats_line": (
#             "📢 Channels: <b>{channels}</b>\n"
#             "📝 Posts: <b>{posts}</b>"
#         ),
#         "choose_language": "🌐 Choose bot language:",
#         "language_saved_ar": "✅ Arabic selected.",
#         "language_saved_en": "✅ English selected.",

#         "btn_create_post": "✨ Create Post",
#         "btn_my_channels": "📢 My Channels",
#         "btn_my_posts": "📋 My Posts",
#         "btn_stats": "📊 Statistics",
#         "btn_language": "🌐 Language",
#         "btn_home": "🏠 Home",
#         "btn_help": "ℹ️ Help",
#         "btn_add_channel": "➕ Add Channel",
#         "btn_back": "◀️ Back",
#         "btn_cancel": "❌ Cancel",
#         "btn_skip": "⏭️ Skip",
#         "btn_done": "✅ Done",
#         "btn_publish": "🚀 Publish",
#         "btn_preview": "👀 Preview",
#         "btn_edit": "✏️ Edit Text",
#         "btn_delete": "🗑️ Delete",

#         "no_channels": (
#             "You don't have any channels.\n\n"
#             "Use /addchannel to add one."
#         ),
#         "channel_list": "📢 <b>Your channels:</b>\n\n",
#         "channel_added": "✅ Channel added:\n<b>{}</b>",
#         "channel_add_help": (
#             "➕ <b>Add Channel</b>\n\n"
#             "1. Add the bot as admin in your channel.\n"
#             "2. Give it permission to post messages.\n"
#             "3. Send the channel username:\n\n"
#             "<code>@yourchannel</code>"
#         ),
#         "channel_not_found": (
#             "❌ I couldn't access this channel.\n\n"
#             "Make sure the bot is an admin and the username is correct."
#         ),
#         "not_admin": "❌ The bot is not an admin in this channel.",
#         "channel_deleted": "🗑️ Channel deleted.",
#         "confirm_delete_channel": "Delete channel <b>{}</b>?",
#         "delete_confirm_yes": "🗑️ Yes, delete",
#         "delete_confirm_no": "❌ No",

#         "help_text": (
#             "ℹ️ <b>How to use</b>\n\n"
#             "• Add a channel from «My Channels»\n"
#             "• Create a post from «Create Post»\n"
#             "• Choose channel → write text → add media (optional)\n"
#             "• Preview then Publish 🚀"
#         ),

#         "choose_channel": "📢 <b>Choose a channel:</b>",
#         "no_channel_available": "❌ No channels. Add one first.",
#         "send_post_text": (
#             "✍️ Send the <b>post text</b> now.\n\n"
#             "Up to 4096 characters."
#         ),
#         "text_too_long": "⚠️ Text too long (max 4096).",
#         "text_empty": "⚠️ Text is empty.",
#         "send_media_or_skip": (
#             "📎 Send a <b>photo/video/file</b> or press «Skip»."
#         ),
#         "media_received": "✅ Media received.",
#         "buttons_info": (
#             "🔘 <b>Post buttons</b>\n\n"
#             "You can add buttons (text + URL) or skip.\n\n"
#             "When done press «Done»."
#         ),
#         "buttons_choose": "Do you want to add buttons?",
#         "btn_add_button": "➕ Add button",
#         "button_text_prompt": "Send the button text:",
#         "button_url_prompt": "Send the button URL (starts with https://):",
#         "button_invalid_url": "⚠️ Invalid URL. Send a URL starting with https://",
#         "button_added": "✅ Button added.",
#         "preview_title": "👀 <b>Post preview</b>",
#         "preview_channel": "📢 Channel: <b>{}</b>",
#         "preview_text": "📝 Text:\n{}",
#         "preview_media": "📎 Media: {}",
#         "preview_buttons": "🔘 Buttons: {}",
#         "publish_confirm": (
#             "Are you sure you want to publish?\n\n"
#             "Press «🚀 Publish» to send to channel."
#         ),
#         "published": "✅ Published successfully 🚀",
#         "publish_failed": "❌ Publish failed: {}",
#         "cancelled": "❌ Cancelled.",

#         "no_posts": "📭 No posts yet.",
#         "posts_list": "📋 <b>Your posts:</b>\n\n",
#         "post_item": (
#             "#{id} · {media}\n"
#             "{text}"
#         ),
#         "post_view": (
#             "📋 <b>Post #{id}</b>\n\n"
#             "📝 Text:\n{text}\n\n"
#             "{media_line}"
#             "🕐 {date}"
#         ),
#         "edit_prompt": "✏️ Send the new text:",
#         "edit_success": "✅ Post updated.",
#         "edit_failed": "❌ Edit failed: {}",
#         "edit_no_channel": "❌ Channel not connected.",

#         "stats_title": "📊 <b>Your statistics</b>",
#         "stats_body": (
#             "📢 Channels: <b>{channels}</b>\n"
#             "📝 Posts: <b>{posts}</b>"
#         ),

#         "admin_title": "👑 <b>Admin Dashboard</b>",
#         "admin_stats": (
#             "👥 <b>Total users:</b> {total}\n"
#             "🟢 <b>Active 24h:</b> {a24}\n"
#             "🟢 <b>Active 7d:</b> {a7}\n\n"
#             "📢 <b>Total channels:</b> {channels}\n"
#             "📝 <b>Total posts:</b> {posts}"
#         ),
#         "admin_users": "👥 <b>Latest users:</b>\n\n",
#         "admin_user_row": (
#             "• <code>{tid}</code>\n"
#             "  🌐 {lang} · 🕐 {date}\n"
#         ),
#         "admin_no_access": "❌ Admin only.",

#         "loading": "⏳ ...",
#     }
# }


# def t(language, key):
#     language = language if language in TEXTS else "ar"
#     return TEXTS[language].get(key, key)


# # =========================================================
# # KEYBOARDS
# # =========================================================

# def language_keyboard():
#     return InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text="🇸🇦 العربية",
#                     callback_data="lang_ar"
#                 ),
#                 InlineKeyboardButton(
#                     text="🇬🇧 English",
#                     callback_data="lang_en"
#                 )
#             ]
#         ]
#     )


# def main_reply_keyboard(language):
#     """Persistent reply keyboard at bottom."""
#     return ReplyKeyboardMarkup(
#         keyboard=[
#             [
#                 KeyboardButton(text=t(language, "btn_create_post"))
#             ],
#             [
#                 KeyboardButton(text=t(language, "btn_my_channels")),
#                 KeyboardButton(text=t(language, "btn_my_posts"))
#             ],
#             [
#                 KeyboardButton(text=t(language, "btn_stats")),
#                 KeyboardButton(text=t(language, "btn_language"))
#             ]
#         ],
#         resize_keyboard=True,
#         is_persistent=True
#     )


# def main_inline_keyboard(language):
#     """Inline main menu."""
#     return InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text=t(language, "btn_create_post"),
#                     callback_data="menu:create"
#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text=t(language, "btn_my_channels"),
#                     callback_data="menu:channels"
#                 ),
#                 InlineKeyboardButton(
#                     text=t(language, "btn_my_posts"),
#                     callback_data="menu:posts"
#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text=t(language, "btn_stats"),
#                     callback_data="menu:stats"
#                 ),
#                 InlineKeyboardButton(
#                     text=t(language, "btn_language"),
#                     callback_data="menu:language"
#                 )
#             ]
#         ]
#     )


# def cancel_keyboard(language):
#     return InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text=t(language, "btn_cancel"),
#                     callback_data="flow:cancel"
#                 )
#             ]
#         ]
#     )


# def skip_keyboard(language, back_callback="flow:cancel"):
#     return InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text=t(language, "btn_skip"),
#                     callback_data="flow:skip_media"
#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text=t(language, "btn_cancel"),
#                     callback_data=back_callback
#                 )
#             ]
#         ]
#     )


# def buttons_keyboard(language):
#     return InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text=t(language, "btn_add_button"),
#                     callback_data="flow:add_button"
#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text=t(language, "btn_done"),
#                     callback_data="flow:buttons_done"
#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text=t(language, "btn_cancel"),
#                     callback_data="flow:cancel"
#                 )
#             ]
#         ]
#     )


# def preview_keyboard(language):
#     return InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text=t(language, "btn_publish"),
#                     callback_data="flow:publish"
#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text=t(language, "btn_cancel"),
#                     callback_data="flow:cancel"
#                 )
#             ]
#         ]
#     )


# def back_home_keyboard(language):
#     return InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text=t(language, "btn_home"),
#                     callback_data="menu:home"
#                 )
#             ]
#         ]
#     )


# def confirm_delete_keyboard(language, channel_id):
#     return InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text=t(language, "delete_confirm_yes"),
#                     callback_data=f"channel:delete:{channel_id}"
#                 ),
#                 InlineKeyboardButton(
#                     text=t(language, "delete_confirm_no"),
#                     callback_data="menu:channels"
#                 )
#             ]
#         ]
#     )


# # =========================================================
# # HELPERS
# # =========================================================

# def build_inline_keyboard(buttons):
#     if not buttons:
#         return None

#     keyboard = []

#     for button in buttons:
#         text = button.get("text")
#         url = button.get("url")

#         if not text or not url:
#             continue

#         keyboard.append(
#             [
#                 InlineKeyboardButton(
#                     text=text[:64],
#                     url=url
#                 )
#             ]
#         )

#     if not keyboard:
#         return None

#     return InlineKeyboardMarkup(inline_keyboard=keyboard)


# def format_date(iso_str):
#     if not iso_str:
#         return "—"
#     return iso_str[:16].replace("T", " ")


# async def safe_edit_or_send(
#     callback: CallbackQuery,
#     text: str,
#     reply_markup=None
# ):
#     """Try to edit callback message; if it fails, send new."""
#     try:
#         await callback.message.edit_text(
#             text=text,
#             reply_markup=reply_markup
#         )
#     except TelegramBadRequest:
#         try:
#             await callback.message.delete()
#         except Exception:
#             pass

#         await callback.message.answer(
#             text=text,
#             reply_markup=reply_markup
#         )


# # =========================================================
# # START
# # =========================================================

# @dp.message(CommandStart())
# async def start_handler(message: Message, state: FSMContext):

#     await state.clear()

#     user = get_user(message.from_user.id)

#     if not user:

#         create_user(message.from_user.id, "ar")
#         log_stat(message.from_user.id, "start")
#         touch_user(message.from_user.id)

#         await message.answer(
#             "🌐 <b>Choose your language / اختر اللغة</b>",
#             reply_markup=language_keyboard()
#         )

#         return

#     touch_user(message.from_user.id)
#     log_stat(message.from_user.id, "start")

#     language = user["language"]

#     await send_main_menu(message, language)


# async def send_main_menu(message: Message, language):

#     channels_count = len(get_channels(message.from_user.id))
#     posts_count = get_posts_count(message.from_user.id)

#     text = (
#         f"{t(language, 'main_title')}\n"
#         "━━━━━━━━━━━━━━━━━━\n\n"
#         f"{t(language, 'welcome')}\n\n"
#         + t(language, "stats_line").format(
#             channels=channels_count,
#             posts=posts_count
#         )
#     )

#     await message.answer(
#         text,
#         reply_markup=main_inline_keyboard(language)
#     )

#     await message.answer(
#         "👇",
#         reply_markup=main_reply_keyboard(language)
#     )


# # =========================================================
# # LANGUAGE
# # =========================================================

# @dp.callback_query(F.data.startswith("lang_"))
# async def language_callback(callback: CallbackQuery, state: FSMContext):

#     await state.clear()

#     language = callback.data.replace("lang_", "")

#     if language not in ("ar", "en"):
#         await callback.answer()
#         return

#     set_language(callback.from_user.id, language)

#     try:
#         await callback.message.delete()
#     except Exception:
#         pass

#     msg = (
#         t(language, "language_saved_ar")
#         if language == "ar"
#         else t(language, "language_saved_en")
#     )

#     await callback.message.answer(
#         msg,
#         reply_markup=main_reply_keyboard(language)
#     )

#     await send_main_menu(callback.message, language)

#     await callback.answer()


# @dp.message(F.text.in_(["🌐 اللغة", "🌐 Language"]))
# async def change_language(message: Message):

#     await message.answer(
#         "🌐 اختر اللغة / Choose language:",
#         reply_markup=language_keyboard()
#     )


# # =========================================================
# # MENU CALLBACKS
# # =========================================================

# @dp.callback_query(F.data == "menu:home")
# async def menu_home(callback: CallbackQuery, state: FSMContext):

#     await state.clear()

#     language = get_language(callback.from_user.id)

#     channels_count = len(get_channels(callback.from_user.id))
#     posts_count = get_posts_count(callback.from_user.id)

#     text = (
#         f"{t(language, 'main_title')}\n"
#         "━━━━━━━━━━━━━━━━━━\n\n"
#         f"{t(language, 'welcome')}\n\n"
#         + t(language, "stats_line").format(
#             channels=channels_count,
#             posts=posts_count
#         )
#     )

#     await safe_edit_or_send(
#         callback,
#         text,
#         main_inline_keyboard(language)
#     )

#     await callback.answer()


# @dp.message(F.text.in_(["🏠 الرئيسية", "🏠 Home"]))
# async def home_reply(message: Message, state: FSMContext):

#     await state.clear()

#     language = get_language(message.from_user.id)

#     await send_main_menu(message, language)


# @dp.callback_query(F.data == "menu:language")
# async def menu_language(callback: CallbackQuery, state: FSMContext):

#     await state.clear()

#     await safe_edit_or_send(
#         callback,
#         "🌐 اختر اللغة / Choose language:",
#         language_keyboard()
#     )

#     await callback.answer()


# @dp.callback_query(F.data == "menu:stats")
# async def menu_stats(callback: CallbackQuery, state: FSMContext):

#     await state.clear()

#     language = get_language(callback.from_user.id)

#     channels_count = len(get_channels(callback.from_user.id))
#     posts_count = get_posts_count(callback.from_user.id)

#     text = (
#         f"{t(language, 'stats_title')}\n"
#         "━━━━━━━━━━━━━━━━━━\n\n"
#         + t(language, "stats_body").format(
#             channels=channels_count,
#             posts=posts_count
#         )
#     )

#     await safe_edit_or_send(
#         callback,
#         text,
#         back_home_keyboard(language)
#     )

#     await callback.answer()


# @dp.message(F.text.in_(["📊 الإحصائيات", "📊 Statistics"]))
# async def stats_reply(message: Message, state: FSMContext):

#     await state.clear()

#     language = get_language(message.from_user.id)

#     channels_count = len(get_channels(message.from_user.id))
#     posts_count = get_posts_count(message.from_user.id)

#     text = (
#         f"{t(language, 'stats_title')}\n"
#         "━━━━━━━━━━━━━━━━━━\n\n"
#         + t(language, "stats_body").format(
#             channels=channels_count,
#             posts=posts_count
#         )
#     )

#     await message.answer(
#         text,
#         reply_markup=back_home_keyboard(language)
#     )


# @dp.message(F.text.in_(["ℹ️ المساعدة", "ℹ️ Help"]))
# async def help_handler(message: Message, state: FSMContext):

#     await state.clear()

#     language = get_language(message.from_user.id)

#     await message.answer(t(language, "help_text"))


# # =========================================================
# # CHANNELS
# # =========================================================

# @dp.message(Command("addchannel"))
# async def addchannel_cmd(message: Message, state: FSMContext):

#     await state.clear()

#     language = get_language(message.from_user.id)

#     await message.answer(
#         t(language, "channel_add_help"),
#         reply_markup=cancel_keyboard(language)
#     )

#     await state.set_state(ChannelFlow.waiting_username)


# @dp.message(F.text.in_(["📢 قنواتي", "📢 My Channels"]))
# async def channels_reply(message: Message, state: FSMContext):

#     await state.clear()

#     language = get_language(message.from_user.id)

#     await show_channels(message, language)


# @dp.callback_query(F.data == "menu:channels")
# async def menu_channels(callback: CallbackQuery, state: FSMContext):

#     await state.clear()

#     language = get_language(callback.from_user.id)

#     channels = get_channels(callback.from_user.id)

#     if not channels:

#         text = t(language, "no_channels")

#         await safe_edit_or_send(
#             callback,
#             text,
#             InlineKeyboardMarkup(
#                 inline_keyboard=[
#                     [
#                         InlineKeyboardButton(
#                             text=t(language, "btn_add_channel"),
#                             callback_data="channel:add"
#                         )
#                     ],
#                     [
#                         InlineKeyboardButton(
#                             text=t(language, "btn_home"),
#                             callback_data="menu:home"
#                         )
#                     ]
#                 ]
#             )
#         )

#         await callback.answer()
#         return

#     text = t(language, "channel_list")

#     buttons = []

#     for channel in channels:

#         username = channel["username"] or channel["title"]

#         text += f"• <b>{username}</b>\n"

#         buttons.append(
#             [
#                 InlineKeyboardButton(
#                     text=f"🗑️ {username}",
#                     callback_data=f"channel:del:{channel['channel_id']}"
#                 )
#             ]
#         )

#     buttons.append(
#         [
#             InlineKeyboardButton(
#                 text=t(language, "btn_add_channel"),
#                 callback_data="channel:add"
#             )
#         ]
#     )

#     buttons.append(
#         [
#             InlineKeyboardButton(
#                 text=t(language, "btn_home"),
#                 callback_data="menu:home"
#             )
#         ]
#     )

#     await safe_edit_or_send(
#         callback,
#         text,
#         InlineKeyboardMarkup(inline_keyboard=buttons)
#     )

#     await callback.answer()


# async def show_channels(message: Message, language):

#     channels = get_channels(message.from_user.id)

#     if not channels:

#         await message.answer(
#             t(language, "no_channels"),
#             reply_markup=InlineKeyboardMarkup(
#                 inline_keyboard=[
#                     [
#                         InlineKeyboardButton(
#                             text=t(language, "btn_add_channel"),
#                             callback_data="channel:add"
#                         )
#                     ]
#                 ]
#             )
#         )
#         return

#     text = t(language, "channel_list")

#     buttons = []

#     for channel in channels:

#         username = channel["username"] or channel["title"]

#         text += f"• <b>{username}</b>\n"

#         buttons.append(
#             [
#                 InlineKeyboardButton(
#                     text=f"🗑️ {username}",
#                     callback_data=f"channel:del:{channel['channel_id']}"
#                 )
#             ]
#         )

#     buttons.append(
#         [
#             InlineKeyboardButton(
#                 text=t(language, "btn_add_channel"),
#                 callback_data="channel:add"
#             )
#         ]
#     )

#     await message.answer(
#         text,
#         reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
#     )


# @dp.callback_query(F.data == "channel:add")
# async def channel_add_cb(callback: CallbackQuery, state: FSMContext):

#     language = get_language(callback.from_user.id)

#     await safe_edit_or_send(
#         callback,
#         t(language, "channel_add_help"),
#         cancel_keyboard(language)
#     )

#     await state.set_state(ChannelFlow.waiting_username)

#     await callback.answer()


# @dp.callback_query(F.data.startswith("channel:del:"))
# async def channel_del_confirm(callback: CallbackQuery):

#     channel_id = callback.data.split(":", 2)[2]

#     language = get_language(callback.from_user.id)

#     channel = get_channel(callback.from_user.id, channel_id)

#     if not channel:
#         await callback.answer("⚠️")
#         return

#     username = channel["username"] or channel["title"]

#     text = t(language, "confirm_delete_channel").format(username)

#     await safe_edit_or_send(
#         callback,
#         text,
#         confirm_delete_keyboard(language, channel_id)
#     )

#     await callback.answer()


# @dp.callback_query(F.data.startswith("channel:delete:"))
# async def channel_delete(callback: CallbackQuery):

#     channel_id = callback.data.split(":", 2)[2]

#     language = get_language(callback.from_user.id)

#     delete_channel(callback.from_user.id, channel_id)

#     await safe_edit_or_send(
#         callback,
#         t(language, "channel_deleted"),
#         back_home_keyboard(language)
#     )

#     await callback.answer()


# # Receive channel username (in channel flow state)

# @dp.message(ChannelFlow.waiting_username)
# async def receive_channel_username(
#     message: Message,
#     state: FSMContext
# ):

#     username = (message.text or "").strip()

#     language = get_language(message.from_user.id)

#     if not username.startswith("@"):
#         username = "@" + username

#     if " " in username or len(username) < 2:

#         await message.answer(
#             "⚠️ صيغة غير صحيحة. مثال: <code>@yourchannel</code>"
#         )
#         return

#     try:

#         chat = await bot.get_chat(chat_id=username)

#         if chat.type != "channel":

#             await message.answer(
#                 "❌ هذا ليس Channel.\n\n"
#                 "أرسل <code>@yourchannel</code>"
#             )
#             return

#         me = await bot.get_me()

#         member = await bot.get_chat_member(
#             chat_id=chat.id,
#             user_id=me.id
#         )

#         if member.status != ChatMemberStatus.ADMINISTRATOR:

#             await message.answer(
#                 t(language, "not_admin")
#             )
#             return

#         can_post = getattr(
#             member,
#             "can_post_messages",
#             False
#         )

#         if not can_post:

#             await message.answer(
#                 "❌ البوت مسؤول لكن لا يملك صلاحية نشر الرسائل."
#             )
#             return

#         channel_username = (
#             f"@{chat.username}"
#             if chat.username
#             else username
#         )

#         add_channel(
#             telegram_id=message.from_user.id,
#             channel_id=str(chat.id),
#             username=channel_username,
#             title=chat.title or username
#         )

#         log_stat(
#             message.from_user.id,
#             "channel_added",
#             channel_username
#         )

#         await state.clear()

#         await message.answer(
#             t(language, "channel_added").format(
#                 chat.title or username
#             ),
#             reply_markup=main_reply_keyboard(language)
#         )

#     except TelegramBadRequest as e:

#         error_text = str(e).lower()

#         if "chat not found" in error_text:

#             await message.answer(
#                 t(language, "channel_not_found")
#             )
#         else:

#             await message.answer(
#                 f"❌ <code>{str(e)[:300]}</code>"
#             )

#     except Exception:

#         logger.exception("Channel verification failed")

#         await message.answer(
#             "❌ حدث خطأ. راجع logs."
#         )


# # =========================================================
# # CREATE POST FLOW
# # =========================================================

# @dp.message(F.text.in_(["✨ إنشاء منشور", "✨ Create Post"]))
# async def create_post_reply(message: Message, state: FSMContext):

#     await state.clear()

#     await start_post_flow(message, state)


# @dp.callback_query(F.data == "menu:create")
# async def create_post_cb(callback: CallbackQuery, state: FSMContext):

#     await state.clear()

#     await start_post_flow(callback.message, state, from_callback=True)

#     await callback.answer()


# async def start_post_flow(
#     message: Message,
#     state: FSMContext,
#     from_callback=False
# ):

#     language = get_language(message.chat.id)

#     channels = get_channels(message.chat.id)

#     if not channels:

#         text = t(language, "no_channel_available")

#         if from_callback:
#             try:
#                 await message.edit_text(text)
#             except Exception:
#                 await message.answer(text)
#         else:
#             await message.answer(text)

#         return

#     buttons = []

#     for channel in channels:

#         username = channel["username"] or channel["title"]

#         buttons.append(
#             [
#                 InlineKeyboardButton(
#                     text=username,
#                     callback_data=f"post:channel:{channel['channel_id']}"
#                 )
#             ]
#         )

#     buttons.append(
#         [
#             InlineKeyboardButton(
#                 text=t(language, "btn_cancel"),
#                 callback_data="flow:cancel"
#             )
#         ]
#     )

#     text = t(language, "choose_channel")

#     if from_callback:
#         try:
#             await message.edit_text(
#                 text,
#                 reply_markup=InlineKeyboardMarkup(
#                     inline_keyboard=buttons
#                 )
#             )
#         except Exception:
#             await message.answer(
#                 text,
#                 reply_markup=InlineKeyboardMarkup(
#                     inline_keyboard=buttons
#                 )
#             )
#     else:
#         await message.answer(
#             text,
#             reply_markup=InlineKeyboardMarkup(
#                 inline_keyboard=buttons
#             )
#         )

#     await state.set_state(PostFlow.choosing_channel)


# @dp.callback_query(PostFlow.choosing_channel, F.data.startswith("post:channel:"))
# async def post_choose_channel(callback: CallbackQuery, state: FSMContext):

#     channel_id = callback.data.split(":", 2)[2]

#     language = get_language(callback.from_user.id)

#     channel = get_channel(callback.from_user.id, channel_id)

#     if not channel:
#         await callback.answer("⚠️")
#         return

#     await state.update_data(
#         channel_id=channel_id,
#         channel_username=channel["username"] or channel["title"],
#         text=None,
#         media_type=None,
#         media_path=None,
#         buttons=[]
#     )

#     await safe_edit_or_send(
#         callback,
#         t(language, "send_post_text"),
#         cancel_keyboard(language)
#     )

#     await state.set_state(PostFlow.waiting_text)

#     await callback.answer()


# @dp.message(PostFlow.waiting_text)
# async def post_receive_text(message: Message, state: FSMContext):

#     language = get_language(message.from_user.id)

#     text = (message.text or "").strip()

#     if not text:
#         await message.answer(t(language, "text_empty"))
#         return

#     if len(text) > 4096:
#         await message.answer(t(language, "text_too_long"))
#         return

#     await state.update_data(text=text)

#     await message.answer(
#         t(language, "send_media_or_skip"),
#         reply_markup=skip_keyboard(language)
#     )

#     await state.set_state(PostFlow.waiting_media)


# @dp.message(PostFlow.waiting_media, F.photo)
# async def post_receive_photo(message: Message, state: FSMContext):

#     language = get_language(message.from_user.id)

#     photo = message.photo[-1]

#     file = await bot.get_file(photo.file_id)

#     path = UPLOAD_DIR / f"{photo.file_unique_id}.jpg"

#     await bot.download_file(file.file_path, destination=path)

#     await state.update_data(
#         media_type="photo",
#         media_path=str(path)
#     )

#     await message.answer(
#         t(language, "media_received"),
#         reply_markup=cancel_keyboard(language)
#     )

#     await ask_buttons(message, state, language)


# @dp.message(PostFlow.waiting_media, F.video)
# async def post_receive_video(message: Message, state: FSMContext):

#     language = get_language(message.from_user.id)

#     video = message.video

#     file = await bot.get_file(video.file_id)

#     ext = (video.file_name or "video.mp4").split(".")[-1]

#     path = UPLOAD_DIR / f"{video.file_unique_id}.{ext}"

#     await bot.download_file(file.file_path, destination=path)

#     await state.update_data(
#         media_type="video",
#         media_path=str(path)
#     )

#     await message.answer(
#         t(language, "media_received"),
#         reply_markup=cancel_keyboard(language)
#     )

#     await ask_buttons(message, state, language)


# @dp.message(PostFlow.waiting_media, F.document)
# async def post_receive_document(message: Message, state: FSMContext):

#     language = get_language(message.from_user.id)

#     doc = message.document

#     file = await bot.get_file(doc.file_id)

#     ext = (doc.file_name or "file.bin").split(".")[-1]

#     path = UPLOAD_DIR / f"{doc.file_unique_id}.{ext}"

#     await bot.download_file(file.file_path, destination=path)

#     await state.update_data(
#         media_type="document",
#         media_path=str(path)
#     )

#     await message.answer(
#         t(language, "media_received"),
#         reply_markup=cancel_keyboard(language)
#     )

#     await ask_buttons(message, state, language)


# @dp.callback_query(PostFlow.waiting_media, F.data == "flow:skip_media")
# async def post_skip_media(callback: CallbackQuery, state: FSMContext):

#     language = get_language(callback.from_user.id)

#     await ask_buttons(callback.message, state, language, from_callback=callback)

#     await callback.answer()


# async def ask_buttons(
#     message: Message,
#     state: FSMContext,
#     language,
#     from_callback=None
# ):

#     await state.update_data(buttons=[])

#     text = t(language, "buttons_info")

#     if from_callback:
#         await safe_edit_or_send(
#             from_callback,
#             text,
#             buttons_keyboard(language)
#         )
#     else:
#         await message.answer(
#             text,
#             reply_markup=buttons_keyboard(language)
#         )

#     await state.set_state(PostFlow.waiting_buttons)


# @dp.callback_query(PostFlow.waiting_buttons, F.data == "flow:add_button")
# async def post_add_button(callback: CallbackQuery, state: FSMContext):

#     language = get_language(callback.from_user.id)

#     await callback.message.answer(
#         t(language, "button_text_prompt"),
#         reply_markup=cancel_keyboard(language)
#     )

#     await state.set_state(ButtonFlow.waiting_text)

#     await callback.answer()


# @dp.message(ButtonFlow.waiting_text)
# async def button_receive_text(message: Message, state: FSMContext):

#     language = get_language(message.from_user.id)

#     text = (message.text or "").strip()

#     if not text:
#         await message.answer("⚠️")
#         return

#     await state.update_data(button_text=text)

#     await message.answer(
#         t(language, "button_url_prompt"),
#         reply_markup=cancel_keyboard(language)
#     )

#     await state.set_state(ButtonFlow.waiting_url)


# @dp.message(ButtonFlow.waiting_url)
# async def button_receive_url(message: Message, state: FSMContext):

#     language = get_language(message.from_user.id)

#     url = (message.text or "").strip()

#     if not (url.startswith("https://") or url.startswith("http://")):

#         await message.answer(t(language, "button_invalid_url"))
#         return

#     data = await state.get_data()

#     button_text = data.get("button_text")

#     buttons = data.get("buttons", [])

#     buttons.append({"text": button_text, "url": url})

#     await state.update_data(buttons=buttons)

#     await message.answer(
#         t(language, "button_added"),
#         reply_markup=buttons_keyboard(language)
#     )

#     await state.set_state(PostFlow.waiting_buttons)


# @dp.callback_query(PostFlow.waiting_buttons, F.data == "flow:buttons_done")
# async def post_buttons_done(callback: CallbackQuery, state: FSMContext):

#     language = get_language(callback.from_user.id)

#     data = await state.get_data()

#     await show_preview(callback, data, language)

#     await state.set_state(PostFlow.previewing)

#     await callback.answer()


# async def show_preview(callback: CallbackQuery, data, language):

#     text = data.get("text") or ""
#     channel = data.get("channel_username") or "—"
#     media_type = data.get("media_type")
#     buttons = data.get("buttons") or []

#     lines = [
#         f"{t(language, 'preview_title')}",
#         "━━━━━━━━━━━━━━━━━━",
#         t(language, "preview_channel").format(channel),
#         "",
#         t(language, "preview_text").format(text)
#     ]

#     if media_type:
#         lines.append("")
#         lines.append(t(language, "preview_media").format(media_type))

#     if buttons:
#         lines.append("")
#         button_labels = " · ".join(b["text"] for b in buttons)
#         lines.append(t(language, "preview_buttons").format(button_labels))

#     lines.append("")
#     lines.append(t(language, "publish_confirm"))

#     await safe_edit_or_send(
#         callback,
#         "\n".join(lines),
#         preview_keyboard(language)
#     )


# @dp.callback_query(PostFlow.previewing, F.data == "flow:publish")
# async def post_publish(callback: CallbackQuery, state: FSMContext):

#     language = get_language(callback.from_user.id)

#     data = await state.get_data()

#     channel_id = data.get("channel_id")
#     text = data.get("text") or ""
#     media_type = data.get("media_type")
#     media_path = data.get("media_path")
#     buttons = data.get("buttons") or []

#     if not channel_id:
#         await callback.answer("⚠️")
#         return

#     channel = get_channel(callback.from_user.id, channel_id)

#     if not channel:
#         await callback.answer("⚠️")
#         return

#     keyboard = build_inline_keyboard(buttons)

#     try:

#         message_id = await publish_to_channel(
#             target=channel["channel_id"],
#             text=text,
#             media_type=media_type,
#             media_path=media_path,
#             keyboard=keyboard
#         )

#         create_post(
#             telegram_id=callback.from_user.id,
#             channel_id=channel_id,
#             text=text,
#             media_type=media_type,
#             media_path=media_path,
#             buttons=json.dumps(buttons, ensure_ascii=False),
#             status="published",
#             message_id=message_id
#         )

#         log_stat(callback.from_user.id, "post_published", channel_id)

#         await safe_edit_or_send(
#             callback,
#             t(language, "published"),
#             back_home_keyboard(language)
#         )

#         await callback.answer("✅")

#     except Exception as e:

#         logger.exception("Publish failed")

#         await safe_edit_or_send(
#             callback,
#             t(language, "publish_failed").format(str(e)[:200]),
#             back_home_keyboard(language)
#         )

#         await callback.answer("❌")

#     await state.clear()


# async def publish_to_channel(
#     target,
#     text,
#     media_type,
#     media_path,
#     keyboard
# ):
#     """Returns message_id of published message."""

#     if media_type == "photo":
#         msg = await bot.send_photo(
#             chat_id=target,
#             photo=FSInputFile(media_path),
#             caption=text[:1024] if text else None,
#             reply_markup=keyboard
#         )
#     elif media_type == "video":
#         msg = await bot.send_video(
#             chat_id=target,
#             video=FSInputFile(media_path),
#             caption=text[:1024] if text else None,
#             reply_markup=keyboard
#         )
#     elif media_type == "document":
#         msg = await bot.send_document(
#             chat_id=target,
#             document=FSInputFile(media_path),
#             caption=text[:1024] if text else None,
#             reply_markup=keyboard
#         )
#     else:
#         msg = await bot.send_message(
#             chat_id=target,
#             text=text,
#             reply_markup=keyboard
#         )

#     return msg.message_id


# @dp.callback_query(F.data == "flow:cancel")
# async def flow_cancel(callback: CallbackQuery, state: FSMContext):

#     await state.clear()

#     language = get_language(callback.from_user.id)

#     await safe_edit_or_send(
#         callback,
#         t(language, "cancelled"),
#         back_home_keyboard(language)
#     )

#     await callback.answer()


# # =========================================================
# # MY POSTS + EDIT
# # =========================================================

# @dp.message(F.text.in_(["📋 منشوراتي", "📋 My Posts"]))
# async def my_posts_reply(message: Message, state: FSMContext):

#     await state.clear()

#     language = get_language(message.from_user.id)

#     await show_posts(message, language)


# @dp.callback_query(F.data == "menu:posts")
# async def menu_posts(callback: CallbackQuery, state: FSMContext):

#     await state.clear()

#     language = get_language(callback.from_user.id)

#     posts = get_posts(callback.from_user.id, limit=20)

#     if not posts:

#         await safe_edit_or_send(
#             callback,
#             t(language, "no_posts"),
#             back_home_keyboard(language)
#         )

#         await callback.answer()
#         return

#     buttons = []

#     for post in posts:

#         preview = (post["text"] or "")[:30].replace("\n", " ")

#         label = f"#{post['id']} · {preview or '📎'}"

#         buttons.append(
#             [
#                 InlineKeyboardButton(
#                     text=label[:60],
#                     callback_data=f"post:view:{post['id']}"
#                 )
#             ]
#         )

#     buttons.append(
#         [
#             InlineKeyboardButton(
#                 text=t(language, "btn_home"),
#                 callback_data="menu:home"
#             )
#         ]
#     )

#     await safe_edit_or_send(
#         callback,
#         t(language, "posts_list"),
#         InlineKeyboardMarkup(inline_keyboard=buttons)
#     )

#     await callback.answer()


# async def show_posts(message: Message, language):

#     posts = get_posts(message.from_user.id, limit=20)

#     if not posts:

#         await message.answer(
#             t(language, "no_posts"),
#             reply_markup=back_home_keyboard(language)
#         )
#         return

#     buttons = []

#     for post in posts:

#         preview = (post["text"] or "")[:30].replace("\n", " ")

#         label = f"#{post['id']} · {preview or '📎'}"

#         buttons.append(
#             [
#                 InlineKeyboardButton(
#                     text=label[:60],
#                     callback_data=f"post:view:{post['id']}"
#                 )
#             ]
#         )

#     await message.answer(
#         t(language, "posts_list"),
#         reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
#     )


# @dp.callback_query(F.data.startswith("post:view:"))
# async def post_view(callback: CallbackQuery, state: FSMContext):

#     await state.clear()

#     post_id = int(callback.data.split(":")[2])

#     language = get_language(callback.from_user.id)

#     post = get_post(callback.from_user.id, post_id)

#     if not post:
#         await callback.answer("⚠️")
#         return

#     text = post["text"] or "—"
#     media_line = (
#         f"📎 {post['media_type']}\n\n"
#         if post["media_type"]
#         else ""
#     )

#     body = t(language, "post_view").format(
#         id=post["id"],
#         text=text[:500],
#         media_line=media_line,
#         date=format_date(post["created_at"])
#     )

#     buttons = InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text=t(language, "btn_edit"),
#                     callback_data=f"post:edit:{post['id']}"
#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text=t(language, "btn_back"),
#                     callback_data="menu:posts"
#                 )
#             ]
#         ]
#     )

#     await safe_edit_or_send(callback, body, buttons)

#     await callback.answer()


# @dp.callback_query(F.data.startswith("post:edit:"))
# async def post_edit_start(callback: CallbackQuery, state: FSMContext):

#     post_id = int(callback.data.split(":")[2])

#     language = get_language(callback.from_user.id)

#     post = get_post(callback.from_user.id, post_id)

#     if not post:
#         await callback.answer("⚠️")
#         return

#     await state.update_data(edit_post_id=post_id)

#     await callback.message.answer(
#         t(language, "edit_prompt"),
#         reply_markup=cancel_keyboard(language)
#     )

#     await state.set_state(EditFlow.waiting_new_text)

#     await callback.answer()


# @dp.message(EditFlow.waiting_new_text)
# async def post_edit_apply(message: Message, state: FSMContext):

#     language = get_language(message.from_user.id)

#     new_text = (message.text or "").strip()

#     if not new_text:
#         await message.answer(t(language, "text_empty"))
#         return

#     if len(new_text) > 4096:
#         await message.answer(t(language, "text_too_long"))
#         return

#     data = await state.get_data()
#     post_id = data.get("edit_post_id")

#     post = get_post(message.from_user.id, post_id)

#     if not post:
#         await message.answer("⚠️")
#         await state.clear()
#         return

#     channel = get_channel(message.from_user.id, post["channel_id"])

#     if not channel:
#         await message.answer(t(language, "edit_no_channel"))
#         await state.clear()
#         return

#     message_id = post["message_id"]

#     if not message_id:
#         await message.answer("❌ لا يمكن التعديل: message_id مفقود.")
#         await state.clear()
#         return

#     try:

#         if post["media_type"]:

#             await bot.edit_message_caption(
#                 chat_id=channel["channel_id"],
#                 message_id=message_id,
#                 caption=new_text[:1024]
#             )
#         else:

#             await bot.edit_message_text(
#                 chat_id=channel["channel_id"],
#                 message_id=message_id,
#                 text=new_text,
#                 reply_markup=build_inline_keyboard(
#                     json.loads(post["buttons"] or "[]")
#                 )
#             )

#         update_post_text(
#             message.from_user.id,
#             post_id,
#             new_text
#         )

#         log_stat(message.from_user.id, "post_edited", str(post_id))

#         await message.answer(
#             t(language, "edit_success"),
#             reply_markup=back_home_keyboard(language)
#         )

#     except TelegramBadRequest as e:

#         await message.answer(
#             t(language, "edit_failed").format(str(e)[:200])
#         )

#     except Exception as e:

#         logger.exception("Edit failed")

#         await message.answer(
#             t(language, "edit_failed").format(str(e)[:200])
#         )

#     await state.clear()


# # =========================================================
# # ADMIN
# # =========================================================

# @dp.message(Command("admin"))
# async def admin_command(message: Message):

#     if message.from_user.id != ADMIN_ID:
#         return

#     stats = get_bot_stats()

#     text = (
#         f"{t('ar', 'admin_title')}\n"
#         "━━━━━━━━━━━━━━━━━━\n\n"
#         + t("ar", "admin_stats").format(
#             total=stats["total_users"],
#             a24=stats["active_24h"],
#             a7=stats["active_7d"],
#             channels=stats["total_channels"],
#             posts=stats["total_posts"]
#         )
#     )

#     await message.answer(text)


# @dp.message(Command("users"))
# async def admin_users(message: Message):

#     if message.from_user.id != ADMIN_ID:
#         return

#     users = get_all_users(limit=20)

#     text = t("ar", "admin_users")

#     for u in users:

#         text += t("ar", "admin_user_row").format(
#             tid=u["telegram_id"],
#             lang=u["language"],
#             date=format_date(u["created_at"])
#         )

#     await message.answer(text)


# # =========================================================
# # FALLBACK
# # =========================================================

# @dp.message()
# async def fallback(message: Message, state: FSMContext):

#     current = await state.get_state()

#     if current is not None:
#         return

#     language = get_language(message.from_user.id)

#     await send_main_menu(message, language)


# # =========================================================
# # STARTUP
# # =========================================================

# async def main():

#     init_db()

#     logger.info("Telegram Publisher Bot started (no web)")

#     await dp.start_polling(bot)


# if __name__ == "__main__":

#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         logger.info("Bot stopped manually")



import asyncio
import json
import logging
import os
import re

from pathlib import Path

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatMemberStatus
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    FSInputFile,
    ChatMemberUpdated,
)
from aiogram.exceptions import TelegramBadRequest

from database import (
    init_db,
    create_user,
    get_user,
    set_language,
    get_language,
    touch_user,
    add_channel,
    get_channels,
    get_channel,
    delete_channel,
    create_post,
    get_posts,
    get_post,
    update_post_text,
    get_posts_count,
    get_channels_count,
    get_bot_stats,
    get_all_users,
    log_stat,
)


# =========================================================
# CONFIG
# =========================================================

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

BASE_DIR = Path(__file__).resolve().parent
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
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# =========================================================
# FSM STATES
# =========================================================

class PostFlow(StatesGroup):
    choosing_channel = State()
    waiting_text = State()
    waiting_media = State()
    waiting_buttons = State()
    previewing = State()


class ChannelFlow(StatesGroup):
    waiting_username = State()


class EditFlow(StatesGroup):
    waiting_new_text = State()


class ButtonFlow(StatesGroup):
    waiting_text = State()
    waiting_url = State()


# =========================================================
# TRANSLATIONS
# =========================================================

TEXTS = {
    "ar": {
        "main_title": "⚡ <b>Telegram Publisher</b>",
        "welcome": (
            "أهلاً بك 👋\n\n"
            "أنشئ منشوراتك وانشرها لقنواتك بسهولة."
        ),
        "stats_line": (
            "📢 القنوات: <b>{channels}</b>\n"
            "📝 المنشورات: <b>{posts}</b>"
        ),
        "choose_language": "🌐 اختر لغة البوت:",
        "language_saved_ar": "✅ تم اختيار اللغة العربية.",
        "language_saved_en": "✅ English selected.",

        "btn_create_post": "✨ إنشاء منشور",
        "btn_my_channels": "📢 قنواتي",
        "btn_my_posts": "📋 منشوراتي",
        "btn_stats": "📊 الإحصائيات",
        "btn_language": "🌐 اللغة",
        "btn_home": "🏠 الرئيسية",
        "btn_help": "ℹ️ المساعدة",
        "btn_add_channel": "➕ إضافة قناة",
        "btn_back": "◀️ رجوع",
        "btn_cancel": "❌ إلغاء",
        "btn_skip": "⏭️ تخطي",
        "btn_done": "✅ تم",
        "btn_publish": "🚀 نشر",
        "btn_preview": "👀 معاينة",
        "btn_edit": "✏️ تعديل النص",
        "btn_delete": "🗑️ حذف",

        "no_channels": (
            "ليس لديك أي قناة.\n\n"
            "استخدم /addchannel لإضافة قناة."
        ),
        "channel_list": "📢 <b>قنواتك:</b>\n\n",
        "channel_added": "✅ تمت إضافة القناة:\n<b>{}</b>",
        "channel_deleted": "🗑️ تم حذف القناة.",
        "confirm_delete_channel": "هل تريد حذف القناة <b>{}</b>؟",
        "delete_confirm_yes": "🗑️ نعم، احذف",
        "delete_confirm_no": "❌ لا",

        "add_channel_help": (
            "➕ <b>إضافة قناة</b>\n\n"
            "🔹 <b>الطريقة 1 — تلقائية (الأسهل):</b>\n"
            "أضف البوت كمسؤول في قناتك، وسيتم ربطها تلقائياً ✅\n\n"
            "🔹 <b>الطريقة 2 — يدوية:</b>\n"
            "أرسل أحد الصيغ التالية:\n"
            "• <code>@razanaltifa</code>\n"
            "• <code>razanaltifa</code>\n"
            "• <code>https://t.me/razanaltifa</code>\n\n"
            "⚠️ الروابط الخاصة (<code>+</code>) غير مدعومة."
        ),
        "channel_private_link": (
            "❌ <b>لا يمكن إضافة الروابط الخاصة (Invite Links).</b>\n\n"
            "استخدم أحد هذه الصيغ:\n"
            "• <code>@razanaltifa</code>\n"
            "• <code>https://t.me/razanaltifa</code>\n\n"
            "أو أضف البوت كمسؤول في القناة وسيتم حفظها تلقائياً ✅"
        ),
        "channel_invalid_format": (
            "⚠️ <b>صيغة غير صحيحة.</b>\n\n"
            "أرسل أحد هذه الصيغ:\n"
            "• <code>@razanaltifa</code>\n"
            "• <code>razanaltifa</code>\n"
            "• <code>https://t.me/razanaltifa</code>"
        ),
        "channel_not_found": (
            "❌ <b>لم يتم العثور على القناة.</b>\n\n"
            "تأكد من الرابط أو Username."
        ),
        "not_admin": (
            "❌ <b>البوت ليس مسؤولاً في هذه القناة.</b>\n\n"
            "أضف البوت كمسؤول ثم حاول مجدداً."
        ),
        "not_can_post": (
            "❌ <b>البوت مسؤول لكنه لا يملك صلاحية نشر الرسائل.</b>\n\n"
            "اذهب إلى:\n"
            "إدارة القناة → المسؤولون → البوت\n"
            "وفعّل: ✅ نشر الرسائل"
        ),
        "not_a_channel": "❌ هذا ليس Channel.\n\nتأكد أنك أرسلت رابط قناة وليس مجموعة.",

        "help_text": (
            "ℹ️ <b>طريقة الاستخدام</b>\n\n"
            "• أضف قناتك من «قنواتي»\n"
            "• أنشئ منشوراً من «إنشاء منشور»\n"
            "• اختر قناة → اكتب النص → أضف وسائط (اختياري)\n"
            "• معاينة ثم نشر 🚀"
        ),

        "choose_channel": "📢 <b>اختر القناة:</b>",
        "no_channel_available": "❌ لا توجد قنوات. أضف قناة أولاً.",
        "send_post_text": (
            "✍️ أرسل <b>نص المنشور</b> الآن.\n\n"
            "يمكنك إرسال حتى 4096 حرف."
        ),
        "text_too_long": "⚠️ النص طويل جداً (الحد 4096).",
        "text_empty": "⚠️ النص فارغ.",
        "send_media_or_skip": (
            "📎 أرسل <b>صورة/فيديو/ملف</b> أو اضغط «تخطي»."
        ),
        "media_received": "✅ تم استلام الوسائط.",
        "buttons_info": (
            "🔘 <b>أزرار المنشور</b>\n\n"
            "يمكنك إضافة أزرار (نص + رابط) أو تخطي.\n\n"
            "عند الانتهاء اضغط «تم»."
        ),
        "btn_add_button": "➕ إضافة زر",
        "button_text_prompt": "أرسل نص الزر:",
        "button_url_prompt": "أرسل رابط الزر (يبدأ بـ https://):",
        "button_invalid_url": "⚠️ رابط غير صحيح. أرسل رابطاً يبدأ بـ https://",
        "button_added": "✅ تم إضافة الزر.",
        "preview_title": "👀 <b>معاينة المنشور</b>",
        "preview_channel": "📢 القناة: <b>{}</b>",
        "preview_text": "📝 النص:\n{}",
        "preview_media": "📎 وسائط: {}",
        "preview_buttons": "🔘 أزرار: {}",
        "publish_confirm": (
            "هل أنت متأكد من النشر؟\n\n"
            "اضغط «🚀 نشر» للنشر في القناة."
        ),
        "published": "✅ تم النشر في القناة بنجاح 🚀",
        "publish_failed": "❌ فشل النشر: {}",
        "cancelled": "❌ تم الإلغاء.",

        "no_posts": "📭 لا توجد منشورات.",
        "posts_list": "📋 <b>منشوراتك:</b>\n\n",
        "post_view": (
            "📋 <b>منشور #{id}</b>\n\n"
            "📝 النص:\n{text}\n\n"
            "{media_line}"
            "🕐 {date}"
        ),
        "edit_prompt": "✏️ أرسل النص الجديد:",
        "edit_success": "✅ تم تعديل المنشور.",
        "edit_failed": "❌ فشل التعديل: {}",
        "edit_no_channel": "❌ القناة غير مرتبطة.",
        "edit_no_message_id": "❌ لا يمكن التعديل: message_id مفقود.",

        "stats_title": "📊 <b>إحصائياتك</b>",
        "stats_body": (
            "📢 القنوات: <b>{channels}</b>\n"
            "📝 المنشورات: <b>{posts}</b>"
        ),

        "admin_title": "👑 <b>لوحة تحكم الأدمن</b>",
        "admin_stats": (
            "👥 <b>إجمالي المستخدمين:</b> {total}\n"
            "🟢 <b>نشطاء 24 ساعة:</b> {a24}\n"
            "🟢 <b>نشطاء 7 أيام:</b> {a7}\n\n"
            "📢 <b>إجمالي القنوات:</b> {channels}\n"
            "📝 <b>إجمالي المنشورات:</b> {posts}"
        ),
        "admin_users": "👥 <b>آخر المستخدمين:</b>\n\n",
        "admin_user_row": (
            "• <code>{tid}</code>\n"
            "  🌐 {lang} · 🕐 {date}\n"
        ),

        # Auto-add notifications
        "auto_added_ok": (
            "✅ <b>تم ربط القناة تلقائياً!</b>\n\n"
            "📢 <b>{title}</b>\n"
            "🔗 <code>{username}</code>\n\n"
            "🎉 البوت جاهز للنشر."
        ),
        "auto_added_no_post": (
            "✅ <b>تم ربط القناة تلقائياً!</b>\n\n"
            "📢 <b>{title}</b>\n"
            "🔗 <code>{username}</code>\n\n"
            "⚠️ البوت <b>لا يملك صلاحية نشر الرسائل</b>.\n\n"
            "اذهب إلى إدارة القناة → المسؤولون → البوت\n"
            "وفعّل: ✅ نشر الرسائل."
        ),
    },

    "en": {
        "main_title": "⚡ <b>Telegram Publisher</b>",
        "welcome": (
            "Welcome 👋\n\n"
            "Create and publish posts to your channels easily."
        ),
        "stats_line": (
            "📢 Channels: <b>{channels}</b>\n"
            "📝 Posts: <b>{posts}</b>"
        ),
        "choose_language": "🌐 Choose bot language:",
        "language_saved_ar": "✅ Arabic selected.",
        "language_saved_en": "✅ English selected.",

        "btn_create_post": "✨ Create Post",
        "btn_my_channels": "📢 My Channels",
        "btn_my_posts": "📋 My Posts",
        "btn_stats": "📊 Statistics",
        "btn_language": "🌐 Language",
        "btn_home": "🏠 Home",
        "btn_help": "ℹ️ Help",
        "btn_add_channel": "➕ Add Channel",
        "btn_back": "◀️ Back",
        "btn_cancel": "❌ Cancel",
        "btn_skip": "⏭️ Skip",
        "btn_done": "✅ Done",
        "btn_publish": "🚀 Publish",
        "btn_preview": "👀 Preview",
        "btn_edit": "✏️ Edit Text",
        "btn_delete": "🗑️ Delete",

        "no_channels": (
            "You don't have any channels.\n\n"
            "Use /addchannel to add one."
        ),
        "channel_list": "📢 <b>Your channels:</b>\n\n",
        "channel_added": "✅ Channel added:\n<b>{}</b>",
        "channel_deleted": "🗑️ Channel deleted.",
        "confirm_delete_channel": "Delete channel <b>{}</b>?",
        "delete_confirm_yes": "🗑️ Yes, delete",
        "delete_confirm_no": "❌ No",

        "add_channel_help": (
            "➕ <b>Add Channel</b>\n\n"
            "🔹 <b>Method 1 — Automatic (easiest):</b>\n"
            "Add the bot as admin to your channel — it will be linked automatically ✅\n\n"
            "🔹 <b>Method 2 — Manual:</b>\n"
            "Send one of these formats:\n"
            "• <code>@razanaltifa</code>\n"
            "• <code>razanaltifa</code>\n"
            "• <code>https://t.me/razanaltifa</code>\n\n"
            "⚠️ Private invite links (<code>+</code>) are not supported."
        ),
        "channel_private_link": (
            "❌ <b>Private invite links are not supported.</b>\n\n"
            "Use one of these formats:\n"
            "• <code>@razanaltifa</code>\n"
            "• <code>https://t.me/razanaltifa</code>\n\n"
            "Or add the bot as admin — it will be linked automatically ✅"
        ),
        "channel_invalid_format": (
            "⚠️ <b>Invalid format.</b>\n\n"
            "Send one of these:\n"
            "• <code>@razanaltifa</code>\n"
            "• <code>razanaltifa</code>\n"
            "• <code>https://t.me/razanaltifa</code>"
        ),
        "channel_not_found": (
            "❌ <b>Channel not found.</b>\n\n"
            "Check the link or username."
        ),
        "not_admin": (
            "❌ <b>The bot is not an admin in this channel.</b>\n\n"
            "Add the bot as admin then try again."
        ),
        "not_can_post": (
            "❌ <b>The bot is admin but cannot post messages.</b>\n\n"
            "Go to:\n"
            "Channel Settings → Admins → Bot\n"
            "Enable: ✅ Post Messages"
        ),
        "not_a_channel": "❌ This is not a channel.\n\nSend a channel link, not a group.",

        "help_text": (
            "ℹ️ <b>How to use</b>\n\n"
            "• Add a channel from «My Channels»\n"
            "• Create a post from «Create Post»\n"
            "• Choose channel → write text → add media (optional)\n"
            "• Preview then Publish 🚀"
        ),

        "choose_channel": "📢 <b>Choose a channel:</b>",
        "no_channel_available": "❌ No channels. Add one first.",
        "send_post_text": (
            "✍️ Send the <b>post text</b> now.\n\n"
            "Up to 4096 characters."
        ),
        "text_too_long": "⚠️ Text too long (max 4096).",
        "text_empty": "⚠️ Text is empty.",
        "send_media_or_skip": (
            "📎 Send a <b>photo/video/file</b> or press «Skip»."
        ),
        "media_received": "✅ Media received.",
        "buttons_info": (
            "🔘 <b>Post buttons</b>\n\n"
            "You can add buttons (text + URL) or skip.\n\n"
            "When done press «Done»."
        ),
        "btn_add_button": "➕ Add button",
        "button_text_prompt": "Send the button text:",
        "button_url_prompt": "Send the button URL (starts with https://):",
        "button_invalid_url": "⚠️ Invalid URL. Send a URL starting with https://",
        "button_added": "✅ Button added.",
        "preview_title": "👀 <b>Post preview</b>",
        "preview_channel": "📢 Channel: <b>{}</b>",
        "preview_text": "📝 Text:\n{}",
        "preview_media": "📎 Media: {}",
        "preview_buttons": "🔘 Buttons: {}",
        "publish_confirm": (
            "Are you sure you want to publish?\n\n"
            "Press «🚀 Publish» to send to channel."
        ),
        "published": "✅ Published successfully 🚀",
        "publish_failed": "❌ Publish failed: {}",
        "cancelled": "❌ Cancelled.",

        "no_posts": "📭 No posts yet.",
        "posts_list": "📋 <b>Your posts:</b>\n\n",
        "post_view": (
            "📋 <b>Post #{id}</b>\n\n"
            "📝 Text:\n{text}\n\n"
            "{media_line}"
            "🕐 {date}"
        ),
        "edit_prompt": "✏️ Send the new text:",
        "edit_success": "✅ Post updated.",
        "edit_failed": "❌ Edit failed: {}",
        "edit_no_channel": "❌ Channel not connected.",
        "edit_no_message_id": "❌ Cannot edit: message_id missing.",

        "stats_title": "📊 <b>Your statistics</b>",
        "stats_body": (
            "📢 Channels: <b>{channels}</b>\n"
            "📝 Posts: <b>{posts}</b>"
        ),

        "admin_title": "👑 <b>Admin Dashboard</b>",
        "admin_stats": (
            "👥 <b>Total users:</b> {total}\n"
            "🟢 <b>Active 24h:</b> {a24}\n"
            "🟢 <b>Active 7d:</b> {a7}\n\n"
            "📢 <b>Total channels:</b> {channels}\n"
            "📝 <b>Total posts:</b> {posts}"
        ),
        "admin_users": "👥 <b>Latest users:</b>\n\n",
        "admin_user_row": (
            "• <code>{tid}</code>\n"
            "  🌐 {lang} · 🕐 {date}\n"
        ),

        # Auto-add notifications
        "auto_added_ok": (
            "✅ <b>Channel linked automatically!</b>\n\n"
            "📢 <b>{title}</b>\n"
            "🔗 <code>{username}</code>\n\n"
            "🎉 The bot is ready to publish."
        ),
        "auto_added_no_post": (
            "✅ <b>Channel linked automatically!</b>\n\n"
            "📢 <b>{title}</b>\n"
            "🔗 <code>{username}</code>\n\n"
            "⚠️ The bot <b>cannot post messages</b>.\n\n"
            "Go to: Channel Settings → Admins → Bot\n"
            "Enable: ✅ Post Messages."
        ),
    }
}


def t(language, key):
    language = language if language in TEXTS else "ar"
    return TEXTS[language].get(key, key)


# =========================================================
# PARSE CHANNEL INPUT
# =========================================================

def parse_channel_input(raw: str):
    """
    Accepts multiple formats and returns a normalized @username or None.

    Examples:
        "@razanaltifa"                      → "@razanaltifa"
        "razanaltifa"                       → "@razanaltifa"
        "https://t.me/razanaltifa"          → "@razanaltifa"
        "t.me/razanaltifa"                  → "@razanaltifa"
        "https://telegram.me/razanaltifa"   → "@razanaltifa"
        "telegram.me/razanaltifa"           → "@razanaltifa"
        "https://t.me/+AbCdEf"              → None (private invite)
    """

    if not raw:
        return None

    text = raw.strip().strip("/")

    # Detect private invite links
    if "+" in text and "t.me" in text.lower():
        return None

    if "joinchat" in text.lower():
        return None

    # Full URLs / short URLs
    url_patterns = [
        r"^https?://t\.me/([A-Za-z0-9_]+)/?$",
        r"^https?://telegram\.me/([A-Za-z0-9_]+)/?$",
        r"^https?://www\.t\.me/([A-Za-z0-9_]+)/?$",
        r"^t\.me/([A-Za-z0-9_]+)/?$",
        r"^telegram\.me/([A-Za-z0-9_]+)/?$",
    ]

    for pattern in url_patterns:
        match = re.match(pattern, text, re.IGNORECASE)
        if match:
            return "@" + match.group(1)

    # @username
    if text.startswith("@"):
        username = text[1:]

        if re.match(r"^[A-Za-z0-9_]{4,32}$", username):
            return "@" + username

        return None

    # Plain username
    if re.match(r"^[A-Za-z0-9_]{4,32}$", text):
        return "@" + text

    return None


# =========================================================
# KEYBOARDS
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


def main_reply_keyboard(language):
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t(language, "btn_create_post"))
            ],
            [
                KeyboardButton(text=t(language, "btn_my_channels")),
                KeyboardButton(text=t(language, "btn_my_posts"))
            ],
            [
                KeyboardButton(text=t(language, "btn_stats")),
                KeyboardButton(text=t(language, "btn_language"))
            ]
        ],
        resize_keyboard=True,
        is_persistent=True
    )


def main_inline_keyboard(language):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(language, "btn_create_post"),
                    callback_data="menu:create"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "btn_my_channels"),
                    callback_data="menu:channels"
                ),
                InlineKeyboardButton(
                    text=t(language, "btn_my_posts"),
                    callback_data="menu:posts"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "btn_stats"),
                    callback_data="menu:stats"
                ),
                InlineKeyboardButton(
                    text=t(language, "btn_language"),
                    callback_data="menu:language"
                )
            ]
        ]
    )


def cancel_keyboard(language):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(language, "btn_cancel"),
                    callback_data="flow:cancel"
                )
            ]
        ]
    )


def skip_keyboard(language, back_callback="flow:cancel"):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(language, "btn_skip"),
                    callback_data="flow:skip_media"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "btn_cancel"),
                    callback_data=back_callback
                )
            ]
        ]
    )


def buttons_keyboard(language):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(language, "btn_add_button"),
                    callback_data="flow:add_button"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "btn_done"),
                    callback_data="flow:buttons_done"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "btn_cancel"),
                    callback_data="flow:cancel"
                )
            ]
        ]
    )


def preview_keyboard(language):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(language, "btn_publish"),
                    callback_data="flow:publish"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "btn_cancel"),
                    callback_data="flow:cancel"
                )
            ]
        ]
    )


def back_home_keyboard(language):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(language, "btn_home"),
                    callback_data="menu:home"
                )
            ]
        ]
    )


def confirm_delete_keyboard(language, channel_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(language, "delete_confirm_yes"),
                    callback_data=f"channel:delete:{channel_id}"
                ),
                InlineKeyboardButton(
                    text=t(language, "delete_confirm_no"),
                    callback_data="menu:channels"
                )
            ]
        ]
    )


# =========================================================
# HELPERS
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

        keyboard.append(
            [
                InlineKeyboardButton(
                    text=text[:64],
                    url=url
                )
            ]
        )

    if not keyboard:
        return None

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def format_date(iso_str):
    if not iso_str:
        return "—"
    return iso_str[:16].replace("T", " ")


async def safe_edit_or_send(
    callback: CallbackQuery,
    text: str,
    reply_markup=None
):
    try:
        await callback.message.edit_text(
            text=text,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    except TelegramBadRequest:
        try:
            await callback.message.delete()
        except Exception:
            pass

        await callback.message.answer(
            text=text,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )


# =========================================================
# START
# =========================================================

@dp.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):

    await state.clear()

    user = get_user(message.from_user.id)

    if not user:

        create_user(message.from_user.id, "ar")
        log_stat(message.from_user.id, "start")
        touch_user(message.from_user.id)

        await message.answer(
            "🌐 <b>Choose your language / اختر اللغة</b>",
            reply_markup=language_keyboard()
        )

        return

    touch_user(message.from_user.id)
    log_stat(message.from_user.id, "start")

    language = user["language"]

    await send_main_menu(message, language)


async def send_main_menu(message: Message, language):

    channels_count = len(get_channels(message.from_user.id))
    posts_count = get_posts_count(message.from_user.id)

    text = (
        f"{t(language, 'main_title')}\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"{t(language, 'welcome')}\n\n"
        + t(language, "stats_line").format(
            channels=channels_count,
            posts=posts_count
        )
    )

    await message.answer(
        text,
        reply_markup=main_inline_keyboard(language),
        disable_web_page_preview=True
    )

    await message.answer(
        "👇",
        reply_markup=main_reply_keyboard(language)
    )


# =========================================================
# LANGUAGE
# =========================================================

@dp.callback_query(F.data.startswith("lang_"))
async def language_callback(callback: CallbackQuery, state: FSMContext):

    await state.clear()

    language = callback.data.replace("lang_", "")

    if language not in ("ar", "en"):
        await callback.answer()
        return

    set_language(callback.from_user.id, language)

    try:
        await callback.message.delete()
    except Exception:
        pass

    msg = (
        t(language, "language_saved_ar")
        if language == "ar"
        else t(language, "language_saved_en")
    )

    await callback.message.answer(
        msg,
        reply_markup=main_reply_keyboard(language)
    )

    await send_main_menu(callback.message, language)

    await callback.answer()


@dp.message(F.text.in_(["🌐 اللغة", "🌐 Language"]))
async def change_language(message: Message):

    await message.answer(
        "🌐 اختر اللغة / Choose language:",
        reply_markup=language_keyboard()
    )


# =========================================================
# MENU CALLBACKS
# =========================================================

@dp.callback_query(F.data == "menu:home")
async def menu_home(callback: CallbackQuery, state: FSMContext):

    await state.clear()

    language = get_language(callback.from_user.id)

    channels_count = len(get_channels(callback.from_user.id))
    posts_count = get_posts_count(callback.from_user.id)

    text = (
        f"{t(language, 'main_title')}\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"{t(language, 'welcome')}\n\n"
        + t(language, "stats_line").format(
            channels=channels_count,
            posts=posts_count
        )
    )

    await safe_edit_or_send(
        callback,
        text,
        main_inline_keyboard(language)
    )

    await callback.answer()


@dp.message(F.text.in_(["🏠 الرئيسية", "🏠 Home"]))
async def home_reply(message: Message, state: FSMContext):

    await state.clear()

    language = get_language(message.from_user.id)

    await send_main_menu(message, language)


@dp.callback_query(F.data == "menu:language")
async def menu_language(callback: CallbackQuery, state: FSMContext):

    await state.clear()

    await safe_edit_or_send(
        callback,
        "🌐 اختر اللغة / Choose language:",
        language_keyboard()
    )

    await callback.answer()


@dp.callback_query(F.data == "menu:stats")
async def menu_stats(callback: CallbackQuery, state: FSMContext):

    await state.clear()

    language = get_language(callback.from_user.id)

    channels_count = len(get_channels(callback.from_user.id))
    posts_count = get_posts_count(callback.from_user.id)

    text = (
        f"{t(language, 'stats_title')}\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        + t(language, "stats_body").format(
            channels=channels_count,
            posts=posts_count
        )
    )

    await safe_edit_or_send(
        callback,
        text,
        back_home_keyboard(language)
    )

    await callback.answer()


@dp.message(F.text.in_(["📊 الإحصائيات", "📊 Statistics"]))
async def stats_reply(message: Message, state: FSMContext):

    await state.clear()

    language = get_language(message.from_user.id)

    channels_count = len(get_channels(message.from_user.id))
    posts_count = get_posts_count(message.from_user.id)

    text = (
        f"{t(language, 'stats_title')}\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        + t(language, "stats_body").format(
            channels=channels_count,
            posts=posts_count
        )
    )

    await message.answer(
        text,
        reply_markup=back_home_keyboard(language)
    )


@dp.message(F.text.in_(["ℹ️ المساعدة", "ℹ️ Help"]))
async def help_handler(message: Message, state: FSMContext):

    await state.clear()

    language = get_language(message.from_user.id)

    await message.answer(t(language, "help_text"))


# =========================================================
# CHANNELS
# =========================================================

@dp.message(Command("addchannel"))
async def addchannel_cmd(message: Message, state: FSMContext):

    await state.clear()

    language = get_language(message.from_user.id)

    await message.answer(
        t(language, "add_channel_help"),
        reply_markup=cancel_keyboard(language),
        disable_web_page_preview=True
    )

    await state.set_state(ChannelFlow.waiting_username)


@dp.message(F.text.in_(["📢 قنواتي", "📢 My Channels"]))
async def channels_reply(message: Message, state: FSMContext):

    await state.clear()

    language = get_language(message.from_user.id)

    await show_channels(message, language)


@dp.callback_query(F.data == "menu:channels")
async def menu_channels(callback: CallbackQuery, state: FSMContext):

    await state.clear()

    language = get_language(callback.from_user.id)

    channels = get_channels(callback.from_user.id)

    if not channels:

        text = t(language, "no_channels")

        await safe_edit_or_send(
            callback,
            text,
            InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=t(language, "btn_add_channel"),
                            callback_data="channel:add"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text=t(language, "btn_home"),
                            callback_data="menu:home"
                        )
                    ]
                ]
            )
        )

        await callback.answer()
        return

    text = t(language, "channel_list")

    buttons = []

    for channel in channels:

        username = channel["username"] or channel["title"]

        text += f"• <b>{username}</b>\n"

        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"🗑️ {username}",
                    callback_data=f"channel:del:{channel['channel_id']}"
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text=t(language, "btn_add_channel"),
                callback_data="channel:add"
            )
        ]
    )

    buttons.append(
        [
            InlineKeyboardButton(
                text=t(language, "btn_home"),
                callback_data="menu:home"
            )
        ]
    )

    await safe_edit_or_send(
        callback,
        text,
        InlineKeyboardMarkup(inline_keyboard=buttons)
    )

    await callback.answer()


async def show_channels(message: Message, language):

    channels = get_channels(message.from_user.id)

    if not channels:

        await message.answer(
            t(language, "no_channels"),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=t(language, "btn_add_channel"),
                            callback_data="channel:add"
                        )
                    ]
                ]
            )
        )
        return

    text = t(language, "channel_list")

    buttons = []

    for channel in channels:

        username = channel["username"] or channel["title"]

        text += f"• <b>{username}</b>\n"

        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"🗑️ {username}",
                    callback_data=f"channel:del:{channel['channel_id']}"
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text=t(language, "btn_add_channel"),
                callback_data="channel:add"
            )
        ]
    )

    await message.answer(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@dp.callback_query(F.data == "channel:add")
async def channel_add_cb(callback: CallbackQuery, state: FSMContext):

    language = get_language(callback.from_user.id)

    await safe_edit_or_send(
        callback,
        t(language, "add_channel_help"),
        cancel_keyboard(language)
    )

    await state.set_state(ChannelFlow.waiting_username)

    await callback.answer()


@dp.callback_query(F.data.startswith("channel:del:"))
async def channel_del_confirm(callback: CallbackQuery):

    channel_id = callback.data.split(":", 2)[2]

    language = get_language(callback.from_user.id)

    channel = get_channel(callback.from_user.id, channel_id)

    if not channel:
        await callback.answer("⚠️")
        return

    username = channel["username"] or channel["title"]

    text = t(language, "confirm_delete_channel").format(username)

    await safe_edit_or_send(
        callback,
        text,
        confirm_delete_keyboard(language, channel_id)
    )

    await callback.answer()


@dp.callback_query(F.data.startswith("channel:delete:"))
async def channel_delete(callback: CallbackQuery):

    channel_id = callback.data.split(":", 2)[2]

    language = get_language(callback.from_user.id)

    delete_channel(callback.from_user.id, channel_id)

    await safe_edit_or_send(
        callback,
        t(language, "channel_deleted"),
        back_home_keyboard(language)
    )

    await callback.answer()


# =========================================================
# RECEIVE CHANNEL USERNAME / LINK
# =========================================================

@dp.message(ChannelFlow.waiting_username)
async def receive_channel_username(
    message: Message,
    state: FSMContext
):

    raw = (message.text or "").strip()

    language = get_language(message.from_user.id)

    # -----------------------------------------------------
    # Detect private invite
    # -----------------------------------------------------

    if ("+" in raw and "t.me" in raw.lower()) or "joinchat" in raw.lower():

        await message.answer(
            t(language, "channel_private_link"),
            disable_web_page_preview=True
        )
        return

    # -----------------------------------------------------
    # Parse input
    # -----------------------------------------------------

    username = parse_channel_input(raw)

    if not username:

        await message.answer(
            t(language, "channel_invalid_format"),
            disable_web_page_preview=True
        )
        return

    # -----------------------------------------------------
    # Verify with Telegram
    # -----------------------------------------------------

    try:

        chat = await bot.get_chat(chat_id=username)

        if chat.type != "channel":

            await message.answer(
                t(language, "not_a_channel")
            )
            return

        me = await bot.get_me()

        member = await bot.get_chat_member(
            chat_id=chat.id,
            user_id=me.id
        )

        if member.status != ChatMemberStatus.ADMINISTRATOR:

            await message.answer(
                t(language, "not_admin")
            )
            return

        can_post = getattr(
            member,
            "can_post_messages",
            False
        )

        if not can_post:

            await message.answer(
                t(language, "not_can_post")
            )
            return

        channel_username = (
            f"@{chat.username}"
            if chat.username
            else username
        )

        add_channel(
            telegram_id=message.from_user.id,
            channel_id=str(chat.id),
            username=channel_username,
            title=chat.title or username
        )

        log_stat(
            message.from_user.id,
            "channel_added",
            channel_username
        )

        await state.clear()

        await message.answer(
            "✅ <b>تمت إضافة القناة بنجاح!</b>\n\n"
            f"📢 <b>{chat.title or username}</b>\n"
            f"🔗 <code>{channel_username}</code>",
            reply_markup=main_reply_keyboard(language),
            disable_web_page_preview=True
        )

    except TelegramBadRequest as e:

        error_text = str(e).lower()

        logger.error(
            "TelegramBadRequest verifying %s: %s",
            username,
            e
        )

        if "chat not found" in error_text:

            await message.answer(
                t(language, "channel_not_found")
            )

        elif "not enough rights" in error_text:

            await message.answer(
                "❌ البوت لا يملك صلاحيات كافية."
            )

        else:

            await message.answer(
                f"❌ <code>{str(e)[:300]}</code>"
            )

    except Exception:

        logger.exception("Channel verification failed")

        await message.answer(
            "❌ حدث خطأ. راجع logs."
        )


# =========================================================
# AUTO-ADD CHANNEL (my_chat_member)
# =========================================================

@dp.my_chat_member()
async def on_my_chat_member(update: ChatMemberUpdated):

    chat = update.chat
    new_status = update.new_chat_member.status
    old_status = update.old_chat_member.status

    # Only care about channels
    if chat.type != "channel":
        return

    # -----------------------------------------------------
    # Bot was added as administrator
    # -----------------------------------------------------

    if (
        new_status == ChatMemberStatus.ADMINISTRATOR
        and old_status != ChatMemberStatus.ADMINISTRATOR
    ):

        can_post = getattr(
            update.new_chat_member,
            "can_post_messages",
            False
        )

        adder = update.from_user

        if not adder:
            logger.warning(
                "Bot added to channel %s but no from_user",
                chat.id
            )
            return

        user = get_user(adder.id)

        if not user:

            logger.info(
                "Bot added to channel %s by user %s (not started)",
                chat.id,
                adder.id
            )
            return

        channel_username = (
            f"@{chat.username}"
            if chat.username
            else str(chat.id)
        )

        add_channel(
            telegram_id=adder.id,
            channel_id=str(chat.id),
            username=channel_username,
            title=chat.title or channel_username
        )

        log_stat(
            adder.id,
            "channel_added_auto",
            channel_username
        )

        language = user["language"]

        try:

            if can_post:
                note = t(language, "auto_added_ok").format(
                    title=chat.title or channel_username,
                    username=channel_username
                )
            else:
                note = t(language, "auto_added_no_post").format(
                    title=chat.title or channel_username,
                    username=channel_username
                )

            await bot.send_message(
                chat_id=adder.id,
                text=note,
                disable_web_page_preview=True
            )

        except Exception:

            logger.exception(
                "Could not notify user %s",
                adder.id
            )

    # -----------------------------------------------------
    # Bot was removed from channel
    # -----------------------------------------------------

    elif new_status in (
        ChatMemberStatus.LEFT,
        ChatMemberStatus.KICKED,
    ):

        logger.info(
            "Bot removed from channel %s",
            chat.id
        )


# =========================================================
# CREATE POST FLOW
# =========================================================

@dp.message(F.text.in_(["✨ إنشاء منشور", "✨ Create Post"]))
async def create_post_reply(message: Message, state: FSMContext):

    await state.clear()

    await start_post_flow(message, state)


@dp.callback_query(F.data == "menu:create")
async def create_post_cb(callback: CallbackQuery, state: FSMContext):

    await state.clear()

    await start_post_flow(callback.message, state, from_callback=True)

    await callback.answer()


async def start_post_flow(
    message: Message,
    state: FSMContext,
    from_callback=False
):

    language = get_language(message.chat.id)

    channels = get_channels(message.chat.id)

    if not channels:

        text = t(language, "no_channel_available")

        if from_callback:
            try:
                await message.edit_text(text)
            except Exception:
                await message.answer(text)
        else:
            await message.answer(text)

        return

    buttons = []

    for channel in channels:

        username = channel["username"] or channel["title"]

        buttons.append(
            [
                InlineKeyboardButton(
                    text=username,
                    callback_data=f"post:channel:{channel['channel_id']}"
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text=t(language, "btn_cancel"),
                callback_data="flow:cancel"
            )
        ]
    )

    text = t(language, "choose_channel")

    if from_callback:
        try:
            await message.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=buttons
                )
            )
        except Exception:
            await message.answer(
                text,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=buttons
                )
            )
    else:
        await message.answer(
            text,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=buttons
            )
        )

    await state.set_state(PostFlow.choosing_channel)


@dp.callback_query(PostFlow.choosing_channel, F.data.startswith("post:channel:"))
async def post_choose_channel(callback: CallbackQuery, state: FSMContext):

    channel_id = callback.data.split(":", 2)[2]

    language = get_language(callback.from_user.id)

    channel = get_channel(callback.from_user.id, channel_id)

    if not channel:
        await callback.answer("⚠️")
        return

    await state.update_data(
        channel_id=channel_id,
        channel_username=channel["username"] or channel["title"],
        text=None,
        media_type=None,
        media_path=None,
        buttons=[]
    )

    await safe_edit_or_send(
        callback,
        t(language, "send_post_text"),
        cancel_keyboard(language)
    )

    await state.set_state(PostFlow.waiting_text)

    await callback.answer()


@dp.message(PostFlow.waiting_text)
async def post_receive_text(message: Message, state: FSMContext):

    language = get_language(message.from_user.id)

    text = (message.text or "").strip()

    if not text:
        await message.answer(t(language, "text_empty"))
        return

    if len(text) > 4096:
        await message.answer(t(language, "text_too_long"))
        return

    await state.update_data(text=text)

    await message.answer(
        t(language, "send_media_or_skip"),
        reply_markup=skip_keyboard(language)
    )

    await state.set_state(PostFlow.waiting_media)


@dp.message(PostFlow.waiting_media, F.photo)
async def post_receive_photo(message: Message, state: FSMContext):

    language = get_language(message.from_user.id)

    photo = message.photo[-1]

    file = await bot.get_file(photo.file_id)

    path = UPLOAD_DIR / f"{photo.file_unique_id}.jpg"

    await bot.download_file(file.file_path, destination=path)

    await state.update_data(
        media_type="photo",
        media_path=str(path)
    )

    await message.answer(
        t(language, "media_received"),
        reply_markup=cancel_keyboard(language)
    )

    await ask_buttons(message, state, language)


@dp.message(PostFlow.waiting_media, F.video)
async def post_receive_video(message: Message, state: FSMContext):

    language = get_language(message.from_user.id)

    video = message.video

    file = await bot.get_file(video.file_id)

    ext = (video.file_name or "video.mp4").split(".")[-1]

    path = UPLOAD_DIR / f"{video.file_unique_id}.{ext}"

    await bot.download_file(file.file_path, destination=path)

    await state.update_data(
        media_type="video",
        media_path=str(path)
    )

    await message.answer(
        t(language, "media_received"),
        reply_markup=cancel_keyboard(language)
    )

    await ask_buttons(message, state, language)


@dp.message(PostFlow.waiting_media, F.document)
async def post_receive_document(message: Message, state: FSMContext):

    language = get_language(message.from_user.id)

    doc = message.document

    file = await bot.get_file(doc.file_id)

    ext = (doc.file_name or "file.bin").split(".")[-1]

    path = UPLOAD_DIR / f"{doc.file_unique_id}.{ext}"

    await bot.download_file(file.file_path, destination=path)

    await state.update_data(
        media_type="document",
        media_path=str(path)
    )

    await message.answer(
        t(language, "media_received"),
        reply_markup=cancel_keyboard(language)
    )

    await ask_buttons(message, state, language)


@dp.callback_query(PostFlow.waiting_media, F.data == "flow:skip_media")
async def post_skip_media(callback: CallbackQuery, state: FSMContext):

    language = get_language(callback.from_user.id)

    await ask_buttons(callback.message, state, language, from_callback=callback)

    await callback.answer()


async def ask_buttons(
    message: Message,
    state: FSMContext,
    language,
    from_callback=None
):

    await state.update_data(buttons=[])

    text = t(language, "buttons_info")

    if from_callback:
        await safe_edit_or_send(
            from_callback,
            text,
            buttons_keyboard(language)
        )
    else:
        await message.answer(
            text,
            reply_markup=buttons_keyboard(language)
        )

    await state.set_state(PostFlow.waiting_buttons)


@dp.callback_query(PostFlow.waiting_buttons, F.data == "flow:add_button")
async def post_add_button(callback: CallbackQuery, state: FSMContext):

    language = get_language(callback.from_user.id)

    await callback.message.answer(
        t(language, "button_text_prompt"),
        reply_markup=cancel_keyboard(language)
    )

    await state.set_state(ButtonFlow.waiting_text)

    await callback.answer()


@dp.message(ButtonFlow.waiting_text)
async def button_receive_text(message: Message, state: FSMContext):

    language = get_language(message.from_user.id)

    text = (message.text or "").strip()

    if not text:
        await message.answer("⚠️")
        return

    await state.update_data(button_text=text)

    await message.answer(
        t(language, "button_url_prompt"),
        reply_markup=cancel_keyboard(language)
    )

    await state.set_state(ButtonFlow.waiting_url)


@dp.message(ButtonFlow.waiting_url)
async def button_receive_url(message: Message, state: FSMContext):

    language = get_language(message.from_user.id)

    url = (message.text or "").strip()

    if not (url.startswith("https://") or url.startswith("http://")):

        await message.answer(t(language, "button_invalid_url"))
        return

    data = await state.get_data()

    button_text = data.get("button_text")

    buttons = data.get("buttons", [])

    buttons.append({"text": button_text, "url": url})

    await state.update_data(buttons=buttons)

    await message.answer(
        t(language, "button_added"),
        reply_markup=buttons_keyboard(language)
    )

    await state.set_state(PostFlow.waiting_buttons)


@dp.callback_query(PostFlow.waiting_buttons, F.data == "flow:buttons_done")
async def post_buttons_done(callback: CallbackQuery, state: FSMContext):

    language = get_language(callback.from_user.id)

    data = await state.get_data()

    await show_preview(callback, data, language)

    await state.set_state(PostFlow.previewing)

    await callback.answer()


async def show_preview(callback: CallbackQuery, data, language):

    text = data.get("text") or ""
    channel = data.get("channel_username") or "—"
    media_type = data.get("media_type")
    buttons = data.get("buttons") or []

    lines = [
        f"{t(language, 'preview_title')}",
        "━━━━━━━━━━━━━━━━━━",
        t(language, "preview_channel").format(channel),
        "",
        t(language, "preview_text").format(text)
    ]

    if media_type:
        lines.append("")
        lines.append(t(language, "preview_media").format(media_type))

    if buttons:
        lines.append("")
        button_labels = " · ".join(b["text"] for b in buttons)
        lines.append(t(language, "preview_buttons").format(button_labels))

    lines.append("")
    lines.append(t(language, "publish_confirm"))

    await safe_edit_or_send(
        callback,
        "\n".join(lines),
        preview_keyboard(language)
    )


@dp.callback_query(PostFlow.previewing, F.data == "flow:publish")
async def post_publish(callback: CallbackQuery, state: FSMContext):

    language = get_language(callback.from_user.id)

    data = await state.get_data()

    channel_id = data.get("channel_id")
    text = data.get("text") or ""
    media_type = data.get("media_type")
    media_path = data.get("media_path")
    buttons = data.get("buttons") or []

    if not channel_id:
        await callback.answer("⚠️")
        return

    channel = get_channel(callback.from_user.id, channel_id)

    if not channel:
        await callback.answer("⚠️")
        return

    keyboard = build_inline_keyboard(buttons)

    try:

        message_id = await publish_to_channel(
            target=channel["channel_id"],
            text=text,
            media_type=media_type,
            media_path=media_path,
            keyboard=keyboard
        )

        create_post(
            telegram_id=callback.from_user.id,
            channel_id=channel_id,
            text=text,
            media_type=media_type,
            media_path=media_path,
            buttons=json.dumps(buttons, ensure_ascii=False),
            status="published",
            message_id=message_id
        )

        log_stat(callback.from_user.id, "post_published", channel_id)

        await safe_edit_or_send(
            callback,
            t(language, "published"),
            back_home_keyboard(language)
        )

        await callback.answer("✅")

    except Exception as e:

        logger.exception("Publish failed")

        await safe_edit_or_send(
            callback,
            t(language, "publish_failed").format(str(e)[:200]),
            back_home_keyboard(language)
        )

        await callback.answer("❌")

    await state.clear()


async def publish_to_channel(
    target,
    text,
    media_type,
    media_path,
    keyboard
):
    """Returns message_id of published message."""

    if media_type == "photo":
        msg = await bot.send_photo(
            chat_id=target,
            photo=FSInputFile(media_path),
            caption=text[:1024] if text else None,
            reply_markup=keyboard
        )
    elif media_type == "video":
        msg = await bot.send_video(
            chat_id=target,
            video=FSInputFile(media_path),
            caption=text[:1024] if text else None,
            reply_markup=keyboard
        )
    elif media_type == "document":
        msg = await bot.send_document(
            chat_id=target,
            document=FSInputFile(media_path),
            caption=text[:1024] if text else None,
            reply_markup=keyboard
        )
    else:
        msg = await bot.send_message(
            chat_id=target,
            text=text,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )

    return msg.message_id


@dp.callback_query(F.data == "flow:cancel")
async def flow_cancel(callback: CallbackQuery, state: FSMContext):

    await state.clear()

    language = get_language(callback.from_user.id)

    await safe_edit_or_send(
        callback,
        t(language, "cancelled"),
        back_home_keyboard(language)
    )

    await callback.answer()


# =========================================================
# MY POSTS + EDIT
# =========================================================

@dp.message(F.text.in_(["📋 منشوراتي", "📋 My Posts"]))
async def my_posts_reply(message: Message, state: FSMContext):

    await state.clear()

    language = get_language(message.from_user.id)

    await show_posts(message, language)


@dp.callback_query(F.data == "menu:posts")
async def menu_posts(callback: CallbackQuery, state: FSMContext):

    await state.clear()

    language = get_language(callback.from_user.id)

    posts = get_posts(callback.from_user.id, limit=20)

    if not posts:

        await safe_edit_or_send(
            callback,
            t(language, "no_posts"),
            back_home_keyboard(language)
        )

        await callback.answer()
        return

    buttons = []

    for post in posts:

        preview = (post["text"] or "")[:30].replace("\n", " ")

        label = f"#{post['id']} · {preview or '📎'}"

        buttons.append(
            [
                InlineKeyboardButton(
                    text=label[:60],
                    callback_data=f"post:view:{post['id']}"
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text=t(language, "btn_home"),
                callback_data="menu:home"
            )
        ]
    )

    await safe_edit_or_send(
        callback,
        t(language, "posts_list"),
        InlineKeyboardMarkup(inline_keyboard=buttons)
    )

    await callback.answer()


async def show_posts(message: Message, language):

    posts = get_posts(message.from_user.id, limit=20)

    if not posts:

        await message.answer(
            t(language, "no_posts"),
            reply_markup=back_home_keyboard(language)
        )
        return

    buttons = []

    for post in posts:

        preview = (post["text"] or "")[:30].replace("\n", " ")

        label = f"#{post['id']} · {preview or '📎'}"

        buttons.append(
            [
                InlineKeyboardButton(
                    text=label[:60],
                    callback_data=f"post:view:{post['id']}"
                )
            ]
        )

    await message.answer(
        t(language, "posts_list"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@dp.callback_query(F.data.startswith("post:view:"))
async def post_view(callback: CallbackQuery, state: FSMContext):

    await state.clear()

    post_id = int(callback.data.split(":")[2])

    language = get_language(callback.from_user.id)

    post = get_post(callback.from_user.id, post_id)

    if not post:
        await callback.answer("⚠️")
        return

    text = post["text"] or "—"
    media_line = (
        f"📎 {post['media_type']}\n\n"
        if post["media_type"]
        else ""
    )

    body = t(language, "post_view").format(
        id=post["id"],
        text=text[:500],
        media_line=media_line,
        date=format_date(post["created_at"])
    )

    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(language, "btn_edit"),
                    callback_data=f"post:edit:{post['id']}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "btn_back"),
                    callback_data="menu:posts"
                )
            ]
        ]
    )

    await safe_edit_or_send(callback, body, buttons)

    await callback.answer()


@dp.callback_query(F.data.startswith("post:edit:"))
async def post_edit_start(callback: CallbackQuery, state: FSMContext):

    post_id = int(callback.data.split(":")[2])

    language = get_language(callback.from_user.id)

    post = get_post(callback.from_user.id, post_id)

    if not post:
        await callback.answer("⚠️")
        return

    await state.update_data(edit_post_id=post_id)

    await callback.message.answer(
        t(language, "edit_prompt"),
        reply_markup=cancel_keyboard(language)
    )

    await state.set_state(EditFlow.waiting_new_text)

    await callback.answer()


@dp.message(EditFlow.waiting_new_text)
async def post_edit_apply(message: Message, state: FSMContext):

    language = get_language(message.from_user.id)

    new_text = (message.text or "").strip()

    if not new_text:
        await message.answer(t(language, "text_empty"))
        return

    if len(new_text) > 4096:
        await message.answer(t(language, "text_too_long"))
        return

    data = await state.get_data()
    post_id = data.get("edit_post_id")

    post = get_post(message.from_user.id, post_id)

    if not post:
        await message.answer("⚠️")
        await state.clear()
        return

    channel = get_channel(message.from_user.id, post["channel_id"])

    if not channel:
        await message.answer(t(language, "edit_no_channel"))
        await state.clear()
        return

    message_id = post["message_id"]

    if not message_id:
        await message.answer(t(language, "edit_no_message_id"))
        await state.clear()
        return

    try:

        if post["media_type"]:

            await bot.edit_message_caption(
                chat_id=channel["channel_id"],
                message_id=message_id,
                caption=new_text[:1024]
            )
        else:

            await bot.edit_message_text(
                chat_id=channel["channel_id"],
                message_id=message_id,
                text=new_text,
                reply_markup=build_inline_keyboard(
                    json.loads(post["buttons"] or "[]")
                ),
                disable_web_page_preview=True
            )

        update_post_text(
            message.from_user.id,
            post_id,
            new_text
        )

        log_stat(message.from_user.id, "post_edited", str(post_id))

        await message.answer(
            t(language, "edit_success"),
            reply_markup=back_home_keyboard(language)
        )

    except TelegramBadRequest as e:

        await message.answer(
            t(language, "edit_failed").format(str(e)[:200])
        )

    except Exception as e:

        logger.exception("Edit failed")

        await message.answer(
            t(language, "edit_failed").format(str(e)[:200])
        )

    await state.clear()


# =========================================================
# ADMIN
# =========================================================

@dp.message(Command("admin"))
async def admin_command(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    stats = get_bot_stats()

    text = (
        f"{t('ar', 'admin_title')}\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        + t("ar", "admin_stats").format(
            total=stats["total_users"],
            a24=stats["active_24h"],
            a7=stats["active_7d"],
            channels=stats["total_channels"],
            posts=stats["total_posts"]
        )
    )

    await message.answer(text)


@dp.message(Command("users"))
async def admin_users(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    users = get_all_users(limit=20)

    text = t("ar", "admin_users")

    for u in users:

        text += t("ar", "admin_user_row").format(
            tid=u["telegram_id"],
            lang=u["language"],
            date=format_date(u["created_at"])
        )

    await message.answer(text)


# =========================================================
# FALLBACK
# =========================================================

@dp.message()
async def fallback(message: Message, state: FSMContext):

    current = await state.get_state()

    if current is not None:
        return

    language = get_language(message.from_user.id)

    await send_main_menu(message, language)


# =========================================================
# STARTUP
# =========================================================

async def main():

    init_db()

    # Delete any pending webhook to allow polling
    try:
        await bot.delete_webhook(drop_pending_updates=False)
    except Exception:
        pass

    logger.info("Telegram Publisher Bot started (no web)")

    await dp.start_polling(bot)


if __name__ == "__main__":

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped manually")
