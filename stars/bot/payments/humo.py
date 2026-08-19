"""
Humo karta orqali qo'lda o'tkazma.

Bu boshqa provayderlardan farqli — bu yerda tashqi to'lov tizimiga so'rov
yuborilmaydi. Mijoz to'g'ridan-to'g'ri sizning Humo kartangizga pul o'tkazadi,
so'ng tasdiqlash sizda allaqachon bo'lgan "Humo bot" (karta SMS/push
xabarlarini Telegram guruhga forward qiluvchi bot) orqali avtomatik amalga
oshadi — qarang: bot/handlers/humo_listener.py
"""
from bot.config import config


def get_card_details() -> dict:
    return {
        "card_number": config.humo_card_number,
        "card_holder": config.humo_card_holder,
    }
