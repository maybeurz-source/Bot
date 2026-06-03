# ============================================================
#   Professional Telegram File Share Bot
#   Deploy anywhere: Railway / Render / Oracle / Termux
#   Author: @RdxT3ch
# ============================================================

import json, os, uuid, logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, CallbackQueryHandler
)

# ─────────────────────────────────────────
#   CONFIG — reads from environment variables
#   (Set these on Railway / Render / VPS)
# ─────────────────────────────────────────
BOT_TOKEN    = os.environ.get("BOT_TOKEN",    "8781212130:AAHLFgSv0a4y8UXg6EaxOW5H4HboqD4KJzA")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "RdxFileProviderBot")
ADMIN_ID     = int(os.environ.get("ADMIN_ID", "7724021164"))
DB_FILE      = "files_db.json"
LOG_FILE     = "bot.log"

FILE_CAPTION = (
    "◕ Pre๓ium/Pró Features Unl●cked\n"
    "◕ All Ads Removed / Adfree\n"
    "◕ Compatible for all Devices\n"
    "◕ Optimized & Resources Cleaned\n"
    "◕ All Debug Info Removed\n"
    "﹌﹌﹌﹌﹌﹌﹌﹌﹌﹌﹌﹌﹌﹌\n"
    "﻿❪ ⌗ Share & Support ~ @RdxT3ch ❫"
)

# ─────────────────────────────────────────
#   LOGGING
# ─────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────
#   IN-MEMORY DATABASE
# ─────────────────────────────────────────
_cache: dict = {}

def load_db() -> dict:
    global _cache
    if _cache:
        return _cache
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            _cache = json.load(f)
    return _cache

def save_db(db: dict):
    global _cache
    _cache = db
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

def create_entry(file_data: dict) -> tuple[str, str]:
    db = load_db()
    key = str(uuid.uuid4())[:8]
    file_data["uploaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db[key] = file_data
    save_db(db)
    return key, f"https://t.me/{BOT_USERNAME}?start={key}"

# ─────────────────────────────────────────
#   HELPERS
# ─────────────────────────────────────────
def extract_file(message) -> dict | None:
    if message.document:
        return {"file_id": message.document.file_id, "type": "document",
                "name": message.document.file_name or "File",
                "size": message.document.file_size or 0}
    if message.photo:
        return {"file_id": message.photo[-1].file_id, "type": "photo",
                "name": "Photo", "size": 0}
    if message.video:
        return {"file_id": message.video.file_id, "type": "video",
                "name": message.video.file_name or "Video",
                "size": message.video.file_size or 0}
    if message.audio:
        return {"file_id": message.audio.file_id, "type": "audio",
                "name": message.audio.title or "Audio",
                "size": message.audio.file_size or 0}
    return None

async def send_file(context, chat_id: int, fd: dict):
    fid, ft = fd["file_id"], fd["type"]
    cap = FILE_CAPTION
    if ft == "document":
        await context.bot.send_document(chat_id=chat_id, document=fid, caption=cap)
    elif ft == "photo":
        await context.bot.send_photo(chat_id=chat_id, photo=fid, caption=cap)
    elif ft == "video":
        await context.bot.send_video(chat_id=chat_id, video=fid, caption=cap)
    elif ft == "audio":
        await context.bot.send_audio(chat_id=chat_id, audio=fid, caption=cap)

def fmt_size(b: int) -> str:
    if b == 0: return "N/A"
    for u in ["B","KB","MB","GB"]:
        if b < 1024: return f"{b:.1f} {u}"
        b /= 1024
    return f"{b:.1f} TB"

# ─────────────────────────────────────────
#   COMMANDS
# ─────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    user = update.effective_user
    if args:
        key = args[0]
        db  = load_db()
        if key in db:
            fd   = db[key]
            wait = await update.message.reply_text("⏳ Fetching your file, please wait...")
            try:
                await send_file(context, update.effective_chat.id, fd)
                await wait.delete()
            except Exception as e:
                await wait.edit_text(f"❌ Error: {e}")
        else:
            await update.message.reply_text(
                "❌ *File not found!*\nThis link may have expired or been removed.",
                parse_mode="Markdown")
        return
    kb = [[InlineKeyboardButton("📢 Join Channel", url="https://t.me/MODxRDX")]]
    await update.message.reply_text(
        f"👋 *Welcome, {user.first_name}!*\n\n"
        "This bot delivers premium files shared by the admin.\n\n"
        "📌 Click a shared link to receive your file.\n"
        "📢 Join our channel for more updates!",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb)
    )

async def cmd_myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🆔 *Your Telegram ID:*\n`{update.effective_user.id}`",
        parse_mode="Markdown")

