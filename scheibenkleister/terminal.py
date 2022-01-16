#    This file is part of Scheibenkleister 1.0.
#    Copyright (C) 2022  Carine Dengler
#
#    Scheibenkleister is free software: you can redistribute it and/or modify
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
:synopsis: Curses-based terminal.
"""


# standard library imports
import curses
import unicodedata

# third party imports
# library specific imports
from scheibenkleister.utils import Buffer
from scheibenkleister.errors import EOLInterrupt, ResizeInterrupt


class Terminal:
    """Curses-based terminal.

    :ivar window window: window
    :ivar str banner: banner
    :ivar tuple prompt: prompt
    :ivar bool box: toggle drawing a border around the edges on/off
    :ivar tuple pool: tab completion pool
    :ivar list history: command history
    :ivar Buffer buffer: character buffer
    :ivar list upper_window: upper window stack
    :ivar list lower_window: lower window stack
    """

    def __init__(self, window, banner="", prompt="$", box=False, pool=()):
        """Initialize terminal.

        :param window window: window
        :param str banner: banner
        :param str prompt: prompt
        :param bool box: toggle drawing a border around the edges on/off
        :param tuple pool: tab completion pool
        """
        self._window = window
        self.banner = banner
        self.prompt = ((prompt, curses.color_pair(0)),) if prompt else tuple()
        self.box = box
        self.pool = pool
        self.history = []
        self.buffer = Buffer()
        self.reinit()

    def reinit(self, clear=True):
        """Reinitialize terminal.

        :param bool clear: toggle clearing the window on/off
        """
        self.window.idlok(True)
        self.window.keypad(True)
        self.window.scrollok(True)
        if clear:
            self.buffer = Buffer(iterable=self.banner)
            self.upper_window = []
            self.lower_window = []
            if self.box:
                self.window.box()
                self.window.move(1, 1)
            if self.banner:
                y, x = self.window.getyx()
                self.window.addstr(y, x, self.banner)
                self.window.move(y + 2, x)

    @property
    def prompt_length(self):
        """Prompt length."""
        return sum(len(part[0]) for part in self.prompt)

    @property
    def window(self):
        """Window."""
        return self._window

    @window.setter
    def window(self, window):
        """Replace window."""
        self._window = window

    @property
    def min_x(self):
        """Minimum x position."""
        return int(self.box) + self.prompt_length

    @property
    def max_x(self):
        """Maximum (legal) x position."""
        return self.window.getmaxyx()[1] - 1 - int(self.box)

    @property
    def min_y(self):
        """Minimum y position."""
        return int(self.box)

    @property
    def content_length(self):
        """Content length."""
        return self.max_x - self.min_x

    def _insch(self, ch):
        """Insert character.

        :param str ch: character
        """
        y, x = self.window.getyx()
        if x < self.min_x:
            x = self.min_x
            self.buffer.move_to_start()
        self.buffer.insert(self.buffer.pos, ch)
        if x == self.max_x:
            self.window.delch(y, self.min_x)
            self.window.move(y, x)
        self.window.insstr(y, x, ch)
        self.window.move(y, x + 1 if x < self.max_x else x)

    def _delch(self):
        """Delete character."""
        y, x = self.window.getyx()
        if x < self.min_x:
            x = self.min_x
            self.buffer.move_to_start()
            return
        if x > self.min_x:
            self.buffer.pop(self.buffer.pos - 1)
            if self.box:
                self.window.delch(y, self.window.getmaxyx()[1] - 1)
            self.window.delch(y, x - 1)
        if len(self.buffer) > self.content_length and self.buffer.pos >= self.max_x:
            self.window.insstr(
                y,
                self.min_x,
                self.buffer[self.buffer.pos - self.max_x],
            )
            self.window.move(y, x)

    def _move_right(self):
        raise NotImplementedError

    def _move_left(self):
        raise NotImplementedError

    def _scroll_up_down(self):
        raise NotImplementedError

    def _browse_command_history(self):
        raise NotImplementedError

    def _completeline(self):
        raise NotImplementedError

    def _readch(self, upper_history, lower_history, scroll=False):
        """Read character.

        :param list upper_history: upper command history
        :param list lower_history: lower command history
        :param bool scroll: toggle scrolling the screen on/off
        """
        ch = self.window.get_wch()
        if exception := {
                curses.KEY_RESIZE: ResizeInterrupt,
                "\x03": KeyboardInterrupt,
                "\x04": EOFError,
        }.get(ch):
            raise exception
        if ch == "\x09":
            self._completeline()
            return
        if ch in (curses.KEY_DOWN, curses.KEY_UP):
            self._browse_command_history()
            return
        if isinstance(ch, int) and curses.keyname(ch) in (b"kDN5", b"kUP5"):
            if scroll:
                self._scroll_up_down(ch)
            return
        if ch == curses.KEY_LEFT:
            self._move_left()
            return
        if ch == curses.KEY_RIGHT:
            self._move_right()
            return
        if ch == curses.KEY_ENTER:
            raise EOLInterrupt
        if ch == curses.KEY_BACKSPACE:
            self._delch()
            return
        if isinstance(ch, int):
            return
        if unicodedata.category(ch).startswith("C"):
            return
        self._insch()

    def readline(self, scroll=False, clear=False):
        """Read line.

        :param bool scroll: toggle scrolling the screen on/off
        :param bool clear: toggle clearing line on/off
        """
        y, _ = self.window.getyx()
        max_y, max_x = self.window.getmaxyx()
        if self.prompt:
            self.writeline(y, self.min_x, self.prompt, move_down=False)
        self.buffer.clear()
        upper_history = self.history.copy()
        lower_history = []
        while True:
            try:
                y, x = self.window.getyx()
                if x == 0:
                    while y < max_y and self.lower_window:
                        self._scroll_down()
                        y, _ = self.window.getyx()
                    self.window.move(y, len(self.scrapeline(y)[0][0]))
                self._readch(upper_history, lower_history, scroll=scroll)
            except (
                ResizeInterrupt,
                KeyboardInterrupt,
                EOFError,
                EOLInterrupt,
            ) as exception:
                raise exception
        if clear:
            self.window.move(y, int(self.box))
            self.window.clrtoeol()
        return "".join(self.buffer)
