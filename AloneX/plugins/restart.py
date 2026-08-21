# Copyright (c) 2026 THE ARCHON 
# Licensed under the MIT License.
# This file is part of MahiMusic
# DEVELOPER - THE ARCHON 

import os
import sys
import shutil
import asyncio

from pyrogram import filters, types
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from AloneX import app, db, lang, stop


@app.on_message(filters.command(["logs"]) & app.sudoers)
@lang.language()
async def _logs(_, m: types.Message):
    sent = await m.reply_text(m.lang["log_fetch"])

    if not os.path.exists("log.txt"):
        return await sent.edit_text(m.lang["log_not_found"])

    await m.reply_document(
        document="log.txt",
        caption=m.lang["log_sent"].format(app.name),
    )

    await sent.delete()


@app.on_message(filters.command(["logger"]) & app.sudoers)
@lang.language()
async def _logger(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(
            m.lang["logger_usage"].format(m.command[0])
        )

    if m.command[1] not in ("on", "off"):
        return await m.reply_text(
            m.lang["logger_usage"].format(m.command[0])
        )

    if m.command[1] == "on":
        await db.set_logger(True)
        await m.reply_text(m.lang["logger_on"])
    else:
        await db.set_logger(False)
        await m.reply_text(m.lang["logger_off"])


# ==========================================
# 🔄 RESTART COMMAND WITH INLINE BUTTONS
# ==========================================

@app.on_message(filters.command(["restart"]) & app.sudoers)
@lang.language()
async def _restart(_, m: types.Message):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔄 Rᴇsᴛᴀʀᴛ",
                    callback_data="bot_reboot"
                ),
                InlineKeyboardButton(
                    "⬇️ Uᴘᴅᴀᴛᴇ",
                    callback_data="bot_update"
                )
            ],
            [
                InlineKeyboardButton(
                    "❌ Cᴀɴᴄᴇʟ",
                    callback_data="bot_cancel"
                )
            ]
        ]
    )

    await m.reply_text(
        "<blockquote><b>⚠️ ᴡʜᴀᴛ ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴏ ᴡɪᴛʜ ᴛʜᴇ ʙᴏᴛ?</b></blockquote>",
        reply_markup=keyboard
    )


# ==========================================
# 🛠️ COMMON RESTART LOGIC
# ==========================================

async def reboot_system():
    for directory in ["cache", "downloads"]:
        shutil.rmtree(directory, ignore_errors=True)

    asyncio.create_task(stop())
    await asyncio.sleep(2)

    try:
        os.remove("log.txt")
    except OSError:
        pass

    os.execl(
        sys.executable,
        sys.executable,
        "-m",
        "AloneX"
    )


# ==========================================
# 🔄 RESTART CALLBACK
# ==========================================

@app.on_callback_query(
    filters.regex("^bot_reboot$") & app.sudoers
)
async def restart_cb(_, query: types.CallbackQuery):
    await query.answer()

    try:
        await query.message.edit_text(
            "<blockquote><b>🔄 ʀᴇsᴛᴀʀᴛɪɴɢ ʙᴏᴛ... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.</b></blockquote>"
        )
    except Exception:
        pass

    await reboot_system()


# ==========================================
# ⬇️ GITHUB UPDATE CALLBACK
# ==========================================

