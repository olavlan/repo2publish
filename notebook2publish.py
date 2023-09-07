import os
import sys
import subprocess
from pathlib import Path
from settings import *
from split_files import split_file

#Get notebook file and create relevant folders
nb = Path.cwd() / Path(sys.argv[1])
main = nb.parent.parent
markdown_folder = main / "markdown"
articles_folder = main / "articles" / nb.stem

#Convert notebook to markdown
markdown_filename =  markdown_folder / f"{nb.stem}.md" 
cmd = f'jupyter nbconvert --to markdown --output {markdown_filename} {nb}'
subprocess.run(cmd, shell=True, check=True)

#Convert markdown to articles
split_file(markdown_filename, output_folder=articles_folder)