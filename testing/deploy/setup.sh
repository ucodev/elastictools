#!/bin/bash
#
#
# uCodev ELK Deployment Scripts v0.01
#
# Date: 19/08/2015
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


if [ ${#} -ne 2 ]; then
	echo "Usage: ${0} <module> <prefix>"
	echo ""
	echo "   module - ES, LS, KB or ELK"
	echo "   prefix - A single descriptive word (eg: acronym of the organization)"
	echo ""
	exit 1;
fi

if [ ${1} = "ES" ]; then
	echo "Deploying elasticsearch (salve)..."
	./install/deps.sh
	./install/es_deploy.sh ${2}
	cd config && ./es_config_slave.sh && cd ..
elif [ ${1} = "LS" ]; then
	echo "Deploying logstash..."
	./install/deps.sh
	./install/ls_deploy.sh ${2}
	cd config && ./ls_config.sh && cd ..
elif [ ${1} = "KB" ]; then
	echo "Deploying kibana..."
	./install/deps.sh
	./install/kb_deploy.sh ${2}
	cd config && ./kb_config.sh && cd ..
elif [ ${1} = "ELK" ]; then
	echo "Deploying ELK..."
	./install/deps.sh
	./install/es_deploy.sh ${2}
	cd config && ./es_config_master.sh && cd ..
	./install/ls_deploy.sh ${2}
	cd config && ./ls_config.sh && cd ..
	./install/kb_deploy.sh ${2}
	cd config && ./kb_config.sh && cd ..
	echo "Done."
fi

