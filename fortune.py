#    Mr.SarcasticLover(A Telegram Bot Project)
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


import random
import sys
import codecs
import re

from optparse import OptionParser


def _random_int(start, end):
    try:
        r = random.SystemRandom()
    except BaseException:
        r = random

    return r.randint(start, end)


def _read_fortunes(fortune_file):
    with codecs.open(fortune_file, mode="r", encoding="utf-8") as f:
        contents = f.read()

    lines = [line.rstrip() for line in contents.split("\n")]

    delim = re.compile(r"^%$")

    fortunes = []
    cur = []

    def save_if_nonempty(buf):
        fortune = "\n".join(buf)
        if fortune.strip():
            fortunes.append(fortune)

    for line in lines:
        if delim.match(line):
            save_if_nonempty(cur)
            cur = []
            continue

        cur.append(line)

    if cur:
        save_if_nonempty(cur)

    return fortunes


def get_random_fortune(fortune_file):
    fortunes = list(_read_fortunes(fortune_file))
    randomRecord = _random_int(0, len(fortunes) - 1)
    return fortunes[randomRecord]


def main():
    usage = "Usage: %prog [OPTIONS] [fortune_file]"
    arg_parser = OptionParser(usage=usage)
    options, args = arg_parser.parse_args(sys.argv)
    if len(args) == 2:
        fortune_file = args[1]

    else:
        try:
            fortune_file = "notes.txt"
        except KeyError:
            print("Missing fortune file.", file=sys.stderr)
            print(usage, file=sys.stderr)
            sys.exit(1)

    try:
        print(get_random_fortune(fortune_file))
    except ValueError as msg:
        print(msg, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
