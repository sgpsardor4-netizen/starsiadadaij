from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

from bot.config import config

router = Router()


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⭐ Stars sotib olish",
                    web_app=WebAppInfo(url=config.webapp_url),
                )
            ],
            [InlineKeyboardButton(text="🆘 Yordam", callback_data="help")],
        ]
    )


@router.message(CommandStart())
async def cmd_start(message: Message):
    text = (
        "⭐ <b>STARS SHOP</b>ga xush kelibsiz!\n\n"
        "Bu yerda Telegram Stars'ni qulay narxda, "
        "🇺🇿 Click/Payme yoki 🇷🇺 YooKassa orqali sotib olishingiz mumkin.\n\n"
        "Boshlash uchun pastdagi tugmani bosing 👇"
    )
    await message.answer(text, reply_markup=main_menu_kb())


@router.callback_query(F.data == "help")
async def cb_help(callback):
    await callback.message.answer(
        "Savol bo'lsa admin bilan bog'laning: @your_admin_username\n"
        "Buyurtma tarixini ko'rish uchun: /orders"
    )
    await callback.answer()
