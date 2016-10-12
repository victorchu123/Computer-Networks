cache_dict = {}

# Purpose & Behavior: Sets entry in rpc dict with the given key to the given value; 
# if the entry doesn't exist, then the entry will be added to the dict.
# Input: Given key and given value.
# Output: None
def set(key, value):
	cache_dict[key] = value

# Purpose & Behavior: Gets the entry in rpc dict with the given key;
# if the entry doesn't exist, then display an error.
# Input: Given key that you want the value of.
# Output: Corresponding value to the given key.
def get(key):
	try:
		if (cache_dict[key] is not None):
			return cache_dict[key]
	except LookupError:
		return None

# Purpose & Behavior: Prints out all keys with entries in the rpc dict;
# if there are none, then display an error.
# Input: None
# Output: A list of all keys that are in rpc dict.
def query_all_keys():
	keys_queried = []
	for key, value in cache_dict.items():
		keys_queried.append(key)

	if (len(keys_queried) == 0):
		return None	
	else:
		return keys_queried
