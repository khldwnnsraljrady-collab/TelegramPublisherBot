# import asyncio
# import json
# import logging
# import os
# import re

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
#     ChatMemberUpdated,
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
# # TRANSLATIONS & DESIGNS
# # =========================================================

# TEXTS = {
#     "ar": {
#         "main_title": "✨ <b>منصة النشر الاحترافي المتطورة</b> 🚀",
#         "welcome": (
#             "مرحباً بك أهلاً وسهلاً 👋\n\n"
#             "استمتع بإدارة قنواتك ومجموعاتك ونشر المحتوى بتصميم أنيق ومميز."
#         ),
#         "stats_line": (
#             "📢 القنوات والمجموعات المضافة: <b>{channels}</b>\n"
#             "📝 إجمالي المنشورات الصادرة: <b>{posts}</b>"
#         ),
#         "choose_language": "🌐 اختر لغة البوت المفضلة لديك:",
#         "language_saved_ar": "✅ تم تفعيل اللغة العربية بنجاح.",
#         "language_saved_en": "✅ English language activated.",

#         "btn_create_post": "✨ إنشاء منشور جديد",
#         "btn_my_channels": "📢 إدارة القنوات والمجموعات",
#         "btn_my_posts": "📋 أرشيف المنشورات",
#         "btn_stats": "📊 إحصاءات الاستخدام",
#         "btn_language": "🌐 تغيير اللغة",
#         "btn_home": "🏠 القائمة الرئيسية",
#         "btn_help": "ℹ️ دليل الاستخدام",
#         "btn_add_channel": "➕ ربط قناة أو مجموعة جديدة",
#         "btn_back": "◀️ عودة للسابق",
#         "btn_cancel": "❌ إلغاء العملية",
#         "btn_skip": "⏭️ تخطي هذه الخطوة",
#         "btn_done": "✅ إنهاء وإضافة الأزرار",
#         "btn_publish": "🚀 نشر الآن في الوجهة",
#         "btn_preview": "👀 معاينة المنشور",
#         "btn_edit": "✏️ تعديل النص الحالي",
#         "btn_delete": "🗑️ حذف نهائي",

#         "no_channels": (
#             "⚠️ <b>عذراً، لا توجد أي قناة أو مجموعة مرتبطة بحسابك.</b>\n\n"
#             "قم بإضافة البوت مشرفاً (أدمن) في قناتك أو مجموعتك، أو استخدم /addchannel للإضافة اليدوية."
#         ),
#         "channel_list": "📢 <b>قنواتك ومجموعاتك المرتبطة:</b>\n\n",
#         "channel_added": "✅ تم ربط الوجهة بنجاح:\n<b>{}</b>",
#         "channel_deleted": "🗑️ تم إزالة ربط الوجهة بنجاح.",
#         "confirm_delete_channel": "هل أنت متأكد من رغبتك في حذف وإلغاء ربط الوجهة <b>{}</b>؟",
#         "delete_confirm_yes": "🗑️ نعم، احذف الوجهة",
#         "delete_confirm_no": "❌ تراجع وإلغاء",

#         "add_channel_help": (
#             "➕ <b>إضافة وجهة جديدة (قناة أو مجموعة)</b>\n\n"
#             "🔹 <b>الطريقة الأسهل والأسرع:</b>\n"
#             "فقط قم بإضافة البوت مشرفاً (Administrator) في قناتك أو مجموعتك، وسيتم ربطها وتفعيلها **تلقائياً** بصلاحيات النشر! ✅\n\n"
#             "🔹 <b>الطريقة اليدوية:</b>\n"
#             "أرسل معرف الوجهة أو الرابط بهذا الشكل:\n"
#             "• <code>@YourChannelUsername</code>\n"
#             "• <code>https://t.me/YourChannelUsername</code>"
#         ),
#         "channel_private_link": (
#             "❌ <b>عذراً، الروابط الخاصة (Invite Links التي تحتوى على +) غير مدعومة حالياً.</b>\n\n"
#             "قم بإضافة البوت مشرفاً مباشرة في القناة أو المجموعة وسيتم ربطها تلقائياً بكل سهولة."
#         ),
#         "channel_invalid_format": (
#             "⚠️ <b>الصيغة المدخلة غير صحيحة.</b>\n\n"
#             "يرجى إرسال المعرف أو الرابط بشكل صحيح مثل:\n"
#             "• <code>@ChannelName</code>"
#         ),
#         "channel_not_found": (
#             "❌ <b>لم يتم العثور على الوجهة.</b>\n\n"
#             "تأكد من صحة الرابط أو المعرف وأن البوت يمتلك صلاحية الوصول إليها."
#         ),
#         "not_admin": (
#             "❌ <b>البوت ليس مشرفاً (Admin) في هذه الوجهة.</b>\n\n"
#             "يرجى منح البوت صلاحية الإشراف ثم حاول مرة أخرى."
#         ),
#         "not_can_post": (
#             "❌ <b>البوت مشرف ولكن لا يمتلك صلاحية نشر الرسائل.</b>\n\n"
#             "الرجاء الذهاب إلى: إدارة القناة/المجموعة ← المسؤولون ← اختر البوت ← وقم بتفعيل **(نشر الرسائل)**."
#         ),
#         "not_a_channel": "❌ عذراً، هذه الوجهة غير مدعومة (يجب أن تكون قناة عامة أو مجموعة تفاعلية).",

#         "help_text": (
#             "ℹ️ <b>دليل الاستخدام السريع</b>\n\n"
#             "• أضف قناتك أو مجموعتك من قسم «إدارة القنوات والمجموعات» أو أضف البوت مشرفاً مباشرة.\n"
#             "• انقر على «إنشاء منشور جديد» لتصميم منشورك مع إمكانية إضافة أزرار تفاعلية مخصصة (بروابط وأيقونات جميلة).\n"
#             "• اختر الوجهة، أضف النص، الوسائط، والأزرار، ثم عاين منشورك وانشره بكل ثقة 🚀"
#         ),

#         "choose_channel": "📢 <b>اختر الوجهة المستهدفة للنشر:</b>",
#         "no_channel_available": "❌ لا توجد أي قنوات أو مجموعات متاحة للنشر حالياً. يجدر بك إضافة واحدة أولاً.",
#         "send_post_text": (
#             "✍️ أرسل الآن **نص المنشور** المميز الخاص بك.\n\n"
#             "*(يدعم التنسيقات والرموز التعبيرية بحد أقصى 4096 حرف)*"
#         ),
#         "text_too_long": "⚠️ عذراً، النص طويل جداً (الحد الأقصى المسموح هو 4096 حرف).",
#         "text_empty": "⚠️ النص فارغ، يرجى كتابة نص صالح.",
#         "send_media_or_skip": (
#             "📎 يمكنك إرسال **صورة، فيديو، أو ملف مرفق**، أو النقر على زر **«تخطي»** لنشر نص فقط."
#         ),
#         "media_received": "✅ تم استلام الملف والوسائط بنجاح.",
#         "buttons_info": (
#             "🔘 <b>تخصيص أزرار التفاعل الشفافة (Inline Buttons)</b>\n\n"
#             "يمكنك إضافة أزرار أنيقة ومخصصة بالكامل (مثل: زيارة الموقع 🌐، انضمام للقناة 🚀، تواصل معنا 💬).\n\n"
#             "اختر ما يناسبك أدناه:"
#         ),
#         "btn_add_button": "➕ إضافة زر تفاعلي جديد",
#         "button_text_prompt": "أدخل **نص الزر** المطلوب ظهوره للمستخدمين (يمكنك إرفاق رموز تعبيرية جمالية مثل 🔗 أو 🌟):",
#         "button_url_prompt": "أدخل **رابط الزر** (يجب أن يبدأ بـ `https://` أو `http://`):",
#         "button_invalid_url": "⚠️ الرابط المدخل غير صحيح. تأكد أنه يبدأ بـ https://",
#         "button_added": "✅ تم إضافة الزر بنجاح! يمكنك إضافة زر آخر أو الضغط على «إنهاء».",
#         "preview_title": "👀 <b>معاينة شكل المنشور النهائي</b>",
#         "preview_channel": "🎯 الوجهة المستهدفة: <b>{}</b>",
#         "preview_text": "📝 نص المنشور:\n{}",
#         "preview_media": "📎 المرفقات: {}",
#         "preview_buttons": "🔘 الأزرار المخصصة: {}",
#         "publish_confirm": (
#             "هل أنت جاهز لنشر هذا المحتوى بالصيغة أعلاه؟\n\n"
#             "اضغط على زر **«🚀 نشر الآن في الوجهة»** أدناه للتنفيذ الفوري."
#         ),
#         "published": "🎉 تم النشر بنجاح تام في الوجهة المحددة 🚀",
#         "publish_failed": "❌ حدث خطأ أثناء عملية النشر: {}",
#         "cancelled": "❌ تم إلغاء العملية الحالية بنجاح.",

#         "no_posts": "📭 لا توجد أي منشورات سابقة مسجلة في سجلك.",
#         "posts_list": "📋 <b>سجل المنشورات السابقة:</b>\n\n",
#         "post_view": (
#             "📋 <b>تفاصيل المنشور #{id}</b>\n\n"
#             "📝 النص:\n{text}\n\n"
#             "{media_line}"
#             "🕐 تاريخ الإنشاء: {date}"
#         ),
#         "edit_prompt": "✏️ أرسل النص الجديد المعدل للمنشور:",
#         "edit_success": "✅ تم تحديث وتعديل المنشور بنجاح.",
#         "edit_failed": "❌ فشل تعديل المنشور: {}",
#         "edit_no_channel": "❌ عذراً، الوجهة غير مرتبطة أو محذوفة.",
#         "edit_no_message_id": "❌ لا يمكن التعديل المباشر نظراً لفقدان معرّف الرسالة.",

#         "stats_title": "📊 <b>إحصاءات نشاطك الشخصي</b>",
#         "stats_body": (
#             "📢 القنوات والمجموعات: <b>{channels}</b>\n"
#             "📝 المنشورات المنشورة: <b>{posts}</b>"
#         ),

#         "admin_title": "👑 <b>لوحة تحكم المشرف العام</b>",
#         "admin_stats": (
#             "👥 إجمالي المستخدمين: <b>{total}</b>\n"
#             "🟢 النشطون خلال 24 ساعة: <b>{a24}</b>\n"
#             "🟢 النشطون خلال 7 أيام: <b>{a7}</b>\n\n"
#             "📢 إجمالي القنوات والمجموعات: <b>{channels}</b>\n"
#             "📝 إجمالي المنشورات الكلي: <b>{posts}</b>"
#         ),
#         "admin_users": "👥 <b>قائمة آخر المستخدمين المنضمين:</b>\n\n",
#         "admin_user_row": (
#             "• <code>{tid}</code>\n"
#             "  🌐 {lang} · 🕐 {date}\n"
#         ),

#         "auto_added_ok": (
#             "✅ <b>تم ربط الوجهة (قناة/مجموعة) تلقائياً بنجاح!</b>\n\n"
#             "📢 <b>{title}</b>\n"
#             "🔗 <code>{username}</code>\n\n"
#             "🎉 البوت مستعد تماماً للنشر فيها."
#         ),
#         "auto_added_no_post": (
#             "✅ <b>تم ربط الوجهة تلقائياً!</b>\n\n"
#             "📢 <b>{title}</b>\n"
#             "🔗 <code>{username}</code>\n\n"
#             "⚠️ تنبيه: البوت <b>لا يمتلك صلاحية النشر</b> حالياً.\n\n"
#             "يرجى منحه صلاحية (نشر الرسائل) من إعدادات المشرفين."
#         ),
#     },

