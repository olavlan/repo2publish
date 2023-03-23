#Join list of regex patterns with or operator
def join_patterns(patterns):
	return "(" + "|".join(patterns) + ")"