#!/usr/bin/python

# @file elastictools-shard-reassign.py
# @brief uCodev Elastic Tools
#        Elasticsearch shard reassigning tool.
#
# Date: 02/08/2015
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
# uCodev Elastic Tools v0.1
#
# Description: Elasticsearch analysis, report and handling tools.
#
# Author: Pedro A. Hortas
# Email:  pah@ucodev.org
# Date:   02/08/2015
#


import sys
import time

from elastictools import *

# Globals
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

ES_NODE_HOST = "localhost"
ES_NODE_PORT = "9200"
ES_REQ_WAIT_SECS = 1

# Class: Elasticsearch Shard
class UETReassign(ESShard):
	# SECTION: Handler
	def tool_reassign_shards(self):
		for count, shard in enumerate(filter(lambda s: (s[3] == "UNASSIGNED"), self.shard_data_list)):
			sys.stdout.write("    * Re-assigning shard '%s' of type '%s' from index '%s' to node '%s' on host '%s' (%s of %s)... " % (shard[1], shard[2], shard[0], self.shard_node_list[count % len(self.shard_node_list)], self.es_host, count + 1, self.shard_status_unassigned_count()))

			post_data = {
			    "commands" : [ {
			        "allocate" : {
				    "index"         : "%s" % shard[0],
			            "shard"         : "%s" % shard[1],
			            "node"          : "%s" % self.shard_node_list[count % len(self.shard_node_list)],
			            "allow_primary" : True
			        }
			    } ]
			}

			# Request cluster reroute op for the current unassigned shard
			res = self.es_request_http("POST", "/_cluster/reroute", post_data)

			# TODO: 400 is obviously an error, but is there more stuff to be handled here?
			if res["status"] == 400:
				print(res["error"])
				print("Failed.")
				continue

			print("Reassigned.")

			self.shard_stat_reassigned += 1
			
			time.sleep(ES_REQ_WAIT_SECS)

	def do(self):
		print("Loading shard status...")
		self.shard_status_load()
		print("Parsing shard data...")
		self.shard_status_parse()

		print("  * Number of shards started:      %s" % self.shard_status_started_count())
		print("  * Number of shards initializing: %s" % self.shard_status_initializing_count())
		print("  * Number of shards unassigned:   %s" % self.shard_status_unassigned_count())
		print("  * Total number of shards:        %s" % self.shard_status_total_count())

		# Re-assign shards if unassigned shards are present
		if self.shard_status_unassigned_count():
			print("Enabling routing allocation...")
			self.cluster_settings_set("cluster.routing.allocation.enable", "all")
			print("Reassigning unassigned shards...")
			self.tool_reassign_shards()

		# Check if there are shards in initializing state
		if self.shard_status_initializing_count():
			print("There are shards in initialization state. If the problem persists, restart the node.")

		print("\nSummary:")
		print("  * Reassigned shards: %d" % self.shard_stat_reassigned)
		print("  * Failed Reassigns:  %d" % self.shard_stat_failed_reassign)
		print("  * Moved shards:      %d" % self.shard_stat_moved)
		print("  * Failed moves:      %d" % self.shard_stat_failed_move)
		print("  * Total warnings:    %d" % self.warnings)
		print("  * Total errors:      %d" % self.errors)

		print("\nResetting data...")
		self.shard_reset_data_status()
		print("Loading shard status...")
		self.shard_status_load()
		print("Parsing shard data...")
		self.shard_status_parse()

		print("\nCurrent status:")
		print("  * Number of shards started:      %s" % self.shard_status_started_count())
		print("  * Number of shards initializing: %s" % self.shard_status_initializing_count())
		print("  * Number of shards unassigned:   %s" % self.shard_status_unassigned_count())
		print("  * Total number of shards:        %s" % self.shard_status_total_count())


		print("\nDone.")

# Class: Usage
class Usage:
	args = { 
		"target": None
	}

	def usage_show(self):
		print("Usage: %s <target filename OR url>" % (sys.argv[0]))

	def usage_check(self):
		if len(sys.argv) > 2:
			self.usage_show()
			sys.exit(EXIT_FAILURE)
		elif len(sys.argv) < 2:
			self.args["target"] = "http://%s:%s" % (ES_NODE_HOST, ES_NODE_PORT)

	def do(self):
		self.usage_check()

		if self.args["target"] == None:
			self.args["target"] = sys.argv[1]


class Main:
	def do(self):
		usage = Usage()
		usage.do()
		elastic = UETReassign(usage.args["target"])
		elastic.do()

## Entry Point
if __name__ == "__main__":
	Main().do()

