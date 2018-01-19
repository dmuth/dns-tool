#
# This module holds our code for printing out our responses.
#


import json
import logging


logger = logging.getLogger()


def printResponse(args, response):
	"""
	printResponse(args, response): Print up our response in 1 or more formats.
	"""

	#print(formatHex(response)) # Debugging
	#print(response)
	if args.json:
		print(json.dumps(response))

	if args.json_pretty_print:
		print(json.dumps(response, indent = 2))

	if args.text:
		printResponseText(response)


def printResponseText(response):
	"""
	printResponseText(response): Print up our response as text.
	"""

	sanity = response["sanity"]

	question = response["question"]
	print("Question")
	print("========")
	print("   Question: %s (len: %s)" % (question["question"], question["question_length"]))
	print("   Type:     %d (%s)" % (question["qtype"], question["qtype_text"]))
	print("   Class:    %d (%s)" % (question["qclass"], question["qclass_text"]))

	print("")

	printHeader(response["header"], sanity["header"])

	print("")

	printAnswers(response["answers"], sanity["answers"])

	print("")


def printHeader(header, sanity):
	"""
	printHeader(header): Print up our headers
	"""

	text = header["header_text"]
	print("Header")
	print("======")
	print("   Request ID:         %s" % header["request_id"])
	print("   Questions:          %d" % int(header["num_questions"]))
	print("   Answers:            %d" % int(header["num_answers"]))
	print("   Authority records:  %d" % (int(header["num_authority_records"])))
	print("   Additional records: %d" % (int(header["num_additional_records"])))
	print("   QR:      %s" % text["qr"])
	print("   AA:      %s" % text["aa"])
	print("   TC:      %s" % text["tc"])
	print("   RD:      %s" % text["rd"])
	print("   RA:      %s" % text["ra"])
	print("   OPCODE:  %s" % text["opcode"])
	print("   RCODE:   %s" % text["rcode"])

	if len(sanity):
		for warning in sanity:
			print("   WARNING: %s" % warning)


def printAnswers(answers, sanity):

	print("Answers")
	print("=======")

	index = 0
	for answer in answers:

		headers = answer["headers"]

		print("   Answer #%d:   %s" % (index, answer["rddata_text"]))
		print("   QCLASS:      %s (%s)" % (headers["qclass"], headers["qclass_text"]))
		print("   QTYPE:       %s (%s)" % (headers["qtype"], headers["qtype_text"]))
		print("   TTL:         %s" % (headers["ttl"]))
		print("   Raw RRDATA:  %s (len %s)" % (answer["rddata_hex"], headers["rdlength"]))
		print("   Full RRDATA: %s" % (answer["rddata"]))

		sanity_answer = sanity[index]
		if len(sanity_answer):
			for warning in sanity_answer:
				print("   WARNING:     %s" % warning)

		index += 1
		print("")


