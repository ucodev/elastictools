#!/usr/bin/python

# @file elastictools.py
# @brief uCodev Elastic Tools
#        Main classes and procedures for Elasticsearch communication and handling
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
import re
import urllib
import urllib2
import httplib
import json

# Globals
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

ES_NODE_HOST = "localhost"
ES_NODE_PORT = "9200"
ES_REQ_WAIT_SECS = 1

# Class: Elasticsearch Base
class ESBase:
	es_host = ES_NODE_HOST
	es_port = ES_NODE_PORT
	es_url = "http://%s:%s" % (ES_NODE_HOST, ES_NODE_PORT)
	data_origin_url = None
	data_origin_filename = None

	error_status = False
	error_message = ""

	errors = 0
	warnings = 0

	def __init__(self, data_origin = "http://%s:%s" % (ES_NODE_HOST, ES_NODE_PORT)):
		if data_origin.startswith("http://"):
			self.es_url = data_origin
			self.data_origin_url = data_origin
		else:
			self.data_origin_filename = data_origin

	# SECTION: Request
	def es_request_http(self, method, path, data = None, jsonify = True):
		res = None
		post_data_json = None

		if data != None:
			post_data_json = json.dumps(data)

		try:
			conn = httplib.HTTPConnection(self.es_url[7:])

			if data != None:
				conn.request(method, path, post_data_json)
			else:
				conn.request(method, path)

			res = conn.getresponse().read()
		except Exception as e:
			self.errors += 1
			self.error_message = "Failed to perform request (method: %s, path: %s): %s" % (method, path, str(e))
			return None

		if jsonify:
			try:
				return json.loads(res)
			except ValueError:
				return None

		return res

	# SECTION: Reset
	def es_reset_data_config(self):
		self.es_host = ES_NODE_HOST
		self.es_port = ES_NODE_PORT
		self.es_url = "http://%s:%s" % (ES_NODE_HOST, ES_NODE_PORT)
		self.data_origin_url = None
		self.data_origin_filename = None

	def es_reset_data_state(self):
		self.error_status = False
		self.error_message = ""
		self.errors = 0
		self.warnings = 0

# Class: Elasticsearch Cluster
class ESCluster(ESBase):
	cluster_health = None
	cluster_state = None

	# SECTION: Settings
	def cluster_get_health(self, force_request = True):
		if force_request or self.cluster_health == None:
			self.cluster_health = self.es_request_http("GET", "/_cluster/health?level=indices")

		return self.cluster_health

	def cluster_get_state(self, force_request = True):
		if force_request or self.cluster_state == None:
			self.cluster_state = self.es_request_http("GET", "/_cluster/state")

		return self.cluster_state

	def cluster_settings_set(self, key, value, persistent = False):
		mode = "transient" if not persistent else "persistent"

		post_data = {
			mode : {
				key: value
			}
		}

		res = self.es_request_http("PUT", "/_cluster/settings", post_data)

		if res == None:
			return False

		return res["acknowledged"]

	def cluster_settings_get(self, key, persistent = False):
		value = None
		mode = "transient" if not persistent else "persistent"

		res = self.es_request_http("GET", "/_cluster/settings")

		try:
			# FIXME: A little bit lame :(... Lazyness took over me
			value = eval("res[mode]" + "[\"" + key.replace('.', '\"][\"') + "\"]")
		except KeyError:
			return None

		return value

# Class: Elasticsearch Node
class ESNode(ESCluster):
	node_list = None        # []
	node_list_data = None   # []
	node_list_client = None # []
	node_map = None         # {}
	node_count = None       # %d

	def node_get(self, attribute, nodes = None):
		value = None

		path = "/_nodes/" if nodes == None else "/_nodes/" + ",".join(map(lambda x: urllib.quote(x), nodes)) + "/"

		res = self.es_request_http("GET", path + ("" if attribute == None else attribute))

		return res

	def node_get_list_data(self, force_request = True):
		if force_request == False and self.node_list_data != None:
			return self.node_list_data

		if force_request == True or self.node_list == None:
			self.node_get_list()

		self.node_list_data = []

		for node in self.node_list:
			node_stat = self.node_get(None, [ node ])

			if "attributes" not in node_stat["nodes"][node]:
				self.node_list_data.append([ node, node_stat["nodes"][node]["name"], node_stat["nodes"][node]["ip"] ])
				continue

			if node_stat["nodes"][node]["attributes"]["data"] == True:
				self.node_list_data.append([ node, node_stat["nodes"][node]["name"], node_stat["nodes"][node]["ip"] ])

		return self.node_list_data

	def node_get_list_client(self, force_request = True):
		if force_request == False and self.node_list_client != None:
			return self.node_list_data

		if force_request == True or self.node_list == None:
			self.node_get_list()

		self.node_list_client = []

		for node in self.node_list:
			node_stat = self.node_get(None, [ node ])

			if "attributes" not in node_stat["nodes"][node]:
				continue

			if node_stat["nodes"][node]["attributes"]["client"] == "true":
				self.node_list_client.append([ node, node_stat["nodes"][node]["name"], node_stat["nodes"][node]["ip"] ])

		return self.node_list_client

	def node_get_list(self, force_request = True):
		if not force_request and self.node_list != None:
			return self.node_list

		nodes = self.node_get("process")

		if nodes == None:
			self.node_list = None
		else:
			self.node_list = []
			for node_id in nodes["nodes"]:
				self.node_list.append(node_id)

		return self.node_list

	def node_get_map(self, force_request = True):
		if not force_request and self.node_map != None:
			return self.node_map

		nodes = self.node_get("process")

		if nodes == None:
			self.node_map = None
		else:
			self.node_map = {}
			for node_id in nodes["nodes"]:
				self.node_map[nodes["nodes"][node_id]["name"]] = node_id

		return self.node_map

	def node_get_count(self, force_request = True):
		if not force_request and self.node_count != None:
			return self.node_count

		nodes = self.node_get("process")

		if nodes == None:
			return None

		return len(nodes["nodes"])


