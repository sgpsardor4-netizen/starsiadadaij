from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def humo_review_kb(order_id: int) -> InlineKeyboardMarkup:
    """Humo qo'lda to'lovini admin tasdiqlashi/bekor qilishi uchun tugmalar."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"humo_ok:{order_id}"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"humo_no:{order_id}"),
            ]
        ]
    )
