# Copyright (c) 2025 TheHamkerAlone
# Licensed under the MIT License.
# This file is part of AloneXMusic

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

# VC notifications are PERMANENT.
# No automatic deletion is performed.
DELETE_DELAY = None


# Premium Custom Emoji ID
PROFILE_EMOJI_ID = 5217822164362739968


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
            pass

        self.user_cache[user_id] = (
            name,
            username,
        )

        return name, username

    # ========================================================
    # PROFILE BUTTON
    # ========================================================

    def _profile_button(
        self,
        user_id: int,
        name: str,
    ) -> InlineKeyboardMarkup:

        try:

            button = InlineKeyboardButton(
                text=name,
                url=f"tg://user?id={user_id}",
                icon_custom_emoji_id=str(
                    PROFILE_EMOJI_ID
                ),
            )

        except TypeError:

            # Fallback for Pyrogram versions
            # which don't support custom emoji
            # button icons.
            button = InlineKeyboardButton(
                text=name,
                url=f"tg://user?id={user_id}",
            )

        return InlineKeyboardMarkup(
            [
                [button]
            ]
        )

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

            await app.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML,
            )

            # IMPORTANT:
            # VC notification is intentionally
            # NOT deleted.

        except Exception as e:

            logger.error(
                "[VCLogger] Failed to send "
                f"VC notification for "
                f"{chat_id}: {e}"
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

        name, _ = (
            await self._get_user_info(
                chat_id,
                user_id,
            )
        )

        text = (
            "<b>╭━━━━━━━━━━━━━━━━━━╮</b>\n"
            "<b>      🎧 Jᴏɪɴᴇᴅ Vᴄ</b>\n"
            "<b>╰━━━━━━━━━━━━━━━━━━╯</b>\n\n"

            "<b>◈ Nᴀᴍᴇ:</b>\n"
            f"<b>{name}</b>\n\n"

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

        name, _ = (
            await self._get_user_info(
                chat_id,
                user_id,
            )
        )

        text = (
            "<b>╭━━━━━━━━━━━━━━━━━━╮</b>\n"
            "<b>       🔇 Lᴇғᴛ Vᴄ</b>\n"
            "<b>╰━━━━━━━━━━━━━━━━━━╯</b>\n\n"

            "<b>◈ Nᴀᴍᴇ:</b>\n"
            f"<b>{name}</b>\n\n"

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

        self.mute_state.pop(
            (chat_id, user_id),
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

        if self.mute_state.get(key) is True:
            return

        self.mute_state[key] = True

        name, _ = (
            await self._get_user_info(
                chat_id,
                user_id,
            )
        )

        text = (
            "<b>╭━━━━━━━━━━━━━━━━━━╮</b>\n"
            "<b>       🔕 Mᴜᴛᴇᴅ Vᴄ</b>\n"
            "<b>╰━━━━━━━━━━━━━━━━━━╯</b>\n\n"

            "<b>◈ Nᴀᴍᴇ:</b>\n"
            f"<b>{name}</b>\n\n"

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

        if self.mute_state.get(key) is not True:
            return

        self.mute_state[key] = False

        name, _ = (
            await self._get_user_info(
                chat_id,
                user_id,
            )
        )

        text = (
            "<b>╭━━━━━━━━━━━━━━━━━━╮</b>\n"
            "<b>       🔊 Uɴᴍᴜᴛᴇᴅ Vᴄ</b>\n"
            "<b>╰━━━━━━━━━━━━━━━━━━╯</b>\n\n"

            "<b>◈ Nᴀᴍᴇ:</b>\n"
            f"<b>{name}</b>\n\n"

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
    # CLEAN CHAT CACHE
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


vclogger = VCLogger()