#     "en": {
#         "main_title": "✨ <b>Advanced Professional Publisher Platform</b> 🚀",
#         "welcome": (
#             "Welcome 👋\n\n"
#             "Easily manage your channels and groups and publish content with style."
#         ),
#         "stats_line": (
#             "📢 Connected Destinations: <b>{channels}</b>\n"
#             "📝 Total Posts: <b>{posts}</b>"
#         ),
#         "choose_language": "🌐 Choose your preferred language:",
#         "language_saved_ar": "✅ Arabic selected.",
#         "language_saved_en": "✅ English selected.",

#         "btn_create_post": "✨ Create New Post",
#         "btn_my_channels": "📢 Manage Destinations",
#         "btn_my_posts": "📋 Posts Archive",
#         "btn_stats": "📊 Statistics",
#         "btn_language": "🌐 Language",
#         "btn_home": "🏠 Main Menu",
#         "btn_help": "ℹ️ Help Guide",
#         "btn_add_channel": "➕ Add Channel/Group",
#         "btn_back": "◀️ Back",
#         "btn_cancel": "❌ Cancel",
#         "btn_skip": "⏭️ Skip",
#         "btn_done": "✅ Done",
#         "btn_publish": "🚀 Publish Now",
#         "btn_preview": "👀 Preview Post",
#         "btn_edit": "✏️ Edit Text",
#         "btn_delete": "🗑️ Delete",

#         "no_channels": (
#             "⚠️ No channels or groups linked yet.\n\n"
#             "Add the bot as an admin to your channel/group or use /addchannel."
#         ),
#         "channel_list": "📢 <b>Your Connected Destinations:</b>\n\n",
#         "channel_added": "✅ Destination linked:\n<b>{}</b>",
#         "channel_deleted": "🗑️ Destination unlinked.",
#         "confirm_delete_channel": "Do you want to unlink <b>{}</b>?",
#         "delete_confirm_yes": "🗑️ Yes, Unlink",
#         "delete_confirm_no": "❌ Cancel",

#         "add_channel_help": (
#             "➕ <b>Add New Destination</b>\n\n"
#             "🔹 <b>Method 1 (Automatic):</b> Add the bot as an admin to your channel or group.\n"
#             "🔹 <b>Method 2 (Manual):</b> Send the username or link like <code>@channel</code>."
#         ),
#         "channel_private_link": "❌ Private invite links are not supported.",
#         "channel_invalid_format": "⚠️ Invalid format. Send a valid username or link.",
#         "channel_not_found": "❌ Destination not found.",
#         "not_admin": "❌ The bot is not an admin in this destination.",
#         "not_can_post": "❌ The bot is an admin but lacks 'Post Messages' permission.",
#         "not_a_channel": "❌ Invalid destination type.",

#         "help_text": "ℹ️ <b>How to use</b>\n\nConnect destinations, create posts with custom buttons, preview and publish!",

#         "choose_channel": "📢 <b>Select target destination:</b>",
#         "no_channel_available": "❌ No available destinations.",
#         "send_post_text": "✍️ Send the post text now (up to 4096 characters).",
#         "text_too_long": "⚠️ Text is too long.",
#         "text_empty": "⚠️ Text is empty.",
#         "send_media_or_skip": "📎 Send photo, video, file or press 'Skip'.",
#         "media_received": "✅ Media received.",
#         "buttons_info": "🔘 <b>Custom Inline Buttons</b>\n\nAdd your custom button texts and URLs below:",
#         "btn_add_button": "➕ Add Custom Button",
#         "button_text_prompt": "Send the button text (with optional emojis):",
#         "button_url_prompt": "Send the button URL (starting with https://):",
#         "button_invalid_url": "⚠️ Invalid URL. Must start with https://",
#         "button_added": "✅ Button added successfully.",
#         "preview_title": "👀 <b>Post Preview</b>",
#         "preview_channel": "🎯 Destination: <b>{}</b>",
#         "preview_text": "📝 Text:\n{}",
#         "preview_media": "📎 Media: {}",
#         "preview_buttons": "🔘 Buttons: {}",
#         "publish_confirm": "Ready to publish? Click '🚀 Publish Now'.",
#         "published": "🎉 Published successfully 🚀",
#         "publish_failed": "❌ Publish failed: {}",
#         "cancelled": "❌ Cancelled.",

#         "no_posts": "📭 No posts found.",
#         "posts_list": "📋 <b>Your Posts:</b>\n\n",
#         "post_view": "📋 <b>Post #{id}</b>\n\n📝 Text:\n{text}\n\n{media_line}🕐 {date}",
#         "edit_prompt": "✏️ Send the new text:",
#         "edit_success": "✅ Post updated.",
#         "edit_failed": "❌ Update failed: {}",
#         "edit_no_channel": "❌ Destination not found.",
#         "edit_no_message_id": "❌ Message ID missing.",

#         "stats_title": "📊 <b>Your Statistics</b>",
#         "stats_body": "📢 Destinations: <b>{channels}</b>\n📝 Posts: <b>{posts}</b>",

#         "admin_title": "👑 <b>Admin Dashboard</b>",
#         "admin_stats": "👥 Total users: <b>{total}</b>\n🟢 Active 24h: <b>{a24}</b>\n🟢 Active 7d: <b>{a7}</b>\n📢 Destinations: <b>{channels}</b>\n📝 Posts: <b>{posts}</b>",
#         "admin_users": "👥 <b>Latest users:</b>\n\n",
#         "admin_user_row": "• <code>{tid}</code>\n  🌐 {lang} · 🕐 {date}\n",

#         "auto_added_ok": "✅ <b>Destination linked automatically!</b>\n\n📢 <b>{title}</b>",
#         "auto_added_no_post": "✅ <b>Destination linked automatically!</b>\n\n⚠️ Bot needs 'Post Messages' permission.",
#     }
# }


# def t(language, key):
#     language = language if language in TEXTS else "ar"
#     return TEXTS[language].get(key, key)


# # =========================================================
# # PARSE CHANNEL / GROUP INPUT
# # =========================================================

# def parse_channel_input(raw: str):
#     if not raw:
#         return None

#     text = raw.strip().strip("/")

#     if "+" in text and "t.me" in text.lower():
#         return None

#     if "joinchat" in text.lower():
#         return None

#     url_patterns = [
#         r"^https?://t\.me/([A-Za-z0-9_]+)/?$",
#         r"^https?://telegram\.me/([A-Za-z0-9_]+)/?$",
#         r"^https?://www\.t\.me/([A-Za-z0-9_]+)/?$",
#         r"^t\.me/([A-Za-z0-9_]+)/?$",
#         r"^telegram\.me/([A-Za-z0-9_]+)/?$",
#     ]

#     for pattern in url_patterns:
#         match = re.match(pattern, text, re.IGNORECASE)
#         if match:
#             return "@" + match.group(1)

#     if text.startswith("@"):
#         username = text[1:]
#         if re.match(r"^[A-Za-z0-9_]{4,32}$", username):
#             return "@" + username
#         return None

#     if re.match(r"^[A-Za-z0-9_]{4,32}$", text):
#         return "@" + text

#     return None


# # =========================================================
# # KEYBOARDS (تصاميم الأزرار ولوحات المفاتيح)
# # =========================================================

# def language_keyboard():
#     return InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text="🇸🇦 العربية (Arabic)",
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
#     return InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text=f"✨ {t(language, 'btn_create_post')}",
#                     callback_data="menu:create"
#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text=f"📢 {t(language, 'btn_my_channels')}",
#                     callback_data="menu:channels"
#                 ),
#                 InlineKeyboardButton(
#                     text=f"📋 {t(language, 'btn_my_posts')}",
#                     callback_data="menu:posts"
#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text=f"📊 {t(language, 'btn_stats')}",
#                     callback_data="menu:stats"
#                 ),
#                 InlineKeyboardButton(
#                     text=f"🌐 {t(language, 'btn_language')}",
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
#     try:
#         await callback.message.edit_text(
#             text=text,
#             reply_markup=reply_markup,
#             disable_web_page_preview=True
#         )
#     except TelegramBadRequest:
#         try:
#             await callback.message.delete()
#         except Exception:
#             pass

#         await callback.message.answer(
#             text=text,
#             reply_markup=reply_markup,
#             disable_web_page_preview=True
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
#             "🌐 <b>Choose your language / اختر لغة البوت:</b>",
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
#         "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
#         f"{t(language, 'welcome')}\n\n"
#         + t(language, "stats_line").format(
#             channels=channels_count,
#             posts=posts_count
#         )
#     )

#     await message.answer(
#         text,
#         reply_markup=main_inline_keyboard(language),
#         disable_web_page_preview=True
#     )

#     await message.answer(
#         "👇 لوحة التحكم السريعة:",
#         reply_markup=main_reply_keyboard(language)
#     )


# # =========================================================
# # LANGUAGE
# # =========================================================

# @dp.callback_query(F.data.startswith("lang_"))
# async def language_callback(callback: CallbackQuery, state: FSMContext):
#     try:
#         await callback.answer()
#     except Exception:
#         pass

#     await state.clear()

#     language = callback.data.replace("lang_", "")

#     if language not in ("ar", "en"):
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
#     try:
#         await callback.answer()
#     except Exception:
#         pass

#     await state.clear()

#     language = get_language(callback.from_user.id)

#     channels_count = len(get_channels(callback.from_user.id))
#     posts_count = get_posts_count(callback.from_user.id)

#     text = (
#         f"{t(language, 'main_title')}\n"
#         "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
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


# @dp.message(F.text.in_(["🏠 الرئيسية", "🏠 Main Menu"]))
# async def home_reply(message: Message, state: FSMContext):
#     await state.clear()
#     language = get_language(message.from_user.id)
#     await send_main_menu(message, language)


# @dp.callback_query(F.data == "menu:language")
# async def menu_language(callback: CallbackQuery, state: FSMContext):
#     try:
#         await callback.answer()
#     except Exception:
#         pass

#     await state.clear()

#     await safe_edit_or_send(
#         callback,
#         "🌐 اختر اللغة / Choose language:",
#         language_keyboard()
#     )


# @dp.callback_query(F.data == "menu:stats")
# async def menu_stats(callback: CallbackQuery, state: FSMContext):
#     try:
#         await callback.answer()
#     except Exception:
#         pass

#     await state.clear()

#     language = get_language(callback.from_user.id)

#     channels_count = len(get_channels(callback.from_user.id))
#     posts_count = get_posts_count(callback.from_user.id)

#     text = (
#         f"{t(language, 'stats_title')}\n"
#         "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
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


# @dp.message(F.text.in_(["📊 الإحصائيات", "📊 Statistics"]))
# async def stats_reply(message: Message, state: FSMContext):
#     await state.clear()

#     language = get_language(message.from_user.id)

#     channels_count = len(get_channels(message.from_user.id))
#     posts_count = get_posts_count(message.from_user.id)

#     text = (
#         f"{t(language, 'stats_title')}\n"
#         "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
#         + t(language, "stats_body").format(
#             channels=channels_count,
#             posts=posts_count
#         )
#     )

#     await message.answer(
#         text,
#         reply_markup=back_home_keyboard(language)
#     )


