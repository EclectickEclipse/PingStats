#!/usr/bin/env python
# coding: utf-8

"""
    python-ping unittests
    ~~~~~~~~~~~~~~~~~~~~~

    Note that ICMP messages can only be sent from processes running as root,
    therefore it requires you use the sudo command as displayed here. This
    may cause issues for users without sudo permission.
        .../python-ping$ sudo python tests.py

    :homepage: https://github.com/l4m3rx/python-ping/
    :copyleft: 1989-2016 by the python-ping team, see AUTHORS for more details.
    :license: GNU GPL v2, see LICENSE for more details.
"""

# import socket
import unittest
import ping


class MyStats_test(unittest.TestCase):

    def test_instantiation(self):
        self.assertIsInstance(ping.MyStats(), ping.MyStats, msg="Failed MyStats instantiation!")


class checksum_test(unittest.TestCase):

    def test_fail_arraypack(self):
        """ Confirm that checksum properly throws errors during runtime by giving it a string and int object i
        respectively. """
        with self.assertRaises(TypeError):  # the function should fail to pack an array without a bytes like string.
            x = ping.checksum('test string')
            x = ping.checksum(12345)
            del x

    def test_succeed_arraypack(self):
        """ Confirm that the checksum returns predictable output. """
        self.assertEqual(ping.checksum(b'12345'), 26265)
        self.assertEqual(ping.checksum(b'asdfg'), 54053)


if __name__ == '__main__':
    unittest.main()
