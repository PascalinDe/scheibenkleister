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
:synopsis: Utils test cases.
"""


# standard library imports
import unittest
# third party imports
# library specific imports
from scheibenkleister.utils import Buffer


class TestBuffer(unittest.TestCase):
    """Buffer test cases."""

    def test_init(self):
        """Test initializing buffer.

        Trying: initialize buffer
        Expecting: buffer has been initialized
        """
        for iterable in (tuple(), "abcde"):
            buffer = Buffer(iterable=iterable)
            self.assertEqual(buffer.pos, len(iterable) - 1)
            if iterable:
                self.assertEqual(buffer.cursor, iterable[-1])
                return
            with self.assertRaises(IndexError):
                buffer.cursor

    def test_append(self):
        """Test appending a new character to the end of the buffer.

        Trying: append a new character
        Expecting: cursor position has been updated accordingly
        """
        buffer = Buffer(iterable="abcde")
        buffer.append("f")  # current cursor position is at the end
        self.assertEqual(buffer.pos, 5)
        self.assertEqual(buffer.cursor, "f")
        buffer = Buffer(iterable="abcde")
        buffer._pos -= 1
        buffer.append("f")  # current cursor position is before the end
        self.assertEqual(buffer.pos, 3)
        self.assertEqual(buffer.cursor, "d")

    def test_extend(self):
        """Test appending characters from iterable to the end of the
        buffer.

        Trying: appending characters
        Expecting: cursor position has been updated accordingly
        """
        buffer = Buffer(iterable="abc")
        buffer.extend("def")    # current cursor position is at the end
        self.assertEqual(buffer.pos, 5)
        self.assertEqual(buffer.cursor, "f")
        buffer = Buffer(iterable="abc")
        buffer._pos -= 1
        buffer.extend("def")    # current cursor position is before the end
        self.assertEqual(buffer.pos, 1)
        self.assertEqual(buffer.cursor, "b")

    def test_insert(self):
        """Test inserting character x in the buffer before
        position i.

        Trying: inserting character
        Expecting: cursor position has been updated accordingly
        """
        buffer = Buffer(iterable="abcde")
        buffer.insert(0, "f")   # i before current cursor position
        self.assertEqual(buffer.pos, 5)
        self.assertEqual(buffer.cursor, "e")
        buffer = Buffer(iterable="abcde")
        buffer.insert(4, "f")   # i at current cursor position
        self.assertEqual(buffer.pos, 5)
        self.assertEqual(buffer.cursor, "e")
        buffer = Buffer(iterable="abcde")
        buffer.insert(5, "f")   # i after current cursor position
        self.assertEqual(buffer.pos, 4)
        self.assertEqual(buffer.cursor, "e")

    def test_remove(self):
        """Test removing the first occurrence of character x from the buffer.

        Trying: removing character x
        Expecting: cursor has been updated accordingly
        """
        buffer = Buffer(iterable="abcde")
        buffer = Buffer(iterable="abcde")
        try:
            buffer.remove("f")
        except Exception:
            pass
        self.assertEqual(buffer.pos, 4)
        self.assertEqual(buffer.cursor, "e")
        buffer._pos -= 2
        buffer.remove("d")  # x after current cursor position
        self.assertEqual(buffer.pos, 2)
        self.assertEqual(buffer.cursor, "c")
        buffer = Buffer(iterable="abcde")
        buffer.remove("e")  # x at current cursor position
        self.assertEqual(buffer.pos, 3)
        self.assertEqual(buffer.cursor, "d")
        buffer = Buffer(iterable="abcde")
        buffer.remove("a")  # x before current cursor position
        self.assertEqual(buffer.pos, 3)
        self.assertEqual(buffer.cursor, "e")

    def test_pop(self):
        """Test removing the character with the index index from
        the buffer and return it.

        Trying: removing the character with the index index
        Expecting: cursor position has been updated accordingly
        """
        buffer = Buffer("abcde")
        try:
            buffer.pop(5)
        except Exception:
            pass
        self.assertEqual(buffer.pos, 4)
        self.assertEqual(buffer.cursor, "e")
        buffer._pos -= 1
        buffer.pop(4)   # index after current cursor position
        self.assertEqual(buffer.pos, 3)
        self.assertEqual(buffer.cursor, "d")
        buffer = Buffer(iterable="abcde")   # index at current cursor position
        buffer.pop(4)
        self.assertEqual(buffer.pos, 3)
        self.assertEqual(buffer.cursor, "d")
        buffer = Buffer(iterable="abcde")   # index before current cursor position
        buffer.pop(0)
        self.assertEqual(buffer.pos, 3)
        self.assertEqual(buffer.cursor, "e")

    def test_clear(self):
        """Test removing all characters from the buffer.

        Trying: removing all characters
        Expecting: cursor position has been updated accordingly
        """
        buffer = Buffer(iterable="abcde")
        buffer.clear()
        self.assertEqual(buffer.pos, -1)
        with self.assertRaises(IndexError):
            buffer.cursor

    def test_reverse(self):
        """Test reversing the characters of the buffer in place.

        Trying: reversing the characters
        Expecting: cursor position has been updated accordingly
        """
        buffer = Buffer(iterable="abcde")
        buffer._pos -= 1
        buffer.reverse()
        self.assertEqual(buffer.pos, 1)
        self.assertEqual(buffer.cursor, "d")

    def test_move(self):
        """Test moving cursor position n steps to the right.

        Trying: moving cursor position
        Expecting: cursor position has been updated accordingly
        """
        buffer = Buffer(iterable="abcde")
        # current cursor position is at the end
        with self.assertRaises(IndexError):
            buffer.move(1)
        with self.assertRaises(IndexError):
            buffer.move(-10)
        buffer.move(-2)
        self.assertEqual(buffer.pos, 2)
        self.assertEqual(buffer.cursor, "c")
        # current cursor position is at the beginning
        buffer = Buffer(iterable="abcde")
        buffer._pos = 0
        with self.assertRaises(IndexError):
            buffer.move(5)
        with self.assertRaises(IndexError):
            buffer.move(-6)
        buffer.move(1)
        self.assertEqual(buffer.pos, 1)
        self.assertEqual(buffer.cursor, "b")
        # current cursor position is in the middle
        buffer = Buffer(iterable="abcde")
        buffer._pos = 2
        with self.assertRaises(IndexError):
            buffer.move(3)
        with self.assertRaises(IndexError):
            buffer.move(-8)
        buffer.move(1)
        self.assertEqual(buffer.pos, 3)
        self.assertEqual(buffer.cursor, "d")

    def test_move_to_start(self):
        """Test moving cursor position to start.

        Trying: moving cursor position
        Expecting: cursor position has been updated accordingly
        """
        buffer = Buffer(iterable="abcde")
        buffer.move_to_start()
        self.assertEqual(buffer.pos, 0)

    def test_move_to_end(self):
        """Test moving cursor position to end.

        Trying: moving cursor position
        Expecting: cursor position has been updated accordingly
        """
        buffer = Buffer(iterable="abcde")
        buffer._pos = 0
        buffer.move_to_end()
        self.assertEqual(buffer.pos, 4)
