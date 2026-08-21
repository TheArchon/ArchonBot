import random
import re
from pyrogram import enums, types
from pyrogram.enums import ButtonStyle

from AloneX import app, config, lang
from AloneX.core.lang import lang_codes

# Safe fallback if PREMIUM_EMOJIS is not defined in config
# ============================================================
# PREMIUM / CUSTOM EMOJI CONFIG
# Put your VALID Telegram custom emoji IDs here.
# Leave a value empty ("") if you do not want an icon on that button.
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
        value = " ".join(str(x).lower() for x in (text, callback_data, url, copy_text) if x is not None)
        rules = (
            ("autoplay_disable", ("autoplay_enable", "autoplay_disable", "auto play disable")),
            ("autoplay_status", ("autoplay_status", "auto play :", "enabled", "disabled")),
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
        )
        for key, needles in rules:
            if any(needle in value for needle in needles):
                return key
        return "default"

    def pkb(self, *args, emoji_key=None, **kwargs):
        # Explicit IDs always win. Otherwise select an ID from PREMIUM_EMOJIS.
        explicit_id = kwargs.get("icon_custom_emoji_id")
        if not explicit_id:
            key = emoji_key or self._emoji_key(
                kwargs.get("text"), kwargs.get("callback_data"),
                kwargs.get("url"), kwargs.get("copy_text")
            )
            emoji_id = PREMIUM_EMOJIS.get(key) or PREMIUM_EMOJIS.get("default")
            if emoji_id:
                kwargs["icon_custom_emoji_id"] = str(emoji_id)
        return self._button(*args, **kwargs)

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
                        icon_custom_emoji_id="5408843502027033965",
                    ),
                    self.ikb(
                        text="Aᴜᴛᴏ Pʟᴀʏ DɪSᴀʙʟᴇ",
                        callback_data=f"AUTOPLAY_DISABLE|{chat_id}",
                        style=ButtonStyle.DANGER,
                        icon_custom_emoji_id="5408943604829794451",
                    ),
                ],
                [
                    self.ikb(
                        text=f"Aᴜᴛᴏ Pʟᴀʏ : {status}",
                        callback_data="AUTOPLAY_STATUS",
                        style=ButtonStyle.PRIMARY,
                        icon_custom_emoji_id="6172312314423808834",
                    )
                ],
                [
                    self.ikb(
                        text="Cʟᴏsᴇ",
                        callback_data="close",
                        style=ButtonStyle.DANGER,
                        icon_custom_emoji_id="5258453452631056344",
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
                    icon_custom_emoji_id="6100125944381444896",
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
                        icon_custom_emoji_id="6235576525563895420",
                    ),
                    self.ikb(
                        text="Sᴜᴘᴘᴏʀᴛ",
                        callback_data="support_panel",
                        style=ButtonStyle.PRIMARY,
                        icon_custom_emoji_id="6039381989985882045",
                    ),
                ],
                [
                    self.ikb(
                        text=lang["help"],
                        callback_data="help",
                        style=ButtonStyle.PRIMARY,
                        icon_custom_emoji_id="5409368076447657845",
                    ),
                    self.ikb(
                        text="Tʜᴇ Aʀᴄʜᴏɴ",
                        user_id=config.OWNER_ID,
                        style=ButtonStyle.DANGER,
                        icon_custom_emoji_id="6237864166879663987",
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
