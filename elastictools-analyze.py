#!/usr/bin/python

# @file elastictools-analyze.py
# @brief uCodev Elastic Tools
#        Status analyzer and reporting tool for Elasticsearch clusters.
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
class UETAnalyze(ESShard):
	cluster_data = {}
	node_data = {}
	index_data = {}
	shard_data = {}

	index_data_list = {}

	def tool_analyze_init(self):
		# Shard
		self.shard_status_load()
		self.shard_status_parse()

		self.shard_data["list"] = self.shard_data_list

		self.shard_data["started_count"] = self.shard_status_started_count()
		self.shard_data["initializing_count"] = self.shard_status_initializing_count()
		self.shard_data["unassigned_count"] = self.shard_status_unassigned_count()
		self.shard_data["total_count"] = self.shard_status_total_count()

		# Cluster
		cluster_health = self.cluster_get_health()

		self.cluster_data["status"] = cluster_health["status"]
		self.cluster_data["name"] = cluster_health["cluster_name"]
		self.cluster_data["number_of_nodes"] = cluster_health["number_of_nodes"]
		self.cluster_data["number_of_data_nodes"] = cluster_health["number_of_data_nodes"]
		self.cluster_data["active_shards"] = cluster_health["active_shards"]
		self.cluster_data["active_primary_shards"] = cluster_health["active_primary_shards"]
		self.cluster_data["relocating_shards"] = cluster_health["relocating_shards"]
		self.cluster_data["initializing_shards"] = cluster_health["initializing_shards"]
		self.cluster_data["unassigned_shards"] = cluster_health["unassigned_shards"]
		self.cluster_data["indices"] = cluster_health["indices"]
		self.cluster_data["state"] = self.cluster_get_state()

		# Node
		self.node_data["total_count"] = self.node_get_count()
		self.node_data["data_count"] = cluster_health["number_of_data_nodes"]
		self.node_data["list"] = self.node_get_list()
		self.node_data["map"] = self.node_get_map()
		self.node_data["client_list"] = self.node_get_list_client()
		self.node_data["data_list"] = self.node_get_list_data()
	
		# Index
		self.index_data["list"] = { }
		self.index_data["total_green"] = 0
		self.index_data["total_yellow"] = 0
		self.index_data["total_red"] = 0
		self.index_data["total_primary"] = 0
		self.index_data["total_replica"] = 0
		self.index_data["total_size"] = 0
		self.index_data["total_docs_count"] = 0
		self.index_data["total_docs_deleted"] = 0
		self.index_data["total_search_query"] = 0
		self.index_data["zero_search_query"] = 0
		self.index_data["total_search_time"] = 0
		self.index_data["zero_search_time"] = 0
		self.index_data["max_search_query"] = [ None, 0 ]
		self.index_data["min_search_query"] = [ None, 1152921504606846976 ]
		self.index_data["max_search_time"] = [ None, 0 ]
		self.index_data["min_search_time"] = [ None, 1152921504606846976 ]
		self.index_data["max_docs"] = [ None, 0 ]
		self.index_data["min_docs"] = [ None, 1152921504606846976 ]
		self.index_data["max_size"] = [ None, 0 ]
		self.index_data["min_size"] = [ None, 1152921504606846976 ] # 1 EB seems fine
		self.index_data["initializing_primary_count"] = 0
		self.index_data["initializing_replica_count"] = 0
		self.index_data["unassigned_primary_count"] = 0
		self.index_data["unassigned_replica_count"] = 0
		self.index_data["started_primary_count"] = 0
		self.index_data["started_replica_count"] = 0

		for shard in self.shard_data["list"]:
			# shard[0] -> index
			# shard[1] -> id
			# shard[2] -> level
			# shard[3] -> state
			# shard[4] -> ndocs
			# shard[5] -> size
			# shard[6] -> host
			# shard[7] -> node

			if shard[0] not in self.index_data["list"]:
				self.index_data["list"][shard[0]] = { }
				self.index_data["list"][shard[0]]["primary_count"] = 0
				self.index_data["list"][shard[0]]["replica_count"] = 0
				self.index_data["list"][shard[0]]["size"] = None
				self.index_data["list"][shard[0]]["docs_count"] = None
				self.index_data["list"][shard[0]]["docs_deleted"] = None

			self.index_data["list"][shard[0]]["primary_count"] += int(shard[2] == "p")
			self.index_data["list"][shard[0]]["replica_count"] += int(shard[2] == "r")

			if shard[3] == "INITIALIZING" and shard[2] == "p":
				self.index_data["initializing_primary_count"] += 1

			if shard[3] == "INITIALIZING" and shard[2] == "r":
				self.index_data["initializing_replica_count"] += 1

			if shard[3] == "UNASSIGNED" and shard[2] == "p":
				self.index_data["unassigned_primary_count"] += 1

			if shard[3] == "UNASSIGNED" and shard[2] == "r":
				self.index_data["unassigned_replica_count"] += 1

			if shard[3] == "STARTED" and shard[2] == "p":
				self.index_data["started_primary_count"] += 1

			if shard[3] == "STARTED" and shard[2] == "r":
				self.index_data["started_replica_count"] += 1

			if self.index_data["list"][shard[0]]["size"] == None:
				cur_index_stats = self.index_stat_get(shard[0])["_all"]
				self.index_data["list"][shard[0]]["size"] = cur_index_stats["total"]["store"]["size_in_bytes"]
				self.index_data["list"][shard[0]]["docs_count"] = cur_index_stats["total"]["docs"]["count"]
				self.index_data["list"][shard[0]]["docs_deleted"] = cur_index_stats["total"]["docs"]["deleted"]
				self.index_data["list"][shard[0]]["search_total"] = cur_index_stats["total"]["search"]["query_total"]
				self.index_data["list"][shard[0]]["search_time"] = cur_index_stats["total"]["search"]["query_time_in_millis"]

		for index in self.index_data["list"]:
			if self.index_data["list"][index]["size"] > self.index_data["max_size"][1]:
				self.index_data["max_size"] = [ index, self.index_data["list"][index]["size"] ]

			if self.index_data["list"][index]["size"] < self.index_data["min_size"][1]:
				self.index_data["min_size"] = [ index, self.index_data["list"][index]["size"] ]

			if self.index_data["list"][index]["docs_count"] > self.index_data["max_docs"][1]:
				self.index_data["max_docs"] = [ index, self.index_data["list"][index]["docs_count"] ]

			if self.index_data["list"][index]["docs_count"] < self.index_data["min_docs"][1] and self.index_data["list"][index]["docs_count"] != 0:
				self.index_data["min_docs"] = [ index, self.index_data["list"][index]["docs_count"] ]

			if self.index_data["list"][index]["search_time"] > self.index_data["max_search_time"][1]:
				self.index_data["max_search_time"] = [ index, self.index_data["list"][index]["search_time"] ]

			if self.index_data["list"][index]["search_time"] < self.index_data["min_search_time"][1] and self.index_data["list"][index]["search_time"] != 0:
				self.index_data["min_search_time"] = [ index, self.index_data["list"][index]["search_time"] ]

			if self.index_data["list"][index]["search_time"] == 0:
				self.index_data["zero_search_time"] += 1

			if self.index_data["list"][index]["search_total"] > self.index_data["max_search_query"][1]:
				self.index_data["max_search_query"] = [ index, self.index_data["list"][index]["search_total"] ]

			if self.index_data["list"][index]["search_total"] < self.index_data["min_search_query"][1] and self.index_data["list"][index]["search_total"] != 0:
				self.index_data["min_search_query"] = [ index, self.index_data["list"][index]["search_total"] ]

			if self.index_data["list"][index]["search_total"] == 0:
				self.index_data["zero_search_query"] += 1

			self.index_data["total_size"] += self.index_data["list"][index]["size"]
			self.index_data["total_primary"] += self.index_data["list"][index]["primary_count"]
			self.index_data["total_replica"] += self.index_data["list"][index]["replica_count"]
			self.index_data["total_docs_count"] += self.index_data["list"][index]["docs_count"]
			self.index_data["total_docs_deleted"] += self.index_data["list"][index]["docs_deleted"]
			self.index_data["total_search_time"] += self.index_data["list"][index]["search_time"]
			self.index_data["total_search_query"] += self.index_data["list"][index]["search_total"]
			self.index_data["total_green"] += 1 if self.cluster_data["indices"][index]["status"] == "green" else 0
			self.index_data["total_yellow"] += 1 if self.cluster_data["indices"][index]["status"] == "yellow" else 0
			self.index_data["total_red"] += 1 if self.cluster_data["indices"][index]["status"] == "red" else 0


	# SECTION: Analyze
	def tool_analyze_print(self):
		print("Summary:\n")

		# Get cluster information
		print(" == Cluster ==\n")

		print("  * Cluster Status:                  " + self.cluster_data["status"])
		print("  * Cluster Name:                    " + self.cluster_data["name"])

		# Get node information
		print("\n == Nodes ==\n")

		print("  * Master node:                     %s" % self.cluster_data["state"]["master_node"])
		print("  * Number of nodes:                 %d" % self.node_data["total_count"])
		print("  * Number of data nodes:            %d" % self.node_data["data_count"])
		print("  * Nodes list:                      " + ", ".join(self.node_data["list"]))
		sys.stdout.write("  * Nodes map:                       ")
		for key in self.node_data["map"]:
			sys.stdout.write(self.node_data["map"][key] + "[" + key + "], ")
		print("")
		sys.stdout.write("  * Client nodes:                    ")
		for node in self.node_data["client_list"]:
			sys.stdout.write(node[0] + "[" + node[1] + "@" + node[2] + "], ")
		print("")
		sys.stdout.write("  * Data nodes:                      ")
		for node in self.node_data["data_list"]:
			sys.stdout.write(node[0] + "[" + node[1] + "@" + node[2] + "], ")
		print("")

		# Get index information
		print("\n == Indices ==\n")

		print("  * Number of indices:               %d" % len(self.index_data["list"]))
		print("  * Total green indices:             %d" % self.index_data["total_green"])
		print("  * Total yellow indices:            %d" % self.index_data["total_yellow"])
		print("  * Total red indices:               %d" % self.index_data["total_red"])
		print("  * Number of primary shards:        %d" % self.index_data["total_primary"])
		print("  * Number of replica shards:        %d" % self.index_data["total_replica"])
		print("  * Average primaries per index:     %d" % (self.index_data["total_primary"] / len(self.index_data["list"])))
		print("  * Average replicas per index:      %d" % (self.index_data["total_replica"] / len(self.index_data["list"])))
		print("  * Total indices size:              %d bytes" % self.index_data["total_size"])
		print("  * Average index size:              %d bytes" % (self.index_data["total_size"] / len(self.index_data["list"])))
		print("  * Biggest index size:              %d bytes (%s)" % (self.index_data["max_size"][1], self.index_data["max_size"][0]))
		print("  * Smallest index size:             %d bytes (%s)" % (self.index_data["min_size"][1], self.index_data["min_size"][0]))
		print("  * Total documents:                 %d" % self.index_data["total_docs_count"])
		print("  * Total documents deleted:         %d" % self.index_data["total_docs_deleted"])
		print("  * Average documents per index:     %.2f" % (self.index_data["total_docs_count"] / float(len(self.index_data["list"]))))
		print("  * Index with most documents:       %d (%s)" % (self.index_data["max_docs"][1], self.index_data["max_docs"][0]))
		print("  * Index with least documents:      %d (%s) [Excluding zeros]" % (self.index_data["min_docs"][1], self.index_data["min_docs"][0]))
		print("  * Index total search queries:      %d" % self.index_data["total_search_query"])
		print("  * Indices without searches:        %d" % self.index_data["zero_search_query"])
		print("  * Index average search queries:    %.2f [Excluding zeros]" % (self.index_data["total_search_query"] / float(len(self.index_data["list"]) - self.index_data["zero_search_query"])))
		print("  * Index with most searches:        %d (%s)" % (self.index_data["max_search_query"][1], self.index_data["max_search_query"][0]))
		print("  * Index with less searches:        %d (%s)" % (self.index_data["min_search_query"][1], self.index_data["min_search_query"][0]))
		print("  * Index total search time:         %d" % self.index_data["total_search_time"])
		print("  * Index average search time:       %.2f ms [Excluding zeros]" % (self.index_data["total_search_time"] / float(len(self.index_data["list"]) - self.index_data["zero_search_time"])))
		print("  * Index fastest search time:       %d ms (%s) [Excluding zeros]" % (self.index_data["min_search_time"][1], self.index_data["min_search_time"][0]))
		print("  * Index slowest search time:       %d ms (%s)" % (self.index_data["max_search_time"][1], self.index_data["max_search_time"][0]))

		# Get shard information
		print("\n == Shards ==\n")
		print("  * Number of shards started:        %s" % self.shard_data["started_count"])
		print("  * Number of active primary shards: %s" % self.cluster_data["active_primary_shards"])
		print("  * Relocating Shards:               %s" % self.cluster_data["relocating_shards"])
		print("  * Number of shards initializing:   %s" % self.shard_data["initializing_count"])
		print("  * Number of shards unassigned:     %s" % self.shard_data["unassigned_count"])
		print("  * Total number of shards:          %s" % self.shard_data["total_count"])
		print("  * Total primaries initializing:    %d" % self.index_data["initializing_primary_count"])
		print("  * Total replicas initializing:     %d" % self.index_data["initializing_replica_count"])
		print("  * Total primaries unassigned:      %d" % self.index_data["unassigned_primary_count"])
		print("  * Total replicas unassigned:       %d" % self.index_data["unassigned_replica_count"])
		print("  * Total primaries started:         %d" % self.index_data["started_primary_count"])
		print("  * Total replicas started:          %d" % self.index_data["started_replica_count"])

		print("")

	def tool_report_print(self):
		print("Report:\n")

		if self.index_data["total_green"] != len(self.index_data["list"]):
			print(" [-] More than one index have problems.")

			if self.shard_data["unassigned_count"]:
				print("       [w] There are unassigned shards.")

			if self.shard_data["unassigned_count"] and self.index_data["total_replica"] and self.cluster_data["number_of_data_nodes"] < 2:
				print("       [c] There are unassigned replica shards and less than 2 data nodes.")

			if self.index_data["unassigned_primary_count"]:
				print("       [c] There are %d primary shards unassigned." % self.index_data["unassigned_primary_count"])

			if self.shard_data["initializing_count"]:
				print("       [w] There are shards in initializing state (p: %d, r: %d)." % (self.index_data["initializing_primary_count"], self.index_data["initializing_replica_count"]))
		else:
			print(" [+] All indices look good.")

	def do(self):
		print("Analyzing cluster...")
		self.tool_analyze_init()

		print("Printing results...")
		self.tool_analyze_print()

		print("Showing report...")
		self.tool_report_print()

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
		elastic = UETAnalyze(usage.args["target"])
		elastic.do()

## Entry Point
if __name__ == "__main__":
	Main().do()

