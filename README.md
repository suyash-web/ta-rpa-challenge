# Bot to fetch the news

Accepts workitems having search phrase, section and number of months.

Example of how to feed workitems:

```JSON
{
 "phrase": "medicines",
 "section": "new york",
 "months": 3
}
```

- Value for "month" can either be an integer or a string.

There can also be multiple sections and they can be passed as a list in workitems as shown below:

```JSON
{
 "phrase": "medicines",
 "section": ["section1", "section2"],
 "months": 3
}
```

## Note:

- Excel file and zip folder with all the downloaded images will be available as artifacts on robocorp.
