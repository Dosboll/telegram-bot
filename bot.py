import asyncio
import aiohttp
from bs4 import BeautifulSoup
from telegram import Bot

BOT_TOKEN = "8787982429:AAGpfzIibK7e58YtvAl6g5m1EG2sZtEdFYA"
CHAT_ID = "6318865778"

URL = "https://www.agropraktika.eu/vacancies"
CHECK_INTERVAL = 100

bot = Bot(token="8787982429:AAGpfzIibK7e58YtvAl6g5m1EG2sZtEdFYA")
previous_vacancies = []

async def check_site():
    global previous_vacancies
    
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(URL) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    vacancies = []

                    # ищем все ссылки вакансий
                    for a in soup.find_all("a"):
                        link = a.get("href")
                        text = a.text.strip()

                        if link and "vac" in link.lower():
                            vacancies.append(text + " - " + link)

                    if previous_vacancies == []:
                        previous_vacancies = vacancies
                        await bot.send_message(chat_id=CHAT_ID, text="Бот начал отслеживать вакансии")
                    
                    else:
                        new_vacancies = [v for v in vacancies if v not in previous_vacancies]

                        if new_vacancies:
                            for v in new_vacancies:
                                await bot.send_message(chat_id=CHAT_ID, text=f"Новая вакансия:\n{v}")

                            previous_vacancies = vacancies

            except Exception as e:
                await bot.send_message(chat_id=CHAT_ID, text=f"Ошибка: {e}")

            await asyncio.sleep(CHECK_INTERVAL)

async def main():
    await check_site()

if __name__ == "__main__":
    asyncio.run(main())