import random
import re
from pyrogram import enums, types
from pyrogram.enums import ButtonStyle

from AloneX import app, config, lang
from AloneX.core.lang import lang_codes

# ============================================================
# PREMIUM / CUSTOM EMOJI CONFIG
# Replace the values below with your own Telegram custom emoji IDs.
# Leave a value as "" to keep that button without a custom emoji. ops
# ============================================================

PREMIUM_EMOJIS = {
    "play": "5408843502027033965",
    "pause": "",
    "replay": "",
    "skip": "",
    "stop": "",
    "autoplay": "5408843502027033965",
    "autoplay_disable": "5408943604829794451",
    "autoplay_status": "6172312314423808834",
    "add": "6100125944381444896",
    "close": "5258453452631056344",
    "back": "",
    "home": "",
    "help": "5409368076447657845",
    "source": "6235576525563895420",
    "support": "6039381989985882045",
    "owner": "6237864166879663987",
    "language": "",
    "settings": "",
    "queue": "",
    "stats": "",
    "admins": "",
    "auth": "",
    "blacklist": "",
    "sudo": "",
    "vclogger": "",
    "ping": "",
    "confirm": "",
    "cancel": "",
    "copy": "",
    "youtube": "",
    "updates": "",
    "force_play": "",
    "status": "",
    "default": "",
}

# Existing config.py values can override the defaults above.
_config_emojis = getattr(config, "PREMIUM_EMOJIS", None)
if isinstance(_config_emojis, dict):
    PREMIUM_EMOJIS.update(_config_emojis)

def time_to_seconds(time_str: str) -> int:
    """Helper function to convert time string to seconds"""
    try:
        parts = time_str.split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 1:
            return int(parts[0])
    except:
        return 0
    return 0


