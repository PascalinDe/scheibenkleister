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
:synopsis: Curses-based terminal test cases.
"""


# standard library imports
import curses
import string
import unittest

from unittest.mock import MagicMock

# third party imports
# library specific imports
from scheibenkleister.utils import Buffer
from scheibenkleister.terminal import Terminal


class TestTerminal(unittest.TestCase):
    """Curses-based terminal test cases."""

    def setUp(self):
        self.stdscr = curses.initscr()
        curses.start_color()

    def tearDown(self):
        curses.endwin()

    def _get_input(self, length):
        """Get input.

        :param int length: length

        :returns: input
        :rtype: str
        """
        q, r = divmod(length, len(string.ascii_letters))
        return (
            list(q*string.ascii_letters)
            + [string.ascii_letters[i] for i in range(r)]
        )

    def test_init(self):
        """Test initalizing terminal.

        Trying: initializing terminal
        Expecting: character buffer and window positions
        have been updated accordingly
        """
        # empty banner
        # no border around the edges
        terminal = Terminal(self.stdscr)
        buffer = Buffer()
        self.assertEqual(terminal.window.getyx(), (0, 0))
        self.assertSequenceEqual(terminal.buffer, buffer, seq_type=Buffer)
        self.stdscr.clear()
        # border around the edges
        terminal = Terminal(self.stdscr, box=True)
        self.assertEqual(terminal.window.getyx(), (1, 1))
        self.assertSequenceEqual(terminal.buffer, buffer, seq_type=Buffer)
        self.stdscr.clear()
        # banner
        banner = "Lorem ipsum"
        # no border around the edges
        terminal = Terminal(self.stdscr, banner=banner)
        buffer = Buffer(iterable=banner)
        self.assertEqual(terminal.window.getyx(), (2, 0))
        self.assertSequenceEqual(terminal.buffer, buffer, seq_type=Buffer)
        self.stdscr.clear()
        # border around the edges
        terminal = Terminal(self.stdscr, banner=banner, box=True)
        buffer = Buffer(iterable=banner)
        self.assertEqual(terminal.window.getyx(), (3, 1))
        self.assertSequenceEqual(terminal.buffer, buffer, seq_type=Buffer)

    def test_insch(self):
        """Test inserting character.

        Trying: inserting character
        Expecting: character buffer and window have been updated
        """
        terminal = Terminal(self.stdscr)
        terminal.window.move(terminal.min_y, terminal.min_x)
        input_ = self._get_input(terminal.content_length)
        # x < max_x
        j = terminal.min_x
        for i in range(len(input_)):
            terminal._insch(input_[i])
            j += 1
            self.assertEqual(terminal.buffer.cursor, input_[i])
            self.assertEqual(
                terminal.window.getyx(),
                (terminal.min_y, j)
            )
            self.assertEqual(
                chr(terminal.window.inch(terminal.min_y, j-1) & curses.A_CHARTEXT),
                input_[i]
            )
            terminal.window.move(terminal.min_y, j)
        self.assertEqual(terminal.window.getyx()[1], terminal.max_x)
        # x == max_x
        ch = "0"
        terminal._insch(ch)
        self.assertEqual(terminal.buffer.cursor, ch)
        self.assertEqual(terminal.window.getyx(), (terminal.min_y, terminal.max_x))
        self.assertEqual(
            chr(
                terminal.window.inch(terminal.min_y, terminal.max_x)
                & curses.A_CHARTEXT
            ),
            ch
        )
        self.assertEqual(
            chr(
                terminal.window.inch(terminal.min_y, terminal.min_x)
                & curses.A_CHARTEXT
            ),
            input_[1]
        )
        self.assertEqual(terminal.buffer, [*input_, ch])

    def test_delch(self):
        """Test deleting character.

        Trying: deleting character
        Expecting: character buffer and window have been updated
        """
        pass

    def test_move_right(self):
        pass

    def test_move_left(self):
        pass

    def test_scroll_up_down(self):
        pass

    def test_browse_command_history(self):
        pass

    def test_completeline(self):
        pass

    def test_readch(self):
        """Test reading character.

        Trying: reading character
        Expecting: character
        """
        terminal = Terminal(self.stdscr)
        scroll = False
        for ch, exception in (
            # https://bugs.python.org/issue15785
            # curses.unget_wch cannot push special keys
            # (curses.KEY_RESIZE, ResizeInterrupt),
            ("\x03", KeyboardInterrupt),
            ("\x04", EOFError),
            # (curses.KEY_ENTER, EOLInterrupt),
        ):
            curses.unget_wch(ch)
            with self.assertRaises(exception):
                terminal._readch([], [], scroll=scroll)
        for ch, method in (
            ("\x09", "_completeline"),
            # https://bugs.python.org/issue15785
            # curses.unget_wch cannot push keypad keys
            # (curses.KEY_DOWN, "_browse_command_history"),
            # (curses.KEY_DOWN, "_browse_command_history"),
            # (526, "_scroll_up_down"),
            # (567, "_scroll_up_down"),
            # (curses.KEY_LEFT, "_move_left"),
            # (curses.KEY_RIGHT, "_move_right"),
            # (curses.KEY_BACKSPACE, "_delch"),
            ("a", "_insch"),
        ):
            curses.unget_wch(ch)
            setattr(terminal, method, MagicMock())
            if ch in (528, 569):
                scroll = True
            terminal._readch([], [], scroll=scroll)
            getattr(terminal, method).assert_called()
        # https://bugs.python.org/issue15785
        # terminal._insch.reset_mock()
        # curses.unget_wch(544)
        # terminal._readch([], [], scroll=scroll)
        # terminal._insch.assert_not_called()
