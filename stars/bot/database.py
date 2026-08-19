import aiosqlite
from datetime import datetime
from bot.config import config

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    username TEXT,
    package_id TEXT NOT NULL,
    stars INTEGER NOT NULL,
    currency TEXT NOT NULL,        -- UZS | RUB
    amount INTEGER NOT NULL,
    provider TEXT NOT NULL,        -- click | payme | yookassa | humo
    status TEXT NOT NULL DEFAULT 'pending',  -- pending | paid | fulfilled | failed
    provider_payment_id TEXT,
    created_at TEXT NOT NULL,
    paid_at TEXT,
    user_confirmed_at TEXT,          -- foydalanuvchi "to'lov qildim" bosgan vaqt (humo uchun)
    admin_msg_id INTEGER              -- admin chatidagi tekshirish xabari ID'si (tugmalarni yangilash uchun)
);
"""


async def init_db():
    async with aiosqlite.connect(config.database_path) as db:
        await db.execute(CREATE_TABLE_SQL)
        await db.commit()


async def create_order(user_id: int, username: str, package_id: str, stars: int,
                        currency: str, amount: int, provider: str) -> int:
    async with aiosqlite.connect(config.database_path) as db:
        cursor = await db.execute(
            """INSERT INTO orders (user_id, username, package_id, stars, currency,
               amount, provider, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?)""",
            (user_id, username, package_id, stars, currency, amount, provider,
             datetime.utcnow().isoformat()),
        )
        await db.commit()
        return cursor.lastrowid


async def mark_paid(order_id: int, provider_payment_id: str = ""):
    async with aiosqlite.connect(config.database_path) as db:
        await db.execute(
            """UPDATE orders SET status='paid', provider_payment_id=?, paid_at=?
               WHERE id=?""",
            (provider_payment_id, datetime.utcnow().isoformat(), order_id),
        )
        await db.commit()


async def mark_user_confirmed(order_id: int):
    """Foydalanuvchi mini-app'da 'To'lov qildim' tugmasini bosganda chaqiriladi (Humo oqimi)."""
    async with aiosqlite.connect(config.database_path) as db:
        await db.execute(
            "UPDATE orders SET user_confirmed_at=? WHERE id=?",
            (datetime.utcnow().isoformat(), order_id),
        )
        await db.commit()


async def find_matching_humo_order(amount: int) -> dict | None:
    """Humo bot guruhidan kelgan xabardagi summaga mos, hali to'lanmagan buyurtmani topadi.

    Avval foydalanuvchi 'to'lov qildim' deb belgilagan buyurtmalar ustuvor,
    keyin eng eski (birinchi yaratilgan) buyurtma tanlanadi.
    """
    async with aiosqlite.connect(config.database_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT * FROM orders
               WHERE provider='humo' AND status='pending'
                 AND currency='UZS' AND amount=?
               ORDER BY (user_confirmed_at IS NULL) ASC, created_at ASC
               LIMIT 1""",
            (amount,),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def set_admin_msg_id(order_id: int, message_id: int):
    """Admin chatidagi tekshirish xabari ID'sini saqlaydi (keyin tugmalarni yangilash uchun)."""
    async with aiosqlite.connect(config.database_path) as db:
        await db.execute(
            "UPDATE orders SET admin_msg_id=? WHERE id=?", (message_id, order_id)
        )
        await db.commit()


async def mark_failed(order_id: int):
    """Admin buyurtmani 'bekor qilish' tugmasi orqali rad etganda chaqiriladi."""
    async with aiosqlite.connect(config.database_path) as db:
        await db.execute("UPDATE orders SET status='failed' WHERE id=?", (order_id,))
        await db.commit()


async def mark_fulfilled(order_id: int):
    async with aiosqlite.connect(config.database_path) as db:
        await db.execute("UPDATE orders SET status='fulfilled' WHERE id=?", (order_id,))
        await db.commit()


async def get_order(order_id: int) -> dict | None:
    async with aiosqlite.connect(config.database_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM orders WHERE id=?", (order_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None
