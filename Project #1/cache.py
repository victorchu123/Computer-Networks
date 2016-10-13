#!/usr/bin/env python3
#
# COMP 360, Section 1, Fall 2016
# Victor Chu
#
# This is a cache, made from a dictionary, that stores all the most recent HTTP Responses 
# as entries with the form of {URL: [Date_Last_Modified, HTTP Response]}.
#

cache_dict = {}

# Purpose & Behavior: Sets entry in cache with the given key to the given value; 
# if the entry doesn't exist, then the entry will be added to the dict.
# Input: Given key and given value.
# Output: None
def set(key, value):
	cache_dict[key] = value

# Purpose & Behavior: Gets the entry in cache with the given key;
# if the entry doesn't exist, then display an error.
# Input: Given key that you want the value of.
# Output: Corresponding value to the given key.
def get(key):
	try:
		if (cache_dict[key] is not None):
			return cache_dict[key]
	except LookupError:
		return None

# Purpose & Behavior: Prints out all keys with entries in the cache;
# if there are none, then display an error.
# Input: None
# Output: A list of all keys that are in cache.
def query_all_keys():
	keys_queried = []
	for key, value in cache_dict.items():
		keys_queried.append(key)

	if (len(keys_queried) == 0):
		return None	
	else:
		return keys_queried
