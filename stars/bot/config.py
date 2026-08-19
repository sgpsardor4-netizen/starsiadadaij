import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class StarPackage:
    id: str
    stars: int
    price_uzs: int   # so'm
    price_rub: int   # rubl


# ⭐ Stars paketlari — narxlarni bu yerda o'zgartirasiz
PACKAGES: list[StarPackage] = [
    StarPackage(id="p50", stars=50, price_uzs=9_900, price_rub=79),
    StarPackage(id="p100", stars=100, price_uzs=18_900, price_rub=149),
    StarPackage(id="p250", stars=250, price_uzs=44_900, price_rub=349),
    StarPackage(id="p500", stars=500, price_uzs=86_900, price_rub=679),
    StarPackage(id="p1000", stars=1000, price_uzs=169_900, price_rub=1_329),
]


@dataclass
class Config:
    bot_token: str = os.getenv("BOT_TOKEN", "")
    admin_chat_id: int = int(os.getenv("ADMIN_CHAT_ID", "0") or 0)
    webapp_url: str = os.getenv("WEBAPP_URL", "http://localhost:8000")

    click_merchant_id: str = os.getenv("CLICK_MERCHANT_ID", "demo")
    click_service_id: str = os.getenv("CLICK_SERVICE_ID", "demo")
    click_secret_key: str = os.getenv("CLICK_SECRET_KEY", "demo")
    click_mode: str = os.getenv("CLICK_MODE", "demo")

    payme_merchant_id: str = os.getenv("PAYME_MERCHANT_ID", "demo")
    payme_key: str = os.getenv("PAYME_KEY", "demo")
    payme_mode: str = os.getenv("PAYME_MODE", "demo")

    yookassa_shop_id: str = os.getenv("YOOKASSA_SHOP_ID", "demo")
    yookassa_secret_key: str = os.getenv("YOOKASSA_SECRET_KEY", "demo")
    yookassa_mode: str = os.getenv("YOOKASSA_MODE", "demo")

    # Humo karta orqali qo'lda to'lov (Humo bot guruhidan avtomatik tasdiqlash)
    humo_card_number: str = os.getenv("HUMO_CARD_NUMBER", "8600 0000 0000 0000")
    humo_card_holder: str = os.getenv("HUMO_CARD_HOLDER", "F. F. ISMOV")
    humo_notify_chat_id: int = int(os.getenv("HUMO_NOTIFY_CHAT_ID", "0") or 0)

    database_path: str = os.getenv("DATABASE_PATH", "./stars_shop.db")


config = Config()


def get_package(package_id: str) -> StarPackage | None:
    return next((p for p in PACKAGES if p.id == package_id), None)
