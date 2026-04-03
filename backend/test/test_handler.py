import numpy as np
import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from handler import Handler

class TestBoard(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handler = Handler()

    def test_parse_basic_move(self):
        # Arrange
        move = "e2e4"

        # Act
        res = self.handler.parse_move(move)

        # Assert
        self.assertEqual(res["valid"], True)

    def test_parse_promotion_move(self):
        # Arrange
        move = "e7e8=q"

        # Act
        res = self.handler.parse_move(move)

        # Assert
        self.assertEqual(res["valid"], True)

    def test_parse_invalid_move_too_short(self):
        # Arrange
        move = "ee"

        # Act
        res = self.handler.parse_move(move)

        # Assert
        self.assertEqual(res["valid"], False)

    def test_parse_invalid_move_too_long(self):
        # Arrange
        move = "e7e8=qq"

        # Act
        res = self.handler.parse_move(move)

        # Assert
        self.assertEqual(res["valid"], False)

    def test_parse_invalid_move_len_5(self):
        # Arrange
        move = "e7e87"

        # Act
        res = self.handler.parse_move(move)

        # Assert
        self.assertEqual(res["valid"], False)

    def test_parse_invalid_move_invalid_promote(self):
        # Arrange
        move = "e7e8=w"

        # Act
        res = self.handler.parse_move(move)

        # Assert
        self.assertEqual(res["valid"], False)

