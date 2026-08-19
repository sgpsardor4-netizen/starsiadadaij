import re
from aiogram import Router
from aiogram.types import Message

from bot.config import config
from bot.database import mark_fulfilled, get_order

router = Router()


@router.message(lambda m: m.text and re.match(r"^/fulfill_\d+$", m.text))
async def cmd_fulfill(message: Message):
    if message.from_user.id != config.admin_chat_id:
        return  # faqat admin uchun

    order_id = int(message.text.split("_")[1])
    order = await get_order(order_id)
    if not order:
        await message.answer("Buyurtma topilmadi.")
        return

    await mark_fulfilled(order_id)
    await message.answer(f"✅ Buyurtma #{order_id} 'bajarildi' deb belgilandi.")

    try:
        await message.bot.send_message(
            order["user_id"],
            f"⭐ {order['stars']} Stars hisobingizga o'tkazildi! Rahmat 🙏",
        )
    except Exception:
        pass
