import random
import re

from pyrogram import types
from pyrogram.enums import ButtonStyle

from AloneX import app, config, lang
from AloneX.core.lang import lang_codes


# ============================================================
# PREMIUM / CUSTOM EMOJI IDS
# ============================================================

PREMIUM_EMOJIS = {
    "play": "5409025823388741707",
    "pause": "5408916593780470262",
    "replay": "6023773095284707791",
    "skip": "5215480011322042129",
    "stop": "5161208387957950108",

    "autoplay": "5260687681733533075",
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

    "language": "5260512129240276089",
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
            if value:
                PREMIUM_EMOJIS[str(key)] = str(value)

except Exception:
    pass


# ============================================================
# TIME HELPER
# ============================================================

def time_to_seconds(time_str: str) -> int:
    try:
        parts = str(time_str).strip().split(":")

        if len(parts) == 3:
            return (
                int(parts[0]) * 3600
                + int(parts[1]) * 60
                + int(parts[2])
            )

        if len(parts) == 2:
            return (
                int(parts[0]) * 60
                + int(parts[1])
            )

        if len(parts) == 1:
            return int(parts[0])

    except (ValueError, TypeError):
        return 0

    return 0


# ============================================================
# INLINE KEYBOARD
# ============================================================

class Inline:

    def __init__(self):
        self.ikm = types.InlineKeyboardMarkup
        self._button = types.InlineKeyboardButton

    # ========================================================
    # GET EMOJI ID
    # ========================================================

    def _get_emoji_id(self, key):
        if not key:
            key = "default"

        value = PREMIUM_EMOJIS.get(str(key))

        if not value:
            value = PREMIUM_EMOJIS.get("default")

        if not value:
            return None

        return str(value)

    # ========================================================
    # AUTOMATIC EMOJI DETECTION
    # ========================================================

    def _emoji_key(
        self,
        text=None,
        callback_data=None,
        url=None,
        copy_text=None,
    ):
        value = " ".join(
            str(x).lower()
            for x in (
                text,
                callback_data,
                url,
                copy_text,
            )
            if x is not None
        )

        rules = (
            (
                "autoplay_disable",
                (
                    "autoplay_disable",
                    "auto play disable",
                    "dɪsᴀʙʟᴇ",
                ),
            ),
            (
                "autoplay_status",
                (
                    "autoplay_status",
                    "auto play :",
                    "enabled",
                    "disabled",
                ),
            ),
            (
                "autoplay",
                (
                    "autoplay",
                    "aᴜᴛᴏ pʟᴀʏ",
                ),
            ),
            (
                "pause",
                (
                    "controls pause",
                    "iɪ",
                ),
            ),
            (
                "replay",
                (
                    "controls replay",
                    "⥁",
                ),
            ),
            (
                "skip",
                (
                    "controls skip",
                    "‣‣i",
                    "‣‣I",
                ),
            ),
            (
                "stop",
                (
                    "controls stop",
                    "▢",
                ),
            ),
            (
                "play",
                (
                    "controls resume",
                    "▷",
                ),
            ),
            (
                "force_play",
                (
                    "controls force",
                ),
            ),
            (
                "close",
                (
                    "close",
                    "cʟᴏsᴇ",
                ),
            ),
            (
                "back",
                (
                    "help back",
                    "bᴀᴄᴋ",
                ),
            ),
            (
                "home",
                (
                    "help home",
                    "hᴏᴍᴇ",
                ),
            ),
            (
                "help",
                (
                    "help",
                ),
            ),
            (
                "source",
                (
                    "source",
                    "sᴏᴜʀᴄᴇ",
                ),
            ),
            (
                "support",
                (
                    "support",
                    "sᴜᴘᴘᴏʀᴛ",
                ),
            ),
            (
                "language",
                (
                    "language",
                    "lᴀɴɢᴜᴀɢᴇ",
                ),
            ),
            (
                "queue",
                (
                    "queue",
                    "qᴜᴇᴜᴇ",
                ),
            ),
            (
                "stats",
                (
                    "stats",
                    "sᴛᴀᴛs",
                ),
            ),
            (
                "admins",
                (
                    "admins",
                    "aᴅᴍɪɴs",
                ),
            ),
            (
                "auth",
                (
                    "auth",
                    "aᴜᴛʜ",
                ),
            ),
            (
                "blacklist",
                (
                    "blist",
                    "blacklist",
                ),
            ),
            (
                "sudo",
                (
                    "sudo",
                    "sᴜᴅᴏ",
                ),
            ),
            (
                "vclogger",
                (
                    "vclogger",
                    "vᴄ ʟᴏɢɢᴇʀ",
                ),
            ),
            (
                "ping",
                (
                    "ping",
                    "pɪɴɢ",
                ),
            ),
            (
                "add",
                (
                    "startgroup=true",
                    "aᴅᴅ mᴇ",
                ),
            ),
            (
                "owner",
                (
                    "tʜᴇ aʀᴄʜᴏɴ",
                ),
            ),
            (
                "youtube",
                (
                    "youtube",
                ),
            ),
            (
                "copy",
                (
                    "copy_text",
                    "❐",
                ),
            ),
            (
                "updates",
                (
                    "updates",
                ),
            ),
        )

        for key, needles in rules:
            for needle in needles:
                if needle in value:
                    return key

        return "default"

    # ========================================================
    # PREMIUM EMOJI BUTTON BUILDER
    # ========================================================

    def pkb(
        self,
        *args,
        emoji_key=None,
        **kwargs,
    ):
        """
        Build a Kurigram/Pyrogram inline button.

        emoji_key is handled internally and is never forwarded
        to InlineKeyboardButton.
        """

        explicit_id = kwargs.get(
            "icon_custom_emoji_id"
        )

        if explicit_id:
            kwargs["icon_custom_emoji_id"] = str(
                explicit_id
            )

        else:
            key = emoji_key

            if not key:
                key = self._emoji_key(
                    kwargs.get("text"),
                    kwargs.get("callback_data"),
                    kwargs.get("url"),
                    kwargs.get("copy_text"),
                )

            emoji_id = self._get_emoji_id(key)

            if emoji_id:
                kwargs["icon_custom_emoji_id"] = emoji_id

        return self._button(
            *args,
            **kwargs,
        )

    # ========================================================
    # COMPATIBILITY ALIAS
    # ========================================================

    @property
    def ikb(self):
        return self.pkb

    # ========================================================
    # RANDOM ROW STYLE
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

    def get_progress_bar(
        self,
        played_str: str,
        dur_str: str,
    ) -> str:

        played_sec = time_to_seconds(
            str(played_str)
        )

        duration_value = str(
            dur_str
        ).lower()

        if duration_value in (
            "live",
            "unknown",
            "0",
            "00:00",
        ):
            duration_sec = 0

        else:
            duration_sec = time_to_seconds(
                str(dur_str)
            )

        total_blocks = 10

        if duration_sec > 0:
            filled_blocks = int(
                (
                    played_sec
                    / duration_sec
                )
                * total_blocks
            )
        else:
            filled_blocks = 0

        filled_blocks = min(
            max(filled_blocks, 0),
            total_blocks,
        )

        if filled_blocks == 0:

            bar = (
                "🎵"
                + "▱" * (
                    total_blocks - 1
                )
            )

        elif filled_blocks == total_blocks:

            bar = (
                "▰" * (
                    total_blocks - 1
                )
                + "🎵"
            )

        else:

            bar = (
                "▰" * filled_blocks
                + "🎵"
                + "▱" * (
                    total_blocks
                    - filled_blocks
                    - 1
                )
            )

        return bar

    # ========================================================
    # CANCEL DOWNLOAD
    # ========================================================

    def cancel_dl(
        self,
        text,
    ) -> types.InlineKeyboardMarkup:

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
    ) -> types.InlineKeyboardMarkup:

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
                        text=(
                            f"Aᴜᴛᴏ Pʟᴀʏ : "
                            f"{status}"
                        ),
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
    ) -> types.InlineKeyboardMarkup:

        keyboard = []
        style = self.get_row_styles()

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        if status:

            keyboard.append(
                [
                    self.ikb(
                        text=status,
                        callback_data=(
                            f"controls status "
                            f"{chat_id}"
                        ),
                        style=style[0],
                        emoji_key="stats",
                    )
                ]
            )

        # ----------------------------------------------------
        # TIMER / PROGRESS
        # ----------------------------------------------------

        elif timer:

            try:

                times = re.findall(
                    r"\d+:\d+(?::\d+)?",
                    str(timer),
                )

                if len(times) == 2:

                    played_str = times[0]
                    dur_str = times[1]

                    new_bar = (
                        self.get_progress_bar(
                            played_str,
                            dur_str,
                        )
                    )

                    timer = (
                        f"{played_str} "
                        f"{new_bar} "
                        f"{dur_str}"
                    )

                elif (
                    len(times) == 1
                    and "live"
                    in str(timer).lower()
                ):

                    played_str = times[0]

                    new_bar = (
                        self.get_progress_bar(
                            played_str,
                            "0",
                        )
                    )

                    timer = (
                        f"{played_str} "
                        f"{new_bar} "
                        f"Live"
                    )

            except Exception:
                pass

            keyboard.append(
                [
                    self.ikb(
                        text=timer,
                        callback_data=(
                            f"controls status "
                            f"{chat_id}"
                        ),
                        style=style[0],
                        emoji_key="stats",
                    )
                ]
            )

        # ----------------------------------------------------
        # PLAYER BUTTONS
        # ----------------------------------------------------

        if not remove:

            # IMPORTANT:
            # Empty text means the old symbols
            # (▷ Iɪ ⥁ ‣‣I ▢) will not appear.
            #
            # Premium/custom emoji is supplied through
            # icon_custom_emoji_id.

            keyboard.extend(
                [
                    [
                        self.ikb(
                            text="",
                            callback_data=(
                                f"controls resume "
                                f"{chat_id}"
                            ),
                            style=style[1],
                            emoji_key="play",
                        ),

                        self.ikb(
                            text="",
                            callback_data=(
                                f"controls pause "
                                f"{chat_id}"
                            ),
                            style=style[1],
                            emoji_key="pause",
                        ),

                        self.ikb(
                            text="",
                            callback_data=(
                                f"controls replay "
                                f"{chat_id}"
                            ),
                            style=style[1],
                            emoji_key="replay",
                        ),
                    ],

                    [
                        self.ikb(
                            text="",
                            callback_data=(
                                f"controls skip "
                                f"{chat_id}"
                            ),
                            style=style[1],
                            emoji_key="skip",
                        ),

                        self.ikb(
                            text="",
                            callback_data=(
                                f"controls stop "
                                f"{chat_id}"
                            ),
                            style=style[1],
                            emoji_key="stop",
                        ),
                    ],
                ]
            )

            # ------------------------------------------------
            # AUTOPLAY + ADD ME
            # ------------------------------------------------

            keyboard.append(
                [
                    self.ikb(
                        text="Aᴜᴛᴏ Pʟᴀʏ",
                        callback_data=(
                            "AUTOPLAY_PANEL_OPEN|"
                            f"{chat_id}"
                        ),
                        style=style[2],
                        emoji_key="autoplay",
                    ),

                    self.ikb(
                        text="Aᴅᴅ Mᴇ",
                        url=(
                            "https://t.me/"
                            "ArchonBeatsBot"
                            "?startgroup=true"
                        ),
                        style=style[0],
                        emoji_key="add",
                    ),
                ]
            )

            # ------------------------------------------------
            # CLOSE
            # ------------------------------------------------

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
                        style=style[0],
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
    ) -> types.InlineKeyboardMarkup:

        style = self.get_row_styles()

        if back:

            rows = [
                [
                    self.ikb(
                        text=_lang.get(
                            "back",
                            "Bᴀᴄᴋ",
                        ),
                        callback_data="help back",
                        style=style[0],
                        emoji_key="back",
                    ),

                    self.ikb(
                        text=_lang.get(
                            "home_btn",
                            "Hᴏᴍᴇ",
                        ),
                        callback_data="help home",
                        style=style[0],
                        emoji_key="home",
                    ),

                    self.ikb(
                        text=_lang.get(
                            "close",
                            "Cʟᴏsᴇ",
                        ),
                        callback_data="close",
                        style=style[0],
                        emoji_key="close",
                    ),
                ]
            ]

        else:

            button_names = {
                "admins": "Aᴅᴍɪɴs",
                "auth": "Aᴜᴛʜ",
                "blist": "B•Lɪsᴛ",
                "lang": "Lᴀɴɢ",
                "ping": "Pɪɴɢ",
                "play": "Pʟᴀʏ",
                "queue": "Qᴜᴇᴜᴇ",
                "stats": "Sᴛᴀᴛs",
                "sudo": "Sᴜᴅᴏ",
                "autoplay": "A•Pʟᴀʏ",
                "vclogger": "Vᴄ Lᴏɢs",
            }

            emoji_map = {
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

            cbs = list(
                button_names.keys()
            )

            rows = []

            for i in range(
                0,
                len(cbs),
                3,
            ):

                row_cbs = cbs[
                    i:i + 3
                ]

                row_style = style[
                    (i // 3) % 3
                ]

                rows.append(
                    [
                        self.ikb(
                            text=button_names[cb],
                            callback_data=(
                                f"help {cb}"
                            ),
                            style=row_style,
                            emoji_key=(
                                emoji_map.get(
                                    cb,
                                    "default",
                                )
                            ),
                        )
                        for cb in row_cbs
                    ]
                )

            last_style = style[
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
    ) -> types.InlineKeyboardMarkup:

        style = self.get_row_styles()

        langs = list(
            lang.get_languages().items()
        )

        rows = []

        for i in range(
            0,
            len(langs),
            2,
        ):

            row_langs = langs[
                i:i + 2
            ]

            row_style = style[
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
                    for code, name in row_langs
                ]
            )

        return self.ikm(rows)

    # ========================================================
    # PING
    # ========================================================

    def ping_markup(
        self,
        text: str,
    ) -> types.InlineKeyboardMarkup:

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
    ) -> types.InlineKeyboardMarkup:

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
    ) -> types.InlineKeyboardMarkup:

        action = (
            "pause"
            if playing
            else "resume"
        )

        emoji_key = (
            "pause"
            if playing
            else "play"
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
                        emoji_key=emoji_key,
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
    ) -> types.InlineKeyboardMarkup:

        style = self.get_row_styles()

        return self.ikm(
            [
                [
                    self.ikb(
                        text=(
                            lang["play_mode"]
                            + " ➜"
                        ),
                        callback_data="settings",
                        style=style[0],
                        emoji_key="stats",
                    ),

                    self.ikb(
                        text=str(admin_only),
                        callback_data="settings play",
                        style=style[0],
                        emoji_key="play",
                    ),
                ],

                [
                    self.ikb(
                        text=(
                            lang["cmd_delete"]
                            + " ➜"
                        ),
                        callback_data="settings",
                        style=style[1],
                        emoji_key="close",
                    ),

                    self.ikb(
                        text=str(cmd_delete),
                        callback_data="settings delete",
                        style=style[1],
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
                        style=style[2],
                        emoji_key="language",
                    ),

                    self.ikb(
                        text=lang_codes[language],
                        callback_data="language",
                        style=style[2],
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
    ) -> types.InlineKeyboardMarkup:

        style = self.get_row_styles()

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
                        style=style[2],
                        emoji_key="source",
                    ),

                    self.ikb(
                        text="Sᴜᴘᴘᴏʀᴛ",
                        callback_data="support_panel",
                        style=style[2],
                        emoji_key="support",
                    ),
                ],

                [
                    self.ikb(
                        text=lang["language"],
                        callback_data="language",
                        style=style[0],
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
    ) -> types.InlineKeyboardMarkup:

        if not _lang:
            _lang = lang.languages["en"]

        style = self.get_row_styles()

        return self.ikm(
            [
                [
                    self.ikb(
                        text=_lang.get(
                            "close",
                            "Cʟᴏsᴇ",
                        ),
                        callback_data="close",
                        style=style[0],
                        emoji_key="close",
                    ),

                    self.ikb(
                        text="Bᴀᴄᴋ",
                        callback_data="help home",
                        style=style[1],
                        emoji_key="back",
                    ),
                ]
            ]
        )

    # ========================================================
    # SUPPORT PANEL
    # ========================================================

    def support_markup(
        self,
    ) -> types.InlineKeyboardMarkup:

        style = self.get_row_styles()

        return self.ikm(
            [
                [
                    self.ikb(
                        text="Sᴜᴘᴘᴏʀᴛ",
                        url=config.SUPPORT_CHAT,
                        style=style[0],
                        emoji_key="support",
                    ),

                    self.ikb(
                        text="Uᴘᴅᴀᴛᴇs",
                        url=config.SUPPORT_CHANNEL,
                        style=style[0],
                        emoji_key="updates",
                    ),
                ],

                [
                    self.ikb(
                        text="Bᴀᴄᴋ",
                        callback_data="help home",
                        style=style[1],
                        emoji_key="back",
                    )
                ],
            ]
        )

    # ========================================================
    # YOUTUBE
    # ========================================================

    def yt_key(
        self,
        link: str,
    ) -> types.InlineKeyboardMarkup:

        style = self.get_row_styles()

        return self.ikm(
            [
                [
                    self.ikb(
                        text="",
                        copy_text=link,
                        style=style[0],
                        emoji_key="copy",
                    ),

                    self.ikb(
                        text="Yᴏᴜᴛᴜʙᴇ",
                        url=link,
                        style=style[0],
                        emoji_key="youtube",
                    ),
                ]
            ]
        )
