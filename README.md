# google-emails README

Using selenium and requests, this scrapes business emails based on users' inputted keywords and location.

## Setup
<h3>1. Download Chrome-for-testing and chromedriver:</h3>
You can use other browsers too but this was built and tested on Google Chrome 121.0.6167.85, which can be downloaded <a href="https://googlechromelabs.github.io/chrome-for-testing/"> here</a> with its chromedriver.
Once these have been downloaded, drag them into the root directory of the project still with the containing folders.
<h3>2. Install requirements</h3>
Run `pip3 install requirements.txt` to install all requirements for this project.
<h3>3. Run code</h3>
Refer to <a href="?tab=readme-ov-file#usage">Usage</a> below for more arguments but for general use, run `python3 scrape.py`

## Usage

`python3 scrape.py`
<h3>Arguments:</h3>

* f: allows user to use a .txt file of keywords
* i: allows user to add more keywords or just input them without using file.
  
  **Currently this only supports singular words, for more than one word it must be manually concatenated with + e.g. web+agency**
* n: number of businesses to scrape

Advanced usage: `python3 scrape.py -f keywords.txt -i newkeyword anotherkeyword -n 5`


## Requirements
This project requires at least python 3.1

`pip3 install requirements.txt`

## Release Notes
### 1.0.0

Initial commit
---
