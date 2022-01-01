#    This file is part of Scheibenkleister.
#    Copyright (C) 2022  Carine Dengler
#
#    Eichhoernchen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
:synopsis: Subwindows and menus.
"""


# standard library imports
import curses

# third party imports
# library specific imports
from src import UserAbort
from src.curses import (
    get_panel,
    loop,
    ResizeError,
    WindowManager,
    WindowUpdateError,
)


def launch(stdscr, interpreter):
    """Launch shell.

    :param window stdscr: whole screen
    :param Interpreter interpreter: command-line interpreter
    :param dict config: configuration
    """
    panel = get_panel(*stdscr.getmaxyx(), 0, 0)
    window = panel.window()
    window_mgr = WindowManager(
        window,
        banner="Welcome to Eichhörnchen.\tType help or ? to list commands.",
        commands=(),
        tags=interpreter.timer.tags,
    )
    curses.start_color()
    curses.raw()
    curses.use_default_colors()
    for color_pair in (
        (1, 2, -1),  # name
        (2, 8, -1),  # tags
        (3, 5, -1),  # time span
        (4, 11, -1),  # total runtime
        (5, 9, -1),  # error message
    ):
        curses.init_pair(*color_pair)
    loop(interpreter, window_mgr)


def draw_stats_window(stats, interpreter, new_loop=True):
    """Draw stats subwindow.

    :param tuple stats: stats
    :param StatsInterpreter interpreter: interpreter
    :param bool new_loop: toggle starting a new loop on/off
    """
    panel = curses.panel.top_panel()
    old_window = panel.window()
    new_window = curses.newwin(*old_window.getmaxyx(), 0, 0)
    window_mgr = WindowManager(
        new_window,
        commands=(*interpreter.aliases.keys(), *interpreter.subcommands.keys()),
    )
    window_mgr.writelines(*new_window.getyx(), stats)
    panel.replace(new_window)
    curses.panel.update_panels()
    curses.doupdate()
    if new_loop:
        while True:
            try:
                loop(interpreter, window_mgr, type_="")
            except (EOFError, UserAbort):
                break
            except WindowUpdateError:
                window_mgr.window = curses.panel.top_panel().window()
    else:
        raise WindowUpdateError
    panel.replace(old_window)
    curses.panel.update_panels()
    curses.doupdate()


def draw_menu(items, banner=""):
    """Draw menu.

    :param list items: menu items
    :param str banner: banner

    :returns: menu item index
    :rtype: int
    """
    if len(items) == 1:
        return 0
    while True:
        max_y, max_x = curses.panel.top_panel().window().getmaxyx()
        nlines = max_y // 2
        ncols = max_x // 2
        panel = get_panel(nlines, ncols, (max_y - nlines) // 2, (max_x - ncols) // 2)
        window_mgr = WindowManager(panel.window(), box=True, banner=banner)
        y, x = window_mgr.window.getyx()
        window_mgr.writelines(
            y + 1,
            x + 1,
            (
                ((f"{i}: {item}", curses.color_pair(0)),)
                for i, item in enumerate(items, start=1)
            ),
        )
        y, _ = window_mgr.window.getyx()
        line = ""
        try:
            while line not in (str(i) for i in range(1, len(items) + 1)):
                line = window_mgr.readline(
                    [],
                    y=y,
                    prompt=((">", curses.color_pair(0)),),
                    scroll=True,
                    clear=True,
                )
        except EOFError:
            return -1
        except ResizeError:
            panel.bottom()
            window_mgr.reinitialize()
            continue
        else:
            break
        finally:
            del panel
            curses.panel.update_panels()
    return int(line) - 1


def draw_input_box(banner="", prompt=tuple()):
    """Draw input box.

    :param str banner: banner
    :param tuple prompt: prompt

    :returns: input
    :rtype: str
    """
    while True:
        try:
            max_y, max_x = curses.panel.top_panel().window().getmaxyx()
            nlines = max_y // 2
            ncols = max_x // 2
            panel = get_panel(
                nlines,
                ncols,
                (max_y - nlines) // 2,
                (max_x - ncols) // 2,
            )
            window_mgr = WindowManager(panel.window(), box=True, banner=banner)
            y, _ = window_mgr.window.getyx()
            line = window_mgr.readline([], prompt=prompt, y=y if banner else 1)
        except ResizeError:
            panel.bottom()
            window_mgr.window.reinitialize()
            continue
        else:
            return line
        finally:
            del panel
            curses.panel.update_panels()
