# Copyright (c) 2026 THE SHIV
# Welcome card plugin for TestBot
#
# Place this file at:
#   AloneX/plugins/welcome.py
#
# Keeps the existing welcome-card/profile-image generator and adds:
#   1) User profile button with the new member's name + custom emoji
#   2) Add Bot button with custom emoji
#
# Premium/custom emoji IDs:
#   Add Bot     = 6100125944381444896
#   User Profile= 6235576525563895420

import io
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
from pyrogram import filters, types, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from AloneX import app


BASE_DIR = Path(__file__).resolve().parent.parent
FONT_DIR = BASE_DIR / "helpers"

WIDTH, HEIGHT = 1600, 900

# ============================================================
# PREMIUM / CUSTOM EMOJI IDS
# ============================================================

USER_PROFILE_EMOJI_ID = "6235576525563895420"
ADD_BOT_EMOJI_ID = "6100125944381444896"


# ============================================================
# FONT HELPER
# ============================================================

def _font(name: str, size: int):
    path = FONT_DIR / name

    if path.exists():
        try:
            return ImageFont.truetype(str(path), size)
        except Exception:
            pass

    return ImageFont.load_default()


# ============================================================
# TEXT FIT HELPER
# ============================================================

def _fit_text(draw, text, font, max_width):
    text = str(text or "User")

    try:
        if draw.textbbox((0, 0), text, font=font)[2] <= max_width:
            return text

        text = text[:30].rstrip()

        while text and draw.textbbox(
            (0, 0),
            text + "...",
            font=font
        )[2] > max_width:
            text = text[:-1]

        return (text + "...") if text else "User"

    except Exception:
        return text[:30] or "User"


# ============================================================
# PROFILE PHOTO
# ============================================================

def _circle_photo(photo_bytes, size=500):
    """Crop a downloaded Telegram profile photo into a circle."""
    if not photo_bytes:
        return None

    try:
        photo = Image.open(photo_bytes).convert("RGB")
    except Exception:
        return None

    try:
        side = min(photo.size)

        left = (photo.width - side) // 2
        top = (photo.height - side) // 2

        photo = photo.crop(
            (left, top, left + side, top + side)
        )

        photo = ImageOps.fit(
            photo,
            (size, size),
            method=Image.Resampling.LANCZOS
        )

        mask = Image.new("L", (size, size), 0)

        ImageDraw.Draw(mask).ellipse(
            (0, 0, size - 1, size - 1),
            fill=255
        )

        result = Image.new(
            "RGBA",
            (size, size),
            (0, 0, 0, 0)
        )

        result.paste(
            photo,
            (0, 0),
            mask
        )

        return result

    except Exception:
        return None


# ============================================================
# WELCOME CARD GENERATOR
# ============================================================

