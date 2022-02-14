# timeline_parse
Hacky repo to parse Google Timeline exports in JSON format

1. Go to google and export your timeline https://takeout.google.com/settings/takeout
2. Unzip all the files somewhere
3. python timeline_parse.py FILENAME (where FILENAME is one of the JSON files which is under the "Takeout\Location History\Semantic Location History\YEAR" subdirectories)

You may want to edit the example as it does some filtering and tries to be a bit intelligent but probably fails in some cases.
