import asyncio
from telegram import Bot
import aiohttp

BOT_TOKEN = "8787982429:AAGpfzIibK7e58YtvAl6g5m1EG2sZtEdFYA"
CHAT_ID = 6318865778

BASE_URL = "https://agropraktika.eu/vacancies"
CHECK_INTERVAL = 60
PAGES = 2

bot = Bot(token="8787982429:AAGpfzIibK7e58YtvAl6g5m1EG2sZtEdFYA")

previous_status = {}

async def get_status(session):
    status = {}
    for page in range(1, PAGES + 1):
        url = f"{BASE_URL}?page={page}"
        async with session.get(url) as response:
            html = await response.text()
            html_lower = html.lower()

            if "регистрация временно приостановлена" in html_lower:
                status[page] = 1  # закрыто
            else:
                status[page] = 0  # открыто

    return status


async def check():
    global previous_status

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                current_status = await get_status(session)

                if not previous_status:
                    previous_status = current_status
                    print("Первичная проверка выполнена")

                else:
                    for page in current_status:
                        # было закрыто -> стало открыто
                        if previous_status[page] == 1 and current_status[page] == 0:
                            await bot.send_message(
                                chat_id=CHAT_ID,
                                text=f"🚨 РЕГИСТРАЦИЯ ОТКРЫЛАСЬ!\nСтраница: {page}\n{BASE_URL}?page={page}"
                            )

                    previous_status = current_status

            except Exception as e:
                await bot.send_message(chat_id=CHAT_ID, text=f"Ошибка: {e}")

            await asyncio.sleep(CHECK_INTERVAL)


async def main():
    await bot.send_message(chat_id=CHAT_ID, text="Бот запущен и следит за Agropraktika")
    await check()


if __name__ == "__main__":
    asyncio.run(main())
