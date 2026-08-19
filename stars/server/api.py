import logging
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from bot.config import config, PACKAGES, get_package
from bot.database import (
    init_db, create_order, mark_paid, mark_fulfilled, get_order,
    mark_user_confirmed, set_admin_msg_id,
)
from bot.payments import click, payme, yookassa, humo
from bot.notify import notify_payment_success
from bot.keyboards import humo_review_kb

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Stars Shop API")

bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML)) \
    if config.bot_token else None


@app.on_event("startup")
async def on_startup():
    await init_db()


# ---------- Mini App statik fayllari ----------
app.mount("/app", StaticFiles(directory="miniapp", html=True), name="miniapp")


@app.get("/", response_class=HTMLResponse)
async def root():
    return "<meta http-equiv='refresh' content='0; url=/app/index.html'>"


# ---------- API: paketlar ro'yxati ----------
@app.get("/api/packages")
async def api_packages():
    return [
        {
            "id": p.id,
            "stars": p.stars,
            "price_uzs": p.price_uzs,
            "price_rub": p.price_rub,
        }
        for p in PACKAGES
    ]


# ---------- API: buyurtma yaratish + to'lov linki ----------
class CreateOrderRequest(BaseModel):
    user_id: int
    username: str = ""
    package_id: str
    currency: str  # UZS | RUB
    provider: str  # click | payme | yookassa


@app.post("/api/create-order")
async def api_create_order(req: CreateOrderRequest):
    pkg = get_package(req.package_id)
    if not pkg:
        raise HTTPException(404, "Paket topilmadi")

    if req.currency == "UZS":
        amount = pkg.price_uzs
        if req.provider not in ("click", "payme", "humo"):
            raise HTTPException(400, "UZS uchun faqat Click, Payme yoki Humo")
    elif req.currency == "RUB":
        amount = pkg.price_rub
        if req.provider != "yookassa":
            raise HTTPException(400, "RUB uchun faqat YooKassa")
    else:
        raise HTTPException(400, "Noto'g'ri valyuta")

    order_id = await create_order(
        user_id=req.user_id,
        username=req.username,
        package_id=pkg.id,
        stars=pkg.stars,
        currency=req.currency,
        amount=amount,
        provider=req.provider,
    )

    return_url = f"{config.webapp_url}/app/index.html?paid=1&order_id={order_id}"

    if req.provider == "click":
        link = click.create_payment_link(order_id, amount, return_url)
        return {"order_id": order_id, "payment_url": link}

    if req.provider == "payme":
        link = payme.create_payment_link(order_id, amount)
        return {"order_id": order_id, "payment_url": link}

    if req.provider == "yookassa":
        link = yookassa.create_payment_link(order_id, amount, return_url)
        return {"order_id": order_id, "payment_url": link}

    # humo — tashqi to'lov linki yo'q, karta ma'lumotlari qaytariladi
    card = humo.get_card_details()
    return {
        "order_id": order_id,
        "manual": {
            "amount": amount,
            "card_number": card["card_number"],
            "card_holder": card["card_holder"],
        },
    }


# ---------- Demo to'lov sahifasi (faqat DEMO rejim uchun) ----------
@app.get("/demo-pay", response_class=HTMLResponse)
async def demo_pay(provider: str, order_id: int, amount: int):
    return f"""
    <html><body style="font-family:sans-serif;text-align:center;padding-top:60px;">
      <h2>🧪 DEMO to'lov — {provider.upper()}</h2>
      <p>Summasi: <b>{amount}</b></p>
      <button onclick="confirmPay()" style="padding:12px 24px;font-size:16px;">
        ✅ To'lovni tasdiqlash (demo)
      </button>
      <script>
        async function confirmPay() {{
          await fetch('/api/confirm-payment', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{order_id: {order_id}, provider_payment_id: 'demo-tx'}})
          }});
          document.body.innerHTML = "<h2>✅ To'lov tasdiqlandi!</h2><p>Botga qayting.</p>";
          if (window.Telegram && window.Telegram.WebApp) {{
            window.Telegram.WebApp.close();
          }}
        }}
      </script>
    </body></html>
    """


# ---------- To'lov tasdiqlash (demo tugmasi yoki real webhook shu yerga tushadi) ----------
class ConfirmPaymentRequest(BaseModel):
    order_id: int
    provider_payment_id: str = ""


@app.post("/api/confirm-payment")
async def api_confirm_payment(req: ConfirmPaymentRequest):
    """Click/Payme/YooKassa demo tugmasi (yoki live webhook) shu yerga tushadi.
    Humo uchun ishlatilmaydi — u avtomatik guruh xabari orqali tasdiqlanadi."""
    order = await get_order(req.order_id)
    if not order:
        raise HTTPException(404, "Buyurtma topilmadi")

    await mark_paid(req.order_id, req.provider_payment_id)
    await notify_payment_success(bot, order)
    return {"ok": True}


class MarkSentRequest(BaseModel):
    order_id: int


@app.post("/api/mark-sent")
async def api_mark_sent(req: MarkSentRequest):
    """Humo oqimida: mijoz 'To'lov qildim' tugmasini bosganda chaqiriladi.
    Buyurtmani hali 'to'landi' deb belgilamaydi — faqat Humo bot guruhidan
    xabar kelganda mos summa bilan solishtirish uchun ustuvorlik beradi.
    Shu bilan birga adminga tekshirish uchun tugmali xabar yuboriladi —
    avtomatik aniqlash ishlamasa yoki kechiksa, admin qo'lda tasdiqlashi/bekor
    qilishi mumkin bo'ladi."""
    order = await get_order(req.order_id)
    if not order:
        raise HTTPException(404, "Buyurtma topilmadi")
    if order["provider"] != "humo":
        raise HTTPException(400, "Bu endpoint faqat Humo buyurtmalari uchun")

    await mark_user_confirmed(req.order_id)

    if bot and config.admin_chat_id:
        try:
            msg = await bot.send_message(
                config.admin_chat_id,
                f"💳 Humo to'lovi — Buyurtma #{order['id']}\n\n"
                f"Foydalanuvchi: {order['user_id']} (@{order['username']})\n"
                f"⭐ {order['stars']} Stars\n"
                f"Summasi: {order['amount']:,} so'm\n\n"
                f"Mijoz \"to'lov qildim\" dedi. Tizim avtomatik tekshiradi, "
                f"ammo kerak bo'lsa qo'lda ham hal qilishingiz mumkin:",
                reply_markup=humo_review_kb(order["id"]),
            )
            await set_admin_msg_id(order["id"], msg.message_id)
        except Exception as e:
            logging.warning(f"Admin xabari yuborilmadi: {e}")

    return {"ok": True}
