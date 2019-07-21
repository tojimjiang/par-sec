# ParSEC-y by Jim Jiang

# Required Imported Libraries
import requests
from bs4 import BeautifulSoup

# Built-In Libraries
import re
import os
import sys
import configparser

# Repeated Input Functions
def getCik(inputArg):
    global cik
    try:
        cik = str(int(inputArg))
        if (len(cik) > 10):
            raise SyntaxError
    except:
        print('Entered CIK is not valid. Program Exiting.')
        sys.exit()


def getIndex(inputArg):
    global nth
    try:
        index = int(inputArg)
        if (index >= 0 and index < 100):
            nth = index
        else:
            # Not valid index provided (fall back to default)
            nth = 0
            print('Error for index, using default.')
    except:
        print('Entered index is not a number value. Program Exiting.')
        sys.exit()


def getMode(inputArg):
    global mode
    if (inputArg.upper() == '13F-HR' or inputArg.upper() == '13F'):
        mode = inputArg
    else:
        # Not valid arg provided (fall back to default)
        mode = '13F-HR'
        print('Error for mode, using default.')


def getCoal(inputArg):
    global coal
    if (inputArg == 'true'):
        coal = True
    elif (inputArg == 'false'):
        coal = False
    else:
        # Not valid arg provided (fall back to default)
        coal = True
        print('Error for coal, using default.')


def getOver(inputArg):
    global overwrite
    if (inputArg == 'overwrite'):
        overwrite = True
    elif (inputArg == 'keep'):
        overwrite = False
    else:
        # Not valid arg provided (fall back to default)
        overwrite = True
        print('Error for over, using default.')


def getSomething(inputArg):
    if (inputArg.isdigit()):
        #print('Observed exclusively numerical argument, identifying index.')
        getIndex(inputArg.lower())
    elif (inputArg.isalpha()):
        if (inputArg[0] == 'o' or inputArg[0] == 'k'):
            #print('Observed exclusively alphabetical argument, identifying overwrite setting.')
            getOver(inputArg.lower())
        else:
            #print('Observed exclusively alphabetical argument, identifying coalesce pattern.')
            getCoal(inputArg.lower())
    else:
        #print('Observed exclusively alpha-numeric argument, identifying mode.')
        getMode(inputArg.lower())


# Globals
cik = None
nth = None
mode = None
coal = None
overwrite = None
path = os.path.dirname(os.path.realpath(__file__))

# Read from Config
config = configparser.ConfigParser()
try:
    config.read(os.path.join(path, 'app.ini'))
    getIndex(config['DEFAULT']['index'].strip().lower())
    getMode(config['DEFAULT']['mode'].strip().upper())
    getCoal(config['DEFAULT']['coal'].strip().lower())
    getOver(config['DEFAULT']['over'].strip().lower())
    # Get Args
    # Fully Interactive
    if (len(sys.argv) == 1):
        # Prompt for input
        getCik(input('What is the desired CIK/Ticker?\n'))

        if (config['DEFAULT']['override'] == 'true'):
            getIndex(input(
                'What is the desired report index? 0 is default (most recent), 99 is max\n').strip().lower())
            getMode(input(
                'What is the desired record retrival mode? 13F-HR is default (assets), 13F is any\n').strip().upper())
            getCoal(
                input('What is the desired coalescing setting? true is default, false is off \n').strip().lower())
            getOver(
                input('What is the desired file overwrite setting? overwrite is default, keep is off \n').strip().lower())
    # Non-interactive Terminal
    elif (len(sys.argv) > 1 and len(sys.argv) < 7):
        # Get CIK
        getCik(sys.argv[1])
        for i in range(2, len(sys.argv)):
            getSomething(sys.argv[i].lower())
    else:
        # Invalid # of args
        print('Invocation Error.')
        sys.exit()
except:
    print('Invocation / Config File Error. Program Exiting.')
    sys.exit()

# Fix "short" CIKs
if (len(cik) < 10):
    cik = f"{(10-len(cik)) * '0'}{cik}"

