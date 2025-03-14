import csv
import argparse
import sys

if len(sys.argv) > 1:
    anyArguments = True
else:
    anyArguments = False

global convertedFromCSVToOutput
convertedFromCSVToOutput = []

def setArgs(PILCSVArg):
    global PILCSVFilepath
    PILCSVFilepath = PILCSVArg

if(anyArguments):
    parser = argparse.ArgumentParser(description="Converts CSV to formatted text for PIL.", add_help=False)
    #spacer
    inputGroup = parser.add_argument_group("Input")
    inputGroup.add_argument("--pil_csv", required=True, help="Path to PIL csv file")
    helpGroup = parser.add_argument_group("Help")
    helpGroup.add_argument("-h", "--help", action="help", help="Displays this help message and exits.")
    args = parser.parse_args()
    setArgs(args.pil_csv)

def readIdFile(PILFilePath):
    with open(PILFilePath) as csvfile:
        csvReader = csv.reader(csvfile, delimiter=',')
        rowcount = 0
        for row in csvReader:
            print(row)
            convertedFromCSVToOutput.append("blah") #testing append
            #convertedFromCSVToOutput += row
            #if(rowcount >= 1):
            #use \n for newlines
                #print("Your pil file is incorrect")
                #exit()
                # not robust and could be worked around but don't want to deal with it as I don't need it
            #else:
                #separateIds(row)
                #rowcount += 1

def createOutputFile():
    file = open("pil_script_output.txt", "w")
    #yadda yadda 
#notes for writing the file later. Also could just be a printout intitially as well.
## Method 1
#f = open("Path/To/Your/File.txt", "w")   # 'r' for reading and 'w' for writing
#f.write("Hello World from " + f.name)    # Write inside file 
#f.close()                                # Close file 

readIdFile(PILCSVFilepath)
print(''.join(convertedFromCSVToOutput))
