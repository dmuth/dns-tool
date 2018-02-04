#!/bin/bash
# 
# This script runs tests again our DNS tool, but does so on an automated bassis.
#

# Errors are fatal
set -e


#
# Our query types to run
#
declare -a QUERY_TYPES=("a" "aaaa" "mx" "soa" "cname" "ns")

#
# The answers we are expecting.
#
declare -a ANSWERS=(
	"127.0.0.100"
	"fe80:0000:0000:0000:0000:0000:0000:0001"
	"10 test.dmuth.org"
	"ns-765.awsdns-31.net awsdns-hostmaster.amazon.com 1 7200 900 1209600 86400"
	"a.test.dmuth.org"
	#"BADns.test.dmuth.org" # Debugging
	"ns.test.dmuth.org"
	)

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'


#
# Check our results against what was expected.
#
function test_result() {

	QUERY=$1
	RESULT=$2
	EXPECTED=$3

	if test "$RESULT" == "$EXPECTED"
	then
		echo -e "   ${GREEN}[OK]${NC}    : result '${RESULT}' == '${EXPECTED}' for query '${QUERY}'"

	else
		echo -e "   ${RED}[ERROR]${NC} : result '${RESULT}' != '${EXPECTED}' for query '${QUERY}'"
		exit 1

	fi

} # End of test_result()


#
# Loop through our query types, run a query for each test record, 
# and compare the results!
#
INDEX=0
for TYPE in ${QUERY_TYPES[@]}
do

	DNS_SERVER=""

	if test "$TYPE" == "ns"
	then
		DNS_SERVER="ns-49.awsdns-06.com"
	fi

	QUERY="${TYPE}.test.dmuth.org"
	EXPECTED="${ANSWERS[$INDEX]}"
	
	RESULT=$(./dns-tool.py -q --query-type ${TYPE} --json ${QUERY} ${DNS_SERVER} | jq -r .answers[].rddata_text)

	test_result "$QUERY" "$RESULT" "$EXPECTED"

	INDEX=$((INDEX += 1))

done




