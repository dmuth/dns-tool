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

	question = response["question"]
	print("Question")
	print("========")
	print("   Question: %s (len: %s)" % (question["question"], question["question_length"]))
	print("   Type:     %d (%s)" % (question["qtype"], question["qtype_text"]))
	print("   Class:    %d (%s)" % (question["qclass"], question["qclass_text"]))

	print("")

	header = response["header"]
	text = header["header_text"]
	print("Header")
	print("======")
	print("   Request ID:         %s" % header["request_id"])
	print("   Questions:          %d" % int(header["num_questions"]))
	print("   Answers:            %d" % int(header["num_answers"]))
	print("   Authority records:  %d" % (int(header["num_authority_records"])))
	print("   Additional records: %d" % (int(header["num_additional_records"])))
    	print("   QR:     %s" % text["qr"])
	print("   AA:     %s" % text["aa"])
	print("   TC:     %s" % text["tc"])
	print("   RD:     %s" % text["rd"])
	print("   RA:     %s" % text["ra"])
	print("   OPCODE: %s" % text["opcode"])
	print("   RCODE:  %s" % text["rcode"])

	print("")

	answer = response["answer"]
	print("Answer")
	print("======")
	print("   Answer:     %s" % answer["rddata_text"])
	print("   QCLASS:     %s (%s)" % (answer["qclass"], answer["qclass_text"]))
	print("   QTYPE:      %s (%s)" % (answer["qtype"], answer["qtype_text"]))
	print("   TTL:        %s" % (answer["ttl"]))
	print("   Raw RRDATA: %s (len %s)" % (answer["rddata_hex"], answer["rdlength"]))
	print("   Full RRDATA: %s" % (answer["rddata"]))

	print("")

	sanity = response["sanity"]

	if not len(sanity):
		return

	print("Sanity Checks Failed")
	print("====================")
	for val in sanity:
		print("   %s" % val)

	print("")


