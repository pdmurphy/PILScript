import csv
import argparse
import sys
from unidecode import unidecode

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

#reference for specific sections/labels
#**Pics or Text:**
#**Clips:**
#**Videos**
#**Articles/News/Other**
#* Pokemon news
#PILScriptTestFile

def readIdFile(PILFilePath):
    with open(PILFilePath) as csvfile:
        csvReader = csv.reader(csvfile, delimiter=',')
        for row in csvReader:
            #print(row) #for debugging
            cleanRow = list(filter(None, row)) #filter used to remove empty columns from the row   
            if not cleanRow: #purge rows with no entries
                #if empty row, skip
                continue
            convertedFromCSVToOutput.append("\n")
            convertedFromCSVToOutput.append("\n")
            convertedFromCSVToOutput.append("* ")
            for i, column in enumerate(cleanRow): 
                #print (i, column) for debugging
                #if one of the title spots. then pop/remove? convertedFromCSVToOutput.pop()
                column = unidecode(column)
                if i == 0:  #for each new row have a specific start without an extra new line and bullet.
                    if column.__eq__("Pics or Text:") or column.__eq__("Clips:") or column.__eq__("Videos:") or column.__eq__("Articles/News/Other:"):
                        #need to pop first to remove the space + *
                        convertedFromCSVToOutput.pop() #this removes the bullet already created since the categories shouldn't be a bullet.
                        convertedFromCSVToOutput.append("**" + column.lstrip() + "**")
                    else:
                        convertedFromCSVToOutput.append(column.lstrip()) #lstrip removes leading spaces
                else:  #add entry for other parameters
                    convertedFromCSVToOutput.append("\n * ")
                    convertedFromCSVToOutput.append(column.lstrip()) #lstrip removes leading spaces
    #delete initial two newlines. Could do same behavior with a if statement checking index but I did it this way to learn how to delete from front of a list.
    del convertedFromCSVToOutput[0]
    del convertedFromCSVToOutput[0]

def createOutputFile():
    file = open("pil_script_output.txt", "w")
    file.write(''.join(convertedFromCSVToOutput)) 
    file.close()
    #yadda yadda 
#notes for writing the file later. Also could just be a printout intitially as well.
## Method 1
#f = open("Path/To/Your/File.txt", "w")   # 'r' for reading and 'w' for writing
#f.write("Hello World from " + f.name)    # Write inside file 
#f.close()                                # Close file 

readIdFile(PILCSVFilepath)
print(''.join(convertedFromCSVToOutput))
