#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python
import math

def nCr(n, k):
	f = math.factorial
	return f(n) / f(k) / f(n-k)


def calculate_probability():
	p = 0.2
	Mc = 156 # users
	Mp = 2 * Mc
	prob_LEQ_mc = 0

	for i in range(0, Mc):
		prob_LEQ_mc += nCr(Mp,i) * (p ** i) * ((1-p) ** (Mp - i))

	prob_greater_than_mc = 1 - prob_LEQ_mc

	print (prob_greater_than_mc)

calculate_probability()