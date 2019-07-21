# Par-sec
## What is this?
This is a python program that parses SEC's EDGAR system for 13F SEC documents, and creates a `.tsv` file for the parsed results. Par-sec aims to get the most recent 13F-HR available for the given CIK. By default, it provides just the companies, value and percentage of the holdings listed in a 13F-HR.

Optionally, Par-sec can instead get any 13F or 13F-HR filing, and parse all the data in the XML file and include such data in the `.tsv.` file. See [Config Values (and Useable as Arguments)](#config) to enable.

### TL;DR of Implementation
Takes a CIK to craft a URL to access EDGAR, and scrap the page for the desired document filing link. Access the document filing, and scrap the page for the XML link for reports. Access the XML to get the data that is used to generate `.tsv` file.

## Depends On
_Should be a part of __any__ python build:_ os, re, sys, and configparser   
_External Libraries:_ requests, beautifulsoup, lxml
## How to Run This 
### Native Using `pip`
#### Installation of Dependencies
Install the requirements using `pip install -r requirements.txt`, to install `requests`, `beautifulsoup`, and `lxml`. 

#### Interactive Terminal Invocation
##### In Your Working Directory
Have the file loaded in your working directory, with write access. Run using the command `python parsec.py`. Then you will be prompted for the CIK of the desired mutual fund to look up. _If configured for interactive override, you will be prompted for settings for report index, look up mode, coalescing settings, and overwrite settings._   

Then given correct input, the `.tsv` file will be generated in the same directory as the python file.

##### Path to the Directory
Have the file loaded in your working directory, with write access. Run using the command `python path_to/parsec.py`. The program runs the same as if it were loaded in your working directory.

#### Single Line Invocation
##### In Your Working Directory
Have the file loaded in your working directory, with write access. Run using the command `python parsec.py CIK_CODE`.   

Then given correct input, the `.tsv` file will be generated in the same directory as the python file.   

_Single Line Invocation allows for immediate override of any configuration settings in the `app.ini` file. See details in Arguments (and config types)

##### Path to the Directory
Have the file loaded in your working directory, with write access. Run using the command `python path_to/parsec.py CIK_CODE`. The program runs the same as if it were loaded in your working directory.

### Using `pipenv` as a Virtual Environment
#### Installation of Dependencies
Install the requirements using `pipenv install -r requirements.txt`, to install `requests`, `beautifulsoup`, and `lxml`. 

#### Invocation In Your Working Directory
Run using the same commands as above when using `pip`, but prepended with `pipenv run` to the command. The program runs the same as if it were run outside of a virtual environment.

## Arguments (and Config Values)
### Arguments
- `CIK_CODE` is an argument that is 10 digit number for a mutual fund. Must be provided to be able to look up the mutual fund.
### Config Values (and Useable as Arguments) <a name="config"></a>
These config values can be overridden in a single line invocation by simply typing the preferred value instead. When using this in single line invocation mode, these config values must be after the `CIK_CODE` argument, and be at the very end. _There is a hard limit of a total of __6__ maximum command line words total. `python` and words to the left of it, are not counted. Only `parsec.py` and words to the right are counted._   
If these arguments are not specified, then the program will use config file (`app.ini`) values first, and if they are invalid will fall back to default values.   
- `index` is a config value that is an integer from 0 to 99 to load that many records back from the most recent for the mutual fund. If there are not enough records in the mutual fund, program will exit. _Default is `0`, to load the most recent record._
- `mode` is a config value that is a string either `13F` or `13F-HR` to specify type of record to look up. A `13F` record is a generic filing that may or may not show assets, whereas a `13F-HR` record is a filing that will almost always show assets in an XML file. _Default is `13F-HR`, to more likely load asset filings._
- `coal`(esce) is a config value that is a string either `true` or `false` to specify whether or not to coalesce records and to remove details from the XML data available. When `true` the `.tsv` file will only contain company name, holding value, and percentage of holdings in the company. When `false` the `.tsv` file will contain all information from the XML data, plus the percentage of holdings in the company. _Default is `true`, to only show the most relevant information._
- `over`(write) is a config value that is a string either `overwrite` or `keep` to specify whether or not to overwrite files if the XML file being parsed has a matching record on file already. When `overwrite` the files will always try to be overwritten, but may fail if the file is open in another program. When `keep` the files will never be overwritten, and instead the program will exit. File names are based on the CIK, as well as the SEC filing code that should be unique to each filing, therefore an overwrite should only occur when making a request for data that has already been obtained. _Default is `overwrite`._
### Config Values (_NOT_ Useable as Arguments)
- `override` is a config value _that is not accepted as an argument that is a string either `true` or `false` to specify whether or not to allow overriding of config values in _Interactive Terminal Invocation_. When `true`, you will be prompted for preferred config values for each aspect above in the _Interactive Terminal Invocation_. When `false`, the program will use config file (`app.ini`) values first, and if they are invalid will fall back to default values.


## Error (and Program Exiting) Explanations
>Entered CIK is not valid. Program Exiting.

The given value for CIK is not a valid CIK. Valid CIKs are numbers only, up to 10 digits in length. Check CIK code used to resolve.

>Error for ___, using default.

The given value or config value was not valid, and has been replaced in this invocation with the default value. Check invocation or config file to resolve.

>Entered index is not a number value. Program Exiting.

The given value for index is not a valid CIK. Valid indexes are integers between 0 and 99. Check index used to resolve.

>Invocation Error.

There are too many or too few arguments provided. Check command, argument, CIK code, and config arguments used to resolve. _Typically occurs with `Invocation / Config File Error. Program Exiting.`_

>Invocation / Config File Error. Program Exiting.

There was a configuration file or invocation error. If the `Invocation Error` did not occur, your configuration file is missing or damaged. Check your configuration file or see above issues to resolve.

>Specified index is greater than number of reports for specified CIK. Max index is ##. Program exiting.

The report index specified for `index` is greater than all the number of reports that exist for the mutual fund. Check that index specified is less than ## given to resolve. _If max index given is -1, there were no results._

>There is no asset report in XML format at specified index. Program exiting.

The report desired to be obtained is either not available in an XML format or does not contain any information about assets and holdings for the mutual fund. Look at the report manually as a workaround.

>File is open in another program. Please close it to overwrite. Program Exiting.

A file with the file name of this CIK code and the SEC filing number exists in the directory as a `.tsv` file and is open in another program. Close the program with the file open to resolve.

>Will not overwrite. Program Exiting.

A file with the file name of this CIK code and the SEC filing number exists in the directory as a `.tsv` file. Either check the file and move it, or allow overwriting to resolve.

## Features
- There are actually error messages and a explanation guide above to help resolve issues.
- Percentage of holdings in all output files.
- Interactive Terminal Mode.
- Program is aware when there is no XML file to parse, and indicates that status to terminal.
- Old-ish filings are not in XML format and are not parsed by this program.
- Can be called outside of working directory, and places results in the directory of the python file.
- CIK code fixing, automatically adds leading 0's as needed. As in, using `1166559` as a CIK code will get auto-corrected to `0001166559`.
- Single Line Invocation config arguments after the CIK code can be in any order.
- You can look up more than just the most recent value, by indicating how many reports your want to go back from 0 to the maximum number of filings or 99, whichever is lower. See [Config Values (and Useable as Arguments) **index**](#config) to use.
- Two output modes, a coalesced version (default) that only indicate companies, value of holdings and percentage of holdings, that also coalesces multiple entires into a single entry per company name. The optional detailed mode more shows all the data from the filing, but still features percentage of holdings. See [Config Values (and Useable as Arguments) **coal**](#config) to enable.
- Optional overwrite awareness. See [Config Values (and Useable as Arguments) **over**](#config) to enable.
- Optional wide-net lookup mode. See [Config Values (and Useable as Arguments) **mode**](#config) to enable.

### Example Single Line Invocations
- `parsec.py 1166559`: Looks up Gates Foundation using configuration defaults (most recent report, in strict 13F-HR mode, with coalesced report, and file overwriting).
- `parsec.py 01756111 false`: Looks up Peak6 with a detailed report from `false`. The rest uses configuration defaults (most recent report, in strict 13F-HR mode, and file overwriting)
- `parsec.py 0001357955 1 false`: Looks up Proshare Advisors for the second most recent report (`0` is most recent, `1` is one behind or second most recent), with a detailed report from `false`. The rest uses configuration defaults (in strict 13F-HR mode, and file overwriting)
- `parsec.py 0001397545 keep false 13F 2`: Looks up HHR Asset Management, for the third most recent report (`0` is most recent, `1` is one behind, `2` is two behind or third most recent), in loose `13F` mode, with a detailed report from `false`, and with**out** file overwriting from `keep`. This call overrode all config settings because of single line override regardless of config file settings.
- `parsec.py 01543160 13F-HR false 1 overwrite`: Looks up HHR Asset Management, for the second most recent report (`0` is most recent, `1` is one behind or second most recent), in strict `13F-HR` mode, with a detailed report from `false`, and with file overwriting from `overwrite`. This call overrode all config settings because of single line override regardless of config file settings.

### Limitations and Bugs
- Expects semi-perfect input. As in the guidelines above.
- Expects perfect connectivity. Requests will raise errors if there is no connectivity.
- Expects english input. 
- Invocation Error might display two error messages.
- Uses a config file.
