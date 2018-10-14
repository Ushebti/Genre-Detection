def hls_sort2(a, b):
	a = a[0]
	b = b[0]

	if a[1] > b[1]:  # L
		return 1
	elif a[1] < b[1]:
		return -1
	else:
		if a[0] > b[0]:  # H
			return 1
		elif a[0] < b[0]:
			return -1
		else:
			if a[2] > b[2]:  # S
				return 1
			elif a[2] < b[2]:
				return -1
			else:
				return 0
