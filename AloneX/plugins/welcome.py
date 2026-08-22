# Copyright (c) 2026 THE SHIV
# Welcome card plugin for TestBot
#
# Place this file at:
#   AloneX/plugins/welcome.py
#
# Pillow is already present in requirements.txt.

import io
from datetime import datetime

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
from pyrogram import filters, types

from AloneX import app


BASE_DIR = Path(__file__).resolve().parent.parent
FONT_DIR = BASE_DIR / "helpers"

# Card size
WIDTH, HEIGHT = 1600, 900


def _font(name: str, size: int):
    """Load one of the fonts already included in the repository."""
    path = FONT_DIR / name
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def _fit_text(draw, text, font, max_width):
    """Return a shortened text that fits the requested width."""
    if draw.textbbox((0, 0), text, font=font)[2] <= max_width:
        return text

    text = text[:30].rstrip()
    while text and draw.textbbox((0, 0), text + "…", font=font)[2] > max_width:
        text = text[:-1]
    return (text + "…") if text else "User"


def _rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, size[0] - 1, size[1] - 1),
        radius=radius,
        fill=255,
    )
    return mask


def _circle_photo(photo_bytes, size=500):
    """Crop a downloaded Telegram profile photo into a circle."""
    try:
        photo = Image.open(photo_bytes).convert("RGB")
    except Exception:
        return None

    side = min(photo.size)
    left = (photo.width - side) // 2
    top = (photo.height - side) // 2
    photo = photo.crop((left, top, left + side, top + side))
    photo = ImageOps.fit(photo, (size, size), method=Image.Resampling.LANCZOS)

    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)

    result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    result.paste(photo, (0, 0), mask)
    return result


