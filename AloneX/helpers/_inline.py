
import random
import re

from pyrogram import types
from pyrogram.enums import ButtonStyle

from AloneX import app, config, lang
from AloneX.core.lang import lang_codes


# ============================================================
# PREMIUM / CUSTOM EMOJI IDs
# ============================================================
# IMPORTANT:
# Keep these as STRINGS.
# Replace any ID here with your own valid Telegram custom emoji ID.
# Empty string = no icon.
# ============================================================

PREMIUM_EMOJIS = {
    "play": "5258362837411045098",
    "pause": "6102938383456146362",
    "replay": "5408943604829794451",
    "skip": "5409368076447657845",
    "stop": "6100397162976252509",

    "autoplay": "5373310679241466020",
    "autoplay_disable": "5408916593780470262",
    "autoplay_status": "5776182936638329359",

    "add": "5258389041006518073",
    "close": "5936143551854285132",
    "back": "5891211339170326418",
    "home": "5267421370114914946",
    "help": "6271611232457855630",

    "source": "6271674836628541366",
    "support": "6257780484281997093",
    "owner": "5778455936410588193",

    "language": "5409320020058584473",
    "queue": "5408843502027033965",
    "stats": "5258337316715373336",
    "admins": "5767288287001580715",
    "auth": "6021618194228187816",
    "blacklist": "5850346984501680054",
    "sudo": "6100514338274020922",
    "vclogger": "6030657343744644592",
    "ping": "5318840353510408444",

    "confirm": "5463122435425448565",
    "cancel": "6041720006973067267",
    "copy": "5355051922862653659",
    "youtube": "6172312314423808834",
    "updates": "6271537028307881531",
    "force_play": "6170455814810112778",

    "default": "5275969776668134187",
}


# ============================================================
# OPTIONAL CONFIG OVERRIDE
# ============================================================

try:
    _config_emojis = getattr(config, "PREMIUM_EMOJIS", None)

    if isinstance(_config_emojis, dict):
        for key, value in _config_emojis.items():
            if value is not None:
                PREMIUM_EMOJIS[key] = str(value)

except Exception:
    pass


def time_to_seconds(time_str: str) -> int:
    """Convert HH:MM:SS / MM:SS / SS to seconds."""
    try:
        parts = str(time_str).split(":")

        if len(parts) == 3:
            return (
                int(parts[0]) * 3600
                + int(parts[1]) * 60
                + int(parts[2])
            )

        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])

        if len(parts) == 1:
            return int(parts[0])

    except (ValueError, TypeError):
        pass

    return 0


