#!/bin/bash
#
# @file dev-elevator.sh
# @brief uCodev Elastic Tools - Utilities
#        Retrieves the elevator assigned to a device support a specific fs path
#
# Date: 08/08/2015
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
# Date:   08/08/2015
#

# TODO: LVM not yet supported, but it's planned

if [ $# -ne 1 ]; then
	echo "Usage: ${0} <path>"
	exit 1
fi

DEV_RAW=`df ${1} | tail -n 1 | cut -d' ' -f1`
DEV_REAL=`readlink -e ${DEV_RAW}`
DEV_FINAL=""

if [ $? == 0 ]; then
	DEV_FINAL=`echo ${DEV_REAL} | awk -F '/' '{print $NF}' | sed 's/[0-9]*//g'`
else
	DEV_FINAL=`echo ${DEV_RAW} | awk -F '/' '{print $NF}' | sed 's/[0-9]*//g'`
fi

DEV_ELEVATOR=`cat /sys/block/${DEV_FINAL}/queue/scheduler`

echo $DEV_ELEVATOR | sed 's/.*\[\(.*\)\].*/\1/g'

exit 0

