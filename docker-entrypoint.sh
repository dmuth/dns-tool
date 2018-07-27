#!/bin/sh
#
# This script is run when the countainer is started.
#

# Errors are fatal
set -e

echo "# "
echo "# The dns-tool app has been installed and can be run by typing 'dns-tool'."
echo "# "
echo "# If you want to do any development, just cd into /mnt/ and you can run dns-tool from there."
echo "# "

#
# Run whatever was passed in
#
exec /app/dns-tool $@