def _make_welcome_card(
    name: str,
    username: str,
    group_name: str,
    member_number: int,
    join_date: str,
    photo_bytes=None,
):
    """Create the final welcome image in memory."""
    # Dark, soft background.
    canvas = Image.new("RGB", (WIDTH, HEIGHT), (11, 16, 25))

    # Abstract blurred background.
    bg = Image.new("RGB", (WIDTH, HEIGHT), (17, 29, 45))
    bd = ImageDraw.Draw(bg, "RGBA")
    bd.ellipse((-250, -220, 650, 620), fill=(35, 92, 130, 130))
    bd.ellipse((1050, 380, 1850, 1150), fill=(25, 75, 115, 100))
    bd.ellipse((650, 150, 1250, 750), fill=(50, 65, 95, 70))
    bg = bg.filter(ImageFilter.GaussianBlur(90))
    canvas.paste(bg)

    # Main glass card.
    card = Image.new("RGBA", (1450, 760), (20, 27, 39, 238))
    cd = ImageDraw.Draw(card, "RGBA")
    cd.rounded_rectangle(
        (0, 0, 1449, 759),
        radius=42,
        fill=(20, 27, 39, 235),
        outline=(92, 132, 165, 85),
        width=2,
    )

    # Left photo area.
    photo_x, photo_y, photo_size = 55, 55, 650
    cd.rounded_rectangle(
        (photo_x, photo_y, photo_x + photo_size, photo_y + photo_size),
        radius=34,
        fill=(12, 18, 28, 255),
    )

    photo = _circle_photo(photo_bytes, 470) if photo_bytes else None

    if photo is None:
        # Clean fallback avatar.
        fallback = Image.new("RGBA", (470, 470), (28, 43, 58, 255))
        fd = ImageDraw.Draw(fallback)
        fd.ellipse((145, 90, 325, 270), fill=(110, 130, 145, 255))
        fd.rounded_rectangle((90, 245, 380, 430), radius=80, fill=(110, 130, 145, 255))
        photo = fallback

    photo_x2 = photo_x + (photo_size - photo.width) // 2
    photo_y2 = photo_y + 70
    card.alpha_composite(photo, (photo_x2, photo_y2))

    # Small greeting on the photo panel.
    white = (245, 248, 252, 255)
    muted = (168, 184, 201, 255)
    blue = (92, 177, 255, 255)

    title_font = _font("Poppins-ExtraBold.ttf", 54)
    name_font = _font("Poppins-ExtraBold.ttf", 38)
    body_font = _font("Inter-Light.ttf", 27)
    small_font = _font("Inter-Light.ttf", 22)

    cd.text((82, 625), "HEY,", font=title_font, fill=muted)
    safe_name = _fit_text(cd, name, name_font, 570)
    cd.text((82, 678), safe_name + " 👋", font=name_font, fill=white)

    # Right information panel.
    rx = 760
    cd.text((rx, 75), "WELCOME ABOARD!", font=title_font, fill=white)
    cd.text(
        (rx, 145),
        "Glad to have you here.",
        font=body_font,
        fill=(185, 201, 217, 255),
    )

    # Divider.
    cd.line((rx, 205, 1370, 205), fill=(92, 132, 165, 90), width=2)

    # Info rows.
    label_font = _font("Inter-Light.ttf", 20)
    value_font = _font("Poppins-ExtraBold.ttf", 28)

    rows = [
        ("USER", f"@{username}" if username else name),
        ("GROUP", group_name),
        ("MEMBER", f"#{member_number}"),
        ("JOINED", join_date),
    ]

    y = 245
    for label, value in rows:
        cd.text((rx, y), label, font=label_font, fill=(122, 151, 177, 255))
        value = _fit_text(cd, value, value_font, 570)
        cd.text((rx, y + 28), value, font=value_font, fill=white)
        y += 105

    # Bottom message pill.
    pill_y = 635
    cd.rounded_rectangle(
        (rx, pill_y, 1370, pill_y + 65),
        radius=28,
        fill=(34, 54, 73, 230),
        outline=(76, 143, 193, 100),
        width=1,
    )
    cd.text(
        (rx + 25, pill_y + 17),
        "Be active, Be respectful & Have fun! 💙",
        font=small_font,
        fill=(207, 222, 236, 255),
    )

    canvas_rgba = canvas.convert("RGBA")
    canvas_rgba.alpha_composite(card, ((WIDTH - card.width) // 2, (HEIGHT - card.height) // 2))

    # Return Telegram-friendly in-memory JPEG.
    output = io.BytesIO()
    canvas_rgba.convert("RGB").save(output, format="JPEG", quality=94, optimize=True)
    output.name = "welcome.jpg"
    output.seek(0)
    return output


@app.on_message(filters.new_chat_members, group=6)
async def welcome_new_members(_, message: types.Message):
    """
    Sends the welcome card whenever a normal user joins a supergroup.
    The existing start.py handler remains responsible for bot-join setup.
    """
    if message.chat.type != "supergroup":
        return

    # Never send a welcome card for the bot itself.
    members = [u for u in message.new_chat_members if u.id != app.id]
    if not members:
        return

    # Get the current member count once for this event.
    try:
        member_number = await app.get_chat_members_count(message.chat.id)
    except Exception:
        member_number = 0

    group_name = message.chat.title or "Our Group"
    join_date = datetime.now().strftime("%d %b %Y")

    for member in members:
        try:
            photo_bytes = None
            username = member.username or ""

            # Download the member's Telegram profile photo if available.
            try:
                user = await app.get_users(member.id)
                if user.photo and user.photo.big_file_id:
                    photo_bytes = await app.download_media(
                        user.photo.big_file_id,
                        in_memory=True,
                    )
            except Exception:
                photo_bytes = None

            card = _make_welcome_card(
                name=member.first_name or "Friend",
                username=username,
                group_name=group_name,
                member_number=member_number,
                join_date=join_date,
                photo_bytes=photo_bytes,
            )

            mention = member.mention
            caption = (
                f"<b>Welcome, {mention}! 👋</b>\n\n"
                f"Welcome to <b>{group_name}</b> 💙\n"
                f"Be active, be respectful & have fun!"
            )

            await message.reply_photo(
                photo=card,
                caption=caption,
                quote=False,
            )

        except Exception as e:
            print(f"[WELCOME] Failed for {member.id}: {e}")