# @dp.message(F.text.in_(["ℹ️ المساعدة", "ℹ️ Help Guide"]))
# async def help_handler(message: Message, state: FSMContext):
#     await state.clear()
#     language = get_language(message.from_user.id)
#     await message.answer(t(language, "help_text"))


# # =========================================================
# # CHANNELS & GROUPS MANAGEMENT
# # =========================================================

# @dp.message(Command("addchannel"))
# async def addchannel_cmd(message: Message, state: FSMContext):
#     await state.clear()
#     language = get_language(message.from_user.id)
#     await message.answer(
#         t(language, "add_channel_help"),
#         reply_markup=cancel_keyboard(language),
#         disable_web_page_preview=True
#     )
#     await state.set_state(ChannelFlow.waiting_username)


# @dp.message(F.text.in_(["📢 قنواتي", "📢 إدارة القنوات والمجموعات"]))
# async def channels_reply(message: Message, state: FSMContext):
#     await state.clear()
#     language = get_language(message.from_user.id)
#     await show_channels(message, language)


# @dp.callback_query(F.data == "menu:channels")
# async def menu_channels(callback: CallbackQuery, state: FSMContext):
#     try:
#         await callback.answer()
#     except Exception:
#         pass

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
#         return

#     text = t(language, "channel_list")
#     buttons = []

#     for channel in channels:
#         username = channel["username"] or channel["title"]
#         text += f"• <b>{username}</b>\n"
#         buttons.append(
#             [
#                 InlineKeyboardButton(
#                     text=f"🗑️ إزالة ربط: {username}",
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
#                     text=f"🗑️ إزالة ربط: {username}",
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
#     try:
#         await callback.answer()
#     except Exception:
#         pass

#     language = get_language(callback.from_user.id)

#     await safe_edit_or_send(
#         callback,
#         t(language, "add_channel_help"),
#         cancel_keyboard(language)
#     )

#     await state.set_state(ChannelFlow.waiting_username)


# @dp.callback_query(F.data.startswith("channel:del:"))
# async def channel_del_confirm(callback: CallbackQuery):
#     try:
#         await callback.answer()
#     except Exception:
#         pass

#     channel_id = callback.data.split(":", 2)[2]
#     language = get_language(callback.from_user.id)
#     channel = get_channel(callback.from_user.id, channel_id)

#     if not channel:
#         return

#     username = channel["username"] or channel["title"]
#     text = t(language, "confirm_delete_channel").format(username)

#     await safe_edit_or_send(
#         callback,
#         text,
#         confirm_delete_keyboard(language, channel_id)
#     )


# @dp.callback_query(F.data.startswith("channel:delete:"))
# async def channel_delete(callback: CallbackQuery):
#     try:
#         await callback.answer()
#     except Exception:
#         pass

#     channel_id = callback.data.split(":", 2)[2]
#     language = get_language(callback.from_user.id)
#     delete_channel(callback.from_user.id, channel_id)

#     await safe_edit_or_send(
#         callback,
#         t(language, "channel_deleted"),
#         back_home_keyboard(language)
#     )


# # =========================================================
# # RECEIVE CHANNEL / GROUP INPUT
# # =========================================================

# @dp.message(ChannelFlow.waiting_username)
# async def receive_channel_username(
#     message: Message,
#     state: FSMContext
# ):
#     raw = (message.text or "").strip()
#     language = get_language(message.from_user.id)

#     if ("+" in raw and "t.me" in raw.lower()) or "joinchat" in raw.lower():
#         await message.answer(
#             t(language, "channel_private_link"),
#             disable_web_page_preview=True
#         )
#         return

#     username = parse_channel_input(raw)

#     if not username:
#         await message.answer(
#             t(language, "channel_invalid_format"),
#             disable_web_page_preview=True
#         )
#         return

#     try:
#         chat = await bot.get_chat(chat_id=username)

#         # دعم القنوات والمجموعات والمجموعات الخارقة (Groups & Supergroups & Channels)
#         if chat.type not in ("channel", "supergroup", "group"):
#             await message.answer(t(language, "not_a_channel"))
#             return

#         me = await bot.get_me()
#         member = await bot.get_chat_member(
#             chat_id=chat.id,
#             user_id=me.id
#         )

#         if member.status != ChatMemberStatus.ADMINISTRATOR:
#             await message.answer(t(language, "not_admin"))
#             return

#         # فحص الصلاحيات إذا كانت قناة
#         if chat.type == "channel":
#             can_post = getattr(member, "can_post_messages", False)
#             if not can_post:
#                 await message.answer(t(language, "not_can_post"))
#                 return

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
#             "✅ <b>تمت إضافة الوجهة بنجاح تام!</b>\n\n"
#             f"📢 <b>{chat.title or username}</b>\n"
#             f"🔗 <code>{channel_username}</code>",
#             reply_markup=main_reply_keyboard(language),
#             disable_web_page_preview=True
#         )

#     except TelegramBadRequest as e:
#         error_text = str(e).lower()
#         logger.error("TelegramBadRequest verifying %s: %s", username, e)

#         if "chat not found" in error_text:
#             await message.answer(t(language, "channel_not_found"))
#         elif "not enough rights" in error_text:
#             await message.answer("❌ البوت لا يملك صلاحيات كافية.")
#         else:
#             await message.answer(f"❌ <code>{str(e)[:300]}</code>")

#     except Exception:
#         logger.exception("Channel verification failed")
#         await message.answer("❌ حدث خطأ أثناء التحقق. تأكد أن البوت مضاف كمشرف.")


# # =========================================================
# # AUTO-ADD DESTINATION (my_chat_member) للقنوات والمجموعات
# # =========================================================

# @dp.my_chat_member()
# async def on_my_chat_member(update: ChatMemberUpdated):
#     chat = update.chat
#     new_status = update.new_chat_member.status
#     old_status = update.old_chat_member.status

#     if chat.type not in ("channel", "supergroup", "group"):
#         return

#     if (
#         new_status == ChatMemberStatus.ADMINISTRATOR
#         and old_status != ChatMemberStatus.ADMINISTRATOR
#     ):
#         adder = update.from_user
#         if not adder:
#             return

#         user = get_user(adder.id)
#         if not user:
#             return

#         channel_username = (
#             f"@{chat.username}"
#             if chat.username
#             else str(chat.id)
#         )

#         add_channel(
#             telegram_id=adder.id,
#             channel_id=str(chat.id),
#             username=channel_username,
#             title=chat.title or channel_username
#         )

#         log_stat(adder.id, "channel_added_auto", channel_username)
#         language = user["language"]

#         try:
#             note = t(language, "auto_added_ok").format(
#                 title=chat.title or channel_username,
#                 username=channel_username
#             )
#             await bot.send_message(
#                 chat_id=adder.id,
#                 text=note,
#                 disable_web_page_preview=True
#             )
#         except Exception:
#             logger.exception("Could not notify user %s", adder.id)

#     elif new_status in (
#         ChatMemberStatus.LEFT,
#         ChatMemberStatus.KICKED,
#     ):
#         logger.info("Bot removed from destination %s", chat.id)


# # =========================================================
# # CREATE POST FLOW & CUSTOM BUTTONS
# # =========================================================

# @dp.message(F.text.in_(["✨ إنشاء منشور", "✨ إنشاء منشور جديد"]))
# async def create_post_reply(message: Message, state: FSMContext):
#     await state.clear()
#     await start_post_flow(message, state)


# @dp.callback_query(F.data == "menu:create")
# async def create_post_cb(callback: CallbackQuery, state: FSMContext):
#     try:
#         await callback.answer()
#     except Exception:
#         pass

#     await state.clear()
#     await start_post_flow(callback.message, state, from_callback=True)


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
#                     text=f"🎯 {username}",
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
#     reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)

#     if from_callback:
#         try:
#             await message.edit_text(text, reply_markup=reply_markup)
#         except Exception:
#             await message.answer(text, reply_markup=reply_markup)
#     else:
#         await message.answer(text, reply_markup=reply_markup)

#     await state.set_state(PostFlow.choosing_channel)


# @dp.callback_query(PostFlow.choosing_channel, F.data.startswith("post:channel:"))
# async def post_choose_channel(callback: CallbackQuery, state: FSMContext):
#     try:
#         await callback.answer()
#     except Exception:
#         pass

#     channel_id = callback.data.split(":", 2)[2]
#     language = get_language(callback.from_user.id)
#     channel = get_channel(callback.from_user.id, channel_id)

#     if not channel:
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
#     try:
#         await callback.answer()
#     except Exception:
#         pass

#     language = get_language(callback.from_user.id)
#     await ask_buttons(callback.message, state, language, from_callback=callback)


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
#     try:
#         await callback.answer()
#     except Exception:
#         pass

#     language = get_language(callback.from_user.id)
#     await callback.message.answer(
#         t(language, "button_text_prompt"),
#         reply_markup=cancel_keyboard(language)
#     )
#     await state.set_state(ButtonFlow.waiting_text)


# @dp.message(ButtonFlow.waiting_text)
# async def button_receive_text(message: Message, state: FSMContext):
#     language = get_language(message.from_user.id)
#     text = (message.text or "").strip()

#     if not text:
#         await message.answer("⚠️ يرجى إدخال نص صالح للزر.")
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
#     try:
#         await callback.answer()
#     except Exception:
#         pass

#     language = get_language(callback.from_user.id)
#     data = await state.get_data()
#     await show_preview(callback, data, language)
#     await state.set_state(PostFlow.previewing)


# async def show_preview(callback: CallbackQuery, data, language):
#     text = data.get("text") or ""
#     channel = data.get("channel_username") or "—"
#     media_type = data.get("media_type")
#     buttons = data.get("buttons") or []

#     lines = [
#         f"{t(language, 'preview_title')}",
#         "━━━━━━━━━━━━━━━━━━━━━━━━━━",
#         t(language, "preview_channel").format(channel),
#         "",
#         t(language, "preview_text").format(text)
#     ]

#     if media_type:
#         lines.append("")
#         lines.append(t(language, "preview_media").format(media_type))

#     if buttons:
#         lines.append("")
#         button_labels = " · ".join(f"[{b['text']}]" for b in buttons)
#         lines.append(t(language, "preview_buttons").format(button_labels))

#     lines.append("")
#     lines.append(t(language, "publish_confirm"))

#     keyboard = build_inline_keyboard(buttons)
#     # إضافة زر النشر صراحة مع الأزرار المخصصة للمعاينة
#     inline_kb = preview_keyboard(language)
    
#     await safe_edit_or_send(
#         callback,
#         "\n".join(lines),
#         inline_kb
#     )


# @dp.callback_query(PostFlow.previewing, F.data == "flow:publish")
# async def post_publish(callback: CallbackQuery, state: FSMContext):
#     try:
#         await callback.answer()
#     except Exception:
#         pass

#     language = get_language(callback.from_user.id)
#     data = await state.get_data()

#     channel_id = data.get("channel_id")
#     text = data.get("text") or ""
#     media_type = data.get("media_type")
#     media_path = data.get("media_path")
#     buttons = data.get("buttons") or []

#     if not channel_id:
#         return

#     channel = get_channel(callback.from_user.id, channel_id)
#     if not channel:
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

#     except Exception as e:
#         logger.exception("Publish failed")
#         await safe_edit_or_send(
#             callback,
#             t(language, "publish_failed").format(str(e)[:200]),
#             back_home_keyboard(language)
#         )

#     await state.clear()


# async def publish_to_channel(
#     target,
#     text,
#     media_type,
#     media_path,
#     keyboard
# ):
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
#             reply_markup=keyboard,
#             disable_web_page_preview=True
#         )

