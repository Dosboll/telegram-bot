import asyncio
from telegram import Bot
import aiohttp
from datetime import datetime

BOT_TOKEN = "8787982429:AAGpfzIibK7e58YtvAl6g5m1EG2sZtEdFYA"
CHAT_ID = 6318865778

BASE_URL = "https://agropraktika.eu/vacancies"
CHECK_INTERVAL = 100
PAGES = 2

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

bot = Bot("8787982429:AAGpfzIibK7e58YtvAl6g5m1EG2sZtEdFYA")

previous_status = {}

def log(text):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {text}", flush=True)

async def get_status(session):
    status = {}

    for page in range(1, PAGES + 1):
        url = f"{BASE_URL}?page={page}"
        log(f"Проверка страницы {page}")

        try:
            async with session.get(url, headers=HEADERS) as response:

                # 🚫 если сайт блокирует
                if response.status == 403:
                    log("Ошибка 403 — сайт блокирует запрос")
                    return None

                html = await response.text()
                html_lower = html.lower()

                # защита от пустых/битых страниц
                if len(html) < 1000:
                    log(f"Страница {page}: подозрительно маленький HTML")
                    return None

                # проверка статуса
                if "регистрация временно приостановлена" in html_lower:
                    status[page] = 1
                    log(f"Страница {page}: закрыто")
                else:
                    status[page] = 0
                    log(f"Страница {page}: ВОЗМОЖНО ОТКРЫТО")

        except Exception as e:
            log(f"Ошибка при запросе страницы {page}: {e}")
            return None

    return status


async def check():
    global previous_status

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                log("Новая проверка сайта")
                current_status = await get_status(session)

                # если ошибка/403 → пропускаем
                if current_status is None:
                    log("Пропуск проверки (ошибка или блок)")
                    await asyncio.sleep(CHECK_INTERVAL)
                    continue

                # первый запуск
                if not previous_status:
                    previous_status = current_status
                    log("Первичная проверка выполнена")

                else:
                    for page in current_status:
                        if (
                            page in previous_status
                            and previous_status[page] == 1
                            and current_status[page] == 0
                        ):
                            log(f"🔥 ОТКРЫЛОСЬ на странице {page}")

                            await bot.send_message(
                                chat_id=CHAT_ID,
                                text=f"🚨 РЕГИСТРАЦИЯ ОТКРЫЛАСЬ!\nСтраница: {page}\n{BASE_URL}?page={page}"
                            )

                    previous_status = current_status

            except Exception as e:
                log(f"Критическая ошибка: {e}")
                await bot.send_message(chat_id=CHAT_ID, text=f"Ошибка: {e}")

            log(f"Жду {CHECK_INTERVAL} секунд")
            await asyncio.sleep(CHECK_INTERVAL)


async def main():
    log("Бот запущен")
    await bot.send_message(chat_id=CHAT_ID, text="Бот запущен и следит за Agropraktika")
    await check()


if __name__ == "__main__":
    asyncio.run(main())