def _make_welcome_card(
    name: str,
    username: str,
    group_name: str,
    member_number: int,
    join_date: str,
    photo_bytes=None,
):
    """Create the welcome image in memory."""

    # --------------------------------------------------------
    # Background
    # --------------------------------------------------------

    canvas = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        (11, 16, 25)
    )

    bg = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        (17, 29, 45)
    )

    bd = ImageDraw.Draw(bg, "RGBA")

    bd.ellipse(
        (-250, -220, 650, 620),
        fill=(35, 92, 130, 130)
    )

    bd.ellipse(
        (1050, 380, 1850, 1150),
        fill=(25, 75, 115, 100)
    )

    bd.ellipse(
        (650, 150, 1250, 750),
        fill=(50, 65, 95, 70)
    )

    bg = bg.filter(
        ImageFilter.GaussianBlur(90)
    )

    canvas.paste(bg)

    # --------------------------------------------------------
    # Main Card
    # --------------------------------------------------------

    card = Image.new(
        "RGBA",
        (1450, 760),
        (20, 27, 39, 238)
    )

    cd = ImageDraw.Draw(card, "RGBA")

    cd.rounded_rectangle(
        (0, 0, 1449, 759),
        radius=42,
        fill=(20, 27, 39, 235),
        outline=(92, 132, 165, 85),
        width=2
    )

    # --------------------------------------------------------
    # Photo Panel
    # --------------------------------------------------------

    photo_x = 55
    photo_y = 55
    photo_size = 650

    cd.rounded_rectangle(
        (
            photo_x,
            photo_y,
            photo_x + photo_size,
            photo_y + photo_size
        ),
        radius=34,
        fill=(12, 18, 28, 255)
    )

    photo = (
        _circle_photo(photo_bytes, 470)
        if photo_bytes
        else None
    )

    # Fallback avatar
    if photo is None:
        fallback = Image.new(
            "RGBA",
            (470, 470),
            (28, 43, 58, 255)
        )

        fd = ImageDraw.Draw(fallback)

        fd.ellipse(
            (145, 90, 325, 270),
            fill=(110, 130, 145, 255)
        )

        fd.rounded_rectangle(
            (90, 245, 380, 430),
            radius=80,
            fill=(110, 130, 145, 255)
        )

        photo = fallback

    card.alpha_composite(
        photo,
        (
            photo_x + (photo_size - photo.width) // 2,
            photo_y + 70
        )
    )

    # --------------------------------------------------------
    # Fonts
    # --------------------------------------------------------

    white = (245, 248, 252, 255)
    muted = (168, 184, 201, 255)

    title_font = _font(
        "Poppins-ExtraBold.ttf",
        54
    )

    name_font = _font(
        "Poppins-ExtraBold.ttf",
        38
    )

    body_font = _font(
        "Inter-Light.ttf",
        27
    )

    small_font = _font(
        "Inter-Light.ttf",
        22
    )

    # --------------------------------------------------------
    # Left Text
    # --------------------------------------------------------

    cd.text(
        (82, 625),
        "HEY,",
        font=title_font,
        fill=muted
    )

    safe_name = _fit_text(
        cd,
        name,
        name_font,
        570
    )

    cd.text(
        (82, 678),
        safe_name + " 👋",
        font=name_font,
        fill=white
    )

    # --------------------------------------------------------
    # Right Panel
    # --------------------------------------------------------

    rx = 760

    cd.text(
        (rx, 75),
        "WELCOME ABOARD!",
        font=title_font,
        fill=white
    )

    cd.text(
        (rx, 145),
        "Glad to have you here.",
        font=body_font,
        fill=(185, 201, 217, 255)
    )

    cd.line(
        (rx, 205, 1370, 205),
        fill=(92, 132, 165, 90),
        width=2
    )

    label_font = _font(
        "Inter-Light.ttf",
        20
    )

    value_font = _font(
        "Poppins-ExtraBold.ttf",
        28
    )

    rows = [
        (
            "USER",
            f"@{username}" if username else name
        ),
        (
            "GROUP",
            group_name
        ),
        (
            "MEMBER",
            f"#{member_number}"
        ),
        (
            "JOINED",
            join_date
        ),
    ]

    y = 245

    for label, value in rows:

        cd.text(
            (rx, y),
            label,
            font=label_font,
            fill=(122, 151, 177, 255)
        )

        value = _fit_text(
            cd,
            value,
            value_font,
            570
        )

        cd.text(
            (rx, y + 28),
            value,
            font=value_font,
            fill=white
        )

        y += 105

    # --------------------------------------------------------
    # Bottom Message
    # --------------------------------------------------------

    pill_y = 635

    cd.rounded_rectangle(
        (
            rx,
            pill_y,
            1370,
            pill_y + 65
        ),
        radius=28,
        fill=(34, 54, 73, 230),
        outline=(76, 143, 193, 100),
        width=1
    )

    cd.text(
        (rx + 25, pill_y + 17),
        "Be active, Be respectful & Have fun! 💙",
        font=small_font,
        fill=(207, 222, 236, 255)
    )

    # --------------------------------------------------------
    # Composite
    # --------------------------------------------------------

    canvas_rgba = canvas.convert("RGBA")

    canvas_rgba.alpha_composite(
        card,
        (
            (WIDTH - card.width) // 2,
            (HEIGHT - card.height) // 2
        )
    )

    # --------------------------------------------------------
    # JPEG Output
    # --------------------------------------------------------

    output = io.BytesIO()

    canvas_rgba.convert("RGB").save(
        output,
        format="JPEG",
        quality=94,
        optimize=True
    )

    output.name = "welcome.jpg"
    output.seek(0)

    return output


