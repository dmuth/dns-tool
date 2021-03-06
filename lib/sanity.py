#
# This module holds code to check the sanity on responses.
#


import logging


logger = logging.getLogger()


def go(header, answers, request_id):
	"""
	go(header, answer, request_id): Do sanity checks on our result.  Anything that is an issue is returned in an array.
	"""

	retval = {}

	retval["header"] = checkHeader(header, request_id)
	retval["answers"] = checkAnswers(answers)

	return(retval)


def checkHeader(header, request_id):
	"""
	checkHeader(header, request_id): Check our header for sanity
	"""

	retval = []

	#header["header"]["z"] = 2 # Debugging
	if header["header"]["z"] != 0:
		warning = "Content of Z field in header is not zero: %s" % header["header"]["z"]
		retval.append(warning)

	#request_id = b"beef" # Debugging
	request_id_text = request_id.decode("utf-8")

	if header["request_id"] != request_id_text:
		warning = "Request ID on answer (%s) != request ID of question (%s)!" % (header["request_id"], request_id_text)
		retval.append(warning)

	#header["header"]["opcode"] = 14 # Debugging
	if header["header"]["opcode"] > 2:
		warning = "OPCODE > 2 reserved for future use! (Qtype = %s)" % header["header"]["opcode"]
		retval.append(warning)

	#header["header"]["rcode"] = 77 # Debugging
	if header["header"]["rcode"] > 5:
		warning = "Invalid RCODE (%s)" % header["header"]["rcode"]
		retval.append(warning)
		
	return(retval)


def checkAnswers(answers):
	"""
	checkAnswers(answers): Check our answers.  This is an array that is returned (even if empty) in the same order as the actual answers.
	"""

	retval = []

	for answer in answers:

		sanity = answer["sanity"]
		headers = answer["headers"]

		#headers["class"] = 0 # Debugging
		if headers["class"] < 1:
			warning = "QCLASS in answer is < 1 (%s)" % headers["class"]
			sanity.append(warning)

		#headers["class"] = 123 # Debugging
		if headers["class"] > 4:
			warning = "QCLASS in answer is > 4 (%s)" % headers["class"]
			sanity.append(warning)

		retval.append(sanity)

	return(retval)



