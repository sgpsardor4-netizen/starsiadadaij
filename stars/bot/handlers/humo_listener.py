"""
Humo bot guruhini tinglovchi handler.

Sozlash:
  1. Yopiq Telegram guruh oching
  2. Ushbu Stars Shop botini guruhga admin qilib qo'shing
  3. Sizning mavjud "Humo bot" (karta SMS/push xabarlarini forward qiluvchi
     bot)ni ham shu guruhga qo'shing
  4. Guruh ID'sini .env dagi HUMO_NOTIFY_CHAT_ID ga yozing

Ishlash tartibi:
  Humo bot guruhga "...+150,000 so'm..." kabi xabar yozganda, bu handler
  xabarni o'qiydi, summani ajratib oladi va shu summadagi eng mos
  (foydalanuvchi "to'lov qildim" degan yoki eng eski) kutilayotgan
  buyurtmani topib, avtomatik "to'landi" deb belgilaydi.

Humo botlar xabar formati har xil bo'lishi mumkin -- agar avtomatik
aniqlash ishlamasa, pastdagi AMOUNT_RE va INCOMING_HINTS ni o'z xabar
formatingizga moslab tahrirlang.
"""
import logging
import re

from aiogram import Router, F
from aiogram.types import Message

from bot.config import config
from bot.database import find_matching_humo_order, mark_paid
from bot.notify import notify_payment_success

AMOUNT_RE = re.compile(r"([\d][\d\s.,]*\d|\d)\s*(?:so['\u2019]?m|sum|uzs)", re.IGNORECASE)
INCOMING_HINTS = ("+", "kirim", "qabul qilindi", "zachislenie", "popolnenie")

router = Router()


def parse_amount(text: str) -> int | None:
    if not text:
        return None
    if not any(hint.lower() in text.lower() for hint in INCOMING_HINTS):
        return None
    match = AMOUNT_RE.search(text)
    if not match:
        return None
    digits = re.sub(r"[^\d]", "", match.group(1))
    return int(digits) if digits else None


@router.message(F.chat.id == config.humo_notify_chat_id)
async def on_humo_notification(message: Message):
    if not config.humo_notify_chat_id:
        return

    text = message.text or message.caption or ""
    amount = parse_amount(text)
    if amount is None:
        return

    order = await find_matching_humo_order(amount)
    if not order:
        logging.info(f"Humo xabari keldi ({amount} so'm), lekin mos buyurtma topilmadi.")
        return

    await mark_paid(order["id"], provider_payment_id="humo-auto")
    order["status"] = "paid"
    await notify_payment_success(message.bot, order)

    # Admindagi "tekshirish" xabarini (agar bo'lsa) yangilab, tugmalarni olib tashlaymiz —
    # buyurtma allaqachon avtomatik tasdiqlangan, admin qayta bosmasin
    if order.get("admin_msg_id") and config.admin_chat_id:
        try:
            await message.bot.edit_message_text(
                chat_id=config.admin_chat_id,
                message_id=order["admin_msg_id"],
                text=(
                    f"💳 Humo to'lovi — Buyurtma #{order['id']}\n\n"
                    f"✅ Tizim tomonidan avtomatik tasdiqlandi ({amount:,} so'm)."
                ),
                reply_markup=None,
            )
        except Exception:
            pass

    try:
        await message.reply(
            f"Buyurtma #{order['id']} avtomatik tasdiqlandi ({amount:,} so'm)."
        )
    except Exception:
        pass
