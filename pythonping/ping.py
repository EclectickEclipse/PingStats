#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    A pure python ping implementation using raw sockets.

    Compatibility:
        OS: Linux, Windows, MacOSX
        Python: 2.6 - 3.5

    Note that due to the usage of RAW sockets root/Administrator
    privileges are requied.

    Derived from ping.c distributed in Linux's netkit. That code is
    copyright (c) 1989 by The Regents of the University of California.
    That code is in turn derived from code written by Mike Muuss of the
    US Army Ballistic Research Laboratory in December, 1983 and
    placed in the public domain. They have my thanks.

    Copyright (c) Matthew Dixon Cowles, <http://www.visi.com/~mdc/>.
    Distributable under the terms of the GNU General Public License
    version 2. Provided with no warranties of any sort.

    website: https://github.com/l4m3rx/python-ping

"""

# TODO Remove any calls to time.sleep
# This would enable extension into larger framework that aren't multi threaded.
import os
import sys
import time
import array
import socket
import struct
import select
import signal

if __name__ == '__main__':
    import argparse


try:
    from _thread import get_ident
except ImportError:
    def get_ident(): return 0

if sys.platform == "win32":
    # On Windows, the best timer is time.clock()
    default_timer = time.clock
else:
    # On most other platforms the best timer is time.time()
    default_timer = time.time

# ICMP parameters

ICMP_ECHOREPLY = 0  # Echo reply (per RFC792)
ICMP_ECHO = 8  # Echo request (per RFC792)
ICMP_ECHO_IPV6 = 128  # Echo request (per RFC4443)
ICMP_ECHO_IPV6_REPLY = 129  # Echo request (per RFC4443)
ICMP_MAX_RECV = 2048  # Max size of incoming buffer

MAX_SLEEP = 1000


class MyStats:
    thisIP = "0.0.0.0"
    pktsSent = 0
    pktsRcvd = 0
    minTime = 999999999
    maxTime = 0
    totTime = 0
    avrgTime = 0
    fracLoss = 1.0

# NOT Used globally anymore.
myStats = MyStats


def _checksum(source_string):
    """
    A port of the functionality of in_cksum() from ping.c
    Ideally this would act on the string as a series of 16-bit ints (host
    packed), but this works.
    Network data is big-endian, hosts are typically little-endian
    """
    if (len(source_string) % 2):
        source_string += "\x00"
    converted = array.array("H", source_string)
    if sys.byteorder == "big":
        converted.bytewap()
    val = sum(converted)

    val &= 0xffffffff  # Truncate val to 32 bits (a variance from ping.c, which
    # uses signed ints, but overflow is unlikely in ping)

    val = (val >> 16) + (val & 0xffff)  # Add high 16 bits to low 16 bits
    val += (val >> 16)  # Add carry from above (if any)
    answer = ~val & 0xffff  # Invert and truncate to 16 bits
    answer = socket.htons(answer)

    return answer


def single_ping(destIP, hostname, timeout, mySeqNumber, numDataBytes,
                myStats=None, quiet=False, ipv6=False):
    """
    Returns either the delay (in ms) or None on timeout.
    """
    delay = None

    if ipv6:
        try:  # One could use UDP here, but it's obscure
            mySocket = socket.socket(socket.AF_INET6, socket.SOCK_RAW,
                                     socket.getprotobyname("ipv6-icmp"))
            mySocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        except OSError as e:
            print("failed. (socket error: '%s')" % str(e))
            print('Note that python-ping uses RAW sockets'
                  'and requiers root rights.')
            raise  # raise the original error
    else:

        try:  # One could use UDP here, but it's obscure
            mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                                     socket.getprotobyname("icmp"))
            mySocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        except OSError as e:
            print("failed. (socket error: '%s')" % str(e))
            print('Note that python-ping uses RAW sockets'
                  'and requires root rights.')
            raise  # raise the original error

    my_ID = (os.getpid() ^ get_ident()) & 0xFFFF

    sentTime = _send(mySocket, destIP, my_ID, mySeqNumber, numDataBytes, ipv6)
    if sentTime is None:
        mySocket.close()
        return delay

    if myStats is not None:
        myStats.pktsSent += 1

    recvTime, dataSize, iphSrcIP, icmpSeqNumber, iphTTL \
        = _receive(mySocket, my_ID, timeout, ipv6)

    mySocket.close()

    if recvTime:
        delay = (recvTime-sentTime)*1000
        if not quiet:
            if ipv6:
                host_addr = hostname
            else:
                try:
                    host_addr = socket.inet_ntop(socket.AF_INET, struct.pack(
                        "!I", iphSrcIP))
                except AttributeError:
                    # Python on windows dosn't have inet_ntop.
                    host_addr = hostname

            print("%d bytes from %s: icmp_seq=%d ttl=%d time=%.2f ms" % (
                dataSize, host_addr, icmpSeqNumber, iphTTL, delay)
            )

        if myStats is not None:
            myStats.pktsRcvd += 1
            myStats.totTime += delay
            if myStats.minTime > delay:
                myStats.minTime = delay
            if myStats.maxTime < delay:
                myStats.maxTime = delay
    else:
        delay = None
        if not quiet:
            print("Request timed out.")

    return delay


def _send(mySocket, destIP, myID, mySeqNumber, numDataBytes, ipv6=False):
    """
    Send one ping to the given >destIP<.
    """
    # destIP  =  socket.gethostbyname(destIP)

    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    # (numDataBytes - 8) - Remove header size from packet size
    myChecksum = 0

    # Make a dummy heder with a 0 checksum.
    if ipv6:
        header = struct.pack(
            "!BbHHh", ICMP_ECHO_IPV6, 0, myChecksum, myID, mySeqNumber
        )
    else:
        header = struct.pack(
            "!BBHHH", ICMP_ECHO, 0, myChecksum, myID, mySeqNumber
        )

    padBytes = []
    startVal = 0x42
    # 'cose of the string/byte changes in python 2/3 we have
    # to build the data differnely for different version
    # or it will make packets with unexpected size.
    if sys.version[:1] == '2':
        _bytes = struct.calcsize("d")
        data = ((numDataBytes - 8) - _bytes) * "Q"
        data = struct.pack("d", default_timer()) + data
    else:
        for i in range(startVal, startVal + (numDataBytes - 8)):
            padBytes += [(i & 0xff)]  # Keep chars in the 0-255 range
        # data = bytes(padBytes)
        data = bytearray(padBytes)

    # Calculate the checksum on the data and the dummy header.
    myChecksum = _checksum(header + data)  # Checksum is in network order

    # Now that we have the right checksum, we put that in. It's just easier
    # to make up a new header than to stuff it into the dummy.
    if ipv6:
        header = struct.pack(
            "!BbHHh", ICMP_ECHO_IPV6, 0, myChecksum, myID, mySeqNumber
        )
    else:
        header = struct.pack(
            "!BBHHH", ICMP_ECHO, 0, myChecksum, myID, mySeqNumber
        )

    packet = header + data

    sendTime = default_timer()

    try:
        mySocket.sendto(packet, (destIP, 1))  # Port number is irrelevant
    except OSError as e:
        print("General failure (%s)" % str(e))
        return
    except socket.error as e:
        print("General failure (%s)" % str(e))
        return

    return sendTime


def _receive(mySocket, myID, timeout, ipv6=False):
    """
    Receive the ping from the socket. Timeout = in ms
    """
    timeLeft = timeout/1000

    while True:  # Loop while waiting for packet or timeout
        startedSelect = default_timer()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (default_timer() - startedSelect)
        if whatReady[0] == []:  # Timeout
            return None, 0, 0, 0, 0

        timeReceived = default_timer()

        recPacket, addr = mySocket.recvfrom(ICMP_MAX_RECV)

        ipHeader = recPacket[:20]

        iphVersion, iphTypeOfSvc, iphLength, iphID, iphFlags, iphTTL, \
            iphProtocol, iphChecksum, iphSrcIP, iphDestIP = struct.unpack(
                "!BBHHHBBHII", ipHeader)

        if ipv6:
            icmpHeader = recPacket[0:8]
        else:
            icmpHeader = recPacket[20:28]

        icmpType, icmpCode, icmpChecksum, icmpPacketID, icmpSeqNumber \
            = struct.unpack("!BBHHH", icmpHeader)

        # Match only the packets we care about
        if (icmpType != 8) and (icmpPacketID == myID):
            dataSize = len(recPacket) - 28
            return timeReceived, (dataSize + 8), iphSrcIP, icmpSeqNumber, \
                iphTTL

        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return None, 0, 0, 0, 0


def _dump_stats(myStats):
    """
    Show stats when pings are done
    """
    print("\n----%s PYTHON PING Statistics----" % (myStats.thisIP))

    if myStats.pktsSent > 0:
        myStats.fracLoss = (myStats.pktsSent - myStats.pktsRcvd) / \
            myStats.pktsSent

    print("%d packets transmitted, %d packets received, %0.1f%% packet loss"
          % (myStats.pktsSent, myStats.pktsRcvd, 100.0 * myStats.fracLoss))

    if myStats.pktsRcvd > 0:
        print("round-trip (ms)  min/avg/max = %0.1f/%0.1f/%0.1f" % (
            myStats.minTime, myStats.totTime/myStats.pktsRcvd, myStats.maxTime
        ))

    print('')
    return


def _signal_handler(signum, frame):
    """ Handle exit via signals """
    _dump_stats(myStats)
    print("\n(Terminated with signal %d)\n" % (signum))
    sys.exit(0)


def verbose_ping(hostname, timeout=3000, count=3,
                 numDataBytes=64, path_finder=False, ipv6=False):
    """
    Send >count< ping to >destIP< with the given >timeout< and display
    the result.

    To continuously attempt ping requests, set >count< to None.

    To consume the generator, use the following syntax:
        >>> import ping
        >>> for return_val in ping.verbose_ping('google.ca'):
            pass  # COLLECT YIELDS AND PERFORM LOGIC.

    Alternatively, you can consume the generator by using list comprehension:
        >>> import ping
        >>> consume = list(ping.verbose_ping('google.ca'))

    Via the same syntax, you can successfully get the exit code via:
        >>> import ping
        >>> consume = list(ping.verbose_ping('google.ca'))
        >>> exit_code = consume[:-1]  # The last yield is the exit code.
        >>> sys.exit(exit_code)
    """
    signal.signal(signal.SIGINT, _signal_handler)  # Handle Ctrl-C
    if hasattr(signal, "SIGBREAK"):
        # Handle Ctrl-Break e.g. under Windows
        signal.signal(signal.SIGBREAK, _signal_handler)

    myStats = MyStats()  # Reset the stats

    mySeqNumber = 0  # Starting value

    try:
        if ipv6:
            info = socket.getaddrinfo(hostname, None)[0]
            destIP = info[4][0]
        else:
            destIP = socket.gethostbyname(hostname)
        print("\nPYTHON PING %s (%s): %d data bytes" % (hostname, destIP,
                                                        numDataBytes))
    except socket.gaierror as e:
        print("\nPYTHON PING: Unknown host: %s (%s)" % (hostname, str(e)))
        print('')
        return

    myStats.thisIP = destIP

    i = 0
    while 1:
        delay = single_ping(destIP, hostname, timeout, mySeqNumber,
                            numDataBytes, ipv6=ipv6, myStats=myStats)
        if delay is None:
            delay = 0

        mySeqNumber += 1

        # Pause for the remainder of the MAX_SLEEP period (if applicable)
        if (MAX_SLEEP > delay):
            time.sleep((MAX_SLEEP - delay)/1000)

        if count is not None and i < count:
            i += 1
            yield myStats.pktsRcvd
        elif count is None:
            yield myStats.pktsRcvd
        elif count is not None and i >= count:
            break

    _dump_stats(myStats)
    # 0 if we receive at least one packet
    # 1 if we don't receive any packets
    yield not myStats.pktsRcvd


def quiet_ping(hostname, timeout=3000, count=3,
               numDataBytes=64, path_finder=False, ipv6=False):
    """ Same as verbose_ping, but the results are yielded as a tuple """
    myStats = MyStats()  # Reset the stats
    mySeqNumber = 0  # Starting value

    try:
        if ipv6:
            info = socket.getaddrinfo(hostname, None)[0]
            destIP = info[4][0]
        else:
            destIP = socket.gethostbyname(hostname)
    except socket.gaierror:
        yield False

    myStats.thisIP = destIP

    # This will send packet that we don't care about 0.5 seconds before it
    # starts actually pinging. This is needed in big MAN/LAN networks where
    # you sometimes loose the first packet. (while the switches find the way)
    if path_finder:
        fakeStats = MyStats()
        single_ping(fakeStats, destIP, hostname, timeout,
                    mySeqNumber, numDataBytes, quiet=True, ipv6=ipv6)
        time.sleep(0.5)

    i = 0
    while 1:
        delay = single_ping(destIP, hostname, timeout, mySeqNumber,
                            numDataBytes, quiet=True, ipv6=ipv6,
                            myStats=myStats)

        if delay is None:
            delay = 0

        mySeqNumber += 1

        # Pause for the remainder of the MAX_SLEEP period (if applicable)
        if (MAX_SLEEP > delay):
            time.sleep((MAX_SLEEP - delay) / 1000)

        yield myStats.pktsSent

        if count is not None and i < count:
            i += 1
        elif count is not None:
            yield myStats.pktsSent
        elif count is not None and i >= count:
            break

    if myStats.pktsSent > 0:
        myStats.fracLoss = (myStats.pktsSent - myStats.pktsRcvd) / \
            myStats.pktsSent

    if myStats.pktsRcvd > 0:
        myStats.avrgTime = myStats.totTime / myStats.pktsRcvd

    # return tuple(max_rtt, min_rtt, avrg_rtt, percent_lost)
    yield myStats.maxTime, myStats.minTime, myStats.avrgTime, myStats.fracLoss


if __name__ == '__main__':
    # FIXME: Add a real CLI (mostly fixed)
    if sys.argv.count('-T') or sys.argv.count('--test_case'):
        print('Running PYTHON PING test case.')
        # These should work:
        for val in verbose_ping("127.0.0.1"):
            pass
        for val in verbose_ping("8.8.8.8"):
            pass
        for val in verbose_ping("heise.de"):
            pass
        for val in verbose_ping("google.com"):
            pass

        # Inconsistent on Windows w/ ActivePython (Python 3.2 resolves
        # correctly to the local host, but 2.7 tries to resolve to the local
        # *gateway*)
        for val in verbose_ping("localhost"):
            pass

        # Should fail with 'getaddrinfo failed':
        for val in verbose_ping("foobar_url.fooobar"):
            pass

        # Should fail (timeout), but it depends on the local network:
        for val in verbose_ping("192.168.255.254"):
            pass

        # Should fails with 'The requested address is not valid in its context'
        for val in verbose_ping("0.0.0.0"):
            pass

        exit()

    parser = argparse.ArgumentParser(prog='python-ping',
                                     description='A pure python implementation\
                                      of the ping protocol. *REQUIRES ROOT*')
    parser.add_argument('address', help='The address to attempt to ping.')

    parser.add_argument('-t', '--timeout', help='The maximum amount of time to\
                         wait until ping timeout.', type=int, default=3000)

    parser.add_argument('-c', '--request_count', help='The number of attempts \
                        to make. See --infinite to attempt requests until \
                        stopped.', type=int, default=3)

    parser.add_argument('-i', '--infinite', help='Flag to continuously ping \
                        a host until stopped.', action='store_true')

    parser.add_argument('-I', '--ipv6', action='store_true', help='Flag to \
                        use IPv6.')

    parser.add_argument('-s', '--packet_size', type=int, help='Designate the\
                        amount of data to send per packet.', default=64)

    parser.add_argument('-T', '--test_case', action='store_true', help='Flag \
                        to run the default test case suite.')

    parsed = parser.parse_args()

    if parsed.infinite:
        sys.exit(list(verbose_ping(parsed.address, parsed.timeout,
                                   None, parsed.packet_size,
                                   ipv6=parsed.ipv6))[:-1])

    else:
        sys.exit(list(verbose_ping(parsed.address, parsed.timeout,
                                   parsed.request_count, parsed.packet_size,
                                   ipv6=parsed.ipv6))[:-1])
