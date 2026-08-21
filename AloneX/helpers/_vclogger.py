# Copyright (c) 2025 TheHamkerAlone
# Licensed under the MIT License.
# This file is part of AloneXMusic

import asyncio

from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from AloneX import app, logger


DELETE_DELAY = 7

# Premium Custom Emoji ID
PROFILE_EMOJI_ID = "5217822164362739968"


class VCLogger:

    def __init__(self):
        self.join_count: dict[tuple, int] = {}
        self.user_cache: dict[int, tuple] = {}

        # (chat_id, user_id) -> True / False
        self.mute_state: dict[tuple, bool] = {}

    # =========================================================
    # USER INFO
    # =========================================================

    async def _get_user_info(
        self,
        chat_id: int,
        user_id: int,
    ) -> tuple:

        cache_key = (chat_id, user_id)

        if cache_key in self.user_cache:
            return self.user_cache[cache_key]

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

        except Exception as e:
            logger.warning(
                f"[VCLogger] User info error "
                f"{chat_id}/{user_id}: {e}"
            )

        self.user_cache[cache_key] = (
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
        username: str | None = None,
    ) -> InlineKeyboardMarkup:

        # Username available -> show it on button.
        # Username unavailable -> use name.
        if username:
            button_text = (
                f"👤 {name} "
                f"({username})"
            )
        else:
            button_text = (
                f"👤 {name}"
            )

        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=button_text,
                        url=f"tg://user?id={user_id}",
                    )
                ]
            ]
        )

    # =========================================================
    # PREMIUM EMOJI
    # =========================================================

    @staticmethod
    def _premium_emoji(
        fallback: str = "✨",
    ) -> str:

        # Telegram HTML custom emoji.
        #
        # The fallback character is only used as
        # the visible placeholder inside the tag.
        #
        # Telegram uses emoji-id to render the
        # actual premium custom emoji.
        return (
            f'<tg-emoji emoji-id="{PROFILE_EMOJI_ID}">'
            f'{fallback}'
            f'</tg-emoji>'
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
        username: str | None = None,
    ) -> None:

        try:

            keyboard = self._profile_button(
                user_id=user_id,
                name=name,
                username=username,
            )

            msg = await app.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )

            asyncio.create_task(
                self._delete_later(
                    chat_id,
                    msg.id,
                )
            )

        except Exception as e:

            logger.error(
                "[VCLogger] Failed to send "
                f"notification in {chat_id}: {e}"
            )

    # =========================================================
    # JOIN
    # =========================================================

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

        emoji = self._premium_emoji(
            "🎧"
        )

        text = (
            "<b>╭━━━━━━━━━━━━━━━━━━╮</b>\n"
            f"     {emoji} <b>Jᴏɪɴᴇᴅ Vᴄ</b>\n"
            "<b>╰━━━━━━━━━━━━━━━━━━╯</b>\n\n"

            f"<b>◈ Nᴀᴍᴇ:</b>\n"
            f"<b>{name}</b>\n\n"

            f"<b>◈ Uѕᴇʀ ID:</b>\n"
            f"<code>{user_id}</code>"
        )

        if username:
            text += (
                f"\n\n<b>◈ Uѕᴇʀɴᴀᴍᴇ:</b>\n"
                f"<b>@{username}</b>"
            )

        if count > 1:
            text += (
                f"\n\n<b>↻ Jᴏɪɴ Cᴏᴜɴᴛ:</b> "
                f"<code>{count}</code>"
            )

        text += (
            "\n\n"
            "<b>━━━━━━━━━━━━━━━━━━</b>\n"
            f"{self._premium_emoji('✦')} "
            "<b>Wᴇʟᴄᴏᴍᴇ Tᴏ Tʜᴇ Vᴏɪᴄᴇ Cʜᴀᴛ</b>"
        )

        await self._send(
            chat_id,
            user_id,
            text,
            name,
            username,
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
            "<b>╭━━━━━━━━━━━━━━━━━━╮</b>\n"
            f"     {self._premium_emoji('🚪')} "
            "<b>Lᴇғᴛ Vᴄ</b>\n"
            "<b>╰━━━━━━━━━━━━━━━━━━╯</b>\n\n"

            f"<b>◈ Nᴀᴍᴇ:</b>\n"
            f"<b>{name}</b>\n\n"

            f"<b>◈ Uѕᴇʀ ID:</b>\n"
            f"<code>{user_id}</code>"
        )

        if username:
            text += (
                f"\n\n<b>◈ Uѕᴇʀɴᴀᴍᴇ:</b>\n"
                f"<b>@{username}</b>"
            )

        text += (
            "\n\n"
            "<b>━━━━━━━━━━━━━━━━━━</b>\n"
            f"{self._premium_emoji('✦')} "
            "<b>Uɴᴛɪʟ Nᴇxᴛ Tɪᴍᴇ</b>"
        )

        await self._send(
            chat_id,
            user_id,
            text,
            name,
            username,
        )

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

        # Prevent duplicate notifications.
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
            "<b>╭━━━━━━━━━━━━━━━━━━╮</b>\n"
            f"     {self._premium_emoji('🔇')} "
            "<b>Mᴜᴛᴇᴅ Vᴄ</b>\n"
            "<b>╰━━━━━━━━━━━━━━━━━━╯</b>\n\n"

            f"<b>◈ Nᴀᴍᴇ:</b>\n"
            f"<b>{name}</b>\n\n"

            f"<b>◈ Uѕᴇʀ ID:</b>\n"
            f"<code>{user_id}</code>"
        )

        if username:
            text += (
                f"\n\n<b>◈ Uѕᴇʀɴᴀᴍᴇ:</b>\n"
                f"<b>@{username}</b>"
            )

        text += (
            "\n\n"
            "<b>━━━━━━━━━━━━━━━━━━</b>\n"
            f"{self._premium_emoji('✦')} "
            "<b>Mɪᴄʀᴏᴘʜᴏɴᴇ Mᴜᴛᴇᴅ</b>"
        )

        await self._send(
            chat_id,
            user_id,
            text,
            name,
            username,
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

        # Only notify when previous state was muted.
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
            "<b>╭━━━━━━━━━━━━━━━━━━╮</b>\n"
            f"     {self._premium_emoji('🔊')} "
            "<b>Uɴᴍᴜᴛᴇᴅ Vᴄ</b>\n"
            "<b>╰━━━━━━━━━━━━━━━━━━╯</b>\n\n"

            f"<b>◈ Nᴀᴍᴇ:</b>\n"
            f"<b>{name}</b>\n\n"

            f"<b>◈ Uѕᴇʀ ID:</b>\n"
            f"<code>{user_id}</code>"
        )

        if username:
            text += (
                f"\n\n<b>◈ Uѕᴇʀɴᴀᴍᴇ:</b>\n"
                f"<b>@{username}</b>"
            )

        text += (
            "\n\n"
            "<b>━━━━━━━━━━━━━━━━━━</b>\n"
            f"{self._premium_emoji('✦')} "
            "<b>Mɪᴄʀᴏᴘʜᴏɴᴇ Uɴᴍᴜᴛᴇᴅ</b>"
        )

        await self._send(
            chat_id,
            user_id,
            text,
            name,
            username,
        )

    # =========================================================
    # CLEAN CHAT
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

        for key in list(
            self.user_cache
        ):
            if key[0] == chat_id:
                del self.user_cache[key]


vclogger = VCLogger()
