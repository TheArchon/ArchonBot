from pyrogram import types

print("Testing custom emoji button...")

try:
    button = types.InlineKeyboardButton(
        text="TEST",
        callback_data="test",
        icon_custom_emoji_id="6100125944381444896",
    )

    print("BUTTON CREATED SUCCESSFULLY")
    print(button)
    print(
        "ICON ID:",
        getattr(button, "icon_custom_emoji_id", None)
    )

except Exception as e:
    print("CUSTOM EMOJI ERROR:")
    print(type(e).__name__)
    print(str(e))