class Inline:
    def __init__(self):
        self.ikm = types.InlineKeyboardMarkup
        self._button = types.InlineKeyboardButton

    def _emoji_key(self, text=None, callback_data=None, url=None, copy_text=None):
        """Choose a custom emoji key automatically from button information."""
        value = " ".join(
            str(x).lower()
            for x in (text, callback_data, url, copy_text)
            if x is not None
        )

        rules = (
            ("autoplay_disable", ("autoplay_disable", "aᴜᴛᴏ pʟᴀʏ dɪsᴀʙʟᴇ")),
            ("autoplay_status", ("autoplay_status", "aᴜᴛᴏ pʟᴀʏ :")),
            ("autoplay", ("autoplay", "aᴜᴛᴏ pʟᴀʏ")),
            ("pause", ("controls pause", "iɪ")),
            ("replay", ("controls replay", "⥁")),
            ("skip", ("controls skip", "‣‣i")),
            ("stop", ("controls stop", "▢")),
            ("play", ("controls resume", "▷")),
            ("force_play", ("controls force",)),
            ("close", ("close", "cʟᴏsᴇ")),
            ("back", ("help back", "bᴀᴄᴋ")),
            ("home", ("help home", "hᴏᴍᴇ")),
            ("help", ("help",)),
            ("source", ("source", "sᴏᴜʀᴄᴇ")),
            ("support", ("support", "sᴜᴘᴘᴏʀᴛ")),
            ("language", ("language", "lᴀɴɢᴜᴀɢᴇ")),
            ("queue", ("queue", "qᴜᴇᴜᴇ")),
            ("stats", ("stats", "sᴛᴀᴛs")),
            ("admins", ("admins", "aᴅᴍɪɴs")),
            ("auth", ("auth", "aᴜᴛʜ")),
            ("blacklist", ("blist", "blacklist")),
            ("sudo", ("sudo", "sᴜᴅᴏ")),
            ("vclogger", ("vclogger", "vᴄ ʟᴏɢɢᴇʀ")),
            ("ping", ("ping", "pɪɴɢ")),
            ("add", ("startgroup=true", "aᴅᴅ mᴇ")),
            ("owner", ("tʜᴇ aʀᴄʜᴏɴ",)),
            ("youtube", ("youtube",)),
            ("copy", ("copy_text", "❐")),
            ("updates", ("updates",)),
            ("settings", ("settings",)),
        )

        for key, needles in rules:
            if any(needle in value for needle in needles):
                return key

        return "default"

    def pkb(self, *args, emoji_key=None, **kwargs):
        """
        Centralized InlineKeyboardButton wrapper.

        - Existing explicit icon_custom_emoji_id is always preserved.
        - Otherwise an emoji ID is selected automatically.
        - Empty IDs are ignored, so buttons continue to work normally.
        """
        explicit_id = kwargs.get("icon_custom_emoji_id")
        if not explicit_id:
            key = emoji_key or self._emoji_key(
                kwargs.get("text"),
                kwargs.get("callback_data"),
                kwargs.get("url"),
                kwargs.get("copy_text"),
            )
            emoji_id = PREMIUM_EMOJIS.get(key) or PREMIUM_EMOJIS.get("default")
            if emoji_id:
                kwargs["icon_custom_emoji_id"] = str(emoji_id)

        return self._button(*args, **kwargs)

    # Keep all existing self.ikb(...) calls working through the centralized wrapper.
    @property
    def ikb(self):
        return self.pkb

    # 🎨 Dynamic Row-Wise Color Generator
    def get_row_styles(self):
        styles = [ButtonStyle.PRIMARY, ButtonStyle.SUCCESS, ButtonStyle.DANGER]
        random.shuffle(styles)
        return styles

    # 🎵 Custom Progress Bar Generator 
    def get_progress_bar(self, played_str: str, dur_str: str) -> str:
        played_sec = time_to_seconds(str(played_str))
        if str(dur_str).lower() in ["live", "unknown", "0", "00:00"]:
            duration_sec = 0
        else:
            duration_sec = time_to_seconds(str(dur_str))
        
        total_blocks = 10
        if duration_sec > 0:
            filled_blocks = int((played_sec / duration_sec) * total_blocks)
        else:
            filled_blocks = 0
            
        filled_blocks = min(max(filled_blocks, 0), total_blocks)
        
        # Smooth progress bar with music note 🎵 leading the way
        if filled_blocks == 0:
            bar = "🎵" + "▱" * (total_blocks - 1)
        elif filled_blocks == total_blocks:
            bar = "▰" * (total_blocks - 1) + "🎵"
        else:
            bar = "▰" * filled_blocks + "🎵" + "▱" * (total_blocks - filled_blocks - 1)
            
        return bar

    def cancel_dl(self, text) -> types.InlineKeyboardMarkup:
        return self.ikm([[self.ikb(text=text, callback_data=f"cancel_dl")]])

    # 🆕 Aᴜᴛᴏᴘʟᴀʏ Panel System
    def autoplay_panel_markup(self, chat_id: int, enabled: bool) -> types.InlineKeyboardMarkup:
        status = "Eɴᴀʙʟᴇᴅ" if enabled else "Dɪsᴀʙʟᴇᴅ"
        
        return self.ikm(
            [
                [
                    self.ikb(
                        text="Aᴜᴛᴏ Pʟᴀʏ Eɴᴀʙʟᴇ",
                        callback_data=f"AUTOPLAY_ENABLE|{chat_id}",
                        style=ButtonStyle.SUCCESS,
                        icon_custom_emoji_id=PREMIUM_EMOJIS["autoplay"],
                    ),
                    self.ikb(
                        text="Aᴜᴛᴏ Pʟᴀʏ DɪSᴀʙʟᴇ",
                        callback_data=f"AUTOPLAY_DISABLE|{chat_id}",
                        style=ButtonStyle.DANGER,
                        icon_custom_emoji_id=PREMIUM_EMOJIS["autoplay_disable"],
                    ),
                ],
                [
                    self.ikb(
                        text=f"Aᴜᴛᴏ Pʟᴀʏ : {status}",
                        callback_data="AUTOPLAY_STATUS",
                        style=ButtonStyle.PRIMARY,
                        icon_custom_emoji_id=PREMIUM_EMOJIS["autoplay_status"],
                    )
                ],
                [
                    self.ikb(
                        text="Cʟᴏsᴇ",
                        callback_data="close",
                        style=ButtonStyle.DANGER,
                        icon_custom_emoji_id=PREMIUM_EMOJIS["close"],
                    )
                ]
            ]
        )

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

        if status:
            keyboard.append(
                [self.ikb(text=status, callback_data=f"controls status {chat_id}", style=style[0])]
            )
        elif timer:
            try:
                times = re.findall(r'\d+:\d+(?::\d+)?', timer)
                if len(times) == 2:
                    played_str = times[0]
                    dur_str = times[1]
                    new_bar = self.get_progress_bar(played_str, dur_str)
                    timer = f"{played_str} {new_bar} {dur_str}"
                elif len(times) == 1 and "live" in timer.lower():
                    played_str = times[0]
                    new_bar = self.get_progress_bar(played_str, "0")
                    timer = f"{played_str} {new_bar} Live"
            except Exception:
                pass

            keyboard.append(
                [self.ikb(text=timer, callback_data=f"controls status {chat_id}", style=style[0])]
            )

        if not remove:
            keyboard.append(
                [
                    self.ikb(text="▷", callback_data=f"controls resume {chat_id}", style=style[1]),
                    self.ikb(text="Iɪ", callback_data=f"controls pause {chat_id}", style=style[1]),
                    self.ikb(text="⥁", callback_data=f"controls replay {chat_id}", style=style[1]),
                    self.ikb(text="‣‣I", callback_data=f"controls skip {chat_id}", style=style[1]),
                    self.ikb(text="▢", callback_data=f"controls stop {chat_id}", style=style[1]),
                ]
            )
            
            keyboard.append(
                [
                    self.ikb(text="Aᴜᴛᴏ Pʟᴀʏ", callback_data=f"AUTOPLAY_PANEL_OPEN|{chat_id}", style=style[2]),
                    self.ikb(text="Aᴅᴅ Mᴇ", url="https://t.me/ArchonBeatsBot?startgroup=true", style=style[0]),
                ]
            )
            
            if not _lang:
                _lang = lang.languages["en"]
                
            keyboard.append(
                [
                    self.ikb(
                        text=_lang.get("close", "Cʟᴏsᴇ"),
                        callback_data="close",
                        style=style[0],
                    ),
                ]
            )
        return self.ikm(keyboard)

    def help_markup(
        self, _lang: dict, back: bool = False
    ) -> types.InlineKeyboardMarkup:
        style = self.get_row_styles()
        
        if back:
            rows = [
                [
                    self.ikb(text=_lang.get("back", "Bᴀᴄᴋ"), callback_data="help back", style=style[0]),
                    self.ikb(text=_lang.get("home_btn", "Hᴏᴍᴇ"), callback_data="help home", style=style[0]),
                    self.ikb(text=_lang.get("close", "Cʟᴏsᴇ"), callback_data="close", style=style[0]),
                ]
            ]
        else:
            button_names = {
                "admins": "👮 Aᴅᴍɪɴs",
                "auth": "🔐 Aᴜᴛʜ",
                "blist": "🚫 Bʟᴀᴄᴋʟɪsᴛ",
                "lang": "🌐 Lᴀɴɢᴜᴀɢᴇ",
                "ping": "🏓 Pɪɴɢ",
                "play": "🎵 Pʟᴀʏ",
                "queue": "📋 Qᴜᴇᴜᴇ",
                "stats": "📊 Sᴛᴀᴛs",
                "sudo": "👑 Sᴜᴅᴏᴇʀs",
                "autoplay": "▶️ Aᴜᴛᴏᴘʟᴀʏ",
                "vclogger": "🎙 Vᴄ ʟᴏɢɢᴇʀ"
            }
            cbs = list(button_names.keys())
            rows = []
            
            for i in range(0, len(cbs), 3):
                row_cbs = cbs[i : i + 3]
                row_style = style[(i // 3) % 3]
                rows.append([
                    self.ikb(text=button_names[cb], callback_data=f"help {cb}", style=row_style)
                    for cb in row_cbs
                ])
                
            last_style = style[len(rows) % 3]
            rows.append(
                [
                    self.ikb(text=_lang.get("home_btn", "Hᴏᴍᴇ"), callback_data="help home", style=last_style),
                    self.ikb(text=_lang.get("close", "Cʟᴏsᴇ"), callback_data="close", style=last_style),
                ]
            )

        return self.ikm(rows)

    def lang_markup(self, _lang: str) -> types.InlineKeyboardMarkup:
        style = self.get_row_styles()
        langs = list(lang.get_languages().items())

        rows = []
        for i in range(0, len(langs), 2):
            row_langs = langs[i : i + 2]
            row_style = style[(i // 2) % 3]
            rows.append([
                self.ikb(
                    text=f"{name} ({code}) {'✔️' if code == _lang else ''}",
                    callback_data=f"lang_change {code}",
                    style=row_style
                )
                for code, name in row_langs
            ])
            
        return self.ikm(rows)

    def ping_markup(self, text: str) -> types.InlineKeyboardMarkup:
        return self.ikm([[self.ikb(text=text, url=config.SUPPORT_CHAT)]])

    def play_queued(
        self, chat_id: int, item_id: str, _text: str
    ) -> types.InlineKeyboardMarkup:
        return self.ikm(
            [
                [
                    self.ikb(
                        text=_text,
                        callback_data=f"controls force {chat_id} {item_id}",
                        style=ButtonStyle.SUCCESS,
                    )
                ]
            ]
        )

    def queue_markup(
        self, chat_id: int, _text: str, playing: bool
    ) -> types.InlineKeyboardMarkup:
        _action = "pause" if playing else "resume"
        return self.ikm(
            [
                [
                    self.ikb(
                        text=_text,
                        callback_data=f"controls {_action} {chat_id} q",
                        style=ButtonStyle.SUCCESS,
                    )
                ]
            ]
        )

    def settings_markup(
        self, lang: dict, admin_only: bool, cmd_delete: bool, language: str, chat_id: int
    ) -> types.InlineKeyboardMarkup:
        style = self.get_row_styles()
        return self.ikm(
            [
                [
                    self.ikb(text=lang["play_mode"] + " ➜", callback_data="settings", style=style[0]),
                    self.ikb(text=admin_only, callback_data="settings play", style=style[0]),
                ],
                [
                    self.ikb(text=lang["cmd_delete"] + " ➜", callback_data="settings", style=style[1]),
                    self.ikb(text=cmd_delete, callback_data="settings delete", style=style[1]),
                ],
                [
                    self.ikb(text=lang["language"] + " ➜", callback_data="settings", style=style[2]),
                    self.ikb(text=lang_codes[language], callback_data="language", style=style[2]),
                ],
            ]
        )

    # 🛠️ START MENU UPDATED WITH SOURCE & SUPPORT CALLBACK BUTTONS
    def start_key(
        self, lang: dict, private: bool = False
    ) -> types.InlineKeyboardMarkup:
        style = self.get_row_styles()

        rows = [
            [
                self.ikb(
                    text=lang["add_me"],
                    url=f"https://t.me/{app.username}?startgroup=true",
                    style=ButtonStyle.SUCCESS,
                    icon_custom_emoji_id=PREMIUM_EMOJIS["add"],
                )
            ]
        ]

        if private:
            rows += [
                [
                    self.ikb(
                        text="Sᴏᴜʀᴄᴇ",
                        callback_data="source_panel",
                        style=ButtonStyle.PRIMARY,
                        icon_custom_emoji_id=PREMIUM_EMOJIS["source"],
                    ),
                    self.ikb(
                        text="Sᴜᴘᴘᴏʀᴛ",
                        callback_data="support_panel",
                        style=ButtonStyle.PRIMARY,
                        icon_custom_emoji_id=PREMIUM_EMOJIS["support"],
                    ),
                ],
                [
                    self.ikb(
                        text=lang["help"],
                        callback_data="help",
                        style=ButtonStyle.PRIMARY,
                        icon_custom_emoji_id=PREMIUM_EMOJIS["help"],
                    ),
                    self.ikb(
                        text="Tʜᴇ Aʀᴄʜᴏɴ",
                        user_id=config.OWNER_ID,
                        style=ButtonStyle.DANGER,
                        icon_custom_emoji_id=PREMIUM_EMOJIS["owner"],
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
                    ),
                    self.ikb(
                        text="Sᴜᴘᴘᴏʀᴛ",
                        callback_data="support_panel",
                        style=style[2],
                    ),
                ],
                [
                    self.ikb(
                        text=lang["language"],
                        callback_data="language",
                        style=style[0],
                    )
                ],
            ]

        return self.ikm(rows)

    # 🛠️ NEW: SOURCE PANEL MARKUP
    def source_markup(self, _lang: dict = None) -> types.InlineKeyboardMarkup:
        if not _lang:
            _lang = lang.languages["en"]

        style = self.get_row_styles()
        
        return self.ikm([
            [
                self.ikb(
                  text=_lang.get("close", "Cʟᴏsᴇ"),
                  callback_data="close",
                  style=style[0],
               ),
               self.ikb(
                 text="Bᴀᴄᴋ",
                 callback_data="help home",
                 style=style[1],
             ),
         ],
     ])

    # 🛠️ NEW: SUPPORT PANEL MARKUP
    def support_markup(self) -> types.InlineKeyboardMarkup:
        style = self.get_row_styles()
        return self.ikm([
            [
                self.ikb(text="Sᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_CHAT, style=style[0]),
                self.ikb(text="Uᴘᴅᴀᴛᴇs", url=config.SUPPORT_CHANNEL, style=style[0])
            ],
            [self.ikb(text="Bᴀᴄᴋ", callback_data="help home", style=style[1])]
        ])

    def yt_key(self, link: str) -> types.InlineKeyboardMarkup:
        style = self.get_row_styles()
        return self.ikm(
            [
                [
                    self.ikb(text="❐", copy_text=link, style=style[0]),
                    self.ikb(text="Yᴏᴜᴛᴜʙᴇ", url=link, style=style[0]),
                ],
            ]
        )
