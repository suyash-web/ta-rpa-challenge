# Bot to fetch the news

Accepts workitems having search phrase, section and number of months.

Example of how to feed workitems:

{"phrase": "machines","section": "opinion","months": 3}

- Value for "month" can either be an integer or a string.

There can also be multiple section and they can be passed as a list in workitems as shown below:
{"phrase": "machines","section": ["section1", "section2"],"months": 3}

## Note:

- Excel file and zip folder with all the downloaded images will be available as artifacts on robocorp.
