#!/usr/bin/env python
#
# A script to send messages to DNS servers and parse the responses.
# Based off of the example at https://routley.io/tech/2017/12/28/hand-writing-dns-messages.html
#
# RFC 1035 was also helpful to me: https://tools.ietf.org/html/rfc1035#page-26
#


import argparse
import binascii
import json
import logging
import math
import socket

import create
import parse
import output
import sanity


logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#
# Parse our arguments.
#
parser = argparse.ArgumentParser(description = "Make DNS queries and tear apart the result packets")
parser.add_argument("query", help = "String to query for (e.g. \"google.com\")")
parser.add_argument("server", nargs = "?", default = "8.8.8.8", help = "DNS server (default: 8.8.8.8)")
parser.add_argument("--query-type", default = "a", help = "Query type (A, CNAME, MX, etc.)")
parser.add_argument("--json", action = "store_true", help = "Output response as JSON")
parser.add_argument("--json-pretty-print", action = "store_true", help = "Output response as JSON Pretty-printed")
parser.add_argument("--text", action = "store_true", help = "Output response as formatted text")
parser.add_argument("--debug", "-d", action = "store_true", help = "Enable debugging")
#parser.add_argument("file", nargs="?", help = "JSON file to write (default: output.json)", default = "output.json")
#parser.add_argument("--filter", help = "Filename text to filter on")

args = parser.parse_args()
logger.info("Args: %s" % args)

if args.debug:
	logger.setLevel(logging.DEBUG)


def sendUdpMessage(message, address, port):
	"""sendUdpMessage(message, address, port): sends a message to UDP server

	message can be a raw string
	"""
    
	retval = {}

	server_address = (address, port)

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	#
	# Set our timeout
	#
	sock.settimeout(3)

	try:
		logger.info("Sending query to %s:%s..." % (address, port))
		sock.sendto(message, server_address)
		data, _ = sock.recvfrom(4096)

		request_id = parse.getRequestId(message)

		retval["header"] = parse.parseHeader(data[0:12])
		retval["question"] = parse.parseQuestion(data[12:])

		answer_index = 12 + retval["question"]["question_length"]
		retval["answer"] = parse.parseAnswer(data[answer_index:])

		retval["raw"] = binascii.hexlify(data).decode("utf-8")

		retval["sanity"] = sanity.get(retval, request_id)

	except socket.error as e:
		logger.error("Error connecting to %s:%s: %s" % (address, port, e))
		raise e

	finally:
		sock.close()

	return(retval)


def formatHex(hex):
	"""formatHex returns a pretty version of a hex string"""
	octets = [hex[i:i+2] for i in range(0, len(hex), 2)]
	pairs = [" ".join(octets[i:i+2]) for i in range(0, len(octets), 2)]
	return "\n".join(pairs)


header = create.createHeader()
logger.debug(parse.parseHeader(header))

question = create.createQuestion(args.query, args.query_type)
logger.debug(parse.parseQuestion(question))

message = header + question

response = sendUdpMessage(message, args.server, 53)

output.printResponse(args, response)