#     return msg.message_id


# @dp.callback_query(F.data == "flow:cancel")
# async def flow_cancel(callback: CallbackQuery, state: FSMContext):
#     try:
#         await callback.answer()
#     except Exception:
#         pass

#     await state.clear()
#     language = get_language(callback.from_user.id)
#     await safe_edit_or_send(
#         callback,
#         t(language, "cancelled"),
#         back_home_keyboard(language)
#     )


# # =========================================================
# # MY POSTS + EDIT
# # =========================================================

# @dp.message(F.text.in_(["📋 منشوراتي", "📋 أرشيف المنشورات"]))
# async def my_posts_reply(message: Message, state: FSMContext):
#     await state.clear()
#     language = get_language(message.from_user.id)
#     await show_posts(message, language)


# @dp.callback_query(F.data == "menu:posts")
# async def menu_posts(callback: CallbackQuery, state: FSMContext):
#     try:
#         await callback.answer()
#     except Exception:
#         pass

#     await state.clear()
#     language = get_language(callback.from_user.id)
#     posts = get_posts(callback.from_user.id, limit=20)

#     if not posts:
#         await safe_edit_or_send(
#             callback,
#             t(language, "no_posts"),
#             back_home_keyboard(language)
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
#     try:
#         await callback.answer()
#     except Exception:
#         pass

#     await state.clear()
#     post_id = int(callback.data.split(":")[2])
#     language = get_language(callback.from_user.id)
#     post = get_post(callback.from_user.id, post_id)

#     if not post:
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


# @dp.callback_query(F.data.startswith("post:edit:"))
# async def post_edit_start(callback: CallbackQuery, state: FSMContext):
#     try:
#         await callback.answer()
#     except Exception:
#         pass

#     post_id = int(callback.data.split(":")[2])
#     language = get_language(callback.from_user.id)
#     post = get_post(callback.from_user.id, post_id)

#     if not post:
#         return

#     await state.update_data(edit_post_id=post_id)
#     await callback.message.answer(
#         t(language, "edit_prompt"),
#         reply_markup=cancel_keyboard(language)
#     )
#     await state.set_state(EditFlow.waiting_new_text)


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
#         await message.answer(t(language, "edit_no_message_id"))
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
#                 ),
#                 disable_web_page_preview=True
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
#         "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
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

#     try:
#         await bot.delete_webhook(drop_pending_updates=False)
#     except Exception:
#         pass

#     logger.info("Telegram Publisher Bot started successfully (with Groups & Channels & Custom Buttons)")
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
# TRANSLATIONS (دعم 5 لغات: العربية، الإنجليزية، التركية، الصينية، الفرنسية)
# =========================================================

