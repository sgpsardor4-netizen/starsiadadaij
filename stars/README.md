# ⭐ Stars Shop — Telegram Bot + Mini App

Telegram Stars sotadigan bot va mini-app. 🇺🇿 UZS uchun Click/Payme/Humo karta, 🇷🇺 RUB uchun YooKassa.

Hozircha **DEMO rejim**da ishlaydi — to'lov tizimlariga haqiqiy so'rov yubormaydi,
faqat butun oqimni (paket tanlash → to'lov → tasdiqlash → xabar) sinab ko'rish uchun.

---

## 1. O'rnatish

```bash
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

`.env` faylni oching va kamida shularni to'ldiring:

```
BOT_TOKEN=...        # @BotFather'dan oling
ADMIN_CHAT_ID=...     # o'zingizning Telegram ID'ingiz (@userinfobot orqali bilib oling)
WEBAPP_URL=http://localhost:8000   # keyinroq real domenga almashtirasiz
```

## 2. Ishga tushirish (lokal test)

Ikkita terminal kerak:

```bash
# 1-terminal — mini app + API server
uvicorn server.api:app --reload --port 8000

# 2-terminal — bot (polling)
python -m bot.main
```

Botga `/start` yozing → "⭐ Stars sotib olish" tugmasi mini-app'ni ochadi.

> Lokal test paytida Telegram WebApp faqat **https** domenlarni ochadi.
> Shu sababli haqiqiy botda sinash uchun serverni internetga chiqarish kerak
> (pastga qarang) yoki `ngrok http 8000` bilan vaqtinchalik https link oling.

## 3. Arzon hosting (~10 000 so'm/oy byudjet uchun)

Bot **polling** rejimida ishlaydi (webhook shart emas), shuning uchun eng arzon variantlar mos keladi:

| Variant | Narx | Izoh |
|---|---|---|
| **Railway.app** free tier | $0 (limitgacha) | Eng oson, git push qilasiz — tayyor |
| **Render.com** free web service | $0 | Uxlab qoladi, lekin bot+API uchun yetarli |
| **PythonAnywhere** | $0 (Always-on task cheklangan) | Bot uchun mos |
| Eng arzon VPS (Timeweb, Hostinger) | ~15 000–25 000 so'm/oy | To'liq nazorat, byudjetdan biroz oshadi |

Tavsiya: avval **Render yoki Railway free tier**da sinab ko'ring — bu amalda 0 so'mga tushadi,
faqat trafik ko'paysa pullik tarifga o'tasiz.

Deploy qilgach, `.env` dagi `WEBAPP_URL`ni haqiqiy domeningizga (masalan
`https://stars-shop.onrender.com`) almashtiring va shu URL'ni bot serverida ham ishlating.

## 4. Real to'lov tizimlarini ulash

Har bir provayder faylida (`bot/payments/click.py`, `payme.py`, `yookassa.py`) `TODO(live)`
belgilangan joylar bor. Kalitlarni olgandan so'ng:

1. `.env`da tegishli `_MODE=live` qiling
2. Merchant kalitlarni to'ldiring
3. Click/Payme uchun webhook (Prepare/Complete) endpointlarini `server/api.py`ga qo'shish kerak
   bo'ladi — hozircha faqat demo tugma orqali tasdiqlash bor

Hujjatlar:
- Click: https://docs.click.uz
- Payme: https://developer.help.paycom.uz
- YooKassa: https://yookassa.ru/developers/api

## 5. ⭐ Stars'ni haqiqiy berish haqida MUHIM eslatma

Telegram bot API orqali botlar ixtiyoriy foydalanuvchiga Stars'ni **avtomatik** kredit qila
olmaydi — bu Telegramning rasmiy Stars ekotizimi (Fragment.com, TON blokcheyn) orqali yoki
qo'lda amalga oshiriladi. Shu sabab loyihada:

- To'lov muvaffaqiyatli bo'lganda **admin chatga** buyurtma tafsilotlari yuboriladi
- Admin Stars'ni Fragment.com (yoki boshqa usul) orqali qo'lda beradi
- So'ng botga `/fulfill_<order_id>` yozib, buyurtmani "bajarildi" deb belgilaydi va
  foydalanuvchiga avtomatik xabar boradi

Agar buyurtmalar ko'payib, qo'lda berish qiyinlashsa, Fragment.com'ning API'siga
(TON kошelek orqali) avtomatik integratsiya qilish mumkin — bu alohida qo'shimcha ish.

## 6. Humo karta orqali qo'lda to'lov (avtomatik tasdiqlash bilan)

Bu usulda mijoz to'g'ridan-to'g'ri sizning Humo kartangizga pul o'tkazadi, keyin mini-app'da
**"To'lov qildim"** tugmasini bosadi. Tizim to'lovni **avtomatik** aniqlash uchun sizda
allaqachon bo'lgan "Humo bot" (karta SMS/push xabarlarini Telegram'ga forward qiluvchi
bot)dan foydalanadi — bu botni o'zingiz allaqachon topgansiz, biz faqat unga "quloq solamiz".

