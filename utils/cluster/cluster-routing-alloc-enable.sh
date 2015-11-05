#!/bin/bash
#
# @file cluster-routing-alloc-enable.sh
# @brief uCodev Elastic Tools - Utilities
#	 Enables routing allocation
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

if [ $? -ne 1 ]; then
	echo "Usage: $0 <host>"
	exit 1
fi

curl -XPUT http://${HOST}:9200/_settings -d '{
	"index.routing.allocation.disable_allocation" : false
}'

curl -XPUT http://${HOST}:9200/_cluster/settings -d '{
	"persistent" : {
			"cluster.routing.allocation.enable" : "all"
	}
}'

echo ""
