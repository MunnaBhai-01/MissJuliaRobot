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


from julia import SUDO_USERS, tbot, OWNER_ID, ANTI_GBAN
from telethon.tl.types import ChatBannedRights
from telethon import events
from telethon.tl.functions.channels import EditBannedRequest
from pymongo import MongoClient
from julia import MONGO_DB_URI, GBAN_LOGS

BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

client = MongoClient()
client = MongoClient(MONGO_DB_URI)
db = client["missjuliarobot"]
gbanned = db.gban


def get_reason(id):
    return gbanned.find_one({"user": id})


@tbot.on(events.NewMessage(pattern="^/gban (.*)"))
async def _(event):
    if event.fwd_from:
        return
    if event.sender_id in SUDO_USERS:
        pass
    elif event.sender_id == OWNER_ID:
        pass
    else:
        return

    quew = event.pattern_match.group(1)

    if "|" in quew:
        iid, reasonn = quew.split("|")
    cid = iid.strip()
    reason = reasonn.strip()
    if cid.isnumeric():
        cid = int(cid)
    entity = await tbot.get_input_entity(cid)
    try:
        r_sender_id = entity.user_id
    except Exception:
        await event.reply("Couldn't fetch that user.")
        return
    if not reason:
        await event.reply("Need a reason for gban.")
        return
    chats = gbanned.find({})

    if r_sender_id == OWNER_ID:
        await event.reply("Fool, how can I gban my master ?")
        return
    if r_sender_id in SUDO_USERS:
        await event.reply("Hey that's a sudo user idiot.")
        return

    for c in chats:
        if r_sender_id == c["user"]:
            to_check = get_reason(id=r_sender_id)
            gbanned.update_one(
                {
                    "_id": to_check["_id"],
                    "bannerid": to_check["bannerid"],
                    "user": to_check["user"],
                    "reason": to_check["reason"],
                },
                {"$set": {"reason": reason, "bannerid": event.sender_id}},
            )
            await event.reply(
                "This user is already gbanned, I am updating the reason of the gban with your reason."
            )
            await event.client.send_message(
                GBAN_LOGS,
                "**GLOBAL BAN UPDATE**\n\n**PERMALINK:** [user](tg://user?id={})\n**UPDATER:** `{}`**\nREASON:** `{}`".format(
                    r_sender_id, event.sender_id, reason
                ),
            )
            return

    gbanned.insert_one(
        {"bannerid": event.sender_id, "user": r_sender_id, "reason": reason}
    )

    await event.client.send_message(
        GBAN_LOGS,
        "**NEW GLOBAL BAN**\n\n**PERMALINK:** [user](tg://user?id={})\n**BANNER:** `{}`\n**REASON:** `{}`".format(
            r_sender_id, event.sender_id, reason
        ),
    )
    await event.reply("Gbanned Successfully !")


@tbot.on(events.NewMessage(pattern="^/ungban (.*)"))
async def _(event):
    if event.fwd_from:
        return
    if event.sender_id in SUDO_USERS:
        pass
    elif event.sender_id == OWNER_ID:
        pass
    else:
        return

    quew = event.pattern_match.group(1)

    if " | " in quew:
        iid, reasonn = quew.split("|")
    cid = iid.strip()
    reason = reasonn.strip()
    if cid.isnumeric():
        cid = int(cid)
    entity = await tbot.get_input_entity(cid)
    try:
        r_sender_id = entity.user_id
    except Exception:
        await event.reply("Couldn't fetch that user.")
        return
    if not reason:
        await event.reply("Need a reason for ungban.")
        return
    chats = gbanned.find({})

    if r_sender_id == OWNER_ID:
        await event.reply("Fool, how can I ungban my master ?")
        return
    if r_sender_id in SUDO_USERS:
        await event.reply("Hey that's a sudo user idiot.")
        return

    for c in chats:
        if r_sender_id == c["user"]:
            to_check = get_reason(id=r_sender_id)
            gbanned.delete_one({"user": r_sender_id})
            await event.client.send_message(
                GBAN_LOGS,
                "**REMOVAL OF GLOBAL BAN**\n\n**PERMALINK:** [user](tg://user?id={})\n**REMOVER:** `{}`\n**REASON:** `{}`".format(
                    r_sender_id, event.sender_id, reason
                ),
            )
            await event.reply("Ungbanned Successfully !")
            return
    await event.reply("Is that user even gbanned ?")


@tbot.on(events.ChatAction())
async def join_ban(event):
    if event.is_private:
        return
    if event.chat_id in ANTI_GBAN:
        return
    pass
    user = event.user_id
    chats = gbanned.find({})
    for c in chats:
        if user == c["user"]:
            if event.user_joined:
                try:
                    to_check = get_reason(id=user)
                    reason = to_check["reason"]
                    bannerid = to_check["bannerid"]
                    await tbot(EditBannedRequest(event.chat_id, user, BANNED_RIGHTS))
                    await event.reply(
                        "This user is gbanned and has been removed !\n\n**Gbanned By**: `{}`\n**Reason**: `{}`".format(
                            bannerid, reason
                        )
                    )
                except Exception as e:
                    print(e)
                    return


@tbot.on(events.NewMessage(pattern=None))
async def type_ban(event):
    if event.is_private:
        return
    if event.chat_id in ANTI_GBAN:
        return
    pass
    chats = gbanned.find({})
    for c in chats:
        if event.sender_id == c["user"]:
            try:
                to_check = get_reason(id=event.sender_id)
                reason = to_check["reason"]
                bannerid = to_check["bannerid"]
                await tbot(
                    EditBannedRequest(event.chat_id, event.sender_id, BANNED_RIGHTS)
                )
                await event.reply(
                    "This user is gbanned and has been removed !\n\n**Gbanned By**: `{}`\n**Reason**: `{}`".format(
                        bannerid, reason
                    )
                )
            except Exception:
                return
