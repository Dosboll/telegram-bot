import asyncio
from telegram import Bot
import aiohttp
from datetime import datetime

BOT_TOKEN = "8787982429:AAGpfzIibK7e58YtvAl6g5m1EG2sZtEdFYA"
CHAT_ID = 6318865778

BASE_URL = "https://agropraktika.eu/vacancies"
CHECK_INTERVAL = 60
PAGES = 2

bot = Bot("8787982429:AAGpfzIibK7e58YtvAl6g5m1EG2sZtEdFYA")

previous_status = {}

def log(text):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {text}", flush=True)

async def get_status(session):
    status = {}
    for page in range(1, PAGES + 1):
        url = f"{BASE_URL}?page={page}"
        log(f"Проверка страницы {page}")

        async with session.get(url) as response:
            html = await response.text()
            html_lower = html.lower()

            if "регистрация временно приостановлена" in html_lower:
                status[page] = 1
                log(f"Страница {page}: закрыто")
            else:
                status[page] = 0
                log(f"Страница {page}: ОТКРЫТО")

    return status


async def check():
    global previous_status

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                log("Новая проверка сайта")
                current_status = await get_status(session)

                if not previous_status:
                    previous_status = current_status
                    log("Первичная проверка выполнена")

                else:
                    for page in current_status:
                        if previous_status[page] == 1 and current_status[page] == 0:
                            log(f"Регистрация открылась на странице {page}")
                            await bot.send_message(
                                chat_id=CHAT_ID,
                                text=f"🚨 РЕГИСТРАЦИЯ ОТКРЫЛАСЬ!\nСтраница: {page}\n{BASE_URL}?page={page}"
                            )

                    previous_status = current_status

            except Exception as e:
                log(f"Ошибка: {e}")
                await bot.send_message(chat_id=CHAT_ID, text=f"Ошибка: {e}")

            log(f"Жду {CHECK_INTERVAL} секунд")
            await asyncio.sleep(CHECK_INTERVAL)


async def main():
    log("Бот запущен")
    await bot.send_message(chat_id=CHAT_ID, text="Бот запущен и следит за Agropraktika")
    await check()


if __name__ == "__main__":
    asyncio.run(main())