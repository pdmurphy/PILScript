import csv
import argparse
import sys

if len(sys.argv) > 1:
    anyArguments = True
else:
    anyArguments = False

def setArgs(pil_csv_arg):
    global pil_csv_filepath
    pil_csv_filepath = pil_csv_arg

if(anyArguments):
    parser = argparse.ArgumentParser(description="Generates P&D image collage from a list of Ids.", add_help=False)
    #spacer
	inputGroup = parser.add_argument_group("Input")
    inputGroup.add_argument("--pil_csv", required=True, help="Path to PIL csv file")
    helpGroup = parser.add_argument_group("Help")
    helpGroup.add_argument("-h", "--help", action="help", help="Displays this help message and exits.")
    args = parser.parse_args()
    setArgs(args.pil_csv)

def readIdFile(pilfilePath):
    with open(pilfilePath) as csvfile:
        csvReader = csv.reader(csvfile, delimiter=',')
        rowcount = 0
        for row in csvReader:
            #if(rowcount >= 1):
                #print("Your pil file is incorrect")
                #exit()
                # not robust and could be worked around but don't want to deal with it as I don't need it
            #else:
                #separateIds(row)
                #rowcount += 1