TEXTS = {
    "ar": {
        "main_title": "✨ <b>منصة النشر الاحترافي المتطورة</b> 🚀",
        "welcome": "مرحباً بك أهلاً وسهلاً 👋\n\nقم بإدارة قنواتك ومجموعاتك وانشر محتواك بأيقونات وأزرار تفاعلية مميزة.",
        "stats_line": "📢 القنوات والمجموعات المضافة: <b>{channels}</b>\n📝 إجمالي المنشورات: <b>{posts}</b>",
        "choose_language": "🌐 اختر لغة البوت المفضلة لديك:",
        "language_saved_ar": "✅ تم تفعيل اللغة العربية بنجاح.",
        
        "btn_create_post": "✨ إنشاء منشور جديد",
        "btn_my_channels": "📢 إدارة القنوات والمجموعات",
        "btn_my_posts": "📋 أرشيف المنشورات",
        "btn_stats": "📊 الإحصاءات",
        "btn_language": "🌐 اللغة",
        "btn_about": "👨‍💻 برمجة وتطوير خلدون",
        "btn_home": "🏠 الرئيسية",
        "btn_help": "ℹ️ المساعدة",
        "btn_add_channel": "➕ ربط قناة أو مجموعة",
        "btn_back": "◀️ عودة",
        "btn_cancel": "❌ إلغاء",
        "btn_skip": "⏭️ تخطي",
        "btn_done": "✅ إنهاء الأزرار",
        "btn_publish": "🚀 نشر الآن",
        "btn_preview": "👀 معاينة",
        "btn_edit": "✏️ تعديل",
        "btn_delete": "🗑️ حذف",
        
        "quick_templates": "💡 <b>أيقونات جاهزة سريعة (انقر للاستخدام):</b>",
        "no_channels": "⚠️ عذراً، لا توجد قنوات أو مجموعات مرتبطة.\n\nأضف البوت مشرفاً أو استخدم /addchannel",
        "channel_list": "📢 <b>القنوات والمجموعات المرتبطة:</b>\n\n",
        "channel_added": "✅ تم ربط الوجهة بنجاح:\n<b>{}</b>",
        "channel_deleted": "🗑️ تم إزالة ربط الوجهة.",
        "confirm_delete_channel": "هل تريد إزالة ربط <b>{}</b>؟",
        "delete_confirm_yes": "🗑️ نعم، إزالة",
        "delete_confirm_no": "❌ تراجع",
        
        "add_channel_help": "➕ <b>إضافة وجهة جديدة</b>\n\nأضف البوت مشرفاً (Admin) في قناتك أو مجموعتك وسيتم ربطها تلقائياً ✅\nأو أرسل المعرف مثل: <code>@ChannelName</code>",
        "channel_private_link": "❌ الروابط الخاصة غير مدعومة.",
        "channel_invalid_format": "⚠️ صيغة غير صحيحة. أرسل المعرف بشكل صحيح.",
        "channel_not_found": "❌ لم يتم العثور على الوجهة.",
        "not_admin": "❌ البوت ليس مشرفاً في هذه الوجهة.",
        "not_can_post": "❌ البوت لا يمتلك صلاحية نشر الرسائل.",
        "not_a_channel": "❌ هذه الوجهة غير مدعومة.",
        
        "help_text": "ℹ️ <b>دليل الاستخدام</b>\n\n• اربط قناتك أو مجموعتك.\n• أنشئ منشوراً مع أيقونات تفاعلية (مثل 🚪 دخول، 🌐 زيارة).\n• انشر بكل إتقان 🚀",
        
        "choose_channel": "📢 <b>اختر الوجهة المستهدفة:</b>",
        "no_channel_available": "❌ لا توجد وجهات متاحة للنشر.",
        "send_post_text": "✍️ أرسل نص المنشور الآن (يدعم التنسيق والرموز).",
        "text_too_long": "⚠️ النص طويل جداً (الحد 4096).",
        "text_empty": "⚠️ النص فارغ.",
        "send_media_or_skip": "📎 أرسل صورة، فيديو أو ملف، أو اضغط «تخطي».",
        "media_received": "✅ تم استلام الوسائط.",
        
        "buttons_info": "🔘 <b>تخصيص الأزرار التفاعلية والأيقونات</b>\n\nاختر نص الزر أو الأيقونة التعبيرية (مثل: 🚪 باب مفتوح / دخول، 🚀 انضمام، 🌐 زيارة الموقع) ثم أرسل الرابط.",
        "btn_add_button": "➕ إضافة زر جديد",
        "button_text_prompt": "أدخل نص الزر (يمكنك استخدام ملصقات وأيقونات مثل 🚪 دخول، 🌐 زيارة، 🚀 انضمام):",
        "button_url_prompt": "أدخل رابط الزر (يجب أن يبدأ بـ https://):",
        "button_invalid_url": "⚠️ الرابط يجب أن يبدأ بـ https://",
        "button_added": "✅ تم إضافة الزر بنجاح.",
        
        "preview_title": "👀 <b>معاينة المنشور النهائي</b>",
        "preview_channel": "🎯 الوجهة: <b>{}</b>",
        "preview_text": "📝 النص:\n{}",
        "preview_media": "📎 الوسائط: {}",
        "preview_buttons": "🔘 الأزرار: {}",
        "publish_confirm": "هل تريد النشر الآن؟\n\nاضغط «🚀 نشر الآن».",
        "published": "🎉 تم النشر بنجاح 🚀",
        "publish_failed": "❌ فشل النشر: {}",
        "cancelled": "❌ تم الإلغاء.",
        
        "no_posts": "📭 لا توجد منشورات مسجلة.",
        "posts_list": "📋 <b>سجل المنشورات:</b>\n\n",
        "post_view": "📋 <b>منشور #{id}</b>\n\n📝 النص:\n{text}\n\n{media_line}🕐 {date}",
        "edit_prompt": "✏️ أرسل النص الجديد:",
        "edit_success": "✅ تم التعديل بنجاح.",
        "edit_failed": "❌ فشل التعديل: {}",
        "edit_no_channel": "❌ الوجهة غير مرتبطة.",
        "edit_no_message_id": "❌ مفقود معرف الرسالة.",
        
        "stats_title": "📊 <b>إحصاءاتك الشخصية</b>",
        "stats_body": "📢 القنوات/المجموعات: <b>{channels}</b>\n📝 المنشورات: <b>{posts}</b>",
        
        "admin_title": "👑 <b>لوحة تحكم المشرف</b>",
        "admin_stats": "👥 المستخدمين: <b>{total}</b>\n🟢 نشط 24س: <b>{a24}</b>\n🟢 نشط 7ي: <b>{a7}</b>\n📢 القنوات: <b>{channels}</b>\n📝 المنشورات: <b>{posts}</b>",
        "admin_users": "👥 <b>آخر المستخدمين:</b>\n\n",
        "admin_user_row": "• <code>{tid}</code>\n  🌐 {lang} · 🕐 {date}\n",
        
        "auto_added_ok": "✅ <b>تم ربط الوجهة تلقائياً!</b>\n\n📢 <b>{title}</b>",
        "auto_added_no_post": "✅ <b>تم ربط الوجهة!</b>\n\n⚠️ يجدر تفعيل صلاحية (نشر الرسائل) للبوت.",
        
        "about_text": (
            "👨‍💻 <b>معلومات المطور والبرمجة</b>\n\n"
            "✨ <b>اسم النظام:</b> Telegram Publisher Pro\n"
            "🛠️ <b>البرمجة والتطوير:</b> خلدون نصر\n"
            "🔗 <b>للتواصل المباشر:</b> @KhaldounNasr\n\n"
            "شكراً لاستخدامك نظامنا السحابي المتطور والمدعوم بقواعد بيانات آمنة."
        )
    },
    
    "en": {
        "main_title": "✨ <b>Advanced Professional Publisher</b> 🚀",
        "welcome": "Welcome 👋\n\nManage channels and groups with interactive icons and styled buttons.",
        "stats_line": "📢 Destinations: <b>{channels}</b>\n📝 Posts: <b>{posts}</b>",
        "choose_language": "🌐 Choose language:",
        "language_saved_ar": "✅ English activated.",
        
        "btn_create_post": "✨ Create Post",
        "btn_my_channels": "📢 Destinations",
        "btn_my_posts": "📋 Posts Archive",
        "btn_stats": "📊 Statistics",
        "btn_language": "🌐 Language",
        "btn_about": "👨‍💻 Khaldoun Nasr",
        "btn_home": "🏠 Home",
        "btn_help": "ℹ️ Help",
        "btn_add_channel": "➕ Add Destination",
        "btn_back": "◀️ Back",
        "btn_cancel": "❌ Cancel",
        "btn_skip": "⏭️ Skip",
        "btn_done": "✅ Done",
        "btn_publish": "🚀 Publish Now",
        "btn_preview": "👀 Preview",
        "btn_edit": "✏️ Edit",
        "btn_delete": "🗑️ Delete",
        
        "no_channels": "⚠️ No destinations linked.",
        "channel_list": "📢 <b>Connected Destinations:</b>\n\n",
        "channel_added": "✅ Destination linked:\n<b>{}</b>",
        "channel_deleted": "🗑️ Unlinked.",
        "confirm_delete_channel": "Unlink <b>{}</b>?",
        "delete_confirm_yes": "🗑️ Yes",
        "delete_confirm_no": "❌ Cancel",
        
        "add_channel_help": "➕ Add bot as admin to channel/group.",
        "channel_private_link": "❌ Private links not supported.",
        "channel_invalid_format": "⚠️ Invalid format.",
        "channel_not_found": "❌ Not found.",
        "not_admin": "❌ Bot is not admin.",
        "not_can_post": "❌ Bot cannot post.",
        "not_a_channel": "❌ Invalid destination.",
        
        "help_text": "ℹ️ <b>Help Guide</b>\nConnect destinations and publish posts easily.",
        
        "choose_channel": "📢 <b>Select destination:</b>",
        "no_channel_available": "❌ No destinations.",
        "send_post_text": "✍️ Send post text.",
        "text_too_long": "⚠️ Text too long.",
        "text_empty": "⚠️ Text is empty.",
        "send_media_or_skip": "📎 Send media or skip.",
        "media_received": "✅ Media received.",
        
        "buttons_info": "🔘 <b>Custom Buttons & Icons</b>\nAdd stylized button labels (e.g., 🚪 Open / Enter, 🚀 Join, 🌐 Visit).",
        "btn_add_button": "➕ Add Button",
        "button_text_prompt": "Send button text/icon (e.g., 🚪 Enter, 🚀 Join):",
        "button_url_prompt": "Send URL (starts with https://):",
        "button_invalid_url": "⚠️ Must start with https://",
        "button_added": "✅ Button added.",
        
        "preview_title": "👀 <b>Preview</b>",
        "preview_channel": "🎯 Destination: <b>{}</b>",
        "preview_text": "📝 Text:\n{}",
        "preview_media": "📎 Media: {}",
        "preview_buttons": "🔘 Buttons: {}",
        "publish_confirm": "Ready to publish?",
        "published": "🎉 Published successfully 🚀",
        "publish_failed": "❌ Failed: {}",
        "cancelled": "❌ Cancelled.",
        
        "no_posts": "📭 No posts.",
        "posts_list": "📋 <b>Posts:</b>\n\n",
        "post_view": "📋 <b>Post #{id}</b>\n\n📝 Text:\n{text}\n\n{media_line}🕐 {date}",
        "edit_prompt": "✏️ Send new text:",
        "edit_success": "✅ Updated.",
        "edit_failed": "❌ Failed: {}",
        "edit_no_channel": "❌ Not found.",
        "edit_no_message_id": "❌ Missing message ID.",
        
        "stats_title": "📊 <b>Statistics</b>",
        "stats_body": "📢 Destinations: <b>{channels}</b>\n📝 Posts: <b>{posts}</b>",
        
        "admin_title": "👑 <b>Admin Dashboard</b>",
        "admin_stats": "Users: {total} | Posts: {posts}",
        "admin_users": "👥 <b>Users:</b>\n\n",
        "admin_user_row": "• <code>{tid}</code>\n",
        
        "auto_added_ok": "✅ <b>Linked automatically!</b>",
        "auto_added_no_post": "✅ <b>Linked!</b> Enable post permissions.",
        
        "about_text": "👨‍💻 <b>Developer Info</b>\n\nSystem: Telegram Publisher Pro\nDeveloper: Khaldoun Nasr\nContact: @KhaldounNasr"
    },
    
    "tr": {
        "main_title": "✨ <b>Gelişmiş Profesyonel Yayıncı</b> 🚀",
        "welcome": "Hoş geldiniz 👋\n\nKanallarınızı ve gruplarınızı etkileşimli simgeler ve şık düğmelerle yönetin.",
        "stats_line": "📢 Bağlı Hedefler: <b>{channels}</b>\n📝 Toplam Gönderi: <b>{posts}</b>",
        "choose_language": "🌐 Dil seçin:",
        "language_saved_ar": "✅ Türkçe etkinleştirildi.",
        
        "btn_create_post": "✨ Yeni Gönderi",
        "btn_my_channels": "📢 Hedefleri Yönet",
        "btn_my_posts": "📋 Gönderi Arşivi",
        "btn_stats": "📊 İstatistikler",
        "btn_language": "🌐 Dil",
        "btn_about": "👨‍💻 Geliştirici Khaldoun",
        "btn_home": "🏠 Ana Menü",
        "btn_help": "ℹ️ Yardım",
        "btn_add_channel": "➕ Hedef Ekle",
        "btn_back": "◀️ Geri",
        "btn_cancel": "❌ İptal",
        "btn_skip": "⏭️ Atla",
        "btn_done": "✅ Tamam",
        "btn_publish": "🚀 Şimdi Yayınla",
        "btn_preview": "👀 Önizleme",
        "btn_edit": "✏️ Düzenle",
        "btn_delete": "🗑️ Sil",
        
        "no_channels": "⚠️ Bağlı hedef yok.",
        "channel_list": "📢 <b>Bağlı Hedefler:</b>\n\n",
        "channel_added": "✅ Hedef bağlandı:\n<b>{}</b>",
        "channel_deleted": "🗑️ Bağlantı kesildi.",
        "confirm_delete_channel": "Kaldırılsın mı: <b>{}</b>?",
        "delete_confirm_yes": "🗑️ Evet",
        "delete_confirm_no": "❌ İptal",
        
        "add_channel_help": "➕ Botu kanala/gruba yönetici olarak ekleyin.",
        "channel_private_link": "❌ Özel davet bağlantıları desteklenmez.",
        "channel_invalid_format": "⚠️ Geçersiz biçim.",
        "channel_not_found": "❌ Bulunamadı.",
        "not_admin": "❌ Bot yönetici değil.",
        "not_can_post": "❌ Botun yayın yetkisi yok.",
        "not_a_channel": "❌ Geçersiz hedef.",
        
        "help_text": "ℹ️ <b>Yardım</b>\nHedefleri bağlayın ve gönderileri kolayca yayınlayın.",
        
        "choose_channel": "📢 <b>Hedef seçin:</b>",
        "no_channel_available": "❌ Hedef yok.",
        "send_post_text": "✍️ Gönderi metnini gönderin.",
        "text_too_long": "⚠️ Metin çok uzun.",
        "text_empty": "⚠️ Metin boş.",
        "send_media_or_skip": "📎 Medya gönderin veya 'Atla'ya basın.",
        "media_received": "✅ Medya alındı.",
        
        "buttons_info": "🔘 <b>Özel Düğmeler ve Simgeler</b>\nÖrnek: 🚪 Giriş / Kapı Açık, 🚀 Katıl, 🌐 Ziyaret Et.",
        "btn_add_button": "➕ Düğme Ekle",
        "button_text_prompt": "Düğme metni/simgesi gönderin (örn. 🚪 Giriş, 🚀 Katıl):",
        "button_url_prompt": "URL gönderin (https:// ile başlasın):",
        "button_invalid_url": "⚠️ https:// ile başlamalıdır",
        "button_added": "✅ Düğme eklendi.",
        
        "preview_title": "👀 <b>Önizleme</b>",
        "preview_channel": "🎯 Hedef: <b>{}</b>",
        "preview_text": "📝 Metin:\n{}",
        "preview_media": "📎 Medya: {}",
        "preview_buttons": "🔘 Düğmeler: {}",
        "publish_confirm": "Yayınlamaya hazır mısınız?",
        "published": "🎉 Başarıyla yayınlandı 🚀",
        "publish_failed": "❌ Başarısız: {}",
        "cancelled": "❌ İptal edildi.",
        
        "no_posts": "📭 Gönderi yok.",
        "posts_list": "📋 <b>Gönderiler:</b>\n\n",
        "post_view": "📋 <b>Gönderi #{id}</b>\n\n📝 Metin:\n{text}\n\n{media_line}🕐 {date}",
        "edit_prompt": "✏️ Yeni metni gönderin:",
        "edit_success": "✅ Güncellendi.",
        "edit_failed": "❌ Başarısız: {}",
        "edit_no_channel": "❌ Hedef yok.",
        "edit_no_message_id": "❌ Mesaj ID eksik.",
        
        "stats_title": "📊 <b>İstatistikler</b>",
        "stats_body": "📢 Hedefler: <b>{channels}</b>\n📝 Gönderiler: <b>{posts}</b>",
        
        "admin_title": "👑 <b>Yönetici Paneli</b>",
        "admin_stats": "Kullanıcı: {total} | Gönderi: {posts}",
        "admin_users": "👥 <b>Kullanıcılar:</b>\n\n",
        "admin_user_row": "• <code>{tid}</code>\n",
        
        "auto_added_ok": "✅ <b>Otomatik bağlandı!</b>",
        "auto_added_no_post": "✅ <b>Bağlandı!</b> Yayın izinlerini etkinleştirin.",
        
        "about_text": "👨‍💻 <b>Geliştirici Bilgisi</b>\n\nSistem: Telegram Publisher Pro\nGeliştirici: Khaldoun Nasr\nİletişim: @KhaldounNasr"
    },
    
    "zh": {
        "main_title": "✨ <b>高级专业发布平台</b> 🚀",
        "welcome": "欢迎 👋\n\n使用互动图标和精美按钮轻松管理您的频道和群组。",
        "stats_line": "📢 已连接目标: <b>{channels}</b>\n📝 总帖子: <b>{posts}</b>",
        "choose_language": "🌐 选择语言:",
        "language_saved_ar": "✅ 中文已激活。",
        
        "btn_create_post": "✨ 创建新帖子",
        "btn_my_channels": "📢 管理目标",
        "btn_my_posts": "📋 帖子存档",
        "btn_stats": "📊 统计信息",
        "btn_language": "🌐 语言",
        "btn_about": "👨‍💻 开发者 Khaldoun",
        "btn_home": "🏠 主菜单",
        "btn_help": "ℹ️ 帮助指南",
        "btn_add_channel": "➕ 添加目标",
        "btn_back": "◀️ 返回",
        "btn_cancel": "❌ 取消",
        "btn_skip": "⏭️ 跳过",
        "btn_done": "✅ 完成",
        "btn_publish": "🚀 立即发布",
        "btn_preview": "👀 预览",
        "btn_edit": "✏️ 编辑",
        "btn_delete": "🗑️ 删除",
        
        "no_channels": "⚠️ 暂无连接的目标。",
        "channel_list": "📢 <b>已连接的目标:</b>\n\n",
        "channel_added": "✅ 目标已连接:\n<b>{}</b>",
        "channel_deleted": "🗑️ 已解除连接。",
        "confirm_delete_channel": "确定解除连接 <b>{}</b> 吗？",
        "delete_confirm_yes": "🗑️ 是",
        "delete_confirm_no": "❌ 取消",
        
        "add_channel_help": "➕ 将机器人添加为频道/群组管理员以自动连接。",
        "channel_private_link": "❌ 不支持私密链接。",
        "channel_invalid_format": "⚠️ 格式无效。",
        "channel_not_found": "❌ 未找到目标。",
        "not_admin": "❌ 机器人不是管理员。",
        "not_can_post": "❌ 机器人没有发布权限。",
        "not_a_channel": "❌ 无效的目标类型。",
        
        "help_text": "ℹ️ <b>帮助指南</b>\n连接目标并轻松发布带有自定义图标按钮的内容。",
        
        "choose_channel": "📢 <b>选择目标发布位置:</b>",
        "no_channel_available": "❌ 没有可用的目标。",
        "send_post_text": "✍️ 发送帖子正文。",
        "text_too_long": "⚠️ 文本太长。",
        "text_empty": "⚠️ 文本为空。",
        "send_media_or_skip": "📎 发送媒体或点击“跳过”。",
        "media_received": "✅ 已收到媒体。",
        
        "buttons_info": "🔘 <b>自定义互动按钮与图标</b>\n例如: 🚪 开启 / 进入, 🚀 加入, 🌐 访问网站。",
        "btn_add_button": "➕ 添加按钮",
        "button_text_prompt": "发送按钮文本/图标 (例如 🚪 进入, 🚀 加入):",
        "button_url_prompt": "发送网址 (以 https:// 开头):",
        "button_invalid_url": "⚠️ 网址必须以 https:// 开头",
        "button_added": "✅ 按钮添加成功。",
        
        "preview_title": "👀 <b>预览</b>",
        "preview_channel": "🎯 目标: <b>{}</b>",
        "preview_text": "📝 文本:\n{}",
        "preview_media": "📎 媒体: {}",
        "preview_buttons": "🔘 按钮: {}",
        "publish_confirm": "准备好发布了吗？",
        "published": "🎉 发布成功 🚀",
        "publish_failed": "❌ 发布失败: {}",
        "cancelled": "❌ 已取消。",
        
        "no_posts": "📭 暂无帖子。",
        "posts_list": "📋 <b>帖子列表:</b>\n\n",
        "post_view": "📋 <b>帖子 #{id}</b>\n\n📝 文本:\n{text}\n\n{media_line}🕐 {date}",
        "edit_prompt": "✏️ 发送新文本:",
        "edit_success": "✅ 更新成功。",
        "edit_failed": "❌ 更新失败: {}",
        "edit_no_channel": "❌ 未找到目标。",
        "edit_no_message_id": "❌ 缺少消息ID。",
        
        "stats_title": "📊 <b>统计信息</b>",
        "stats_body": "📢 目标数: <b>{channels}</b>\n📝 帖子数: <b>{posts}</b>",
        
        "admin_title": "👑 <b>管理面板</b>",
        "admin_stats": "用户: {total} | 帖子: {posts}",
        "admin_users": "👥 <b>用户列表:</b>\n\n",
        "admin_user_row": "• <code>{tid}</code>\n",
        
        "auto_added_ok": "✅ <b>已自动连接！</b>",
        "auto_added_no_post": "✅ <b>已连接！</b> 请赋予发布权限。",
        
        "about_text": "👨‍💻 <b>开发者信息</b>\n\n系统: Telegram Publisher Pro\n开发者: Khaldoun Nasr\n联系方式: @KhaldounNasr"
    },
    
    "fr": {
        "main_title": "✨ <b>Plateforme de Publication Pro</b> 🚀",
        "welcome": "Bienvenue 👋\n\nGérez vos canaux et groupes avec des icônes interactives et des boutons élégants.",
        "stats_line": "📢 Destinations: <b>{channels}</b>\n📝 Publications: <b>{posts}</b>",
        "choose_language": "🌐 Choisissez la langue:",
        "language_saved_ar": "✅ Français activé.",
        
        "btn_create_post": "✨ Créer une publication",
        "btn_my_channels": "📢 Gérer les destinations",
        "btn_my_posts": "📋 Archives",
        "btn_stats": "📊 Statistiques",
        "btn_language": "🌐 Langue",
        "btn_about": "👨‍💻 Développeur Khaldoun",
        "btn_home": "🏠 Accueil",
        "btn_help": "ℹ️ Aide",
        "btn_add_channel": "➕ Ajouter une destination",
        "btn_back": "◀️ Retour",
        "btn_cancel": "❌ Annuler",
        "btn_skip": "⏭️ Passer",
        "btn_done": "✅ Terminé",
        "btn_publish": "🚀 Publier",
        "btn_preview": "👀 Aperçu",
        "btn_edit": "✏️ Modifier",
        "btn_delete": "🗑️ Supprimer",
        
        "no_channels": "⚠️ Aucune destination liée.",
        "channel_list": "📢 <b>Destinations liées:</b>\n\n",
        "channel_added": "✅ Destination liée:\n<b>{}</b>",
        "channel_deleted": "🗑️ Dissocié.",
        "confirm_delete_channel": "Dissocier <b>{}</b> ?",
        "delete_confirm_yes": "🗑️ Oui",
        "delete_confirm_no": "❌ Annuler",
        
        "add_channel_help": "➕ Ajoutez le bot en tant qu'admin.",
        "channel_private_link": "❌ Liens privés non pris en charge.",
        "channel_invalid_format": "⚠️ Format invalide.",
        "channel_not_found": "❌ Non trouvé.",
        "not_admin": "❌ Le bot n'est pas admin.",
        "not_can_post": "❌ Le bot ne peut pas publier.",
        "not_a_channel": "❌ Destination invalide.",
        
        "help_text": "ℹ️ <b>Guide d'aide</b>\nConnectez des destinations et publiez facilement.",
        
        "choose_channel": "📢 <b>Sélectionnez la destination:</b>",
        "no_channel_available": "❌ Aucune destination.",
        "send_post_text": "✍️ Envoyez le texte.",
        "text_too_long": "⚠️ Texte trop long.",
        "text_empty": "⚠️ Texte vide.",
        "send_media_or_skip": "📎 Envoyez un média ou passez.",
        "media_received": "✅ Média reçu.",
        
        "buttons_info": "🔘 <b>Boutons et Icônes Personnalisés</b>\nExemple: 🚪 Entrer / Porte ouverte, 🚀 Rejoindre, 🌐 Visiter.",
        "btn_add_button": "➕ Ajouter un bouton",
        "button_text_prompt": "Envoyez le texte/icône (ex: 🚪 Entrer, 🚀 Rejoindre):",
        "button_url_prompt": "Envoyez l'URL (commence par https://):",
        "button_invalid_url": "⚠️ Doit commencer par https://",
        "button_added": "✅ Bouton ajouté.",
        
        "preview_title": "👀 <b>Aperçu</b>",
        "preview_channel": "🎯 Destination: <b>{}</b>",
        "preview_text": "📝 Texte:\n{}",
        "preview_media": "📎 Média: {}",
        "preview_buttons": "🔘 Boutons: {}",
        "publish_confirm": "Prêt à publier ?",
        "published": "🎉 Publié avec succès 🚀",
        "publish_failed": "❌ Échec: {}",
        "cancelled": "❌ Annulé.",
        
        "no_posts": "📭 Pas de publications.",
        "posts_list": "📋 <b>Publications:</b>\n\n",
        "post_view": "📋 <b>Publication #{id}</b>\n\n📝 Texte:\n{text}\n\n{media_line}🕐 {date}",
        "edit_prompt": "✏️ Envoyez le nouveau texte:",
        "edit_success": "✅ Mis à jour.",
        "edit_failed": "❌ Échec: {}",
        "edit_no_channel": "❌ Non trouvé.",
        "edit_no_message_id": "❌ ID manquant.",
        
        "stats_title": "📊 <b>Statistiques</b>",
        "stats_body": "📢 Destinations: <b>{channels}</b>\n📝 Publications: <b>{posts}</b>",
        
        "admin_title": "👑 <b>Panneau Admin</b>",
        "admin_stats": "Utilisateurs: {total} | Posts: {posts}",
        "admin_users": "👥 <b>Utilisateurs:</b>\n\n",
        "admin_user_row": "• <code>{tid}</code>\n",
        
        "auto_added_ok": "✅ <b>Lié automatiquement !</b>",
        "auto_added_no_post": "✅ <b>Lié !</b> Activez les permissions de publication.",
        
        "about_text": "👨‍💻 <b>Informations Développeur</b>\n\nSystème: Telegram Publisher Pro\nDéveloppeur: Khaldoun Nasr\nContact: @KhaldounNasr"
    }
}


