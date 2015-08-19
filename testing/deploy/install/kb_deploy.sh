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


PREFIX="${1}"
KB_VER="4.1.1-linux-x64"

mkdir -p /opt/${PREFIX}-elk-solution-v1.0
ln -s /opt/${PREFIX}-elk-solution-v1.0 /opt/elk-solution
cd /opt/elk-solution
wget https://download.elastic.co/kibana/kibana/kibana-${KB_VER}.tar.gz
groupadd kibana
useradd kibana -g kibana
tar zxvf kibana-${KB_VER}.tar.gz
rm -f *.gz
chown -R kibana:kibana kibana*
ln -s /opt/elk-solution/kibana-${KB_VER} /opt/elk-solution/kibana
mkdir -p /opt/elk-solution/config

