#! /usr/bin/env python
"""
python script to automate replacing `pick <<hash>> AUTO_COMMIT`
with `fixup ...`
"""
import sys
import os
from .log import logger

SQUASH_LINES = [
    "<transbot@odoo-community.org> "
    "OCA Transbot updated translations from Transifex\n",
    "<oca+oca-travis@odoo-community.org> [UPD] Update product_multi_ean.pot\n",
    "<oca-git-bot@odoo-community.org> [UPD] README.rst\n",
    "<transbot@odoo-community.org> Update translation files\n",
    ]


def autosquash(filepath):
    lines = []
    with open(filepath, "r") as infile:
        for line in infile.readlines():
            if line[13:] in SQUASH_LINES:
                logger.info("Squash commit %s" % line)
                lines.append(line.replace("pick", "squash", 1))
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
