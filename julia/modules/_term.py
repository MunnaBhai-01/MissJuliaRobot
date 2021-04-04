#    Mr.SarcasticLover (A Telegram Bot Project)
#    Copyright (C) 2019-2021 Julia (https://t.me/SarcasticLucky)

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, in version 3 of the License.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see < https://www.gnu.org/licenses/agpl-3.0.en.html/ >.


from julia import tbot
import asyncio
from getpass import getuser
from os import remove

from julia import OWNER_ID
from julia.events import register


@register(pattern="^/term(?: |$)(.*)")
async def terminal_runner(term):
    check = term.message.sender_id
    if int(check) != int(OWNER_ID):
        return
    curruser = getuser()
    command = term.pattern_match.group(1)
    try:
        from os import geteuid

        uid = geteuid()
    except ImportError:
        uid = "This ain't it chief!"

    if term.is_channel and not term.is_group:
        await term.reply("`Term commands aren't permitted on channels!`")
        return

    if not command:
        return

    process = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    result = str(stdout.decode().strip()) + str(stderr.decode().strip())

    if len(result) > 4096:
        output = open("output.txt", "w+")
        output.write(result)
        output.close()
        await tbot.send_file(
            term.chat_id,
            "output.txt",
            reply_to=term.id,
            caption="`Output too large, sending as file`",
        )
        remove("output.txt")
        return

    if uid == 0:
        await term.reply("`" f"{curruser}:~# {command}" f"\n{result}" "`")
    else:
        await term.reply("`" f"{curruser}:~$ {command}" f"\n{result}" "`")