@app.on_callback_query(
    filters.regex("^bot_update$") & app.sudoers
)
async def update_cb(_, query: types.CallbackQuery):
    await query.answer()

    try:
        await query.message.edit_text(
            "<blockquote><b>⬇️ ꜰᴇᴛᴄʜɪɴɢ ʟᴀᴛᴇsᴛ ᴜᴘᴅᴀᴛᴇ ꜰʀᴏᴍ ɢɪᴛʜᴜʙ...</b></blockquote>"
        )

        # ======================================
        # Helper: Run Git command
        # ======================================

        async def run_cmd(command):
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            return (
                process.returncode,
                stdout.decode(errors="ignore").strip(),
                stderr.decode(errors="ignore").strip(),
            )

        # ======================================
        # Check Git repository
        # ======================================

        code, output, error = await run_cmd(
            "git rev-parse --is-inside-work-tree"
        )

        if code != 0:
            return await query.message.edit_text(
                "<blockquote><b>❌ ɢɪᴛ ʀᴇᴘᴏsɪᴛᴏʀʏ ɴᴏᴛ ꜰᴏᴜɴᴅ.</b>\n\n"
                f"<code>{error[:1200]}</code></blockquote>"
            )

        # ======================================
        # Use main branch
        # ======================================

        branch = "main"

        # ======================================
        # Check current local commit
        # ======================================

        code, old_commit, error = await run_cmd(
            "git rev-parse HEAD"
        )

        if code != 0 or not old_commit:
            return await query.message.edit_text(
                "<blockquote><b>❌ ᴄᴏᴜʟᴅ ɴᴏᴛ ʀᴇᴀᴅ ʟᴏᴄᴀʟ ᴄᴏᴍᴍɪᴛ.</b>\n\n"
                f"<code>{error[:1200]}</code></blockquote>"
            )

        # ======================================
        # Fetch latest GitHub main branch
        # ======================================

        code, output, error = await run_cmd(
            "git fetch origin main --prune"
        )

        if code != 0:
            details = error or output

            return await query.message.edit_text(
                "<blockquote><b>❌ ɢɪᴛʜᴜʙ ꜰᴇᴛᴄʜ ꜰᴀɪʟᴇᴅ.</b>\n\n"
                f"<code>{details[:1500]}</code></blockquote>"
            )

        # ======================================
        # Get latest GitHub commit
        # ======================================

        code, remote_commit, error = await run_cmd(
            "git rev-parse origin/main"
        )

        if code != 0 or not remote_commit:
            return await query.message.edit_text(
                "<blockquote><b>❌ ᴄᴏᴜʟᴅ ɴᴏᴛ ʀᴇᴀᴅ ʟᴀᴛᴇsᴛ ɢɪᴛʜᴜʙ ᴄᴏᴍᴍɪᴛ.</b>\n\n"
                f"<code>{error[:1200]}</code></blockquote>"
            )

        # ======================================
        # Already up to date
        # ======================================

        if old_commit == remote_commit:
            return await query.message.edit_text(
                "<blockquote><b>✅ ʙᴏᴛ ɪs ᴀʟʀᴇᴀᴅʏ ᴜᴘ-ᴛᴏ-ᴅᴀᴛᴇ!</b>\n\n"
                f"<b>ʙʀᴀɴᴄʜ:</b> <code>main</code>\n"
                f"<b>ᴄᴏᴍᴍɪᴛ:</b> <code>{old_commit[:12]}</code>\n\n"
                "<b>ɴᴏ ɴᴇᴡ ᴜᴘᴅᴀᴛᴇ ꜰᴏᴜɴᴅ ᴏɴ ɢɪᴛʜᴜʙ.</b></blockquote>"
            )

        # ======================================
        # Update server to exact GitHub commit
        # ======================================

        code, output, error = await run_cmd(
            "git reset --hard origin/main"
        )

        if code != 0:
            details = error or output

            return await query.message.edit_text(
                "<blockquote><b>❌ ᴜᴘᴅᴀᴛᴇ ꜰᴀɪʟᴇᴅ.</b>\n\n"
                f"<code>{details[:1500]}</code></blockquote>"
            )

        # ======================================
        # Verify updated commit
        # ======================================

        code, new_commit, error = await run_cmd(
            "git rev-parse HEAD"
        )

        if code != 0 or not new_commit:
            return await query.message.edit_text(
                "<blockquote><b>❌ ᴜᴘᴅᴀᴛᴇᴅ ʙᴜᴛ ᴄᴏᴜʟᴅ ɴᴏᴛ ᴠᴇʀɪꜰʏ ᴄᴏᴍᴍɪᴛ.</b>\n\n"
                f"<code>{error[:1200]}</code></blockquote>"
            )

        # ======================================
        # Final verification
        # ======================================

        if new_commit != remote_commit:
            return await query.message.edit_text(
                "<blockquote><b>❌ ᴜᴘᴅᴀᴛᴇ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ꜰᴀɪʟᴇᴅ.</b>\n\n"
                f"<b>ɢɪᴛʜᴜʙ:</b> <code>{remote_commit[:12]}</code>\n"
                f"<b>sᴇʀᴠᴇʀ:</b> <code>{new_commit[:12]}</code></blockquote>"
            )

        # ======================================
        # Update successful
        # ======================================

        await query.message.edit_text(
            "<blockquote><b>✅ ᴜᴘᴅᴀᴛᴇ sᴜᴄᴄᴇssꜰᴜʟ!</b>\n\n"
            f"<b>ʙʀᴀɴᴄʜ:</b> <code>main</code>\n"
            f"<b>ᴏʟᴅ ᴄᴏᴍᴍɪᴛ:</b> <code>{old_commit[:12]}</code>\n"
            f"<b>ɴᴇᴡ ᴄᴏᴍᴍɪᴛ:</b> <code>{new_commit[:12]}</code>\n\n"
            "<b>🔄 ʀᴇsᴛᴀʀᴛɪɴɢ ɴᴏᴡ...</b></blockquote>"
        )

        await asyncio.sleep(1)

        await reboot_system()

    except Exception as e:
        try:
            await query.message.edit_text(
                "<blockquote><b>❌ ᴜᴘᴅᴀᴛᴇ ᴇʀʀᴏʀ:</b>\n\n"
                f"<code>{str(e)[:1500]}</code></blockquote>"
            )
        except Exception:
            pass


# ==========================================
# ❌ CANCEL CALLBACK
# ==========================================

@app.on_callback_query(
    filters.regex("^bot_cancel$") & app.sudoers
)
async def cancel_cb(_, query: types.CallbackQuery):
    await query.answer(
        "❌ ᴀᴄᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ",
        show_alert=False
    )

    await query.message.delete()
