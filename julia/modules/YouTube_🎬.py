#    Mr.SarcasticLover(A Telegram Bot Project)
#    Copyright (C) 2019-2021 Lucky (https://t.me/SarcasticLucky)

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, in version 3 of the License.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see < https://www.gnu.org/licenses/agpl-3.0.en.html/ >.


from googleapiclient.discovery import build
from youtubesearchpython import VideosSearch
from julia import *
from html import unescape
import os, re
import requests
from telethon import types
from telethon.tl import functions
from julia.events import register

from pymongo import MongoClient
from julia import MONGO_DB_URI
from telethon import events

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


async def youtube_search(
    query, order="relevance", token=None, location=None, location_radius=None
):
    """ Do a YouTube search. """
    youtube = build(
        "youtube", "v3", developerKey=YOUTUBE_API_KEY, cache_discovery=False
    )
    search_response = (
        youtube.search()
        .list(
            q=query,
            type="video",
            pageToken=token,
            order=order,
            part="id,snippet",
            maxResults=10,
            location=location,
            locationRadius=location_radius,
        )
        .execute()
    )

    videos = []

    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videos.append(search_result)
    try:
        nexttok = search_response["nextPageToken"]
        return (nexttok, videos)
    except HttpError:
        nexttok = "last_page"
        return (nexttok, videos)
    except KeyError:
        nexttok = "KeyError, try again."
        return (nexttok, videos)


@register(pattern="^/yts (.*)")
async def yts_search(video_q):

    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if video_q.is_group:
        if await is_register_admin(video_q.input_chat, video_q.message.sender_id):
            pass
        elif video_q.chat_id == iid and video_q.sender_id == userss:
            pass
        else:
            return

    # For /yts command, do a YouTube search from Telegram.
    query = video_q.pattern_match.group(1)
    result = ""

    if not YOUTUBE_API_KEY:
        await video_q.reply(
            "`Error: YouTube API key missing! Add it to environment vars or config.env.`"
        )
        return

    c = await video_q.reply("```Processing...```")

    full_response = await youtube_search(query)
    videos_json = full_response[1]

    for video in videos_json:
        title = f"{unescape(video['snippet']['title'])}"
        link = f"https://youtu.be/{video['id']['videoId']}"
        result += f"{title}\n{link}\n\n"

    await c.edit(result)


@register(pattern="^/ytinfo (.*)")
async def yts_search(video_q):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if video_q.is_group:
        if await is_register_admin(video_q.input_chat, video_q.message.sender_id):
            pass
        elif video_q.chat_id == iid and video_q.sender_id == userss:
            pass
        else:
            return
    query = video_q.pattern_match.group(1)
    if not query.startswith("https://youtu.be/"):
        await video_q.reply("Invalid youtube link")
        return
    r = requests.get(query)
    if "Video unavailable" in r.text:
        await video_q.reply("Invalid youtube link")
        return
    videosSearch = VideosSearch(query, limit=1)
    h = videosSearch.result()
    if h["result"] == []:
        await video_q.reply("Invalid youtube link")
        return
    title = h["result"][0]["title"]
    ptime = h["result"][0]["publishedTime"]
    dur = h["result"][0]["duration"]
    views = h["result"][0]["viewCount"]["short"]
    des = h["result"][0]["descriptionSnippet"][0]["text"]
    chn = h["result"][0]["channel"]["name"]
    chnl = h["result"][0]["channel"]["link"]
    vlink = h["result"][0]["link"]
    g = h["result"][0]["thumbnails"][0]["url"]
    f = re.sub("\?.*$", "", g)
    final = f"""**Extracted information from youtube**:\n
**Title**: `{title}`
**Published Time**: `{ptime}`
**Duration**: `{dur}`
**Views**: `{views}`
**Description**: `{des}`
**Channel Name**: `{chn}`
**Channel Link**: `{chnl}`
**Video Link**: `{vlink}`
"""
    await tbot.send_file(
        video_q.chat_id, f, reply_to=video_q.id, file_name="thumb.jpg", caption=final
    )


file_help = os.path.basename(__file__)
file_help = file_help.replace(".py", "")
file_helpo = file_help.replace("_", " ")

__help__ = """
 - /yts <query>: Searches your query in youtube and returns results
 - /ytinfo <video link>: Returns information about the youtube video
"""

CMD_HELP.update({file_helpo: [file_helpo, __help__]})
