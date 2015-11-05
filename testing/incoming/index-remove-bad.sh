#!/bin/bash
#
# @file index-remove-bad.sh
# @brief uCodev Elastic Tools - Utilities
#        Removes elasticsearch indices that curator cannot read or cure
#
# Date: 05/11/2015
#
#   Copyright 2015  Pedro A. Hortas (pah@ucodev.org)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#
# uCodev Elastic Tools v0.1 - Utilities
#
# Description: Elasticsearch analysis, report and handling tools.
#
# Author: Pedro A. Hortas
# Email:  pah@ucodev.org
# Date:   05/11/2015
#

CURATOR_BIN=/usr/local/bin/curator

if [ $# -ne 1 ]; then
	echo "Usage: $0 <host>"
	exit 1
fi

HOST=$1

while [ ${PROCEED} -eq 1 ]; do
	KEY_ERROR=`${CURATOR_BIN} --host ${HOST} optimize indices --all-indices 2>&1 | tail -n 1 | grep KeyError | cut -d\' -f2`
	BAD_INDEX=""

	if [ ! -z ${KEY_ERROR} ]; then
		BAD_INDEX=$(echo ${KEY_ERROR} | cut -d\' -f2)
		if [ ! -z ${BAD_INDEX} ]; then
			echo -n "Deleting bad index ${BAD_INDEX}... "
			curl -XDELETE http://${HOST}:9200/${BAD_INDEX}
			echo ""
			continue
		else
			echo "Unable to extract bad index."
			exit 1
		fi
	fi

	# Everything is good
	break
done

echo "Done"

