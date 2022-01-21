import telebot
from telebot.types import InputMediaAudio, InputMediaPhoto, InputMediaDocument
import requests
import json
from sqlighter import SQLighter
from config import *
import logging

bot=telebot.TeleBot(TOKEN_TG_BOT, parse_mode='HTML')

logging.basicConfig(level=logging.INFO)

db = SQLighter('posts.db')


def write_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

def main():
    while True:
        for group in vk_group:
            jsonWallGet = requests.get(url="https://api.vk.com/method/wall.get", params={
                "owner_id": group,
                "count": count_wallGet,
                "filter": filter_wallGet,
                "extended": extended_wallGet,
                "access_token": VK_API_USER,
                "v": VK_API_V}).json()
            for post in jsonWallGet['response']['items']:
                text = edit_text(post)
                if (not (db.post_exists(post['owner_id']))):
                    db.add_post(post['id'], post['owner_id'], text, f"{post['owner_id']}_{post['id']}", None)
                    if "attachments" in post.keys():
                        if len(post["attachments"]) == 1: #Если 1 элемент
                            one_media(post['attachments'], text)
                        else:  # Если не 1 элемент
                            try:
                                bot.send_media_group(CHANEL_ID, media_create(post['attachments'], text))
                            except telebot.apihelper.ApiTelegramException as e:
                                db.add_post(post['id'], post['owner_id'], text, f"{post['owner_id']}_{post['id']}", str(e))
                    else:
                        if text != '':
                            bot.send_message(CHANEL_ID, text)

def edit_text(post):
    text = post['text']
    post_id = post['id']
    owner_id = post['owner_id']
    wall_id = f'{owner_id}_{post_id}'
    if text != "":
        for stop in stop_list:
            if text.find(stop) != -1:
                if not (db.post_exists(wall_id)):
                    db.add_post(post_id, owner_id, text, wall_id, stop)
        for black in blacklist:
            text = text.replace(black, "")
    return text

def one_media(post, text):
    media_list = ['photo', 'doc', 'audio']
    for type in post:
        if type['type'] in media_list:
            if type['type'] == media_list[0]:
                bot.send_photo(CHANEL_ID, type['photo']['sizes'][-1]['url'], caption=text)
            else:
                bot.send_audio(CHANEL_ID, type[type['type']]['url'], caption=text)

def media_create(post, text):
    media = []
    for type in post:
        if type['type'] == 'photo':
            if media == []:
                media.append(
                    InputMediaPhoto(type['photo']['sizes'][-1]['url'], caption=text))
            else:
                media.append(InputMediaPhoto(type['photo']['sizes'][-1]['url']))
        if type['type'] == 'audio':
            if media == []:
                media.append(
                    InputMediaAudio(type['audio']['url'], caption=text))
            else:
                media.append(InputMediaAudio(type['audio']['url']))
        if type['type'] == 'doc':
            if media == []:
                media.append(
                    InputMediaDocument(type['doc']['url'], caption=text))
            else:
                media.append(InputMediaDocument(type['doc']['url']))
        media.append(text)
    return media

if __name__ == '__main__':
    main()