class Inline:

    def __init__(self):
        self.ikm = types.InlineKeyboardMarkup
        self._button = types.InlineKeyboardButton

    # ========================================================
    # PREMIUM EMOJI HELPER
    # ========================================================

    def emoji(self, key: str):
        """
        Return a premium custom emoji ID.

        Always returns a string or None.
        """
        value = PREMIUM_EMOJIS.get(key)

        if value is None:
            return None

        value = str(value).strip()

        if not value:
            return None

        return value

    # ========================================================
    # INLINE BUTTON CREATOR
    # ========================================================

    def pkb(self, *args, emoji_key=None, **kwargs):
        """
        Central InlineKeyboardButton creator.

        Priority:
        1. Explicit icon_custom_emoji_id
        2. emoji_key
        3. No icon
        """

        # ----------------------------------------------------
        # Explicit ID has highest priority.
        # ----------------------------------------------------
        explicit_id = kwargs.get("icon_custom_emoji_id")

        if explicit_id is not None:
            explicit_id = str(explicit_id).strip()

            if explicit_id:
                kwargs["icon_custom_emoji_id"] = explicit_id
            else:
                kwargs.pop("icon_custom_emoji_id", None)

        # ----------------------------------------------------
        # If no explicit ID was supplied, use emoji_key.
        # ----------------------------------------------------
        elif emoji_key:
            emoji_id = self.emoji(emoji_key)

            if emoji_id:
                kwargs["icon_custom_emoji_id"] = emoji_id

        return self._button(*args, **kwargs)

    @property
    def ikb(self):
        return self.pkb

    # ========================================================
    # RANDOM BUTTON STYLES
    # ========================================================

    def get_row_styles(self):
        styles = [
            ButtonStyle.PRIMARY,
            ButtonStyle.SUCCESS,
            ButtonStyle.DANGER,
        ]

        random.shuffle(styles)
        return styles

    # ========================================================
    # PROGRESS BAR
    # ========================================================

    def get_progress_bar(self, played_str: str, dur_str: str) -> str:

        played_sec = time_to_seconds(str(played_str))

        if str(dur_str).lower() in [
            "live",
            "unknown",
            "0",
            "00:00",
        ]:
            duration_sec = 0
        else:
            duration_sec = time_to_seconds(str(dur_str))

        total_blocks = 10

        if duration_sec > 0:
            filled_blocks = int(
                (played_sec / duration_sec) * total_blocks
            )
        else:
            filled_blocks = 0

        filled_blocks = min(
            max(filled_blocks, 0),
            total_blocks,
        )

        if filled_blocks == 0:
            bar = "🎵" + "▱" * (total_blocks - 1)

        elif filled_blocks == total_blocks:
            bar = "▰" * (total_blocks - 1) + "🎵"

        else:
            bar = (
                "▰" * filled_blocks
                + "🎵"
                + "▱" * (
                    total_blocks - filled_blocks - 1
                )
            )

        return bar

    # ========================================================
    # CANCEL DOWNLOAD
    # ========================================================

    def cancel_dl(self, text):
        return self.ikm(
            [
                [
                    self.ikb(
                        text=text,
                        callback_data="cancel_dl",
                        emoji_key="cancel",
                    )
                ]
            ]
        )

    # ========================================================
    # AUTOPLAY PANEL
    # ========================================================

    def autoplay_panel_markup(
        self,
        chat_id: int,
        enabled: bool,
    ):

        status = (
            "Eɴᴀʙʟᴇᴅ"
            if enabled
            else "Dɪsᴀʙʟᴇᴅ"
        )

        return self.ikm(
            [
                [
                    self.ikb(
                        text="Aᴜᴛᴏ Pʟᴀʏ Eɴᴀʙʟᴇ",
                        callback_data=(
                            f"AUTOPLAY_ENABLE|{chat_id}"
                        ),
                        style=ButtonStyle.SUCCESS,
                        emoji_key="autoplay",
                    ),
                    self.ikb(
                        text="Aᴜᴛᴏ Pʟᴀʏ DɪSᴀʙʟᴇ",
                        callback_data=(
                            f"AUTOPLAY_DISABLE|{chat_id}"
                        ),
                        style=ButtonStyle.DANGER,
                        emoji_key="autoplay_disable",
                    ),
                ],
                [
                    self.ikb(
                        text=f"Aᴜᴛᴏ Pʟᴀʏ : {status}",
                        callback_data="AUTOPLAY_STATUS",
                        style=ButtonStyle.PRIMARY,
                        emoji_key="autoplay_status",
                    )
                ],
                [
                    self.ikb(
                        text="Cʟᴏsᴇ",
                        callback_data="close",
                        style=ButtonStyle.DANGER,
                        emoji_key="close",
                    )
                ],
            ]
        )

    # ========================================================
    # MUSIC CONTROLS
    # ========================================================

    def controls(
        self,
        chat_id: int,
        status: str = None,
        timer: str = None,
        remove: bool = False,
        _lang: dict = None,
    ):

        keyboard = []
        styles = self.get_row_styles()

        if status:

            keyboard.append(
                [
                    self.ikb(
                        text=status,
                        callback_data=(
                            f"controls status {chat_id}"
                        ),
                        style=styles[0],
                    )
                ]
            )

        elif timer:

            try:
                times = re.findall(
                    r"\d+:\d+(?::\d+)?",
                    timer,
                )

                if len(times) == 2:

                    played_str = times[0]
                    dur_str = times[1]

                    new_bar = self.get_progress_bar(
                        played_str,
                        dur_str,
                    )

                    timer = (
                        f"{played_str} "
                        f"{new_bar} "
                        f"{dur_str}"
                    )

                elif (
                    len(times) == 1
                    and "live" in timer.lower()
                ):

                    played_str = times[0]

                    new_bar = self.get_progress_bar(
                        played_str,
                        "0",
                    )

                    timer = (
                        f"{played_str} "
                        f"{new_bar} Live"
                    )

            except Exception:
                pass

            keyboard.append(
                [
                    self.ikb(
                        text=timer,
                        callback_data=(
                            f"controls status {chat_id}"
                        ),
                        style=styles[0],
                    )
                ]
            )

        if not remove:

            # ------------------------------------------------
            # PLAYBACK CONTROLS
            # ------------------------------------------------

            keyboard.append(
                [
                    self.ikb(
                        text="▷",
                        callback_data=(
                            f"controls resume {chat_id}"
                        ),
                        style=styles[1],
                        emoji_key="play",
                    ),
                    self.ikb(
                        text="Iɪ",
                        callback_data=(
                            f"controls pause {chat_id}"
                        ),
                        style=styles[1],
                        emoji_key="pause",
                    ),
                    self.ikb(
                        text="⥁",
                        callback_data=(
                            f"controls replay {chat_id}"
                        ),
                        style=styles[1],
                        emoji_key="replay",
                    ),
                    self.ikb(
                        text="‣‣I",
                        callback_data=(
                            f"controls skip {chat_id}"
                        ),
                        style=styles[1],
                        emoji_key="skip",
                    ),
                    self.ikb(
                        text="▢",
                        callback_data=(
                            f"controls stop {chat_id}"
                        ),
                        style=styles[1],
                        emoji_key="stop",
                    ),
                ]
            )

            # ------------------------------------------------
            # AUTOPLAY / ADD ME
            # ------------------------------------------------

            keyboard.append(
                [
                    self.ikb(
                        text="Aᴜᴛᴏ Pʟᴀʏ",
                        callback_data=(
                            f"AUTOPLAY_PANEL_OPEN|{chat_id}"
                        ),
                        style=styles[2],
                        emoji_key="autoplay",
                    ),
                    self.ikb(
                        text="Aᴅᴅ Mᴇ",
                        url=(
                            "https://t.me/"
                            "ArchonBeatsBot"
                            "?startgroup=true"
                        ),
                        style=styles[0],
                        emoji_key="add",
                    ),
                ]
            )

            if not _lang:
                _lang = lang.languages["en"]

            keyboard.append(
                [
                    self.ikb(
                        text=_lang.get(
                            "close",
                            "Cʟᴏsᴇ",
                        ),
                        callback_data="close",
                        style=styles[0],
                        emoji_key="close",
                    )
                ]
            )

        return self.ikm(keyboard)

    # ========================================================
    # HELP MENU
    # ========================================================

    def help_markup(
        self,
        _lang: dict,
        back: bool = False,
    ):

        styles = self.get_row_styles()

        if back:

            rows = [
                [
                    self.ikb(
                        text=_lang.get(
                            "back",
                            "Bᴀᴄᴋ",
                        ),
                        callback_data="help back",
                        style=styles[0],
                        emoji_key="back",
                    ),
                    self.ikb(
                        text=_lang.get(
                            "home_btn",
                            "Hᴏᴍᴇ",
                        ),
                        callback_data="help home",
                        style=styles[0],
                        emoji_key="home",
                    ),
                    self.ikb(
                        text=_lang.get(
                            "close",
                            "Cʟᴏsᴇ",
                        ),
                        callback_data="close",
                        style=styles[0],
                        emoji_key="close",
                    ),
                ]
            ]

        else:

            button_names = {
                "admins": "Aᴅᴍɪɴs",
                "auth": "Aᴜᴛʜ",
                "blist": "Bʟᴀᴄᴋʟɪsᴛ",
                "lang": "Lᴀɴɢᴜᴀɢᴇ",
                "ping": "Pɪɴɢ",
                "play": "Pʟᴀʏ",
                "queue": "Qᴜᴇᴜᴇ",
                "stats": "Sᴛᴀᴛs",
                "sudo": "Sᴜᴅᴏᴇʀs",
                "autoplay": "Aᴜᴛᴏᴘʟᴀʏ",
                "vclogger": "Vᴄ ʟᴏɢɢᴇʀ",
            }

            emoji_keys = {
                "admins": "admins",
                "auth": "auth",
                "blist": "blacklist",
                "lang": "language",
                "ping": "ping",
                "play": "play",
                "queue": "queue",
                "stats": "stats",
                "sudo": "sudo",
                "autoplay": "autoplay",
                "vclogger": "vclogger",
            }

            callbacks = list(
                button_names.keys()
            )

            rows = []

            for i in range(
                0,
                len(callbacks),
                3,
            ):

                row = callbacks[i:i + 3]

                row_style = styles[
                    (i // 3) % 3
                ]

                rows.append(
                    [
                        self.ikb(
                            text=button_names[item],
                            callback_data=(
                                f"help {item}"
                            ),
                            style=row_style,
                            emoji_key=emoji_keys[item],
                        )
                        for item in row
                    ]
                )

            last_style = styles[
                len(rows) % 3
            ]

            rows.append(
                [
                    self.ikb(
                        text=_lang.get(
                            "home_btn",
                            "Hᴏᴍᴇ",
                        ),
                        callback_data="help home",
                        style=last_style,
                        emoji_key="home",
                    ),
                    self.ikb(
                        text=_lang.get(
                            "close",
                            "Cʟᴏsᴇ",
                        ),
                        callback_data="close",
                        style=last_style,
                        emoji_key="close",
                    ),
                ]
            )

        return self.ikm(rows)

    # ========================================================
    # LANGUAGE MENU
    # ========================================================

    def lang_markup(
        self,
        _lang: str,
    ):

        styles = self.get_row_styles()

        languages = list(
            lang.get_languages().items()
        )

        rows = []

        for i in range(
            0,
            len(languages),
            2,
        ):

            row_languages = languages[
                i:i + 2
            ]

            row_style = styles[
                (i // 2) % 3
            ]

            rows.append(
                [
                    self.ikb(
                        text=(
                            f"{name} ({code}) "
                            f"{'✔️' if code == _lang else ''}"
                        ),
                        callback_data=(
                            f"lang_change {code}"
                        ),
                        style=row_style,
                        emoji_key="language",
                    )
                    for code, name in row_languages
                ]
            )

        return self.ikm(rows)

    # ========================================================
    # PING
    # ========================================================

    def ping_markup(self, text: str):

        return self.ikm(
            [
                [
                    self.ikb(
                        text=text,
                        url=config.SUPPORT_CHAT,
                        emoji_key="ping",
                    )
                ]
            ]
        )

    # ========================================================
    # PLAY QUEUED
    # ========================================================

    def play_queued(
        self,
        chat_id: int,
        item_id: str,
        _text: str,
    ):

        return self.ikm(
            [
                [
                    self.ikb(
                        text=_text,
                        callback_data=(
                            f"controls force "
                            f"{chat_id} {item_id}"
                        ),
                        style=ButtonStyle.SUCCESS,
                        emoji_key="force_play",
                    )
                ]
            ]
        )

    # ========================================================
    # QUEUE
    # ========================================================

    def queue_markup(
        self,
        chat_id: int,
        _text: str,
        playing: bool,
    ):

        action = (
            "pause"
            if playing
            else "resume"
        )

        return self.ikm(
            [
                [
                    self.ikb(
                        text=_text,
                        callback_data=(
                            f"controls "
                            f"{action} "
                            f"{chat_id} q"
                        ),
                        style=ButtonStyle.SUCCESS,
                        emoji_key=(
                            "pause"
                            if playing
                            else "play"
                        ),
                    )
                ]
            ]
        )

    # ========================================================
    # SETTINGS
    # ========================================================

    def settings_markup(
        self,
        lang: dict,
        admin_only: bool,
        cmd_delete: bool,
        language: str,
        chat_id: int,
    ):

        styles = self.get_row_styles()

        return self.ikm(
            [
                [
                    self.ikb(
                        text=(
                            lang["play_mode"]
                            + " ➜"
                        ),
                        callback_data="settings",
                        style=styles[0],
                        emoji_key="play",
                    ),
                    self.ikb(
                        text=admin_only,
                        callback_data="settings play",
                        style=styles[0],
                        emoji_key="admins",
                    ),
                ],
                [
                    self.ikb(
                        text=(
                            lang["cmd_delete"]
                            + " ➜"
                        ),
                        callback_data="settings",
                        style=styles[1],
                        emoji_key="cancel",
                    ),
                    self.ikb(
                        text=cmd_delete,
                        callback_data="settings delete",
                        style=styles[1],
                        emoji_key="confirm",
                    ),
                ],
                [
                    self.ikb(
                        text=(
                            lang["language"]
                            + " ➜"
                        ),
                        callback_data="settings",
                        style=styles[2],
                        emoji_key="language",
                    ),
                    self.ikb(
                        text=lang_codes[language],
                        callback_data="language",
                        style=styles[2],
                        emoji_key="language",
                    ),
                ],
            ]
        )

    # ========================================================
    # START MENU
    # ========================================================

    def start_key(
        self,
        lang: dict,
        private: bool = False,
    ):

        styles = self.get_row_styles()

        if private:

            rows = [
                [
                    self.ikb(
                        text=lang["add_me"],
                        url=(
                            f"https://t.me/"
                            f"{app.username}"
                            f"?startgroup=true"
                        ),
                        style=ButtonStyle.SUCCESS,
                        emoji_key="add",
                    )
                ],
                [
                    self.ikb(
                        text="Sᴏᴜʀᴄᴇ",
                        callback_data="source_panel",
                        style=ButtonStyle.PRIMARY,
                        emoji_key="source",
                    ),
                    self.ikb(
                        text="Sᴜᴘᴘᴏʀᴛ",
                        callback_data="support_panel",
                        style=ButtonStyle.PRIMARY,
                        emoji_key="support",
                    ),
                ],
                [
                    self.ikb(
                        text=lang["help"],
                        callback_data="help",
                        style=ButtonStyle.PRIMARY,
                        emoji_key="help",
                    ),
                    self.ikb(
                        text="Tʜᴇ Aʀᴄʜᴏɴ",
                        user_id=config.OWNER_ID,
                        style=ButtonStyle.DANGER,
                        emoji_key="owner",
                    ),
                ],
            ]

        else:

            rows = [
                [
                    self.ikb(
                        text="Sᴏᴜʀᴄᴇ",
                        callback_data="source_panel",
                        style=styles[2],
                        emoji_key="source",
                    ),
                    self.ikb(
                        text="Sᴜᴘᴘᴏʀᴛ",
                        callback_data="support_panel",
                        style=styles[2],
                        emoji_key="support",
                    ),
                ],
                [
                    self.ikb(
                        text=lang["language"],
                        callback_data="language",
                        style=styles[0],
                        emoji_key="language",
                    )
                ],
            ]

        return self.ikm(rows)

    # ========================================================
    # SOURCE PANEL
    # ========================================================

    def source_markup(
        self,
        _lang: dict = None,
    ):

        if not _lang:
            _lang = lang.languages["en"]

        styles = self.get_row_styles()

        return self.ikm(
            [
                [
                    self.ikb(
                        text=_lang.get(
                            "close",
                            "Cʟᴏsᴇ",
                        ),
                        callback_data="close",
                        style=styles[0],
                        emoji_key="close",
                    ),
                    self.ikb(
                        text="Bᴀᴄᴋ",
                        callback_data="help home",
                        style=styles[1],
                        emoji_key="back",
                    ),
                ]
            ]
        )

    # ========================================================
    # SUPPORT PANEL
    # ========================================================

    def support_markup(self):

        styles = self.get_row_styles()

        return self.ikm(
            [
                [
                    self.ikb(
                        text="Sᴜᴘᴘᴏʀᴛ",
                        url=config.SUPPORT_CHAT,
                        style=styles[0],
                        emoji_key="support",
                    ),
                    self.ikb(
                        text="Uᴘᴅᴀᴛᴇs",
                        url=config.SUPPORT_CHANNEL,
                        style=styles[0],
                        emoji_key="updates",
                    ),
                ],
                [
                    self.ikb(
                        text="Bᴀᴄᴋ",
                        callback_data="help home",
                        style=styles[1],
                        emoji_key="back",
                    )
                ],
            ]
        )

    # ========================================================
    # YOUTUBE
    # ========================================================

    def yt_key(self, link: str):

        styles = self.get_row_styles()

        return self.ikm(
            [
                [
                    self.ikb(
                        text="❐",
                        copy_text=link,
                        style=styles[0],
                        emoji_key="copy",
                    ),
                    self.ikb(
                        text="Yᴏᴜᴛᴜʙᴇ",
                        url=link,
                        style=styles[0],
                        emoji_key="youtube",
                    ),
                ]
            ]
        )
