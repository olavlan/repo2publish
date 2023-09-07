import os
import git
import re
from pathlib import Path
from settings import *
from split_files import split_files

def main():

	#Create output folder:
	Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)

	#Clone repo (have to delete old input folder first):
	repo_url = "https://github.com/"+ REPO_NAME + ".git"
	if not os.path.isdir(INPUT_FOLDER):
		repo = git.Repo.clone_from(repo_url, INPUT_FOLDER, branch = BRANCH)

	#Get Markdown files
	files = list(Path(INPUT_FOLDER).rglob("*.md" ))
	
	#Files with content
	content_files = []
	for f in files:
		if  re.search("README", str(f)):
			continue
		else: 
			content_files.append(f)

	split_files(content_files)

if __name__ == "__main__":
	main()