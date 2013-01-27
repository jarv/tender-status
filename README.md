# A simple status board for Tender

## Features


* Number of issues open
* Number of issues pending (issues that have not been responded to by support staff)
* The oldest three pending issues and how long they have gone without a response from support staff
* Number of issues created and resolved for the last three weeks (weekly buckets ending on Friday)


## Requirements

* Chrome running on OSX or Linux attached to a status monitor
* Python w/ virtualenvwrapper 

![Alt text](https://raw.github.com/jarv/tender-status/master/tender-status.png)



## Installation

```
git clone http://github.com/jarv/tender-status
cd tender-status
mkvirtualenv status
pip install -r requirements.txt
vim settings.py
python tender.py
chrome http://localhost:5000
```


## Configuration

* Edit settings.py to add your API key and URLs for the api
* Cache expiration which controls how often data is fetched from Tender is set to 5min in tender.py