def t(language, key):
    language = language if language in TEXTS else "ar"
    return TEXTS[language].get(key, key)


# =========================================================
# PARSE INPUT
# =========================================================

def parse_channel_input(raw: str):
    if not raw:
        return None
    text = raw.strip().strip("/")
    if "+" in text and "t.me" in text.lower():
        return None
    if "joinchat" in text.lower():
        return None

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

    if text.startswith("@"):
        username = text[1:]
        if re.match(r"^[A-Za-z0-9_]{4,32}$", username):
            return "@" + username
        return None

    if re.match(r"^[A-Za-z0-9_]{4,32}$", text):
        return "@" + text

    return None


# =========================================================
# KEYBOARDS (دعم اللغات الخمس + زر المطور + الأيقونات التفاعلية)
# =========================================================

def language_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇸🇦 العربية", callback_data="lang_ar"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
            ],
            [
                InlineKeyboardButton(text="🇹🇷 Türkçe", callback_data="lang_tr"),
                InlineKeyboardButton(text="🇨🇳 中文", callback_data="lang_zh"),
                InlineKeyboardButton(text="🇫🇷 Français", callback_data="lang_fr")
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
            ],
            [
                KeyboardButton(text=t(language, "btn_about"))
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
                    text=f"✨ {t(language, 'btn_create_post')}",
                    callback_data="menu:create"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"📢 {t(language, 'btn_my_channels')}",
                    callback_data="menu:channels"
                ),
                InlineKeyboardButton(
                    text=f"📋 {t(language, 'btn_my_posts')}",
                    callback_data="menu:posts"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"📊 {t(language, 'btn_stats')}",
                    callback_data="menu:stats"
                ),
                InlineKeyboardButton(
                    text=f"🌐 {t(language, 'btn_language')}",
                    callback_data="menu:language"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"👨‍💻 {t(language, 'btn_about')}",
                    callback_data="menu:about"
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
                    text="🚪 [باب مفتوح / دخول]",
                    callback_data="quick:btn_open"
                ),
                InlineKeyboardButton(
                    text="🚀 [انضمام الآن]",
                    callback_data="quick:btn_join"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🌐 [زيارة الموقع]",
                    callback_data="quick:btn_visit"
                ),
                InlineKeyboardButton(
                    text="📥 [تحميل الملف]",
                    callback_data="quick:btn_download"
                )
            ],
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
            "🌐 <b>Choose language / اختر لغة البوت:</b>",
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
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
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
        "👇 لوحة التحكم السريعة:",
        reply_markup=main_reply_keyboard(language)
    )


# =========================================================
# LANGUAGE & ABOUT HANDLERS
# =========================================================

