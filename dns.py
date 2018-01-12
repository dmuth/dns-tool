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


def parseHeader(data):
	"""
	parseHeader(): Extracts the various fields of our header
	
	Returns a dictionary.
	"""

	retval = {}

	retval["request_id"] = binascii.hexlify(data[0:2])

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
	logger.debug("Header Flags: %s: %s %s" % (binascii.hexlify(data[2:4]), bin(ord(data[2])), bin(ord(data[3]))))

	retval["header"] = {}
	retval["header"]["qr"] = (ord(data[2]) & 0b10000000) >> 7
	retval["header"]["aa"] = (ord(data[2]) & 0b01111000) >> 3
	retval["header"]["rd"] = (ord(data[2]) & 0b00000001)
	retval["header"]["ra"] = (ord(data[3]) & 0b10000000) >> 7
	retval["header"]["z"]  = (ord(data[3]) & 0b01110000) >> 4
	retval["header"]["rcode"] = (ord(data[3]) & 0b00001111)
	
	
	retval["num_questions"] = binascii.hexlify(data[4:6])
	retval["num_answers"] = binascii.hexlify(data[6:8])
	retval["num_authority_records"] = binascii.hexlify(data[8:10])
	retval["num_additional_records"] = binascii.hexlify(data[10:12])

	return(retval)


#
# TODO: 
# Deconstruct Question section: put into a function for reusability with query
# Deconstruct answer section: also put into a function
# sendUdpMessage(): Return a data structure with some parsng
# Argument for query to pass in
# Look up code as per http://www.tcpipguide.com/free/t_DNSMessageHeaderandQuestionSectionFormat.htm
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

	header = parseHeader(data)
	logger.info("Header: %s" % header)


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


