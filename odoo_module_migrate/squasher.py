#! /usr/bin/env python
"""
python script to automate replacing `pick <<hash>> AUTO_COMMIT`
with `fixup ...`
"""
import sys
import os
from .log import logger
import re

p = re.compile(r"^pick [0-9a-z]* <(.+)> (.+)$")

MATCHER = {
    "transbot@odoo-community.org": [
        r"OCA Transbot updated translations from Transifex",
        r"Update translation files",
        ],
    "oca+oca-travis@odoo-community.org": [
        r"^\[UPD\] Update [a-zA-Z_]*.pot",
        r"Update translation files",
        ],
    "oca-git-bot@odoo-community.org": [
        r"\[UPD\] README.rst",
        ]
    }


def autosquash(filepath):
    lines = []
    with open(filepath, "r") as infile:
        for line in infile.readlines():
            m = p.match(line)
            if m:
                email, message = m.groups()
                if any([
                        re.match(regex, message)
                        for regex in MATCHER.get(email, [])
                        ]):
                    logger.info("Squash commit %s" % line)
                    lines.append(line.replace("pick", "squash", 1))
                else:
                    lines.append(line)
            else:
                lines.append(line)

    with open(filepath, "w") as outfile:
        for line in lines:
            outfile.write(line)


def commit_message(filepath):
    lines = []
    count = 0
    with open(filepath, "r") as infile:
        for line in infile.readlines():
            if line.startswith("#"):
                count += 1
            # we only commit the first commit message
            # so we cut after the first commit message
            if count >= 3:
                break
            lines.append(line)

    with open(filepath, "w") as outfile:
        for line in lines:
            outfile.write(line)


def main():
    filepath = sys.argv[1]
    filename = os.path.basename(filepath)

    if filename == "git-rebase-todo":
        autosquash(filepath)
    if filename == "COMMIT_EDITMSG":
        commit_message(filepath)


if __name__ == "__main__":
    main()
