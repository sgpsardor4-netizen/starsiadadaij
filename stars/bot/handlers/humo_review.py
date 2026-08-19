"""
Humo qo'lda to'lovlarini admin tomonidan qo'lda tekshirish.

Avtomatik aniqlash (bot/handlers/humo_listener.py) odatda o'zi ishlaydi,
lekin agar Humo botning xabar formati moslashmasa yoki biroz kechiksa,
admin buyurtmani shu tugmalar orqali qo'lda tasdiqlashi yoki bekor qilishi
mumkin. Tugmalar mijoz "To'lov qildim" deganda admin chatga yuboriladi
(qarang: server/api.py -> /api/mark-sent).
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.config import config
from bot.database import get_order, mark_paid, mark_failed
from bot.notify import notify_payment_success

router = Router()


@router.callback_query(F.data.startswith("humo_ok:"))
async def cb_confirm(callback: CallbackQuery):
    if callback.from_user.id != config.admin_chat_id:
        await callback.answer("Faqat admin tasdiqlay oladi.", show_alert=True)
        return

    order_id = int(callback.data.split(":")[1])
    order = await get_order(order_id)
    if not order:
        await callback.answer("Buyurtma topilmadi.", show_alert=True)
        return
    if order["status"] != "pending":
        await callback.answer("Bu buyurtma allaqachon hal qilingan.", show_alert=True)
        return

    await mark_paid(order_id, provider_payment_id="humo-admin-manual")
    order["status"] = "paid"
    await notify_payment_success(callback.bot, order)

    await callback.message.edit_text(
        callback.message.text + "\n\n✅ Admin tomonidan qo'lda tasdiqlandi.",
        reply_markup=None,
    )
    await callback.answer("Tasdiqlandi ✅")


@router.callback_query(F.data.startswith("humo_no:"))
async def cb_cancel(callback: CallbackQuery):
    if callback.from_user.id != config.admin_chat_id:
        await callback.answer("Faqat admin bekor qila oladi.", show_alert=True)
        return

    order_id = int(callback.data.split(":")[1])
    order = await get_order(order_id)
    if not order:
        await callback.answer("Buyurtma topilmadi.", show_alert=True)
        return
    if order["status"] != "pending":
        await callback.answer("Bu buyurtma allaqachon hal qilingan.", show_alert=True)
        return

    await mark_failed(order_id)
    try:
        await callback.bot.send_message(
            order["user_id"],
            f"❌ Buyurtma #{order_id} bekor qilindi.\n"
            f"To'lov qilgan bo'lsangiz-u, xato deb hisoblasangiz, admin bilan bog'laning.",
        )
    except Exception:
        pass

    await callback.message.edit_text(
        callback.message.text + "\n\n❌ Admin tomonidan bekor qilindi.",
        reply_markup=None,
    )
    await callback.answer("Bekor qilindi ❌")
