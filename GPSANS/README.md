# Replace XML XPath


## Note

To date it only replaces XML Value tags, e.g.:
`<tag>value<tag>`
It does not support attribute replacement.
`<tag attribute="value">value<tag>`

## Help:

```
$ ./replace.py -h
usage: replace.py [-h] [-o] -x XPATH NEW_VALUE file [file ...]

Replaces XML values in files

positional arguments:
  file                  files to parse

optional arguments:
  -h, --help            show this help message and exit
  -o, --output-dir      Where the files are beeing stored. Default: ./out
  -x XPATH NEW_VALUE, --xpath XPATH NEW_VALUE
                        XML Xpath followed by the value to assign to the
                        selection. Only supports tag text replacement, not
                        attributes, i.e.: <tag>text</tag>
```

## Example:

For the files `data/HiResSANS_exp3_scan0011_0001.xml` and `data/HiResSANS_exp3_scan0010_0001.xml`, assign `1234` to the XML tag `SPICErack/Motor_Positions/attenuator_pos` and `New Instrument Name` to the tag `SPICErack/Header/Instrument`. The new files are saved to the default output directory.

```
./replace.py \
-x ./Motor_Positions/attenuator_pos 1234 \
-x ./Header/Instrument "New Instrument Name" \
data/HiResSANS_exp3_scan0011_0001.xml data/HiResSANS_exp3_scan0010_0001.xml

```
