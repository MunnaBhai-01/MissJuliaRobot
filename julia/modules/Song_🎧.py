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


from julia import *
import time
import os
import json
from telethon.tl.types import DocumentAttributeAudio
from youtube_dl import YoutubeDL

from youtube_dl.utils import (
    DownloadError,
    ContentTooShortError,
    ExtractorError,
    GeoRestrictedError,
    MaxDownloadsReached,
    PostProcessingError,
    UnavailableVideoError,
    XAttrMetadataError,
)

from julia import tbot
from telethon import types, events
from telethon.tl import functions
from julia.events import register
from youtubesearchpython import SearchVideos
from tswift import Song
from pymongo import MongoClient
from julia import MONGO_DB_URI

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


@register(pattern="^/song (.*)")
async def download_song(v_url):
    try:
        approved_userss = approved_users.find({})
        for ch in approved_userss:
            iid = ch["id"]
            userss = ch["user"]
        if v_url.is_group:
            if await is_register_admin(v_url.input_chat, v_url.message.sender_id):
                pass
            elif v_url.chat_id == iid and v_url.sender_id == userss:
                pass
            else:
                return
        url = v_url.pattern_match.group(1)
        rkp = await v_url.reply("`Processing ...`")
        if not url:
            await rkp.edit("`Error \nusage song <song name>`")
        search = SearchVideos(url, offset=1, mode="json", max_results=1)
        test = search.result()
        p = json.loads(test)
        q = p.get("search_result")
        try:
            url = q[0]["link"]
        except BaseException:
            return await rkp.edit("`Failed to find that song`")
        type = "audio"
        await rkp.edit("`Preparing to download ...`")
        if type == "audio":
            opts = {
                "format": "bestaudio",
                "addmetadata": True,
                "key": "FFmpegMetadata",
                "writethumbnail": True,
                "prefer_ffmpeg": True,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "320",
                    }
                ],
                "outtmpl": "%(id)s.mp3",
                "quiet": True,
                "logtostderr": False,
            }
            video = False
            song = True
        try:
            await rkp.edit("`Fetching data, please wait ...`")
            with YoutubeDL(opts) as rip:
                rip_data = rip.extract_info(url)
        except DownloadError as DE:
            await rkp.edit(f"`{str(DE)}`")
            return
        except ContentTooShortError:
            await rkp.edit("`The download content was too short.`")
            return
        except GeoRestrictedError:
            await rkp.edit(
                "`Video is not available from your geographic location due to geographic restrictions imposed by a website.`"
            )
            return
        except MaxDownloadsReached:
            await rkp.edit("`Max-downloads limit has been reached.`")
            return
        except PostProcessingError:
            await rkp.edit("`There was an error during post processing.`")
            return
        except UnavailableVideoError:
            await rkp.edit("`Media is not available in the requested format.`")
            return
        except XAttrMetadataError as XAME:
            await rkp.edit(f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`")
            return
        except ExtractorError:
            await rkp.edit("`There was an error during info extraction.`")
            return
        except Exception as e:
            await rkp.edit(f"{str(type(e)): {str(e)}}")
            return
        c_time = time.time()
        if song:
            await rkp.edit(f"`Sending the song ...`")
            y = await v_url.client.send_file(
                v_url.chat_id,
                f"{rip_data['id']}.mp3",
                supports_streaming=False,
                force_document=False,
                allow_cache=False,
                attributes=[
                    DocumentAttributeAudio(
                        duration=int(rip_data["duration"]),
                        title=str(rip_data["title"]),
                        performer=str(rip_data["uploader"]),
                    )
                ],
            )
            songname = str(rip_data["title"])
            if JULIASONG:
                pass
            else:
                os.system("rm -rf *.mp3")
                os.system("rm -rf *.webp")
                os.system("rm -rf *.jpg")
                return
            suck = await ubot.get_messages(JULIASONG, limit=None)
            for c in suck:
                if not isinstance(c.message, types.MessageService):
                    if c.media != None:
                        name = c.media.document.attributes[0].title
                        if str(name) == songname:
                            os.system("rm -rf *.mp3")
                            os.system("rm -rf *.webp")
                            return
            await y.forward_to(JULIASONG)
            os.system("rm -rf *.mp3")
            os.system("rm -rf *.webp")
            os.system("rm -rf *.jpg")
    except Exception as e:
        print(e)


@register(pattern="^/videosong (.*)")
async def download_video(v_url):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if v_url.is_group:
        if await is_register_admin(v_url.input_chat, v_url.message.sender_id):
            pass
        elif v_url.chat_id == iid and v_url.sender_id == userss:
            pass
        else:
            return
    url = v_url.pattern_match.group(1)
    rkp = await v_url.reply("`Processing ...`")
    if not url:
        await rkp.edit("`Error \nusage video <song name>`")
    search = SearchVideos(url, offset=1, mode="json", max_results=1)
    test = search.result()
    p = json.loads(test)
    q = p.get("search_result")
    try:
        url = q[0]["link"]
    except BaseException:
        return await rkp.edit("`Failed to find that video song`")
    type = "video"
    await rkp.edit("`Preparing to download ...`")
    if type == "video":
        opts = {
            "format": "best",
            "addmetadata": True,
            "key": "FFmpegMetadata",
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "postprocessors": [
                {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}
            ],
            "outtmpl": "%(id)s.mp4",
            "logtostderr": False,
            "quiet": True,
        }
        song = False
        video = True
    try:
        await rkp.edit("`Fetching data, please wait ...`")
        with YoutubeDL(opts) as rip:
            rip_data = rip.extract_info(url)
    except DownloadError as DE:
        await rkp.edit(f"`{str(DE)}`")
        return
    except ContentTooShortError:
        await rkp.edit("`The download content was too short.`")
        return
    except GeoRestrictedError:
        await rkp.edit(
            "`Video is not available from your geographic location due to geographic restrictions imposed by a website.`"
        )
        return
    except MaxDownloadsReached:
        await rkp.edit("`Max-downloads limit has been reached.`")
        return
    except PostProcessingError:
        await rkp.edit("`There was an error during post processing.`")
        return
    except UnavailableVideoError:
        await rkp.edit("`Media is not available in the requested format.`")
        return
    except XAttrMetadataError as XAME:
        await rkp.edit(f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`")
        return
    except ExtractorError:
        await rkp.edit("`There was an error during info extraction.`")
        return
    except Exception as e:
        await rkp.edit(f"{str(type(e)): {str(e)}}")
        return
    c_time = time.time()
    if video:
        await rkp.edit(f"`Sending the video song ...`")

        y = await v_url.client.send_file(
            v_url.chat_id,
            f"{rip_data['id']}.mp4",
            supports_streaming=True,
            caption=rip_data["title"],
        )
        vsongname = str(rip_data["title"])
        if JULIAVSONG:
            pass
        else:
            os.system("rm -rf *.mp4")
            os.system("rm -rf *.webp")
            os.system("rm -rf *.jpg")
            return
        suck = await ubot.get_messages(JULIAVSONG, limit=None)
        for c in suck:
            if not isinstance(c.message, types.MessageService):
                name = c.message
                if str(name) == vsongname:
                    os.system("rm -rf *.mp4")
                    os.system("rm -rf *.webp")
                    os.system("rm -rf *.jpg")
                    return
        await y.forward_to(JULIAVSONG)
        os.system("rm -rf *.mp4")
        os.system("rm -rf *.webp")
        os.system("rm -rf *.jpg")


@register(pattern="^/lyrics ?(.*)")
async def download_lyrics(v_url):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if v_url.is_group:
        if await is_register_admin(v_url.input_chat, v_url.message.sender_id):
            pass
        elif v_url.chat_id == iid and v_url.sender_id == userss:
            pass
        else:
            return
    query = v_url.pattern_match.group(1)
    if not query:
        await v_url.reply("You haven't specified which song to look for!")
        return
    song = Song.find_song(query)
    if song:
        if song.lyrics:
            reply = song.format()
        else:
            reply = "Couldn't find any lyrics for that song!"
    else:
        reply = "Song not found!"
    if len(reply) > 4090:
        with open("lyrics.txt", "w") as f:
            f.write(f"{reply}")
        with open("lyrics.txt", "rb") as f:
            await v_url.client.send_file(
                v_url.chat_id,
                file=f,
                caption="Message length exceeded max limit! Sending as a text file.",
            )
    else:
        await v_url.reply(reply)


file_help = os.path.basename(__file__)
file_help = file_help.replace(".py", "")
file_helpo = file_help.replace("_", " ")

__help__ = """
 - /song <songname artist(optional)>: uploads the song in it's best quality available
 - /videosong <songname artist(optional)>: uploads the video song in it's best quality available
 - /lyrics <songname artist(optional)>: sends the complete lyrics of the song provided as input

**Also check out - **
 @MissJuliaRobotMP3
 @MissJuliaRobotMP4
"""

CMD_HELP.update({file_helpo: [file_helpo, __help__]})
