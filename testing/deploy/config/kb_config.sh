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


# FIXME and TODO: Service initialization should not reside on rc.local
cat /etc/rc.local | sed -e 's/exit\ 0//g' > /tmp/rc.local.kb
cat system/rc.local.kb >> /tmp/rc.local.kb
echo "exit 0" >> /tmp/rc.local.kb
mv /etc/rc.local /etc/rc.local-$(date +%s)
mv /tmp/rc.local.kb /etc/rc.local
chown root:root /etc/rc.local
chmod 755 /etc/rc.local
sleep 1

cp elk/kibana.yml /opt/elk-solution/kibana/config/

