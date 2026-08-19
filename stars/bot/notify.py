import logging
from aiogram import Bot
from bot.config import config


async def notify_payment_success(bot: Bot, order: dict):
    """Foydalanuvchiga va adminga xabar yuboradi.

    ESLATMA: Telegram bot arbitrar foydalanuvchiga real Stars'ni avtomatik
    kredit qila olmaydi — buning uchun Fragment.com API (TON orqali) yoki
    admin tomonidan qo'lda tasdiqlash kerak. Shu sabab bu yerda:
      1) foydalanuvchiga "to'lov qabul qilindi, Stars tez orada beriladi" deyiladi
      2) admin chatiga buyurtma tafsilotlari yuboriladi (qo'lda/avtomatik
         Fragment orqali bajarish uchun)
    """
    if not bot:
        return

    try:
        await bot.send_message(
            order["user_id"],
            f"✅ To'lovingiz qabul qilindi!\n\n"
            f"⭐ {order['stars']} Stars tez orada hisobingizga o'tkaziladi.\n"
            f"Buyurtma raqami: #{order['id']}",
        )
    except Exception as e:
        logging.warning(f"Foydalanuvchiga xabar yuborilmadi: {e}")

    if config.admin_chat_id:
        try:
            await bot.send_message(
                config.admin_chat_id,
                f"🆕 <b>Yangi to'langan buyurtma</b>\n"
                f"ID: #{order['id']}\n"
                f"Foydalanuvchi: {order['user_id']} (@{order['username']})\n"
                f"⭐ {order['stars']} Stars\n"
                f"Summasi: {order['amount']} {order['currency']}\n"
                f"Provider: {order['provider']}\n\n"
                f"👉 Stars'ni Fragment.com yoki boshqa usul orqali qo'lda bering, "
                f"so'ng /fulfill_{order['id']} buyrug'ini yuboring.",
            )
        except Exception as e:
            logging.warning(f"Adminga xabar yuborilmadi: {e}")