# Make the main request and grab the document link
reqMain = requests.get(
    f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type={mode}&dateb=&owner=exclude&count=100")
soupMain = BeautifulSoup(reqMain.text, "lxml")

# Make the document link request and grab the xml link
# Count number of provided entries
totalEnt = len(soupMain.find_all('a', {'id': 'documentsbutton'}))
if (nth + 1 > totalEnt):
    # Index exceeds number of results
    print(
        f"Specified index is greater than number of reports for specified CIK. Max index is {totalEnt - 1}. Program exiting.")
    sys.exit()
reqDoc = requests.get(
    f"https://www.sec.gov{soupMain.find_all('a', {'id':'documentsbutton'})[nth]['href']}")
soupDoc = BeautifulSoup(reqDoc.text, 'lxml')
# Count the amount of links provided.
if (len(soupDoc.find_all(href=re.compile('xml'))) < 3):
    # There are no assets held
    print('There is no asset report in XML format at specified index. Program exiting.')
    sys.exit()
else:
    # Prepare the file name
    fileName = f"CIK{cik}-SEC{soupDoc.find_all(id='secNum')[0].text.strip().split(' ')[-1]}{'-COALESCED' if(coal) else '-DETAILED'}.tsv"

    # Try to open the file
    tsvFile = None
    try:
        tsvFile = open(os.path.join(path, fileName), 'x')
    except:
        # File exists exception catcher
            # Check for overwrite
        if (overwrite):
            try:
                # Attempt overwrite
                tsvFile = open(os.path.join(path, fileName), 'w')
            except:
                # Overwrite fail due to open in another program
                print(
                    'File is open in another program. Please close it to overwrite. Program Exiting.')
                sys.exit()
        else:
            # No overwrite case
            print('Will not overwrite. Program Exiting.')
            sys.exit()

    # Make the Xml link request and get the data for parsing (last index of links that have a .xml, as the primary docs get indexed first)
    reqXml = requests.get(
        f"https://www.sec.gov{soupDoc.find_all(href=re.compile('xml'))[-1]['href']}")
    soupXml = BeautifulSoup(reqXml.text, 'lxml-xml')

    # Total Assets Tracker
    total = 0

    # Coalesced - Brief Mode
    if (coal):
        # Get Company Names and Value of holdings.
        names = soupXml.find_all('nameOfIssuer')
        value = soupXml.find_all('value')
        # Other elements would be (used in non-coalesce mode)
        # - (Share/Holding Class) 'titleOfClass'
        # - (CUSIP) 'cusip'
        # - (Share or Principal Amount) 'sshPrnamt'
        # - (Share or Principal Type) 'sshPrnamtType'
        # - (Investment Discretion) 'investmentDiscretion'
        # - (Other Manager) 'otherManager' (This data would need to be matched up to times when investment discretion is not SOLE)
        # - (Sole Voting Authority) 'Sole'
        # - (Shared Voting Authority) 'Shared'
        # - (No Voting Authority) 'None'

        # Utilize a Dictionary to Coalesce Companies
        nvDict = {}
        for i in range(len(names)):
            total += int(value[i].text)
            if (names[i].text in nvDict):
                # Duplicate
                nvDict[names[i].text] += int(value[i].text)
            else:
                nvDict[names[i].text] = int(value[i].text)

        # Header
        tsvFile.write('COMPANY\tVALUE($K)\t% OF TOTAL\n')

        # Require second run-through because of totaling above
        for (n, v) in nvDict.items():
            tsvFile.write(f"{n}\t{v}\t{round(v/total*100, 4)}%\n")

    # Non-Coalesced Mode - Detailed Mode
    else:
        # Get Detailed Information
        info = soupXml.find_all('infoTable')
        # Get values (to avoid the need for additional parsing when getting total information)
        value = soupXml.find_all('value')
        for v in value:
            total += int(v.text)

        # Header
        tsvFile.write(
            'COMPANY\tCLASS\tCUSIP\tVALUE($K)\t% OF TOTAL\tQTY\tTYPE\tDISCRETION\tOTHER MGR\tVOTING SOLO\tVOTING SHARED\tVOTING NONE\n')

        # Require second run-through because of totaling above
        for item in info:
            # Parse at each line to get get data in the same format as given
            tsvFile.write(f"{item.find('nameOfIssuer').text}\t{item.find('titleOfClass').text}\t{item.find('cusip').text}\t{item.find('value').text}\t"
                          f"{round(int(value[i].text)/total*100, 4)}%\t{item.find('sshPrnamt').text}\t{item.find('sshPrnamtType').text}\t{item.find('investmentDiscretion').text}\t"
                          f"{item.find('otherManager').text if item.find('otherManager') else ' '}\t{item.find('Sole').text}\t{item.find('Shared').text}\t{item.find('None').text}\n")

    # File Close
    tsvFile.close()
