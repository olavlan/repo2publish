import urllib
from pathlib import Path
import requests
import re
import os
import shutil
from common import join_patterns
from settings import *
import nob_nno_translator


#Returns the line numbers of learning objects and chains, and a correspondence list between the two
def line_numbers_sections(lines):
	line_numbers_chains = []
	line_numbers_learning_objects = []
	
	correspondence = [] 
	#learning object number -> chain number, eg. 3 -> 1 if the third learning object belongs to the first chain

	def pattern(chains):
		pattern = CHAIN_LEVEL if chains else LEARNING_OBJECT_LEVEL
		pattern = "^(" + pattern + ")[^#]+"
		return pattern 

	for i, l in enumerate(lines):
		if re.search(pattern(True), l):
			line_numbers_chains.append(i)
		elif re.search(pattern(False), l):
			line_numbers_learning_objects.append(i)
			try:
				correspondence.append(line_numbers_chains[-1])
			except:
				correspondence.append(None) #Learning object doesn't belong to a chain

	return line_numbers_chains, line_numbers_learning_objects, correspondence

def filename(s):
	s = s.lower()
	s = s.replace(" ", "_")
	return s

def get_titles(lines, line_numbers):
	titles = []
	filenames = []
	p1 = "(#)+(\s)+"
	p2 = "(\n)"
	pattern = join_patterns([p1, p2])
	for i in line_numbers: 
		line = lines[i]
		line = re.sub(pattern, "", line)
		titles.append(line)
		filenames.append(filename(line))
	return titles, filenames


#Change filepath in an image line
def change_image_line(line):
	path_pattern = join_patterns(["", ".*/"]) 
	pattern = "(img src=[\"\'])" + path_pattern + "([^/\"\']+[\"\'])"
	replace = "\g<1>" + PLATFORM_MEDIA_PATH + "\g<3>" 
	line = re.sub(pattern, replace, line)
	return line

#Find image lines and replace filepaths
def change_image_lines(lines):
	pattern = "img src=\"([^\"]+)\""
	new_lines = lines.copy()
	original_filenames = []
	for i, l in enumerate(lines): 
		m = re.search(pattern, l)
		if m: 
			original_filenames.append(m.group(1))
			new_lines[i] = change_image_line(l)
	return new_lines, original_filenames

def split_file(input_file, output_folder=OUTPUT_FOLDER):
	with open(input_file, "r") as f:
		lines = f.readlines()

	line_numbers_chains, line_numbers_learning_objects, correspondence = line_numbers_sections(lines)
	titles_learning_objects, filenames_learning_objects = get_titles(lines, line_numbers_learning_objects)
	titles_chains, filenames_chains = get_titles(lines, line_numbers_chains)

	base_folder = os.path.split(input_file)[0]
	n = len(line_numbers_learning_objects)

	for i in range(n):
		fn = str(i) + "_" + filenames_learning_objects[i]
		start = line_numbers_learning_objects[i]+1
		end = line_numbers_learning_objects[i+1] if (i < n-1) else None

		folder = os.path.join(output_folder, fn)
		Path(folder).mkdir(parents=True, exist_ok=True)
		fn_nob = fn + "_" + NOB + ".md"
		fn_nno = fn + "_" + NNO + ".md"
		fn_nob = os.path.join(folder, fn_nob)
		fn_nno = os.path.join(folder, fn_nno)

		lines_nob = lines[start:end]
		lines_nob, image_filenames = change_image_lines(lines_nob)
		for ffn in image_filenames: 
			src = os.path.join(base_folder, ffn)
			basename = os.path.basename(ffn)
			dst = os.path.join(folder, basename)
			try:
				shutil.copyfile(src, dst)
			except: 
				pass

		def yaml_front_matter(nno):
			lines = []
			lines.append("---\n")

			title_learning_object = titles_learning_objects[i] 
			if nno:
				title_learning_object = nob_nno_translator.translate_line(title_learning_object, add_newline=False)
			lines.append("title: \"" + title_learning_object + "\"\n")
			
			try:
				title_chain = titles_chains[correspondence[i]]
				lines.append("belongs_to_chain: \"" + title_chain + "\"\n")
				"""
				if nno: 
					title_chain = nob_nno_translator.translate_line(title_chain, add_newline=False)
				"""
			except:
				pass

			lines.append("figures_to_include:\n")
			for ffn in image_filenames:
				lines.append("\t- \"" + os.path.basename(ffn) + "\"\n")
			lines.append("---\n")
			return lines

		#write nob file
		with open(fn_nob, "w+") as out:
			out.writelines(yaml_front_matter(False))
			out.writelines(lines_nob)

		#write nno file
		lines_nno = nob_nno_translator.translate_lines(lines_nob)
		with open(fn_nno, "w+") as out:
			out.writelines(yaml_front_matter(True))
			out.writelines(lines_nno)

def split_files(content_files):
	#Progress message
	n = len(content_files)
	def progress_message(i, filename):
		print("Processed ", i, "/", n, ": ", filename)

	#Split files into learning objects:
	for i, f in enumerate(content_files):
		split_file(f)
		progress_message(i+1, f)