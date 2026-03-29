import asyncio
from telegram import Bot
import aiohttp

BOT_TOKEN = "8787982429:AAGpfzIibK7e58YtvAl6g5m1EG2sZtEdFYA"
CHAT_ID = 6318865778

BASE_URL = "https://agropraktika.eu/vacancies"
CHECK_INTERVAL = 90
PAGES = 3

bot = Bot("8787982429:AAGpfzIibK7e58YtvAl6g5m1EG2sZtEdFYA")

previous_status = {}
open_confirm = {}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

async def get_status(session):
    status = {}

    for page in range(1, PAGES + 1):
        url = f"{BASE_URL}?page={page}"

        try:
            async with session.get(url, headers=HEADERS) as response:
                print("Страница", page, "Статус:", response.status)

                # защита от 403 / 404
                if response.status != 200:
                    continue

                html = await response.text()

                # защита от страниц-ошибок
                if len(html) < 5000:
                    print("Маленький HTML, пропуск")
                    continue

                if "Регистрация временно приостановлена" in html:
                    status[page] = 1  # закрыто
                else:
                    status[page] = 0  # открыто

        except Exception as e:
            print("Ошибка:", e)

    return status


async def notify_open(page):
    # 3 уведомления
    for i in range(3):
        await bot.send_message(
            chat_id=CHAT_ID,
            text="🚨🚨🚨 РЕГИСТРАЦИЯ ОТКРЫЛАСЬ!!! СРОЧНО ЗАХОДИ НА САЙТ!!! 🚨🚨🚨"
        )
        await asyncio.sleep(2)

    # ссылка
    await bot.send_message(
        chat_id=CHAT_ID,
        text=f"Ссылка:\n{BASE_URL}?page={page}"
    )

    # напоминание
    await asyncio.sleep(10)

    await bot.send_message(
        chat_id=CHAT_ID,
        text="Ты успел зайти???"
    )


async def check():
    global previous_status, open_confirm

    timeout = aiohttp.ClientTimeout(total=30)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        while True:
            current_status = await get_status(session)

            if not previous_status:
                previous_status = current_status
                print("Первичная проверка выполнена")

            else:
                for page in current_status:
                    if page not in open_confirm:
                        open_confirm[page] = 0

                    if current_status[page] == 0:
                        open_confirm[page] += 1
                    else:
                        open_confirm[page] = 0

                    if (
                        open_confirm[page] >= 2
                        and previous_status.get(page) == 1
                    ):
                        print("ОТКРЫЛОСЬ на странице", page)
                        await notify_open(page)
                        open_confirm[page] = 0

                previous_status = current_status

            print("Проверка завершена")
            await asyncio.sleep(CHECK_INTERVAL)


async def main():
    await bot.send_message(chat_id=CHAT_ID, text="Бот запущен и следит за вакансиями 24/7")
    await check()


if __name__ == "__main__":
    asyncio.run(main())
