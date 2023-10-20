import time

from bs4 import BeautifulSoup
from telebot.async_telebot import AsyncTeleBot
import requests


token = "Telegram Token"
bot = AsyncTeleBot(token)
#Поиск сотрудников на сайте и информацию о них
def FindWorks(textForSearch):
    link = 'https://admhmao.ru/organy-vlasti/telefonnyy-spravochnik-ogv-hmao'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'}
    data = requests.get(link, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    parentContainerWithWorkers = soup.find(class_='section-list')
    containerWithWorkers = parentContainerWithWorkers.find(class_='child')
    workers = containerWithWorkers.find_all(class_='sotr')

    personal = []
    for worker in workers:
        post = worker.find(class_='post').text
        fio = worker.find(class_='fio').text
        info = worker.find(class_='fields').text
        personal.append([post,fio,info])

    resultList = []
    for item in personal:
        for new in item:
            if str(textForSearch).lower() in str(new).lower():
                resultList.append(item)
    return resultList

def convertInfo(text: str):
    mass = ['Кабинет','E-mail','Вн.тел.','Факс']
    for item in mass:
        if text.find(item) != -1:
            text = text.replace(item,f'\n<b>{item}</b>')
    return text

def getOutputData(array):
    resultOutput = []
    for worker in array:
        output = f"<b>ФИО</b>: {worker[1]}\n" \
                 f"<b>Должность</b>: {worker[0]}\n"

        convertedInfo = convertInfo(worker[2])
        splitedInfo = convertedInfo.split('\n')
        numberPhone = splitedInfo[0]
        email = "-"
        room = "-"
        localPhone = "-"
        fax = "-"

        for item in splitedInfo:
            item = item.replace("\xa0",' ')
            if item.find("E-mail") != -1:
                email = item.split(':')[1]
            if item.find("Вн.тел.") != -1:
                localPhone = item.split(':')[1]
            if item.find("Факс") != -1:
                fax = item.split(':')[1]
            if item.find("Кабинет") != -1:
                room = item.split(':')[1]
        output += f"<b>Тел.</b>: {numberPhone}\n" \
                  f"<b>Вн.тел.</b>: {localPhone}\n" \
                  f"<b>Факс</b>: {fax}\n" \
                  f"<b>E-mail</b>: {email}\n" \
                  f"<b>Кабинет:</b> {room}"
        resultOutput.append(output)
    return resultOutput

#Обработчик команды /start
@bot.message_handler(commands=["start"])
async def SendHelp(message):
    await bot.send_message(message.chat.id,"Для получения информации нужно ввести ФИО, номер телефона или должность\nПример: Корчагина Ольга Михайловна")

#Обработчик основных сообщений от пользователей
@bot.message_handler(func=lambda message: True)
async def HandlerGetInfo(message):
    await bot.send_message(message.chat.id,"Идёт поиск...")
    workers = FindWorks(message.text)
    outputData = getOutputData(workers)
    for output in outputData:
        await bot.send_message(message.chat.id,output,parse_mode="HTML")
        time.sleep(0.2)
    await bot.send_message(message.chat.id, f"Поиск выполнен: найдено <b>{len(outputData)}</b> элементов", parse_mode="HTML")

import asyncio
asyncio.run(bot.polling())