async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    db = load_db()
    types = {"document":0,"photo":0,"video":0,"audio":0}
    for v in db.values():
        t = v.get("type","document")
        if t in types: types[t] += 1
    await update.message.reply_text(
        f"📊 *Bot Statistics*\n\n"
        f"📁 Total Files : `{len(db)}`\n"
        f"📄 Documents   : `{types['document']}`\n"
        f"🖼️ Photos      : `{types['photo']}`\n"
        f"🎬 Videos      : `{types['video']}`\n"
        f"🎵 Audio       : `{types['audio']}`",
        parse_mode="Markdown")

async def cmd_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    db = load_db()
    if not db:
        await update.message.reply_text("📭 No files saved yet."); return
    lines = []
    for key, data in list(db.items())[-10:]:
        lines.append(f"📁 *{data['name']}*\n🔗 `https://t.me/{BOT_USERNAME}?start={key}`")
    await update.message.reply_text(
        "📋 *Last 10 Files:*\n\n" + "\n\n".join(lines),
        parse_mode="Markdown")

async def cmd_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args:
        await update.message.reply_text("Usage: `/delete <key>`", parse_mode="Markdown"); return
    db = load_db()
    key = context.args[0]
    if key in db:
        name = db[key].get("name", key)
        del db[key]; save_db(db)
        await update.message.reply_text(f"🗑️ Deleted: *{name}*", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Key not found.")

async def cmd_deleteall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    kb = [[
        InlineKeyboardButton("✅ Yes, Delete All", callback_data="confirm_deleteall"),
        InlineKeyboardButton("❌ Cancel",           callback_data="cancel_deleteall")
    ]]
    await update.message.reply_text(
        "⚠️ *Are you sure?*\nThis will delete ALL saved file links.",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

async def callback_deleteall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.from_user.id != ADMIN_ID: return
    if q.data == "confirm_deleteall":
        save_db({})
        await q.edit_message_text("🗑️ All file links deleted.")
    else:
        await q.edit_message_text("✅ Cancelled.")

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    await update.message.reply_text(
        "🛠️ *Admin Commands*\n\n"
        "/list        — View last 10 files\n"
        "/stats       — Bot statistics\n"
        "/delete `<key>` — Delete a file link\n"
        "/deleteall   — Delete all links\n"
        "/myid        — Get your Telegram ID\n"
        "/help        — Show this message\n\n"
        "📤 *Upload Methods:*\n"
        "• Send file directly to this bot\n"
        "• Upload to your linked channel",
        parse_mode="Markdown")

# ─────────────────────────────────────────
#   FILE HANDLERS
# ─────────────────────────────────────────
async def channel_post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.channel_post
    if not msg: return
    fd = extract_file(msg)
    if not fd: return
    key, link = create_entry(fd)
    log.info(f"Channel upload | {fd['name']} | key={key}")
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(f"✅ *File Saved!*\n\n"
                  f"📁 *Name:* {fd['name']}\n"
                  f"📦 *Size:* {fmt_size(fd['size'])}\n"
                  f"🗂️ *Type:* {fd['type'].capitalize()}\n"
                  f"🔑 *Key:*  `{key}`\n\n"
                  f"🔗 *Share Link:*\n`{link}`"),
            parse_mode="Markdown")
    except Exception as e:
        log.error(f"Admin DM failed: {e}")

async def direct_upload_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Only admin can upload files."); return
    fd = extract_file(update.message)
    if not fd:
        await update.message.reply_text("⚠️ Send a file, photo, video, or audio."); return
    key, link = create_entry(fd)
    log.info(f"Direct upload | {fd['name']} | key={key}")
    await update.message.reply_text(
        f"✅ *File Saved!*\n\n"
        f"📁 *Name:* {fd['name']}\n"
        f"📦 *Size:* {fmt_size(fd['size'])}\n"
        f"🗂️ *Type:* {fd['type'].capitalize()}\n"
        f"🔑 *Key:*  `{key}`\n\n"
        f"🔗 *Share Link:*\n`{link}`",
        parse_mode="Markdown")

# ─────────────────────────────────────────
#   MAIN
# ─────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",     cmd_start))
    app.add_handler(CommandHandler("myid",      cmd_myid))
    app.add_handler(CommandHandler("stats",     cmd_stats))
    app.add_handler(CommandHandler("list",      cmd_list))
    app.add_handler(CommandHandler("delete",    cmd_delete))
    app.add_handler(CommandHandler("deleteall", cmd_deleteall))
    app.add_handler(CommandHandler("help",      cmd_help))
    app.add_handler(CallbackQueryHandler(callback_deleteall,
                    pattern="^(confirm|cancel)_deleteall$"))
    app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POSTS, channel_post_handler))
    app.add_handler(MessageHandler(
        filters.ChatType.PRIVATE & (
            filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO),
        direct_upload_handler))

    log.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    log.info("  Bot started ✅")
    log.info(f"  Admin : {ADMIN_ID}")
    log.info(f"  Bot   : @{BOT_USERNAME}")
    log.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        poll_interval=0.1,
        timeout=10
    )

if __name__ == "__main__":
    main()