# ============================================================
# WELCOME HANDLER
# ============================================================

@app.on_message(
    filters.new_chat_members,
    group=6
)
async def welcome_new_members(
    _,
    message: types.Message
):
    """
    Sends the welcome card for normal users joining a supergroup.

    The existing start.py handler remains responsible
    for bot-join setup.
    """

    # --------------------------------------------------------
    # Only supergroups
    # --------------------------------------------------------

    if message.chat.type != enums.ChatType.SUPERGROUP:
        return

    # --------------------------------------------------------
    # Ignore the bot itself
    # --------------------------------------------------------

    members = [
        user
        for user in (message.new_chat_members or [])
        if user.id != app.id
    ]

    if not members:
        return

    # --------------------------------------------------------
    # Group information
    # --------------------------------------------------------

    group_name = (
        message.chat.title
        or "Our Group"
    )

    try:
        member_number = (
            await app.get_chat_members_count(
                message.chat.id
            )
        )
    except Exception:
        member_number = 0

    join_date = datetime.now().strftime(
        "%d %b %Y"
    )

    # --------------------------------------------------------
    # Process each new member
    # --------------------------------------------------------

    for member in members:

        try:
            username = (
                member.username
                or ""
            )

            photo_bytes = None

            # ------------------------------------------------
            # Download profile photo
            # ------------------------------------------------

            try:
                user = await app.get_users(
                    member.id
                )

                if (
                    user.photo
                    and user.photo.big_file_id
                ):
                    photo_bytes = (
                        await app.download_media(
                            user.photo.big_file_id,
                            in_memory=True
                        )
                    )

            except Exception:
                # No profile photo is fine.
                photo_bytes = None

            # ------------------------------------------------
            # Create welcome card
            # ------------------------------------------------

            card = _make_welcome_card(
                name=(
                    member.first_name
                    or "Friend"
                ),
                username=username,
                group_name=group_name,
                member_number=member_number,
                join_date=join_date,
                photo_bytes=photo_bytes,
            )

            # ------------------------------------------------
            # Caption
            # ------------------------------------------------

            caption = (
                f"<b>Welcome, {member.mention}! 👋</b>\n\n"
                f"Welcome to <b>{group_name}</b> 💙\n"
                f"Be active, be respectful & have fun!"
            )

            # ------------------------------------------------
            # BUTTONS
            #
            # User Profile:
            # - Shows user's first name
            # - Opens Telegram profile
            # - Uses premium/custom emoji ID
            #
            # Add Bot:
            # - Opens group-add flow
            # - Uses premium/custom emoji ID
            # ------------------------------------------------

            user_name = (
                member.first_name
                or "User"
            )

            user_button = InlineKeyboardButton(
                text=user_name,
                url=f"tg://user?id={member.id}",
                icon_custom_emoji_id=USER_PROFILE_EMOJI_ID,
            )

            add_bot_button = InlineKeyboardButton(
                text="Add Bot",
                url=(
                    "https://t.me/"
                    "ArchonBeatsBot"
                    "?startgroup=true"
                ),
                icon_custom_emoji_id=ADD_BOT_EMOJI_ID,
            )

            keyboard = InlineKeyboardMarkup(
                [
                    [
                        user_button,
                        add_bot_button,
                    ]
                ]
            )

            # ------------------------------------------------
            # Send
            # ------------------------------------------------

            await message.reply_photo(
                photo=card,
                caption=caption,
                reply_markup=keyboard,
                quote=False,
            )

        except Exception as e:

            print(
                f"[WELCOME] Failed for "
                f"{member.id}: "
                f"{type(e).__name__}: {e}",
                flush=True
            )
