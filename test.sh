#!/bin/bash
# 
# This script runs tests again our DNS tool, but does so on an automated bassis.
#

# Errors are fatal
set -e

#set -x # Debugging

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
declare -a ANSWERS_MULTI=(
	"127.0.0.101 127.0.0.102 "
	"fe80:0000:0000:0000:0000:0000:0000:0002 fe80:0000:0000:0000:0000:0000:0000:0003 "
	"20 test2.dmuth.org 30 test3.dmuth.org "
	"ns-765.awsdns-31.net awsdns-hostmaster.amazon.com 1 7200 900 1209600 86400 "
	"ns-765.awsdns-31.net awsdns-hostmaster.amazon.com 1 7200 900 1209600 86400 "
	"ns.test.dmuth.org ns2.test.dmuth.org "
	)
declare -a ANSWERS_JSON_HASH=(
	"7570a3eb23f4b644f5949fdea5b07ed700bb0998"
	"d508d5afbca3760461ad99b6ad0d192bb4062b81"
	"54dbab68da9254d815d3040af20653c244459a06"
	"3c1d03d703ba98a8990a44f0a42d07134cc811cc"
	"5eb9204f9bb993ac59618d338e179fe5ddacecd9"
	"e8098cfd64fc8c7685c1f7e707631c2bb3ff7eb4"
	)
declare -a ANSWERS_TEXT_HASH=(
	"a3cb33d7ceb32db21dd810fdbc93d48bb0dd8838"
	"6b1797d07f8d83f16d3c64937790c52146235412"
	"d74db2a8613b50455600484a1dd750333cf6ad26"
	"d9c817d854862b8d862c1933ba289d840f2acc45"
	"687fd940e626bdd2fa088378a31f55f0cd6e2440"
	"d9287823b3ff1ab504ab6975bc42c589ef903254"
	)
declare -a ANSWERS_GRAPH_HASH=(
	"fe538a5673df8793e35cad16c0e3b65c34afd0ba"
	"76a48768d38d5000b5dc55735c9f0861e116655d"
	"31540cd538aaefd9c63673276ccb150acb212832"
	"173fd95f6c87664f86b06892edd6083e87aa937d"
	"75b4522bd83ecff88c611c11d56892221d07a101"
	"48e8a4e10552145fc87482d291477da4b7e543f6"
	)
declare -a ANSWERS_RAW_STDIN_HASH=(
	"a23c392135e9f074e79272715893dd8a417fd66d"
	"f8736fcb84897bc47f0a23eed522fea7605843d8"
	"6815ab31b46732493773d1b4e797b3d559d02e9c"
	"a70824c100d7a01e49febb8fa4fd1ca3e21c39d1"
	"077bdae1df7970082701ca950a6b849ab4eb07cb"
	"f88a2c5db98d170fa4efa15d58532542c144148e"
	)

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'


#
# Check our results against what was expected.
#
function test_result() {

	local QUERY=$1
	local RESULT=$2
	local EXPECTED=$3

	if test "$RESULT" == "$EXPECTED"
	then
		echo -e "   ${GREEN}[OK]${NC}    : result '${RESULT}' checks out for query '${QUERY}'"

	else
		echo -e "   ${RED}[ERROR]${NC} : result '${RESULT}' != '${EXPECTED}' for query '${QUERY}'"
		#exit 1 # Debugging

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
	QUERY2="${TYPE}2.test.dmuth.org"

	EXPECTED="${ANSWERS[$INDEX]}"
	EXPECTED_MULTI="${ANSWERS_MULTI[$INDEX]}"
	EXPECTED_JSON_HASH="${ANSWERS_JSON_HASH[$INDEX]}"
	EXPECTED_TEXT_HASH="${ANSWERS_TEXT_HASH[$INDEX]}"
	EXPECTED_GRAPH_HASH="${ANSWERS_GRAPH_HASH[$INDEX]}"
	EXPECTED_RAW_STDIN_HASH="${ANSWERS_RAW_STDIN_HASH[$INDEX]}"

	ARGS="-q --request-id 1 --fake-ttl"

	RESULT=$(./dns-tool.py ${ARGS} --query-type ${TYPE} --json ${QUERY} ${DNS_SERVER} | jq -r .answers[].rddata_text)
	test_result "$QUERY" "$RESULT" "$EXPECTED"

	#
	# Test against records that return multiple results.
	# Output is sorted and newlines are removed so that answers always the same oneliner.
	#
	# We can't do this for json, text, and graph because the order is not guaranteed.
	# (Maybe I can add an option for sorting in the future)
	#
	RESULT=$(./dns-tool.py ${ARGS} --query-type ${TYPE} --json ${QUERY2} ${DNS_SERVER} | jq -r .answers[].rddata_text |sort |tr "\n" " ")
	test_result "$QUERY" "$RESULT" "$EXPECTED_MULTI"


	RESULT=$(./dns-tool.py ${ARGS} --query-type ${TYPE} ${QUERY} ${DNS_SERVER} --json \
		| sha1sum | awk '{print $1}')
	test_result "$QUERY --json" "$RESULT" "$EXPECTED_JSON_HASH"


	RESULT=$(./dns-tool.py ${ARGS} --query-type ${TYPE} ${QUERY} ${DNS_SERVER} --text \
		| sha1sum | awk '{print $1}')
	test_result "$QUERY --text" "$RESULT" "$EXPECTED_TEXT_HASH"


	RESULT=$(./dns-tool.py ${ARGS} --query-type ${TYPE} ${QUERY} ${DNS_SERVER} --graph \
		| sha1sum | awk '{print $1}')
	test_result "$QUERY --graph" "$RESULT" "$EXPECTED_GRAPH_HASH"


	CMD_OUT="./dns-tool.py ${ARGS} --query-type ${TYPE} --raw ${QUERY} ${DNS_SERVER}"
	CMD_IN="./dns-tool.py -q --text --stdin "
	#echo "$CMD_OUT | $CMD_IN" # Debugging
	RESULT=$($CMD_OUT | $CMD_IN | sha1sum | awk '{print $1}')
	test_result "$QUERY --raw | --stdin --text" "$RESULT" "$EXPECTED_RAW_STDIN_HASH"

	INDEX=$((INDEX += 1))

done


#
# I have no idea if this value will change, so I'm doing this here, and checking plaintext 
# instead of messing with hashes.
#
RESULT=$(./dns-tool.py -q --fake-ttl --request-id 0000 --json testing.invalid | jq -r .answers[].rddata_text)
EXPECTED="a.root-servers.net nstld.verisign-grs.com 2018041701 1800 900 604800 86400"
test_result "bad-tld" "$RESULT" "$EXPECTED"




