"""
YooKassa (RUB) to'lov integratsiyasi.

DEMO rejimda: haqiqiy so'rov yubormaydi.
LIVE rejimga o'tish uchun:
  1. https://yookassa.ru da do'kon (shop) oching
  2. .env faylga YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY yozing
  3. YOOKASSA_MODE=live qiling
  4. pip install qilingan `yookassa` SDK avtomatik ishlatiladi.
     Hujjat: https://yookassa.ru/developers/api
"""
import uuid
from bot.config import config


def create_payment_link(order_id: int, amount_rub: int, return_url: str) -> str:
    if config.yookassa_mode == "demo":
        return f"{config.webapp_url}/demo-pay?provider=yookassa&order_id={order_id}&amount={amount_rub}"

    from yookassa import Configuration, Payment

    Configuration.account_id = config.yookassa_shop_id
    Configuration.secret_key = config.yookassa_secret_key

    payment = Payment.create(
        {
            "amount": {"value": f"{amount_rub}.00", "currency": "RUB"},
            "confirmation": {"type": "redirect", "return_url": return_url},
            "capture": True,
            "description": f"Stars buyurtma #{order_id}",
            "metadata": {"order_id": order_id},
        },
        uuid.uuid4(),
    )
    return payment.confirmation.confirmation_url


def verify_callback(data: dict) -> bool:
    """YooKassa webhook holatini tekshirish (LIVE rejimda kerak)."""
    if config.yookassa_mode == "demo":
        return True
    # TODO(live): webhook IP manzillarini YooKassa docs bo'yicha tekshiring
    return data.get("event") == "payment.succeeded"
