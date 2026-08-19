"""
Payme.uz to'lov integratsiyasi.

DEMO rejimda: haqiqiy so'rov yubormaydi.
LIVE rejimga o'tish uchun:
  1. https://business.payme.uz da merchant oching
  2. .env faylga PAYME_MERCHANT_ID, PAYME_KEY yozing
  3. PAYME_MODE=live qiling
  4. Checkout URL generatsiyasini Payme hujjatiga ko'ra to'ldiring:
     https://developer.help.paycom.uz/
"""
import base64
from bot.config import config


def create_payment_link(order_id: int, amount: int) -> str:
    if config.payme_mode == "demo":
        return f"{config.webapp_url}/demo-pay?provider=payme&order_id={order_id}&amount={amount}"

    # TODO(live): Payme checkout parametrlarini base64 qilib kodlash
    amount_tiyin = amount * 100  # Payme summani tiyin (1/100) da kutadi
    raw = f"m={config.payme_merchant_id};ac.order_id={order_id};a={amount_tiyin}"
    encoded = base64.b64encode(raw.encode()).decode()
    return f"https://checkout.paycom.uz/{encoded}"


def verify_callback(data: dict) -> bool:
    """Payme JSON-RPC so'rovlarini tekshirish (LIVE rejimda kerak)."""
    if config.payme_mode == "demo":
        return True
    # TODO(live): Authorization header'dagi Basic auth'ni PAYME_KEY bilan solishtiring
    return False
