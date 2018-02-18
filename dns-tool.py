#!/usr/bin/env python
#
# A script to send messages to DNS servers and parse the responses.
# Based off of the example at https://routley.io/tech/2017/12/28/hand-writing-dns-messages.html
#
# RFC 1035 was also helpful to me: https://tools.ietf.org/html/rfc1035#page-26
#


import binascii
import json
import logging
import math
import socket
import sys

import args
import create
import parse
import parse_answer
import parse_question
import output
import sanity


logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

args = args.parseArgs()


def getDnsMessage(args):
	"""
	getDnsMessage(args): Construct our DNS message to send
	"""

	header = create.createHeader(args)
	logger.debug(parse.parseHeader(header))

	question = create.createQuestion(args.query, args.query_type)
	logger.debug(parse_question.parseQuestion(0, question))

	retval = header + question

	return(retval)


def sendDnsMessage(args, message):
	"""
	sendDnsMessage(args, message): Send our DNS message and then return the result.
	"""

	retval = ""

	#
	# Otherwise, looks like we're sending an actual DNS query!
	#

	server_address = (args.server, 53)

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	sock.settimeout(3)

	try:
		logger.info("Sending query to %s:%s..." % (args.server, 53))
		sock.sendto(message, server_address)
		#sock.sendto(bytearray(message, "iso8859-1"), server_address)
		retval, _ = sock.recvfrom(4096)

	except socket.error as e:
		logger.error("Error connecting to %s:%s: %s" % (address, port, e))
		raise e

	finally:
		sock.close()

	return(retval)


def parseMessage(args, message):
	"""
	parseMessage(args, message): Parse our message and return a data structure of that.
	"""

	retval = {}

	if args.raw:
		# Source: https://stackoverflow.com/a/4849792/196073
		#sys.stdout.buffer.write(data) # Python 3

		# https://stackoverflow.com/a/2374443/196073
		for c in message:
			sys.stdout.write(c)
		sys.exit(0)

	request_id = parse.getRequestId(message)

	retval["server"] = args.server
	retval["header"] = parse.parseHeader(message[0:12])
	retval["question"] = parse_question.parseQuestion(12, message)

	#
	# Send us past the headers and question and parse the answer(s).
	#
	answer_index = 12 + retval["question"]["question_length"]
	retval["answers"] = parse_answer.parseAnswers(args, message, question_length = retval["question"]["question_length"])

	#
	# Do a sanity check on the results.
	#
	retval["sanity"] = sanity.go(retval["header"], retval["answers"], request_id)

	return(retval)


#
# If we're reading from standard input, do that right here.
#
if args.stdin:
	# Source: https://stackoverflow.com/a/38939320/196073
	#source = sys.stdin.buffer # Python 3
	source = sys.stdin
	message = source.read()

else:
	#
	# Get our DNS message to send if not reading from stdin
	#
	message = getDnsMessage(args)

	#
	# Send out the DNS message
	#
	message = sendDnsMessage(args, message)

#
# Parse our message that we got from the DNS server or stdin.
#
response = parseMessage(args, message)

#
# Print out the parsed response
#
output.printResponse(args, response)





