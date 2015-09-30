#!/bin/bash
#
# @file del-snapshot.sh
# @brief uCodev Elastic Tools - Utilities
#	 Deletes an existing snapshot
#
# Date: 30/09/2015
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
# Date:   19/08/2015
#

if [ $# -lt 3 ]; then
	echo "Usage: ${0} <host> <snapshot_repo_name> <snapshot_name>"
	exit 1
fi

HOST=${1}
SNAPSHOT_REPO=${2}
SNAPSHOT_NAME=${3}

curl -XDELETE "http://${HOST}:9200/_snapshot/${SNAPSHOT_REPO}/${SNAPSHOT_NAME}"

echo ""

exit 0

