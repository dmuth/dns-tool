#!/bin/sh
#
# This script is run when the countainer is started.
#

# Errors are fatal
set -e

#
# Run whatever was passed in
#
exec /app/dns-tool $@

