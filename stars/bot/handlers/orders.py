import aiosqlite
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.config import config

router = Router()


@router.message(Command("orders"))
async def cmd_orders(message: Message):
    async with aiosqlite.connect(config.database_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM orders WHERE user_id=? ORDER BY id DESC LIMIT 10",
            (message.from_user.id,),
        )
        rows = await cursor.fetchall()

    if not rows:
        await message.answer("Sizda hali buyurtmalar yo'q.")
        return

    lines = ["🧾 <b>So'nggi buyurtmalaringiz:</b>\n"]
    status_emoji = {"pending": "⏳", "paid": "✅", "fulfilled": "⭐", "failed": "❌"}
    for row in rows:
        cur_symbol = "so'm" if row["currency"] == "UZS" else "₽"
        lines.append(
            f"{status_emoji.get(row['status'], '•')} #{row['id']} — "
            f"{row['stars']} ⭐ — {row['amount']} {cur_symbol} — {row['status']}"
        )
    await message.answer("\n".join(lines))
