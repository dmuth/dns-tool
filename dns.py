#!/usr/bin/env python
#
# A script to send messages to DNS servers and parse the responses.
# Based off of the example at https://routley.io/tech/2017/12/28/hand-writing-dns-messages.html
#


import argparse
import binascii
import logging
import socket


logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s')
logger = logging.getLogger()

#
# Parse our arguments.
#
parser = argparse.ArgumentParser(description = "Make DNS queries and tear apart the result packets")
#parser.add_argument("bucket")
#parser.add_argument("file", nargs="?", help = "JSON file to write (default: output.json)", default = "output.json")
#parser.add_argument("--filter", help = "Filename text to filter on")

args = parser.parse_args()
logger.info("Args: %s" % args)
logger.setLevel(logging.DEBUG)


#
# TODO: 
# sendUdpMessage(): Return a data structure with some parsng
# Argument for query to pass in
# Look up code as per http://www.tcpipguide.com/free/t_DNSMessageHeaderandQuestionSectionFormat.htm
# Deconstruct Question section: put into a function for reusability with query
#

def sendUdpMessage(message, address, port):
    """sendUdpMessage sends a message to UDP server

    message should be a hexadecimal encoded string
    """
    message = message.replace(" ", "").replace("\n", "")
    server_address = (address, port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(binascii.unhexlify(message), server_address)
        data, _ = sock.recvfrom(4096)

	logger.info("answer(): Request ID: %s" % binascii.hexlify(data[0:2]))
	logger.info("answer(): Flags: %s" % binascii.hexlify(data[2:4]))
	#
	# Header flag bits:
	#
	# 0 - QR: 0 if query, 1 if answer
	# 1-4 - Opcode: 0 is standard query, 1 is reverse query, 2 is server status request
	# 5 - AA: Is the answer authoritative?
	# 6 - TC: Has the message been truncated?
	# 7 - RD: Set to 1 when recursion is desired
	# 8 - RA: Is Recursion available on this DNS server?
	# 9-11 - Z: These reserved bits are always set to zero.
	# 12-15 - RCODE: Result Code.  0 for no errors.
	#
	logger.debug("Header flag bits: %s %s" % (bin(ord(data[2])), bin(ord(data[3]))))

	qr = (ord(data[2]) & 0b10000000) >> 7
	aa = (ord(data[2]) & 0b01111000) >> 3
	rd = (ord(data[2]) & 0b00000001)
	ra = (ord(data[3]) & 0b10000000) >> 7
	z  = (ord(data[3]) & 0b01110000) >> 4
	rcode = (ord(data[3]) & 0b00001111)
	
	logger.info("Header: QR: %s AA: %s RD: %s RA: %s Z: %s RCODE: %s" % (
		binascii.hexlify(chr(qr)), 
		binascii.hexlify(chr(aa)), 
		binascii.hexlify(chr(rd)), 
		binascii.hexlify(chr(ra)), 
		binascii.hexlify(chr(z)), 
		binascii.hexlify(chr(rcode))
		))
	
	logger.info("answer(): Number of questions: %s" % binascii.hexlify(data[4:6]))
	logger.info("answer(): Number of answers: %s" % binascii.hexlify(data[6:8]))
	logger.info("answer(): Number of authority records: %s" % binascii.hexlify(data[8:10]))
	logger.info("answer(): Number of additional records: %s" % binascii.hexlify(data[10:12]))

    finally:
        sock.close()

    return binascii.hexlify(data).decode("utf-8")


def formatHex(hex):
    """formatHex returns a pretty version of a hex string"""
    octets = [hex[i:i+2] for i in range(0, len(hex), 2)]
    pairs = [" ".join(octets[i:i+2]) for i in range(0, len(octets), 2)]
    return "\n".join(pairs)


message = "AA AA 01 00 00 01 00 00 00 00 00 00 " \
"07 65 78 61 6d 70 6c 65 03 63 6f 6d 00 00 01 00 01"

response = sendUdpMessage(message, "8.8.8.8", 53)
print(formatHex(response))


