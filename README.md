

<img src="./img/networking.svg" width="250" align="right" />

# DNS Tool

This is a DNS tool I wrote, based off [example code I found here](https://routley.io/tech/2017/12/28/hand-writing-dns-messages.html).
It creates DNS packets from scratch and sends the queries to a DNS server.

It is a work in progress, and will be updated.


## Features

- Output in text, JSON, and pretty-printed JSON
- Debugging support with Python's builtin logger app
- Sanity Checking module which reports on any inconsistencies it finds in the response.


## Requirements

- Python 2.x
- A desire to learn more about how the Internet works


## Usage

```
$ ./dns-tool.py google.com --text
usage: dns-tool.py [-h] [--query-type QUERY_TYPE] [--json]
                   [--json-pretty-print] [--text] [--debug] [--quiet]
                   query [server]

Make DNS queries and tear apart the result packets

positional arguments:
  query                 String to query for (e.g. "google.com")
  server                DNS server (default: 8.8.8.8)

optional arguments:
  -h, --help            show this help message and exit
  --query-type QUERY_TYPE
                        Query type (Supported types: A, AAAA, CNAME, MX, SOA,
                        NS)
  --json                Output response as JSON
  --json-pretty-print   Output response as JSON Pretty-printed
  --text                Output response as formatted text
  --debug, -d           Enable debugging
  --quiet, -q           Quiet mode--only log errors
```


## Sample Run

Let's run a query for google.com:

```
$ ./dns-tool.py google.com --text 
Question
========
   Question: google.com (len: 16)
   Type:     1 (A (Address))
   Class:    1 (IN)
   Server:   8.8.8.8:53

Header
======
   Request ID:         1aab
   Questions:          1
   Answers:            1
   Authority records:  0
   Additional records: 0
   QR:      Response
   AA:      Server isn't an authority
   TC:      Message not truncated
   RD:      Recursion requested
   RA:      Recursion available!
   OPCODE:  0 - Standard query
   RCODE:   0 - No errors reported

Answers
=======
   Answer #0:   172.217.7.238
   CLASS:       1 (IN)
   TYPE:        1 (A (Address))
   TTL:         154
   Raw RRDATA:  c0 0c 00 01 00 01 00 00 00 9a 00 04 ac d9 07 ee (len 4)
   Full RRDATA: {'ip': '172.217.7.238'}
```


## Sanity Checking

This app also supports sanity checking on responses it gets from DNS servers.
If something is off (usage of a reserved field, etc.), the app will let you know.
Here is sample output from a run with `--text`:

```
Answer
======
   Answer:     172.217.15.110
   QCLASS:     123 (IN)
   QTYPE:      123 (A (Address))
   TTL:        216
   Raw RRDATA: acd90f6e (len 4)

Sanity Checks Failed
====================
   Content of Z field in header is not zero: 2
   Request ID on answer (aaaa) != request ID of question (beef)!
   OPCODE > 2 reserved for future use! (Qtype = 14)
   Invalid RCODE (77)
   QCLASS in answer is < 1 (0)
```


## Module Architecture

- `create.py`: Functions for creating the DNS request
- `output.py`: Functions for printing out the answer to a DNS query
- `parse.py`: Functions to parse the the header
- `parse_answer.py`: Functions to parse the answer headers
- `parse_answer_body.py`: Parse the Resource Records (RR)
- `parse_question.py`: Parse the question
- `sanity.py`: Functions to perform sanity checks on answer


## Testing

There is a wrapper script called `test.sh` which can be used to test against a record
in the zone `test.dmuth.org`.  I have a series of test DNS records set up there that are
guaranteed to return speific results.

To test everything that the tool currently knows about:
`./test.sh a mx soa cname ns --multiple  |jq .answers[].rddata_text`


## TODO List

- Store raw packets to disk with `--raw` and read them with `--stdin`
- BUG: Doing a query for `foobar` returns a payload with a different offset.
- Put this entire app into a Pip package
- Make this run in Python 3 like a civilized application.
- Handle RDNS queries/responses
- Unit testing for parsing functions
- Docker container to run a custom DNS server
- Docker containers to run different DNS servers and verify behavior across different DNS server software


## Further Reading

- https://routley.io/tech/2017/12/28/hand-writing-dns-messages.html
- http://www.tcpipguide.com/free/t_DNSMessageHeaderandQuestionSectionFormat.htm
- https://tools.ietf.org/html/rfc1035


## Development

At the moment, this is written in Python 2.7, so you'll need to install Virtualenv to point 
to your copy of Python 2.7:

```
virtualenv --python=$(which python2.7) virtualenv
. ./virtualenv/bin/activate
pip install -r ./requirements.txt
```




## Credits

- Icon made by <a href="https://www.flaticon.com/authors/gregor-cresnar" title="Gregor Cresnar">Gregor Cresnar</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a> is licensed by <a href="http://creativecommons.org/licenses/by/3.0/" title="Creative Commons BY 3.0" target="_blank">CC 3.0 BY</a>.


## Contact

If you see anything wrong, or anything you'd like add, feel free to open an issue.
You can also find me on [Twitter](http://twitter.com/dmuth) and [Facebook](http://www.facebook.com/dmuth).


