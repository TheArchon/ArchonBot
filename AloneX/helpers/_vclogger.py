# Copyright (c) 2025 TheHamkerAlone
# Licensed under the MIT License.
# This file is part of AloneX

import asyncio

from pyrogram import enums
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from AloneX import app, logger


# ============================================================
# SETTINGS
# ============================================================

# 0 = notification delete nahi hogi
DELETE_DELAY = 0


# ============================================================
# PREMIUM CUSTOM EMOJI
# ============================================================

# Tumhare inline.py me owner emoji wala ID.
# Agar VC button ke liye alag emoji chahiye,
# sirf ye ID replace kar dena.
PROFILE_EMOJI_ID = 5217822164362739968


# ============================================================
# VC LOGGER
# ============================================================

class VCLogger:

    def __init__(self):

        self.join_count: dict[tuple, int] = {}

        self.user_cache: dict[int, tuple] = {}

        # (chat_id, user_id) -> True / False
        self.mute_state: dict[tuple, bool] = {}


    # ========================================================
    # USER INFO
    # ========================================================

    async def _get_user_info(
        self,
        chat_id: int,
        user_id: int,
    ) -> tuple:

        if user_id in self.user_cache:
            return self.user_cache[user_id]

        name = "User"
        username = None

        try:

            member = await app.get_chat_member(
                chat_id,
                user_id,
            )

            if member and member.user:

                user = member.user

                name = (
                    user.first_name
                    or "User"
                )

                if user.last_name:

                    name += (
                        f" {user.last_name}"
                    )

                username = user.username

        except Exception:

            # Fallback: directly get user
            try:

                user = await app.get_users(
                    user_id
                )

                name = (
                    user.first_name
                    or "User"
                )

                if user.last_name:

                    name += (
                        f" {user.last_name}"
                    )

                username = user.username

            except Exception:
                pass

        self.user_cache[user_id] = (
            name,
            username,
        )

        return name, username


    # ========================================================
    # HTML ESCAPE
    # ========================================================

    @staticmethod
    def _escape_html(
        text: str,
    ) -> str:

        if not text:
            return "User"

        return (
            str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )


    # ========================================================
    # PROFILE BUTTON
    # ========================================================

    def _profile_button(
        self,
        user_id: int,
        name: str,
    ) -> InlineKeyboardMarkup:

        safe_name = self._escape_html(
            name
        )

        button = InlineKeyboardButton(
            text=safe_name,
            url=f"tg://user?id={user_id}",
            icon_custom_emoji_id=str(
                PROFILE_EMOJI_ID
            ),
        )

        return InlineKeyboardMarkup(
            [
                [button]
            ]
        )


    # ========================================================
    # DELETE MESSAGE
    # ========================================================

    async def _delete_later(
        self,
        chat_id: int,
        message_id: int,
    ) -> None:

        # DELETE_DELAY = 0 hone par
        # message permanently rahega.
        if DELETE_DELAY <= 0:
            return

        try:

            await asyncio.sleep(
                DELETE_DELAY
            )

            await app.delete_messages(
                chat_id,
                message_id,
            )

        except Exception:
            pass


    # ========================================================
    # SEND MESSAGE
    # ========================================================

    async def _send(
        self,
        chat_id: int,
        user_id: int,
        text: str,
        name: str,
    ) -> None:

        try:

            keyboard = self._profile_button(
                user_id,
                name,
            )

            msg = await app.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True,
            )

            # Sirf agar DELETE_DELAY > 0 ho
            if DELETE_DELAY > 0:

                asyncio.create_task(
                    self._delete_later(
                        chat_id,
                        msg.id,
                    )
                )

        except Exception as e:

            logger.error(
                "[VCLogger] Failed to send "
                f"VC notification in {chat_id}: {e}"
            )


    # ========================================================
    # JOIN
    # ========================================================

    async def notify_join(
        self,
        chat_id: int,
        user_id: int,
    ) -> None:

        if not user_id:
            return

        key = (
            chat_id,
            user_id,
        )

        self.join_count[key] = (
            self.join_count.get(
                key,
                0,
            )
            + 1
        )

        count = self.join_count[key]

        name, username = (
            await self._get_user_info(
                chat_id,
                user_id,
            )
        )

        safe_name = self._escape_html(
            name
        )

        text = (
            "<b>╭━━━━━━━━━━━━━━━━━━╮</b>\n"
            "<b>      🎧 Jᴏɪɴᴇᴅ Vᴄ</b>\n"
            "<b>╰━━━━━━━━━━━━━━━━━━╯</b>\n\n"

            "<b>◈ Nᴀᴍᴇ:</b>\n"
            f"<b>{safe_name}</b>\n\n"

            "<b>◈ Uѕᴇʀ ID:</b>\n"
            f"<code>{user_id}</code>\n\n"

            "<b>━━━━━━━━━━━━━━━━━━</b>\n"
            "<b>✦ Wᴇʟᴄᴏᴍᴇ Tᴏ Tʜᴇ Vᴏɪᴄᴇ Cʜᴀᴛ ✦</b>"
        )

        if count > 1:

            text += (
                "\n\n"
                "<b>↻ Jᴏɪɴ Cᴏᴜɴᴛ:</b> "
                f"<code>{count}</code>"
            )

        await self._send(
            chat_id,
            user_id,
            text,
            name,
        )


    # ========================================================
    # LEAVE
    # ========================================================

    async def notify_leave(
        self,
        chat_id: int,
        user_id: int,
    ) -> None:

        if not user_id:
            return

        name, username = (
            await self._get_user_info(
                chat_id,
                user_id,
            )
        )

        safe_name = self._escape_html(
            name
        )

        text = (
            "<b>╭━━━━━━━━━━━━━━━━━━╮</b>\n"
            "<b>       🔇 Lᴇғᴛ Vᴄ</b>\n"
            "<b>╰━━━━━━━━━━━━━━━━━━╯</b>\n\n"

            "<b>◈ Nᴀᴍᴇ:</b>\n"
            f"<b>{safe_name}</b>\n\n"

            "<b>◈ Uѕᴇʀ ID:</b>\n"
            f"<code>{user_id}</code>\n\n"

            "<b>━━━━━━━━━━━━━━━━━━</b>\n"
            "<b>✦ Tʜᴀɴᴋ Yᴏᴜ Fᴏʀ Jᴏɪɴɪɴɢ ✦</b>"
        )

        await self._send(
            chat_id,
            user_id,
            text,
            name,
        )

        # User leave kar gaya,
        # isliye mute state reset.
        self.mute_state.pop(
            (
                chat_id,
                user_id,
            ),
            None,
        )


    # ========================================================
    # MUTE
    # ========================================================

    async def notify_mute(
        self,
        chat_id: int,
        user_id: int,
    ) -> None:

        if not user_id:
            return

        key = (
            chat_id,
            user_id,
        )

        # Duplicate notification prevent
        if self.mute_state.get(
            key
        ) is True:

            return

        self.mute_state[key] = True

        name, username = (
            await self._get_user_info(
                chat_id,
                user_id,
            )
        )

        safe_name = self._escape_html(
            name
        )

        text = (
            "<b>╭━━━━━━━━━━━━━━━━━━╮</b>\n"
            "<b>       🔕 Mᴜᴛᴇᴅ Vᴄ</b>\n"
            "<b>╰━━━━━━━━━━━━━━━━━━╯</b>\n\n"

            "<b>◈ Nᴀᴍᴇ:</b>\n"
            f"<b>{safe_name}</b>\n\n"

            "<b>◈ Uѕᴇʀ ID:</b>\n"
            f"<code>{user_id}</code>\n\n"

            "<b>━━━━━━━━━━━━━━━━━━</b>\n"
            "<b>✦ Mɪᴄʀᴏᴘʜᴏɴᴇ Mᴜᴛᴇᴅ ✦</b>"
        )

        await self._send(
            chat_id,
            user_id,
            text,
            name,
        )


    # ========================================================
    # UNMUTE
    # ========================================================

    async def notify_unmute(
        self,
        chat_id: int,
        user_id: int,
    ) -> None:

        if not user_id:
            return

        key = (
            chat_id,
            user_id,
        )

        # Agar pehle muted nahi tha
        # to duplicate notification nahi.
        if self.mute_state.get(
            key
        ) is not True:

            return

        self.mute_state[key] = False

        name, username = (
            await self._get_user_info(
                chat_id,
                user_id,
            )
        )

        safe_name = self._escape_html(
            name
        )

        text = (
            "<b>╭━━━━━━━━━━━━━━━━━━╮</b>\n"
            "<b>       🔊 Uɴᴍᴜᴛᴇᴅ Vᴄ</b>\n"
            "<b>╰━━━━━━━━━━━━━━━━━━╯</b>\n\n"

            "<b>◈ Nᴀᴍᴇ:</b>\n"
            f"<b>{safe_name}</b>\n\n"

            "<b>◈ Uѕᴇʀ ID:</b>\n"
            f"<code>{user_id}</code>\n\n"

            "<b>━━━━━━━━━━━━━━━━━━</b>\n"
            "<b>✦ Mɪᴄʀᴏᴘʜᴏɴᴇ Uɴᴍᴜᴛᴇᴅ ✦</b>"
        )

        await self._send(
            chat_id,
            user_id,
            text,
            name,
        )


    # ========================================================
    # CLEAR CHAT
    # ========================================================

    def clear_chat(
        self,
        chat_id: int,
    ) -> None:

        for key in list(
            self.join_count
        ):

            if key[0] == chat_id:

                del self.join_count[key]

        for key in list(
            self.mute_state
        ):

            if key[0] == chat_id:

                del self.mute_state[key]


# ============================================================
# GLOBAL INSTANCE
# ============================================================

vclogger = VCLogger()
