# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 by Simmo Saan <simmo.saan@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

#
# History:
#
#

"""
TODO
"""

from __future__ import print_function

SCRIPT_NAME = "go_buflist"
SCRIPT_AUTHOR = "Simmo Saan <simmo.saan@gmail.com>"
SCRIPT_VERSION = "0.1"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC = "TODO"

SCRIPT_REPO = "TODO"

SCRIPT_COMMAND = SCRIPT_NAME
SCRIPT_BAR_ITEM = SCRIPT_NAME
SCRIPT_LOCALVAR = SCRIPT_NAME
SCRIPT_LOCALVAR_HIDDEN = "{}_hidden".format(SCRIPT_LOCALVAR)

IMPORT_OK = True

try:
    import weechat
except ImportError:
    print("This script must be run under WeeChat.")
    print("Get WeeChat now at: http://www.weechat.org/")
    IMPORT_OK = False

SETTINGS = {
    "format": (
        "${if:${buffer.local_variables.go_buflist}==1?${color:,cyan}}${if:${buffer.local_variables.go_buflist}==2?${color:,brown}}",
        "TODO"  # TODO
    )
}

KEYS = {
    "meta-g": "/%s" % SCRIPT_COMMAND
}


active = False
buflist_buffers = None
buflist_selection = None


def input_text_changed_cb(data, signal, buffer):
    if active:
        input = weechat.buffer_get_string(buffer, 'input')
        set_localvars(input)
        weechat.bar_item_update(SCRIPT_BAR_ITEM)
    return weechat.WEECHAT_RC_OK


def command_cb(data, buffer, args):
    global active
    active = True
    set_localvars("")
    weechat.bar_item_update(SCRIPT_BAR_ITEM)
    return weechat.WEECHAT_RC_OK


def command_run_input_cb(data, buffer, command):
    global active, buflist_buffers, buflist_selection
    input = weechat.buffer_get_string(buffer, 'input')

    if active:
        if command == "/input return":
            jump_buffer = buflist_buffers[buflist_selection]
            active = False
            set_localvars(input)
            buflist_buffers = None
            buflist_selection = None
            weechat.bar_item_update(SCRIPT_BAR_ITEM)
            weechat.bar_item_update("input_text")

            jump_buffer_full_name = weechat.buffer_get_string(jump_buffer, "full_name")
            weechat.command(buffer, "/buffer {}".format(jump_buffer_full_name))
            return weechat.WEECHAT_RC_OK_EAT
        elif command == "/input complete_next":
            buffer_set_localvar(buflist_buffers[buflist_selection], SCRIPT_LOCALVAR, "1")
            buflist_selection += 1
            if buflist_selection >= len(buflist_buffers):
                buflist_selection = 0
            buffer_set_localvar(buflist_buffers[buflist_selection], SCRIPT_LOCALVAR, "2")
            weechat.bar_item_update("buflist")
            # set_localvars(input)
            # weechat.bar_item_update(SCRIPT_BAR_ITEM)
            return weechat.WEECHAT_RC_OK_EAT
        elif command == "/input complete_previous":
            buffer_set_localvar(buflist_buffers[buflist_selection], SCRIPT_LOCALVAR, "1")
            buflist_selection -= 1
            if buflist_selection < 0:
                buflist_selection = len(buflist_buffers) - 1
            buffer_set_localvar(buflist_buffers[buflist_selection], SCRIPT_LOCALVAR, "2")
            weechat.bar_item_update("buflist")
            # set_localvars(input)
            # weechat.bar_item_update(SCRIPT_BAR_ITEM)
            return weechat.WEECHAT_RC_OK_EAT

        set_localvars(input)
        weechat.bar_item_update(SCRIPT_BAR_ITEM)

    return weechat.WEECHAT_RC_OK


def bar_item_cb(data, item, window, buffer, extra_info):
    if active:
        input = weechat.buffer_get_string(buffer, 'input')
        input_pos = weechat.buffer_get_integer(buffer, 'input_pos')

        input_with_cursor = input[:input_pos] + "\x19b#" + input[input_pos:]

        # TODO: input scrolling broken even with bar input start color
        return "Go: \x19b_{}".format(input_with_cursor)
    else:
        return ""


def input_text_display_with_cursor_cb(data, modifier, modifier_data, string):
    if active:
        return ""
    else:
        return string


def set_localvars(input):
    buffers = weechat.infolist_get("buffer", "", "*")
    while weechat.infolist_next(buffers):
        pointer = weechat.infolist_pointer(buffers, "pointer")
        name = weechat.infolist_string(buffers, "short_name")

        localvar = None
        localvar_hidden = None
        if active:
            if input in name:
                localvar = "1"
                localvar_hidden = "0"
            else:
                localvar = "0"
                localvar_hidden = "1"

        buffer_set_localvar(pointer, SCRIPT_LOCALVAR, localvar)
        buffer_set_localvar(pointer, SCRIPT_LOCALVAR_HIDDEN, localvar_hidden)

    weechat.infolist_free(buffers)

    weechat.bar_item_update("buflist")

    if active:
        global buflist_buffers, buflist_selection
        buflist_buffers = []
        buflist_selection = 0

        buflist = weechat.infolist_get("buflist", "", "")
        while weechat.infolist_next(buflist):
            pointer = weechat.infolist_pointer(buflist, "pointer")
            # full_name = weechat.buffer_get_string(pointer, "full_name")
            localvar = weechat.buffer_get_string(pointer, "localvar_{}".format(SCRIPT_LOCALVAR))
            # weechat.prnt("", "{} {}".format(full_name, localvar))
            if localvar == "1":
                buflist_buffers.append(pointer)

        weechat.infolist_free(buflist)

        if buflist_buffers:
            buffer_set_localvar(buflist_buffers[buflist_selection], SCRIPT_LOCALVAR, "2")


def buffer_set_localvar(buffer, localvar, value):
    if value is not None:
        weechat.buffer_set(buffer, "localvar_set_{}".format(localvar), value)
    else:
        weechat.buffer_set(buffer, "localvar_del_{}".format(localvar), "")


if __name__ == "__main__" and IMPORT_OK:
    if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", ""):
        # weechat.hook_signal("input_search", "input_search_cb", "")
        weechat.hook_signal("input_text_changed", "input_text_changed_cb", "")

        weechat.hook_command(SCRIPT_COMMAND, SCRIPT_DESC,
"""""",  # TODO
"""""",  # TODO
"""""".replace("\n", ""),  # TODO
        "command_cb", "")

        weechat.bar_item_new("(extra)%s" % SCRIPT_BAR_ITEM, "bar_item_cb", "")

        weechat.hook_command_run("/input *", "command_run_input_cb", "")
        weechat.hook_modifier("input_text_display_with_cursor", "input_text_display_with_cursor_cb", "")

        for option, value in SETTINGS.items():
            if not weechat.config_is_set_plugin(option):
                weechat.config_set_plugin(option, value[0])

            weechat.config_set_desc_plugin(option, "%s (default: \"%s\")" % (value[1], value[0]))

        weechat.key_bind("default", KEYS)

        set_localvars("")