@dp.callback_query(F.data.startswith("lang_"))
async def language_callback(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
    except Exception:
        pass

    await state.clear()
    language = callback.data.replace("lang_", "")
    if language not in ("ar", "en", "tr", "zh", "fr"):
        return

    set_language(callback.from_user.id, language)

    try:
        await callback.message.delete()
    except Exception:
        pass

    msg = t(language, "language_saved_ar")
    await callback.message.answer(
        msg,
        reply_markup=main_reply_keyboard(language)
    )
    await send_main_menu(callback.message, language)


@dp.message(F.text.in_(["🌐 اللغة", "🌐 Language", "🌐 Dil seçin", "🌐 选择语言", "🌐 Langue"]))
async def change_language(message: Message):
    await message.answer(
        "🌐 اختر اللغة / Choose language / Dil seçin / 选择语言 / Langue:",
        reply_markup=language_keyboard()
    )


@dp.message(F.text.in_(["👨‍💻 برمجة وتطوير خلدون", "👨‍💻 Khaldoun Nasr", "👨‍💻 Geliştirici Khaldoun", "👨‍💻 开发者 Khaldoun", "👨‍💻 Développeur Khaldoun"]))
async def about_dev_reply(message: Message, state: FSMContext):
    await state.clear()
    language = get_language(message.from_user.id)
    await message.answer(
        t(language, "about_text"),
        reply_markup=back_home_keyboard(language),
        disable_web_page_preview=True
    )


@dp.callback_query(F.data == "menu:about")
async def menu_about_cb(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
    except Exception:
        pass
    await state.clear()
    language = get_language(callback.from_user.id)
    await safe_edit_or_send(
        callback,
        t(language, "about_text"),
        back_home_keyboard(language)
    )


# =========================================================
# MENU CALLBACKS
# =========================================================

@dp.callback_query(F.data == "menu:home")
async def menu_home(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
    except Exception:
        pass
    await state.clear()
    language = get_language(callback.from_user.id)
    channels_count = len(get_channels(callback.from_user.id))
    posts_count = get_posts_count(callback.from_user.id)

    text = (
        f"{t(language, 'main_title')}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{t(language, 'welcome')}\n\n"
        + t(language, "stats_line").format(
            channels=channels_count,
            posts=posts_count
        )
    )
    await safe_edit_or_send(callback, text, main_inline_keyboard(language))


@dp.message(F.text.in_(["🏠 الرئيسية", "🏠 Home", "🏠 Ana Menü", "🏠 主菜单", "🏠 Accueil"]))
async def home_reply(message: Message, state: FSMContext):
    await state.clear()
    language = get_language(message.from_user.id)
    await send_main_menu(message, language)


@dp.callback_query(F.data == "menu:language")
async def menu_language(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
    except Exception:
        pass
    await state.clear()
    await safe_edit_or_send(callback, "🌐 اختر اللغة / Choose language:", language_keyboard())


@dp.callback_query(F.data == "menu:stats")
async def menu_stats(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
    except Exception:
        pass
    await state.clear()
    language = get_language(callback.from_user.id)
    channels_count = len(get_channels(callback.from_user.id))
    posts_count = get_posts_count(callback.from_user.id)

    text = (
        f"{t(language, 'stats_title')}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + t(language, "stats_body").format(
            channels=channels_count,
            posts=posts_count
        )
    )
    await safe_edit_or_send(callback, text, back_home_keyboard(language))


@dp.message(F.text.in_(["📊 الإحصائيات", "📊 Statistics", "📊 İstatistikler", "📊 统计信息", "📊 Statistiques"]))
async def stats_reply(message: Message, state: FSMContext):
    await state.clear()
    language = get_language(message.from_user.id)
    channels_count = len(get_channels(message.from_user.id))
    posts_count = get_posts_count(message.from_user.id)
    text = (
        f"{t(language, 'stats_title')}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + t(language, "stats_body").format(
            channels=channels_count,
            posts=posts_count
        )
    )
    await message.answer(text, reply_markup=back_home_keyboard(language))


@dp.message(F.text.in_(["ℹ️ المساعدة", "ℹ️ Help", "ℹ️ Yardım", "ℹ️ 帮助指南", "ℹ️ Aide"]))
async def help_handler(message: Message, state: FSMContext):
    await state.clear()
    language = get_language(message.from_user.id)
    await message.answer(t(language, "help_text"))


# =========================================================
# CHANNELS & GROUPS MANAGEMENT
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


@dp.message(F.text.in_(["📢 قنواتي", "📢 إدارة القنوات والمجموعات", "📢 Destinations", "📢 Hedefleri Yönet", "📢 管理目标", "📢 Gérer les destinations"]))
async def channels_reply(message: Message, state: FSMContext):
    await state.clear()
    language = get_language(message.from_user.id)
    await show_channels(message, language)


@dp.callback_query(F.data == "menu:channels")
async def menu_channels(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
    except Exception:
        pass
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
                    [InlineKeyboardButton(text=t(language, "btn_add_channel"), callback_data="channel:add")],
                    [InlineKeyboardButton(text=t(language, "btn_home"), callback_data="menu:home")]
                ]
            )
        )
        return

    text = t(language, "channel_list")
    buttons = []
    for channel in channels:
        username = channel["username"] or channel["title"]
        text += f"• <b>{username}</b>\n"
        buttons.append([InlineKeyboardButton(text=f"🗑️ إزالة ربط: {username}", callback_data=f"channel:del:{channel['channel_id']}")])

    buttons.append([InlineKeyboardButton(text=t(language, "btn_add_channel"), callback_data="channel:add")])
    buttons.append([InlineKeyboardButton(text=t(language, "btn_home"), callback_data="menu:home")])

    await safe_edit_or_send(callback, text, InlineKeyboardMarkup(inline_keyboard=buttons))


async def show_channels(message: Message, language):
    channels = get_channels(message.from_user.id)
    if not channels:
        await message.answer(
            t(language, "no_channels"),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text=t(language, "btn_add_channel"), callback_data="channel:add")]]
            )
        )
        return

    text = t(language, "channel_list")
    buttons = []
    for channel in channels:
        username = channel["username"] or channel["title"]
        text += f"• <b>{username}</b>\n"
        buttons.append([InlineKeyboardButton(text=f"🗑️ إزالة ربط: {username}", callback_data=f"channel:del:{channel['channel_id']}")])

    buttons.append([InlineKeyboardButton(text=t(language, "btn_add_channel"), callback_data="channel:add")])
    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


