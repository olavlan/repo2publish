#Strings to identify the language variants, in filenames etc.
NOB = "nob"
NNO = "nno" 

#Join list of regex patterns with or operator
def join_patterns(patterns):
	return "(" + "|".join(patterns) + ")"