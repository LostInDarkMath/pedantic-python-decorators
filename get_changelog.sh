#!/bin/bash

SEARCH_TERM="## Pedantic"
# get line number of latest Release Header
FROM=$(
# get lines with the string <## Pedantic> in it (Header lines) together with line numbers
grep "${SEARCH_TERM}" CHANGELOG.md --line-number |
  # only take the first occurrence
  head -n 1 |
  # only keep the line numbers
  sed 's/\(.*\):.*/\1/'
)

# get line number of second latest Release Header
TO=$(
# same as above
grep "${SEARCH_TERM}" CHANGELOG.md --line-number |
  # take the last of the first two lines
  head -n 2 |
  tail -n 1 |
  # same as above
  sed 's/\(.*\):.*/\1/'
)

echo "Take lines ${FROM} - ${TO}"

export RELEASE_BODY=$(
# take content from changelog
cat CHANGELOG.md |
  # take from [0, TO - 1] (-1 to exclude second latest release header)
  head -n $((TO - 1)) |
  # take the last TO - 1 - FROM lines to get the content of the latest release
  # this cuts away the first few lines before the latest release header
  tail -n $((TO - FROM - 1))
)

export RELEASE_NAME=$(
# same as above
cat CHANGELOG.md |
  head -n $((TO - 1)) |
  # throw away the body and only keep the header
  tail -n $((TO - FROM)) |
  head -n 1 |
    sed 's/## //'  # remove leading hashtags
)

echo "Found Release Details:"
echo ""
echo "${RELEASE_NAME}"
echo ""
echo "${RELEASE_BODY}"

export RELEASE_BODY_NO_LINE_BREAKS=echo ${RELEASE_BODY} | tr '\n' ' '