# Class: Elasticsearch Index
class ESIndex(ESNode):
	def index_settings_set(self, key, value, index = None):
		post_data = {
			"index": {
				key: value
			}
		}

		path = "/_settings" if index == None else "/" + index + "/_settings"

		res = self.es_request_http("PUT", path, post_data)

		if res == None:
			return False

		return res["acknowledged"]

	def index_settings_get(self, index, key):
		value = None

		res = self.es_request_http("GET", "/" + urllib.quote(index) + "/_settings")

		try:
			value = res[index]["settings"]["index"][key]
		except KeyError:
			return None

		return value

	def index_stat_get(self, index):
		res = self.es_request_http("GET", "/" + urllib.quote(index) + "/_stats")

		return res

# Class: Elasticsearch Shard
class ESShard(ESIndex):
	shard_status_raw = None
	shard_status_lines = []
	shard_node_list = []
	shard_data_list = []

	shard_stat_reassigned = 0
	shard_stat_failed_reassign = 0
	shard_stat_moved = 0
	shard_stat_failed_move = 0

	# SECTION: Reset
	def shard_reset_data_status(self):
		self.shard_status_raw = None
		self.shard_status_lines = []
		self.shard_node_list = []
		self.shard_data_list = []

	def shard_reset_data_stat(self):
		self.shard_stat_reassigned = 0
		self.shard_stat_failed_reassign = 0
		self.shard_stat_moved = 0
		self.shard_stat_failed_mode = 0

	# SECTION: Status
	def shard_status_load_from_file(self, filename):
		try:
			with open(filename, 'r') as f:
				self.shard_status_raw = f.read()
		except IOError as e:
			self.errors += 1
			self.error_status = True
			self.error_message = str(e)

	def shard_status_load_from_url(self, url):
		self.shard_status_raw = self.es_request_http("GET", "/_cat/shards?bytes=b", jsonify = False)

		if self.shard_status_raw == None:
			print("Fatal: %s" % self.error_message)
			sys.exit(EXIT_FAILURE)

	def shard_status_node_add(self, node):
		if node not in self.shard_node_list:
			self.shard_node_list.append(node)

	def shard_status_parse(self):
		for line in self.shard_status_lines:
			if not line:
				continue

			pat = re.search("^(.+)\s+(\d+)\s+(\w)\s+(\w+)(.*)$", line)

			if not pat:
				self.warnings += 1
				print("Unrecognized shard entry: %s" % line)
				continue

			shard_index = pat.group(1).strip(' ')
			shard_id = pat.group(2).strip(' ')
			shard_level = pat.group(3).strip(' ')
			shard_state = pat.group(4).strip(' ')
			shard_ndocs = None
			shard_size = None
			shard_host = None
			shard_node = None

			# If the shard is assigned, there's more data to parse
			if shard_state != "UNASSIGNED":
				shard_data_extra = pat.group(5).strip(' ')

				pat = re.search("^(\d+)\s+(\d+)\s+([a-zA-Z\-\.0-9]+)\s+(.+)$", shard_data_extra)

				if not pat:
					self.warnings += 1
					print("Unrecognized shard extra data: %s" % shard_data_extra)
					continue

				shard_ndocs = pat.group(1).strip(' ')
				shard_size = pat.group(2).strip(' ')
				shard_host = pat.group(3).strip(' ')
				shard_node = pat.group(4).strip(' ')

			# If there's info regarding the node, process it
			if shard_node != None:
				self.shard_status_node_add(shard_node)

			# Append the new shard entry to the data list
			self.shard_data_list.append([shard_index, shard_id, shard_level, shard_state, shard_ndocs, shard_size, shard_host, shard_node])

	def shard_status_total_count(self):
		return len(self.shard_data_list)

	def shard_status_started_count(self):
		return sum(map(lambda s: int(s[3] == "STARTED"), self.shard_data_list))

	def shard_status_initializing_count(self):
		return sum(map(lambda s: int(s[3] == "INITIALIZING"), self.shard_data_list))

	def shard_status_unassigned_count(self):
		return sum(map(lambda s: int(s[3] == "UNASSIGNED"), self.shard_data_list))

	def shard_status_load(self):
		if self.data_origin_filename != None:
			self.shard_status_load_from_file(self.data_origin_filename)
		elif self.data_origin_url != None:
			self.shard_status_load_from_url(self.data_origin_url)

		if self.error_status:
			print(self.error_message)
			sys.exit(EXIT_FAILURE)

		self.shard_status_lines = self.shard_status_raw.split('\n')