**Sozlash:**

1. Yangi (yopiq) Telegram guruh oching
2. Ushbu Stars Shop botingizni guruhga **admin** qilib qo'shing (xabarlarni o'qishi uchun)
3. Mavjud Humo bot'ni ham shu guruhga qo'shing — u pul kelganda avtomatik xabar yozadi
4. Guruh ID'sini oling (masalan, guruhga biror xabar yuborib, @RawDataBot yordamida)
5. `.env` faylga yozing:
   ```
   HUMO_NOTIFY_CHAT_ID=-1001234567890
   HUMO_CARD_NUMBER=8600 1234 5678 9012
   HUMO_CARD_HOLDER=F. F. ISMOV
   ```

**Ishlash tartibi:**

1. Mijoz mini-app'da "Humo karta"ni tanlaydi → karta raqami va summasi ko'rsatiladi
2. Mijoz pul o'tkazadi va **"✅ To'lov qildim"** tugmasini bosadi
3. Shu zahoti sizga (admin chatga) buyurtma tafsilotlari va **✅ Tasdiqlash / ❌ Bekor qilish**
   tugmalari yuboriladi
4. Humo bot guruhga masalan `"...+150 000 so'm..."` kabi xabar yozganda,
   Stars Shop bot bu xabarni o'qib, summani ajratib oladi
5. Xuddi shu summadagi kutilayotgan buyurtma bilan solishtiradi (avval "to'lov qildim"
   deganlar, keyin eng eski buyurtma bo'yicha)
6. Mos kelsa — buyurtma **avtomatik "to'landi"** deb belgilanadi, sizga yuborilgan
   tekshirish xabaridagi tugmalar olib tashlanadi (qayta bosilmasin uchun)

**Agar avtomatik aniqlash ishlamasa yoki kechiksa** — 3-qadamda kelgan xabardagi
tugmalardan foydalanib, buyurtmani o'zingiz qo'lda **tasdiqlashingiz** yoki
(masalan, mijoz yolg'on aytgan bo'lsa) **bekor qilishingiz** mumkin. Bekor qilingan
buyurtma mijozga xabar bilan birga rad etiladi va avtomatik tekshiruvda endi
qatnashmaydi.

⚠️ **Muhim eslatma:** Humo botlar xabar formati turlicha bo'lishi mumkin (`+150 000 so'm`,
`Kirim: 150,000 UZS` va h.k.). `bot/handlers/humo_listener.py` faylidagi
`AMOUNT_RE` va `INCOMING_HINTS` o'zgaruvchilarini o'zingizdagi Humo bot xabar formatiga
qarab moslashtiring — hozirgi holatda eng keng tarqalgan formatlarni tanib oladi
(yuqorida sinovdan o'tkazilgan).

Ikki yoki undan ortiq mijoz **bir xil summada** to'lov qilsa, tizim avval
"to'lov qildim" tugmasini bosganlarni ustuvor qiladi — shuning uchun mijozlarga har doim
shu tugmani bosishni eslatib turing.

## 7. Loyiha strukturasi

```
stars-shop-bot/
├── bot/
│   ├── main.py            # bot entrypoint (polling)
│   ├── config.py          # sozlamalar, Stars paketlari va narxlar
│   ├── database.py        # SQLite (buyurtmalar)
│   ├── notify.py          # foydalanuvchi/admin xabarlari (umumiy)
│   ├── handlers/
│   │   ├── start.py           # /start, asosiy menyu
│   │   ├── orders.py          # /orders — buyurtmalar tarixi
│   │   ├── admin.py           # /fulfill_<id> — admin uchun
│   │   └── humo_listener.py   # Humo bot guruhini tinglaydi
│   └── payments/
│       ├── click.py
│       ├── payme.py
│       ├── yookassa.py
│       └── humo.py
├── server/
│   └── api.py              # FastAPI: mini-app + /api/* endpointlar
├── miniapp/
│   └── index.html           # mini-app (bitta fayl: HTML+CSS+JS)
├── requirements.txt
└── .env.example
```

## 8. Narxlar va paketlarni o'zgartirish

`bot/config.py` faylidagi `PACKAGES` ro'yxatini tahrirlang — Stars miqdori va
UZS/RUB narxlarini xohlagancha o'zgartirasiz.
