#fileUtils.py

def KeySafe(key):
	key = key.replace(".", "_")
	return key

def StringToType(value):
	if value.isdigit():
		val = int(value)

	elif value.count('.') == 1:
		val = value.split('.')
		if val[0].isdigit() and val[1].isdigit():
			val = float(value)

	else:
		val = value

	return val
	
def strip(item):
	item = item.strip()
	item = item.strip("\"")
	return item
