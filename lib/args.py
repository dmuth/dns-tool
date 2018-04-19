#
# This module handles argument parsing
#

import argparse
import logging

logger = logging.getLogger()


def parseArgs():
	"""
	parseArgs(): Parse our arguments and return an object with the parsed arguments
	"""

	#
	# Parse our arguments.
	#
	parser = argparse.ArgumentParser(description = "Make DNS queries and tear apart the result packets")
	#parser.add_argument("query", help = "String to query for (e.g. \"google.com\")")
	parser.add_argument("query", nargs = "?", help = "String to query for (e.g. \"google.com\")")
	parser.add_argument("server", nargs = "?", default = "8.8.8.8", help = "DNS server (default: 8.8.8.8)")
	parser.add_argument("--query-type", default = "a", help = "Query type (Supported types: A, AAAA, CNAME, MX, SOA, NS) Defalt: a")
	parser.add_argument("--request-id", default = "", help = "Hex value for a request ID (default: random)")
	parser.add_argument("--json", action = "store_true", help = "Output response as JSON")
	parser.add_argument("--json-pretty-print", action = "store_true", help = "Output response as JSON Pretty-printed")
	parser.add_argument("--text", action = "store_true", help = "Output response as formatted text")
	parser.add_argument("--graph", action = "store_true", help = "Output response as ASCII graph of DNS response packet")
	parser.add_argument("--raw", action = "store_true", help = "Output raw DNS packet and immediately exit")
	parser.add_argument("--stdin", action = "store_true", help = "Instead of making DNS query, read packet from stdin. (works great with --raw!)")
	parser.add_argument("--fake-ttl", action = "store_true", help = "Set a fake TTL, for use in test scripts where hashes are made of the output")
	parser.add_argument("--debug", "-d", action = "store_true", help = "Enable debugging")
	parser.add_argument("--quiet", "-q", action = "store_true", help = "Quiet mode--only log errors")
	#parser.add_argument("file", nargs="?", help = "JSON file to write (default: output.json)", default = "output.json")
	#parser.add_argument("--filter", help = "Filename text to filter on")

	args = parser.parse_args()

	#
	# Don't require a query when --raw is used.
	#
	if not args.stdin:
		if not args.query:
			parser.error("A query is needed when --raw is not being used.")
			parse.print_help()

	#
	# Can't use --json or any other output formatter with --raw.
	#
	if args.raw:

		if args.json:
			parser.error("Cannot use --json with --raw")
			parse.print_help()

		if args.text:
			parser.error("Cannot use --text with --raw")
			parse.print_help()

		if args.graph:
			parser.error("Cannot use --graph with --raw")
			parse.print_help()


	#
	# Set our debugging level.
	#
	if args.debug:
		logger.setLevel(logging.DEBUG)

	elif args.quiet:
		logger.setLevel(logging.ERROR)

	logger.info("Args: %s" % args)

	return(args)



