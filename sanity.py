#
# This module holds code to check the sanity on responses.
#


import logging


logger = logging.getLogger()


def get(data, request_id):
	"""
	get(result, request_id): Cheacks our result for general sanity.

	Returns a list of any issues it finds
	"""

	retval = []

	header = data["header"]

	#header["header"]["z"] = 2 # Debugging
	if header["header"]["z"] != 0:
		warning = "Content of Z field in header is not zero: %s" % header["header"]["z"]
		retval.append(warning)

	#request_id = "beef" # Debugging
	if header["request_id"] != request_id:
		warning = "Request ID on answer (%s) != request ID of question (%s)!" % (header["request_id"], request_id)
		retval.append(warning)

	#header["header"]["opcode"] = 14 # Debugging
	if header["header"]["opcode"] > 2:
		warning = "OPCODE > 2 reserved for future use! (Qtype = %s)" % header["header"]["opcode"]
		retval.append(warning)

	#header["header"]["rcode"] = 77 # Debugging
	if header["header"]["rcode"] > 5:
		warning = "Invalid RCODE (%s)" % header["header"]["rcode"]
		retval.append(warning)
		
	#data["answer"]["qclass"] = 0 # Debugging
	if data["answer"]["qclass"] < 1:
		warning = "QCLASS in answer is < 1 (%s)" % data["answer"]["qclass"]
		retval.append(warning)

	#data["answer"]["qclass"] = 123 # Debugging
	if data["answer"]["qclass"] > 4:
		warning = "QCLASS in answer is > 4 (%s)" % data["answer"]["qclass"]

	#data["answer"]["qtype"] = 123 # Debugging
	if data["answer"]["qtype"] > 16:
		warning = "QTYPE in answer is > 16 (%s)" % data["answer"]["qtype"]
		retval.append(warning)

	return(retval)


