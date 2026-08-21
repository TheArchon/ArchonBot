# Copyright (c) 2025 TheHamkerAlone
# Licensed under the MIT License.
# This file is part of AloneXMusic

import asyncio

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from AloneX import app, logger


DELETE_DELAY = 7

# Premium Custom Emoji ID
PROFILE_EMOJI_ID = 5217822164362739968


class VCLogger:
    def __init__(self):
        self.join_count: dict[tuple, int] = {}
        self.user_cache: dict[int, tuple] = {}

        # Track participant mute state:
        # (chat_id, user_id) -> True/False
        self.mute_state: dict[tuple, bool] = {}

    # =========================================================
    # USER INFO
    # =========================================================

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

                name = user.first_name or "User"

                if user.last_name:
                    name += f" {user.last_name}"

                username = user.username

        except Exception:
            pass

        self.user_cache[user_id] = (
            name,
            username,
        )

        return name, username

    # =========================================================
    # PROFILE BUTTON
    # =========================================================

    def _profile_button(
        self,
        user_id: int,
        name: str,
    ) -> InlineKeyboardMarkup:

        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"👤 {name}",
                        url=f"tg://user?id={user_id}",
                    )
                ]
            ]
        )

    # =========================================================
    # DELETE MESSAGE
    # =========================================================

    async def _delete_later(
        self,
        chat_id: int,
        message_id: int,
    ) -> None:

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

    # =========================================================
    # SEND MESSAGE
    # =========================================================

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
            )

            asyncio.create_task(
                self._delete_later(
                    chat_id,
                    msg.id,
                )
            )

        except Exception as e:

            logger.error(
                f"[VCLogger] Failed to send "
                f"VC notification for {chat_id}: {e}"
            )

    # =========================================================
    # JOIN
    # =========================================================

    async def notify_join(
        self,
        chat_id: int,
        user_id: int,
    ) -> None:

        # Ignore invalid IDs
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

        text = (
            "<b>╭━━━━━━━━━━━━━━━━━━╮\n"
            "      🎧 Jᴏɪɴᴇᴅ Vᴄ\n"
            "╰━━━━━━━━━━━━━━━━━━╯</b>\n\n"

            f"<b>◈ Nᴀᴍᴇ:</b>\n"
            f"<b>{name}</b>\n\n"

            f"<b>◈ Uѕᴇʀ ID:</b>\n"
            f"<code>{user_id}</code>\n\n"

            "<b>━━━━━━━━━━━━━━━━━━\n"
            "✦ Wᴇʟᴄᴏᴍᴇ Tᴏ Tʜᴇ Vᴏɪᴄᴇ Cʜᴀᴛ ✦</b>"
        )

        if count > 1:
            text += (
                f"\n\n<b>↻ Jᴏɪɴ Cᴏᴜɴᴛ:</b> "
                f"<code>{count}</code>"
            )

        await self._send(
            chat_id,
            user_id,
            text,
            name,
        )

    # =========================================================
    # LEAVE
    # =========================================================

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

        text = (
            "<b>╭━━━━━━━━━━━━━━━━━━╮\n"
            "       🔇 Lᴇғᴛ Vᴄ\n"
            "╰━━━━━━━━━━━━━━━━━━╯</b>\n\n"

            f"<b>◈ Nᴀᴍᴇ:</b>\n"
            f"<b>{name}</b>\n\n"

            f"<b>◈ Uѕᴇʀ ID:</b>\n"
            f"<code>{user_id}</code>\n\n"

            "<b>━━━━━━━━━━━━━━━━━━\n"
            "✦ Tʜᴀɴᴋ Yᴏᴜ Fᴏʀ Jᴏɪɴɪɴɢ ✦</b>"
        )

        await self._send(
            chat_id,
            user_id,
            text,
            name,
        )

        # Remove mute state when user leaves
        self.mute_state.pop(
            (chat_id, user_id),
            None,
        )

    # =========================================================
    # MUTE
    # =========================================================

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

        # Prevent duplicate mute notifications
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

        text = (
            "<b>╭━━━━━━━━━━━━━━━━━━╮\n"
            "       🔕 Mᴜᴛᴇᴅ Vᴄ\n"
            "╰━━━━━━━━━━━━━━━━━━╯</b>\n\n"

            f"<b>◈ Nᴀᴍᴇ:</b>\n"
            f"<b>{name}</b>\n\n"

            f"<b>◈ Uѕᴇʀ ID:</b>\n"
            f"<code>{user_id}</code>\n\n"

            "<b>━━━━━━━━━━━━━━━━━━\n"
            "✦ Mɪᴄʀᴏᴘʜᴏɴᴇ Mᴜᴛᴇᴅ ✦</b>"
        )

        await self._send(
            chat_id,
            user_id,
            text,
            name,
        )

    # =========================================================
    # UNMUTE
    # =========================================================

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

        # Prevent duplicate unmute notifications
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

        text = (
            "<b>╭━━━━━━━━━━━━━━━━━━╮\n"
            "       🔊 Uɴᴍᴜᴛᴇᴅ Vᴄ\n"
            "╰━━━━━━━━━━━━━━━━━━╯</b>\n\n"

            f"<b>◈ Nᴀᴍᴇ:</b>\n"
            f"<b>{name}</b>\n\n"

            f"<b>◈ Uѕᴇʀ ID:</b>\n"
            f"<code>{user_id}</code>\n\n"

            "<b>━━━━━━━━━━━━━━━━━━\n"
            "✦ Mɪᴄʀᴏᴘʜᴏɴᴇ Uɴᴍᴜᴛᴇᴅ ✦</b>"
        )

        await self._send(
            chat_id,
            user_id,
            text,
            name,
        )

    # =========================================================
    # CLEAN CHAT CACHE
    # =========================================================

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
