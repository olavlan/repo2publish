import urllib
import requests
import re
import os
from settings import *
from common import join_patterns

nob_to_nno_base_url = 'https://apertium.org/apy/translate?format=html&markUnknown=no&langpair=nob%7Cnno&q='

#Avoid translating certain parts of a single  line:
#1. Inline code
#2. Math

inline_code_pattern = "(`[^`\n]+`)"
inline_math_pattern = "(\$[^\$]+\$)"

notrans_tag_name = "apertium-notrans"
notrans_open_tag = "<" + notrans_tag_name + ">"
notrans_close_tag = "</" + notrans_tag_name + ">"
notrans_replace_string = notrans_open_tag + "\g<1>" + notrans_close_tag

notrans_pattern = join_patterns([inline_code_pattern, inline_math_pattern])
notrans_tags_pattern = join_patterns([notrans_open_tag, notrans_close_tag])

def add_notrans_tags(s):
	return re.sub(notrans_pattern, notrans_replace_string, s)
def remove_notrans_tags(s):
	return re.sub(notrans_tags_pattern, "", s)


#Some characters needs to be explicitly encoded
markdown_characters = ["\t", "\s\s", "*"]
markdown_encodings = ["<tab>", "<space>", "<asterisk>"]

def encode(s):
	for ch, enc in zip(markdown_characters, markdown_encodings):
		s = s.replace(ch, enc)
	return s
def decode(s):
	for ch, enc in zip(markdown_characters, markdown_encodings):
		s = s.replace(enc, ch)
	return s

#Translate line from nob to nno, avoiding patterns from above:
def translate_line(line, add_newline = True):
	l = line
	l = add_notrans_tags(l)
	l = encode(l)
	l = urllib.parse.quote_plus(l)
	request_url = nob_to_nno_base_url + l
	response = requests.get(request_url).json()
	try:
		l = response['responseData']['translatedText']
	except:
		return line
	l = remove_notrans_tags(l)
	l = decode(l)
	if add_newline:
		l = l + "\n"
	return l



#Check if a line is without text content:
#1. Lines without letters
#2. Figure lines

letters_pattern = "([a-zA-Z])"
figure_pattern = "(^<)"

def not_text_content(s):
	return (not re.search(letters_pattern, s)) or re.search(figure_pattern, s)



#Return the line numbers to translate, avoiding certain lines:
#1. Code blocks
#2. Other lines without text content
def lines_to_translate(lines):
	line_numbers = []

	is_code_block = False
	for i, l in enumerate(lines):
		if re.search("(```)", l):
			is_code_block = True if not is_code_block else False
		elif is_code_block:
			continue
		elif not_text_content(l):
			continue
		else:
			line_numbers.append(i) 

	return line_numbers

def translate_lines(lines):
	ls = lines.copy()
	for i in lines_to_translate(lines):
		ls[i] = translate_line(lines[i])
	return ls

def translate_file(input_filename, output_filename):
	with open(input_filename, "r") as f:
		lines = f.readlines()
	lines = translate_lines(lines)
	with open(output_filename, "w+") as out:
		out.writelines(lines)

def translate_files(input_files, output_folder):
	for fn in input_files:
		temp = os.path.splitext(fn)
		out = os.path.basename(temp[0])
		out = out + "_" + NNO + ".md"
		out = os.path.join(output_folder, out)
		translate_file(fn, out)

