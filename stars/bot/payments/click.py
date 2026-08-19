"""
Click.uz to'lov integratsiyasi.

DEMO rejimda: haqiqiy so'rov yubormaydi, to'lov linkini simulyatsiya qiladi.
LIVE rejimga o'tish uchun:
  1. https://merchant.click.uz da merchant ro'yxatdan o'tkazing
  2. .env faylga CLICK_MERCHANT_ID, CLICK_SERVICE_ID, CLICK_SECRET_KEY yozing
  3. CLICK_MODE=live qiling
  4. create_payment_link() ichidagi TODO qismini Click hujjatiga ko'ra to'ldiring:
     https://docs.click.uz/click-api-request/
"""
from bot.config import config


def create_payment_link(order_id: int, amount: int, return_url: str) -> str:
    if config.click_mode == "demo":
        # Demo: mini-app o'zi "to'landi" deb hisoblaydigan sahifa
        return f"{config.webapp_url}/demo-pay?provider=click&order_id={order_id}&amount={amount}"

    # TODO(live): Click Checkout URL generatsiya qilish
    # merchant_id, service_id, secret_key asosida imzo (sign) hisoblanadi
    base = "https://my.click.uz/services/pay"
    return (
        f"{base}?service_id={config.click_service_id}"
        f"&merchant_id={config.click_merchant_id}"
        f"&amount={amount}&transaction_param={order_id}"
        f"&return_url={return_url}"
    )


def verify_callback(data: dict) -> bool:
    """Click 'Prepare/Complete' webhook imzosini tekshirish (LIVE rejimda kerak)."""
    if config.click_mode == "demo":
        return True
    # TODO(live): sign_string ni md5(click_trans_id+service_id+SECRET_KEY+...) bo'yicha tekshiring
    return False
