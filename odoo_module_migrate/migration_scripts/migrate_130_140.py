# Copyright (C) 2020 - Today: Iván Todorovich
# @author: Iván Todorovich (https://twitter.com/ivantodorovich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

_TEXT_ERRORS = {
    ".xml": {
        "<act_window(\n|.|\t)*":
        "act_window tag has been deprecated. Use <record> instead",
        "<report(\n|.|\t)*":
        "report tag has been deprecated. Use <record> instead",
    }
}
