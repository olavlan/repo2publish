# Prepare Github repository for publishing platform

## Running the program

1. Clone this repo
2. Change the settings in `settings.py` to desired values
3. Install requirements:
```
pip install -r requirements.txt
```
4. Run the main program
```
python repo2publish.py
```

## What the program does

1. Downloads the given Github repository consisting of .ipynb files and media files.
2. Creates a content folder which is prepared for the publishing platform, regardless of how the content was originally organized. The prepared folder is organized as follows:
	- One folder for each article (learning object).
	- This folder contains two markdown files and the media files to be included in the article.
	- The two markdown files contain the content of the article, in bokmål and nynorsk.
	- The original content is assumed to be in bokmål; the program translates to nynorsk using [Apertium-apy](https://wiki.apertium.org/wiki/Apertium-apy). 
	- The Markdown files also gets a YAML front matter which contains the following information:
		- The title of the article.
		- The title of the chapter (chain) it belongs to.
		- The list of media files to be included. 

## What the original content must satisfy

1. Media files are included using image tags and relative paths, as in the following example:
```
<img src="../fig/programmeringsparadigmer.svg" >
```
2. The same Markdown heading level is used for all articles, and for all chapters. 
