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
:synopsis: Utils.
"""


# standard library imports
from collections import UserList
# third party imports
# library specific imports


class Buffer(UserList):
    """Character buffer."""

    def __init__(self, iterable=tuple()):
        """Initialize character buffer.

        :param iterable: iterable
        """
        self._pos = len(iterable)
        super().__init__(iterable)

    @property
    def pos(self):
        """Return current position.

        :returns: current position
        :rtype: int
        """
        return self._pos

    @property
    def cursor(self):
        """Return character at the current cursor position.

        :raises: IndexError

        :returns: character
        :rtype: str
        """
        if not self.data:
            raise IndexError("empty buffer")
        return self.data[self.pos - 1]

    def append(self, x):
        """Append a new character to the end of the buffer.

        :param str x: new character
        """
        i = int(self.pos == len(self.data) - 1)
        super().append(x)
        self._pos += i

    def extend(self, iterable):
        """Append characters from iterable to the end of the buffer.

        :param iterable: iterable
        """
        i = int(self.pos == len(self.data) - 1)
        super().extend(iterable)
        self._pos += i * len(iterable)

    def insert(self, i, x):
        """Insert character x in the buffer before position i.

        :param int i: position
        :param str x: character
        """
        i = i if i >= 0 else len(self.data) + i
        super().insert(i, x)
        if self._pos >= i:
            self._pos += 1

    def remove(self, x):
        """Remove the first occurrence of character x from the buffer.

        :param str x: character
        """
        try:
            i = self.data.index(x)
        except ValueError:
            pass
        else:
            super().remove(x)
            if self._pos > 0 and self._pos >= i:
                self._pos -= 1

    def pop(self, index):
        """Remove the character with the index index from the buffer
        and return it.

        :param int index: index

        :returns: character
        :rtype: str
        """
        index = index if index >= 0 else len(self.data) + index
        x = super().pop(index)
        if self._pos > 0 and self._pos >= index:
            self._pos -= 1
        return x

    def clear(self):
        """Remove all characters from the buffer."""
        super().clear()
        self._pos = -1

    def reverse(self):
        """Reverse the characters of the buffer in place."""
        super().reverse()
        self._pos = len(self.data) - 1 - self._pos

    def move(self, n):
        """Move cursor position n steps to the right.

        :param int n: number of steps

        :raises: IndexError
        :raises: ValueError
        """
        pos = self._pos + n
        if pos > len(self.data) - 1 or pos < -(len(self.data)):
            raise IndexError(f"new cursor position {pos} out of bounds")
        self._pos += n

    def move_to_start(self):
        """Move cursor position to start."""
        self._pos = 0

    def move_to_end(self):
        """Move cursor position to end."""
        self._pos = len(self.data) - 1
