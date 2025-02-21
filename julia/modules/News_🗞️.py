#    MissJuliaRobot (A Telegram Bot Project)
#    Copyright (C) 2019-2021 Julia (https://t.me/MissJulia_Robot)

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, in version 3 of the License.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see < https://www.gnu.org/licenses/agpl-3.0.en.html/ >.


from julia import tbot, CMD_HELP
import os
import urllib.request
from typing import List
from typing import Optional
from urllib.request import urlopen
import bs4
from pymongo import MongoClient
from telethon import *
from telethon import events
from telethon.tl import functions
from telethon.tl import types
from telethon.tl.types import *

from julia import *
from julia.events import register

client = MongoClient()
client = MongoClient(MONGO_DB_URI)
db = client["missjuliarobot"]
approved_users = db.approve


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await tbot(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerUser):
        return True


@register(pattern="^/news (.*) (.*)")
async def _(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return
    sender = event.sender_id
    country = event.pattern_match.group(1)
    lang = event.pattern_match.group(2)
    index = 0
    chatid = event.chat_id
    msg = await tbot.send_message(chatid, "Loading ...")
    msgid = msg.id
    await tbot.edit_message(
        chatid,
        msgid,
        "Click on the below button to read the latest news headlines 👇",
        buttons=[
            [
                Button.inline(
                    "▶️",
                    data=f"news-{sender}|{country}|{lang}|{index}|{chatid}|{msgid}",
                )
            ],
            [Button.inline("❌", data=f"newsstop-{sender}|{chatid}|{msgid}")],
        ],
    )


@tbot.on(events.CallbackQuery(pattern=r"news(\-(.*))"))
async def paginate_news(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return
    tata = event.pattern_match.group(1)
    data = tata.decode()
    meta = data.split("-", 1)[1]
    # print(meta)
    if "|" in meta:
        sender, country, lang, index, chatid, msgid = meta.split("|")
    sender = int(sender.strip())
    if not event.sender_id == sender:
        await event.answer("You haven't send that command !")
        return
    country = country.strip()
    lang = lang.strip()
    index = int(index.strip())
    num = index
    chatid = int(chatid.strip())
    msgid = int(msgid.strip())
    news_url = f"https://news.google.com/rss?hl={lang}-{country}&gl={country}&ceid={country}:{lang}"
    try:
        Client = urlopen(news_url)
    except Exception:
        await event.reply("Invalid country or language code provided.")
        return
    xml_page = Client.read()
    Client.close()
    soup_page = bs4.BeautifulSoup(xml_page, "xml")
    news_list = soup_page.find_all("item")
    header = f"**#{num} **"
    title = news_list[int(num)].title.text
    text = news_list[int(num)].link.text
    date = news_list[int(num)].pubDate.text
    lastisthis = f"{header}[{title}]({text})" + "\n\n" + f"`{date}`"
    await tbot.edit_message(
        chatid,
        msgid,
        lastisthis,
        link_preview=False,
        buttons=[
            [
                Button.inline(
                    "◀️",
                    data=f"prevnews-{sender}|{country}|{lang}|{num}|{chatid}|{msgid}",
                ),
                Button.inline("❌", data=f"newsstop-{sender}|{chatid}|{msgid}"),
                Button.inline(
                    "▶️",
                    data=f"nextnews-{sender}|{country}|{lang}|{num}|{chatid}|{msgid}",
                ),
            ],
            [
                Button.inline(
                    "Refresh 🔁",
                    data=f"newnews-{sender}|{country}|{lang}|{chatid}|{msgid}",
                )
            ],
        ],
    )


@tbot.on(events.CallbackQuery(pattern=r"prevnews(\-(.*))"))
async def paginate_prevnews(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return
    tata = event.pattern_match.group(1)
    data = tata.decode()
    meta = data.split("-", 1)[1]
    # print(meta)
    if "|" in meta:
        sender, country, lang, index, chatid, msgid = meta.split("|")
    sender = int(sender.strip())
    if not event.sender_id == sender:
        await event.answer("You haven't send that command !")
        return
    country = country.strip()
    lang = lang.strip()
    index = int(index.strip())
    num = index - 1
    chatid = int(chatid.strip())
    msgid = int(msgid.strip())
    news_url = f"https://news.google.com/rss?hl={lang}-{country}&gl={country}&ceid={country}:{lang}"
    try:
        Client = urlopen(news_url)
    except Exception:
        await event.reply("Invalid country or language code provided.")
        return
    xml_page = Client.read()
    Client.close()
    soup_page = bs4.BeautifulSoup(xml_page, "xml")
    news_list = soup_page.find_all("item")
    vector = len(news_list)
    if num < 0:
        num = vector - 1
    # print(vector)
    # print(num)
    header = f"**#{num} **"
    title = news_list[int(num)].title.text
    text = news_list[int(num)].link.text
    date = news_list[int(num)].pubDate.text
    lastisthis = f"{header}[{title}]({text})" + "\n\n" + f"`{date}`"
    await tbot.edit_message(
        chatid,
        msgid,
        lastisthis,
        link_preview=False,
        buttons=[
            [
                Button.inline(
                    "◀️",
                    data=f"prevnews-{sender}|{country}|{lang}|{num}|{chatid}|{msgid}",
                ),
                Button.inline("❌", data=f"newsstop-{sender}|{chatid}|{msgid}"),
                Button.inline(
                    "▶️",
                    data=f"nextnews-{sender}|{country}|{lang}|{num}|{chatid}|{msgid}",
                ),
            ],
            [
                Button.inline(
                    "Refresh 🔁",
                    data=f"newnews-{sender}|{country}|{lang}|{chatid}|{msgid}",
                )
            ],
        ],
    )


@tbot.on(events.CallbackQuery(pattern=r"nextnews(\-(.*))"))
async def paginate_nextnews(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return
    tata = event.pattern_match.group(1)
    data = tata.decode()
    meta = data.split("-", 1)[1]
    # print(meta)
    if "|" in meta:
        sender, country, lang, index, chatid, msgid = meta.split("|")
    sender = int(sender.strip())
    if not event.sender_id == sender:
        await event.answer("You haven't send that command !")
        return
    country = country.strip()
    lang = lang.strip()
    index = int(index.strip())
    num = index + 1
    chatid = int(chatid.strip())
    msgid = int(msgid.strip())
    news_url = f"https://news.google.com/rss?hl={lang}-{country}&gl={country}&ceid={country}:{lang}"
    try:
        Client = urlopen(news_url)
    except Exception:
        await event.reply("Invalid country or language code provided.")
        return
    xml_page = Client.read()
    Client.close()
    soup_page = bs4.BeautifulSoup(xml_page, "xml")
    news_list = soup_page.find_all("item")
    vector = len(news_list)
    if num > vector - 1:
        num = 0
    header = f"**#{num} **"
    title = news_list[int(num)].title.text
    text = news_list[int(num)].link.text
    date = news_list[int(num)].pubDate.text
    lastisthis = f"{header}[{title}]({text})" + "\n\n" + f"`{date}`"
    await tbot.edit_message(
        chatid,
        msgid,
        lastisthis,
        link_preview=False,
        buttons=[
            [
                Button.inline(
                    "◀️",
                    data=f"prevnews-{sender}|{country}|{lang}|{num}|{chatid}|{msgid}",
                ),
                Button.inline("❌", data=f"newsstop-{sender}|{chatid}|{msgid}"),
                Button.inline(
                    "▶️",
                    data=f"nextnews-{sender}|{country}|{lang}|{num}|{chatid}|{msgid}",
                ),
            ],
            [
                Button.inline(
                    "Refresh 🔁",
                    data=f"newnews-{sender}|{country}|{lang}|{chatid}|{msgid}",
                )
            ],
        ],
    )


@tbot.on(events.CallbackQuery(pattern=r"newsstop(\-(.*))"))
async def newsstop(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return
    tata = event.pattern_match.group(1)
    data = tata.decode()
    meta = data.split("-", 1)[1]
    # print(meta)
    if "|" in meta:
        sender, chatid, msgid = meta.split("|")
    sender = int(sender.strip())
    chatid = int(chatid.strip())
    msgid = int(msgid.strip())
    if not event.sender_id == sender:
        await event.answer("You haven't send that command !")
        return
    await tbot.edit_message(chatid, msgid, "Thanks for reading.\n❤️ from Google News !")


@tbot.on(events.CallbackQuery(pattern=r"newnews(\-(.*))"))
async def paginate_nextnews(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return
    tata = event.pattern_match.group(1)
    data = tata.decode()
    meta = data.split("-", 1)[1]
    # print(meta)
    if "|" in meta:
        sender, country, lang, chatid, msgid = meta.split("|")
    sender = int(sender.strip())
    if not event.sender_id == sender:
        await event.answer("You haven't send that command !")
        return
    country = country.strip()
    lang = lang.strip()
    num = 0
    chatid = int(chatid.strip())
    msgid = int(msgid.strip())
    news_url = f"https://news.google.com/rss?hl={lang}-{country}&gl={country}&ceid={country}:{lang}"
    try:
        Client = urlopen(news_url)
    except Exception:
        await event.reply("Invalid country or language code provided.")
        return
    xml_page = Client.read()
    Client.close()
    soup_page = bs4.BeautifulSoup(xml_page, "xml")
    news_list = soup_page.find_all("item")
    vector = len(news_list)
    if num > vector - 1:
        num = 0
    header = f"**#{num} **"
    title = news_list[int(num)].title.text
    text = news_list[int(num)].link.text
    date = news_list[int(num)].pubDate.text
    lastisthis = f"{header}[{title}]({text})" + "\n\n" + f"`{date}`"
    await tbot.edit_message(
        chatid,
        msgid,
        lastisthis,
        link_preview=False,
        buttons=[
            [
                Button.inline(
                    "◀️",
                    data=f"prevnews-{sender}|{country}|{lang}|{num}|{chatid}|{msgid}",
                ),
                Button.inline("❌", data=f"newsstop-{sender}|{chatid}|{msgid}"),
                Button.inline(
                    "▶️",
                    data=f"nextnews-{sender}|{country}|{lang}|{num}|{chatid}|{msgid}",
                ),
            ],
            [
                Button.inline(
                    "Refresh 🔁",
                    data=f"newnews-{sender}|{country}|{lang}|{chatid}|{msgid}",
                )
            ],
        ],
    )


file_help = os.path.basename(__file__)
file_help = file_help.replace(".py", "")
file_helpo = file_help.replace("_", " ")

__help__ = """
 - /news <country code> <LanguageCode>: Returns today's American News Headlines (ONLY WORKS IN PM)
**Example:**
 - /news US en: This will return news for US in english language.
"""

CMD_HELP.update({file_helpo: [file_helpo, __help__]})