@dp.callback_query(F.data == "channel:add")
async def channel_add_cb(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
    except Exception:
        pass
    language = get_language(callback.from_user.id)
    await safe_edit_or_send(callback, t(language, "add_channel_help"), cancel_keyboard(language))
    await state.set_state(ChannelFlow.waiting_username)


@dp.callback_query(F.data.startswith("channel:del:"))
async def channel_del_confirm(callback: CallbackQuery):
    try:
        await callback.answer()
    except Exception:
        pass
    channel_id = callback.data.split(":", 2)[2]
    language = get_language(callback.from_user.id)
    channel = get_channel(callback.from_user.id, channel_id)
    if not channel:
        return
    username = channel["username"] or channel["title"]
    text = t(language, "confirm_delete_channel").format(username)
    await safe_edit_or_send(callback, text, confirm_delete_keyboard(language, channel_id))


@dp.callback_query(F.data.startswith("channel:delete:"))
async def channel_delete(callback: CallbackQuery):
    try:
        await callback.answer()
    except Exception:
        pass
    channel_id = callback.data.split(":", 2)[2]
    language = get_language(callback.from_user.id)
    delete_channel(callback.from_user.id, channel_id)
    await safe_edit_or_send(callback, t(language, "channel_deleted"), back_home_keyboard(language))


@dp.message(ChannelFlow.waiting_username)
async def receive_channel_username(message: Message, state: FSMContext):
    raw = (message.text or "").strip()
    language = get_language(message.from_user.id)

    if ("+" in raw and "t.me" in raw.lower()) or "joinchat" in raw.lower():
        await message.answer(t(language, "channel_private_link"), disable_web_page_preview=True)
        return

    username = parse_channel_input(raw)
    if not username:
        await message.answer(t(language, "channel_invalid_format"), disable_web_page_preview=True)
        return

    try:
        chat = await bot.get_chat(chat_id=username)
        if chat.type not in ("channel", "supergroup", "group"):
            await message.answer(t(language, "not_a_channel"))
            return

        me = await bot.get_me()
        member = await bot.get_chat_member(chat_id=chat.id, user_id=me.id)

        if member.status != ChatMemberStatus.ADMINISTRATOR:
            await message.answer(t(language, "not_admin"))
            return

        if chat.type == "channel":
            can_post = getattr(member, "can_post_messages", False)
            if not can_post:
                await message.answer(t(language, "not_can_post"))
                return

        channel_username = f"@{chat.username}" if chat.username else username
        add_channel(
            telegram_id=message.from_user.id,
            channel_id=str(chat.id),
            username=channel_username,
            title=chat.title or username
        )
        log_stat(message.from_user.id, "channel_added", channel_username)
        await state.clear()

        await message.answer(
            "✅ <b>تمت إضافة الوجهة بنجاح تام!</b>\n\n"
            f"📢 <b>{chat.title or username}</b>\n"
            f"🔗 <code>{channel_username}</code>",
            reply_markup=main_reply_keyboard(language),
            disable_web_page_preview=True
        )
    except TelegramBadRequest as e:
        error_text = str(e).lower()
        if "chat not found" in error_text:
            await message.answer(t(language, "channel_not_found"))
        else:
            await message.answer(f"❌ <code>{str(e)[:300]}</code>")
    except Exception:
        await message.answer("❌ حدث خطأ أثناء التحقق.")


@dp.my_chat_member()
async def on_my_chat_member(update: ChatMemberUpdated):
    chat = update.chat
    new_status = update.new_chat_member.status
    old_status = update.old_chat_member.status

    if chat.type not in ("channel", "supergroup", "group"):
        return

    if new_status == ChatMemberStatus.ADMINISTRATOR and old_status != ChatMemberStatus.ADMINISTRATOR:
        adder = update.from_user
        if not adder:
            return
        user = get_user(adder.id)
        if not user:
            return

        channel_username = f"@{chat.username}" if chat.username else str(chat.id)
        add_channel(
            telegram_id=adder.id,
            channel_id=str(chat.id),
            username=channel_username,
            title=chat.title or channel_username
        )
        log_stat(adder.id, "channel_added_auto", channel_username)
        language = user["language"]

        try:
            note = t(language, "auto_added_ok").format(title=chat.title or channel_username, username=channel_username)
            await bot.send_message(chat_id=adder.id, text=note, disable_web_page_preview=True)
        except Exception:
            pass


# =========================================================
# CREATE POST FLOW & CUSTOM BUTTONS WITH STICKERS/ICONS
# =========================================================

@dp.message(F.text.in_(["✨ إنشاء منشور", "✨ إنشاء منشور جديد", "✨ Create Post", "✨ Yeni Gönderi", "✨ 创建新帖子", "✨ Créer une publication"]))
async def create_post_reply(message: Message, state: FSMContext):
    await state.clear()
    await start_post_flow(message, state)


@dp.callback_query(F.data == "menu:create")
async def create_post_cb(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
    except Exception:
        pass
    await state.clear()
    await start_post_flow(callback.message, state, from_callback=True)


async def start_post_flow(message: Message, state: FSMContext, from_callback=False):
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
        buttons.append([InlineKeyboardButton(text=f"🎯 {username}", callback_data=f"post:channel:{channel['channel_id']}")])

    buttons.append([InlineKeyboardButton(text=t(language, "btn_cancel"), callback_data="flow:cancel")])
    text = t(language, "choose_channel")
    reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    if from_callback:
        try:
            await message.edit_text(text, reply_markup=reply_markup)
        except Exception:
            await message.answer(text, reply_markup=reply_markup)
    else:
        await message.answer(text, reply_markup=reply_markup)

    await state.set_state(PostFlow.choosing_channel)


@dp.callback_query(PostFlow.choosing_channel, F.data.startswith("post:channel:"))
async def post_choose_channel(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
    except Exception:
        pass
    channel_id = callback.data.split(":", 2)[2]
    language = get_language(callback.from_user.id)
    channel = get_channel(callback.from_user.id, channel_id)
    if not channel:
        return

    await state.update_data(
        channel_id=channel_id,
        channel_username=channel["username"] or channel["title"],
        text=None,
        media_type=None,
        media_path=None,
        buttons=[]
    )
    await safe_edit_or_send(callback, t(language, "send_post_text"), cancel_keyboard(language))
    await state.set_state(PostFlow.waiting_text)


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
    await message.answer(t(language, "send_media_or_skip"), reply_markup=skip_keyboard(language))
    await state.set_state(PostFlow.waiting_media)


@dp.message(PostFlow.waiting_media, F.photo)
async def post_receive_photo(message: Message, state: FSMContext):
    language = get_language(message.from_user.id)
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    path = UPLOAD_DIR / f"{photo.file_unique_id}.jpg"
    await bot.download_file(file.file_path, destination=path)

    await state.update_data(media_type="photo", media_path=str(path))
    await message.answer(t(language, "media_received"), reply_markup=cancel_keyboard(language))
    await ask_buttons(message, state, language)


@dp.message(PostFlow.waiting_media, F.video)
async def post_receive_video(message: Message, state: FSMContext):
    language = get_language(message.from_user.id)
    video = message.video
    file = await bot.get_file(video.file_id)
    ext = (video.file_name or "video.mp4").split(".")[-1]
    path = UPLOAD_DIR / f"{video.file_unique_id}.{ext}"
    await bot.download_file(file.file_path, destination=path)

    await state.update_data(media_type="video", media_path=str(path))
    await message.answer(t(language, "media_received"), reply_markup=cancel_keyboard(language))
    await ask_buttons(message, state, language)


@dp.message(PostFlow.waiting_media, F.document)
async def post_receive_document(message: Message, state: FSMContext):
    language = get_language(message.from_user.id)
    doc = message.document
    file = await bot.get_file(doc.file_id)
    ext = (doc.file_name or "file.bin").split(".")[-1]
    path = UPLOAD_DIR / f"{doc.file_unique_id}.{ext}"
    await bot.download_file(file.file_path, destination=path)

    await state.update_data(media_type="document", media_path=str(path))
    await message.answer(t(language, "media_received"), reply_markup=cancel_keyboard(language))
    await ask_buttons(message, state, language)


@dp.callback_query(PostFlow.waiting_media, F.data == "flow:skip_media")
async def post_skip_media(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
    except Exception:
        pass
    language = get_language(callback.from_user.id)
    await ask_buttons(callback.message, state, language, from_callback=callback)


async def ask_buttons(message: Message, state: FSMContext, language, from_callback=None):
    await state.update_data(buttons=[])
    text = t(language, "buttons_info")
    if from_callback:
        await safe_edit_or_send(from_callback, text, buttons_keyboard(language))
    else:
        await message.answer(text, reply_markup=buttons_keyboard(language))
    await state.set_state(PostFlow.waiting_buttons)


# اختصارات سريعة للأيقونات والأزرار التفاعلية الجاهزة (باب مفتوح/دخول، انضمام، زيارة، تحميل)
@dp.callback_query(PostFlow.waiting_buttons, F.data.startswith("quick:"))
async def quick_button_handler(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
    except Exception:
        pass
    action = callback.data.replace("quick:", "")
    language = get_language(callback.from_user.id)
    
    presets = {
        "btn_open": "🚪 باب مفتوح / دخول",
        "btn_join": "🚀 انضمام الآن",
        "btn_visit": "🌐 زيارة الموقع",
        "btn_download": "📥 تحميل الملف"
    }
    
    btn_text = presets.get(action, "🔗 رابط تفاعلي")
    await state.update_data(button_text=btn_text)
    
    await callback.message.answer(
        t(language, "button_url_prompt"),
        reply_markup=cancel_keyboard(language)
    )
    await state.set_state(ButtonFlow.waiting_url)


@dp.callback_query(PostFlow.waiting_buttons, F.data == "flow:add_button")
async def post_add_button(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
    except Exception:
        pass
    language = get_language(callback.from_user.id)
    await callback.message.answer(
        t(language, "button_text_prompt"),
        reply_markup=cancel_keyboard(language)
    )
    await state.set_state(ButtonFlow.waiting_text)


@dp.message(ButtonFlow.waiting_text)
async def button_receive_text(message: Message, state: FSMContext):
    language = get_language(message.from_user.id)
    text = (message.text or "").strip()
    if not text:
        await message.answer("⚠️ يرجى إدخال نص صالح للزر.")
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
    try:
        await callback.answer()
    except Exception:
        pass
    language = get_language(callback.from_user.id)
    data = await state.get_data()
    await show_preview(callback, data, language)
    await state.set_state(PostFlow.previewing)


async def show_preview(callback: CallbackQuery, data, language):
    text = data.get("text") or ""
    channel = data.get("channel_username") or "—"
    media_type = data.get("media_type")
    buttons = data.get("buttons") or []

    lines = [
        f"{t(language, 'preview_title')}",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        t(language, "preview_channel").format(channel),
        "",
        t(language, "preview_text").format(text)
    ]

    if media_type:
        lines.append("")
        lines.append(t(language, "preview_media").format(media_type))

    if buttons:
        lines.append("")
        button_labels = " · ".join(f"[{b['text']}]" for b in buttons)
        lines.append(t(language, "preview_buttons").format(button_labels))

    lines.append("")
    lines.append(t(language, "publish_confirm"))

    inline_kb = preview_keyboard(language)
    await safe_edit_or_send(callback, "\n".join(lines), inline_kb)


@dp.callback_query(PostFlow.previewing, F.data == "flow:publish")
async def post_publish(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
    except Exception:
        pass

    language = get_language(callback.from_user.id)
    data = await state.get_data()

    channel_id = data.get("channel_id")
    text = data.get("text") or ""
    media_type = data.get("media_type")
    media_path = data.get("media_path")
    buttons = data.get("buttons") or []

    if not channel_id:
        return

    channel = get_channel(callback.from_user.id, channel_id)
    if not channel:
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
        await safe_edit_or_send(callback, t(language, "published"), back_home_keyboard(language))
    except Exception as e:
        logger.exception("Publish failed")
        await safe_edit_or_send(callback, t(language, "publish_failed").format(str(e)[:200]), back_home_keyboard(language))

    await state.clear()


async def publish_to_channel(target, text, media_type, media_path, keyboard):
    if media_type == "photo":
        msg = await bot.send_photo(chat_id=target, photo=FSInputFile(media_path), caption=text[:1024] if text else None, reply_markup=keyboard)
    elif media_type == "video":
        msg = await bot.send_video(chat_id=target, video=FSInputFile(media_path), caption=text[:1024] if text else None, reply_markup=keyboard)
    elif media_type == "document":
        msg = await bot.send_document(chat_id=target, document=FSInputFile(media_path), caption=text[:1024] if text else None, reply_markup=keyboard)
    else:
        msg = await bot.send_message(chat_id=target, text=text, reply_markup=keyboard, disable_web_page_preview=True)
    return msg.message_id


@dp.callback_query(F.data == "flow:cancel")
async def flow_cancel(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
    except Exception:
        pass
    await state.clear()
    language = get_language(callback.from_user.id)
    await safe_edit_or_send(callback, t(language, "cancelled"), back_home_keyboard(language))


# =========================================================
# MY POSTS + EDIT
# =========================================================

@dp.message(F.text.in_(["📋 منشوراتي", "📋 أرشيف المنشورات", "📋 Posts Archive", "📋 Gönderi Arşivi", "📋 帖子存档", "📋 Archives"]))
async def my_posts_reply(message: Message, state: FSMContext):
    await state.clear()
    language = get_language(message.from_user.id)
    await show_posts(message, language)


@dp.callback_query(F.data == "menu:posts")
async def menu_posts(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
    except Exception:
        pass
    await state.clear()
    language = get_language(callback.from_user.id)
    posts = get_posts(callback.from_user.id, limit=20)

    if not posts:
        await safe_edit_or_send(callback, t(language, "no_posts"), back_home_keyboard(language))
        return

    buttons = []
    for post in posts:
        preview = (post["text"] or "")[:30].replace("\n", " ")
        label = f"#{post['id']} · {preview or '📎'}"
        buttons.append([InlineKeyboardButton(text=label[:60], callback_data=f"post:view:{post['id']}")])

    buttons.append([InlineKeyboardButton(text=t(language, "btn_home"), callback_data="menu:home")])
    await safe_edit_or_send(callback, t(language, "posts_list"), InlineKeyboardMarkup(inline_keyboard=buttons))


async def show_posts(message: Message, language):
    posts = get_posts(message.from_user.id, limit=20)
    if not posts:
        await message.answer(t(language, "no_posts"), reply_markup=back_home_keyboard(language))
        return

    buttons = []
    for post in posts:
        preview = (post["text"] or "")[:30].replace("\n", " ")
        label = f"#{post['id']} · {preview or '📎'}"
        buttons.append([InlineKeyboardButton(text=label[:60], callback_data=f"post:view:{post['id']}")])

    await message.answer(t(language, "posts_list"), reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


@dp.callback_query(F.data.startswith("post:view:"))
async def post_view(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
    except Exception:
        pass
    await state.clear()
    post_id = int(callback.data.split(":")[2])
    language = get_language(callback.from_user.id)
    post = get_post(callback.from_user.id, post_id)
    if not post:
        return

    text = post["text"] or "—"
    media_line = f"📎 {post['media_type']}\n\n" if post["media_type"] else ""
    body = t(language, "post_view").format(id=post["id"], text=text[:500], media_line=media_line, date=format_date(post["created_at"]))

    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(language, "btn_edit"), callback_data=f"post:edit:{post['id']}")],
            [InlineKeyboardButton(text=t(language, "btn_back"), callback_data="menu:posts")]
        ]
    )
    await safe_edit_or_send(callback, body, buttons)


@dp.callback_query(F.data.startswith("post:edit:"))
async def post_edit_start(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
    except Exception:
        pass
    post_id = int(callback.data.split(":")[2])
    language = get_language(callback.from_user.id)
    post = get_post(callback.from_user.id, post_id)
    if not post:
        return

    await state.update_data(edit_post_id=post_id)
    await callback.message.answer(t(language, "edit_prompt"), reply_markup=cancel_keyboard(language))
    await state.set_state(EditFlow.waiting_new_text)


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
            await bot.edit_message_caption(chat_id=channel["channel_id"], message_id=message_id, caption=new_text[:1024])
        else:
            await bot.edit_message_text(
                chat_id=channel["channel_id"],
                message_id=message_id,
                text=new_text,
                reply_markup=build_inline_keyboard(json.loads(post["buttons"] or "[]")),
                disable_web_page_preview=True
            )

        update_post_text(message.from_user.id, post_id, new_text)
        log_stat(message.from_user.id, "post_edited", str(post_id))
        await message.answer(t(language, "edit_success"), reply_markup=back_home_keyboard(language))
    except Exception as e:
        await message.answer(t(language, "edit_failed").format(str(e)[:200]))

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
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
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
        text += t("ar", "admin_user_row").format(tid=u["telegram_id"], lang=u["language"], date=format_date(u["created_id"] if "created_id" in u else u["created_at"]))
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
    try:
        await bot.delete_webhook(drop_pending_updates=False)
    except Exception:
        pass

    logger.info("Telegram Publisher Bot started successfully with 5 languages & custom interactive icons!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped manually")
