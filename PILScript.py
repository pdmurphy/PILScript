import csv
import argparse
import sys
from unidecode import unidecode

#check if arguments exist
if len(sys.argv) > 1:
    anyArguments = True
else:
    anyArguments = False

#global list which will be used to create the final printout/text file
global convertedFromCSVToOutput
convertedFromCSVToOutput = []

#set arguments 
def setArgs(PILCSVArg, textOutputArg):
    global PILCSVFilepath
    PILCSVFilepath = PILCSVArg
    global textOutputBoolean
    textOutputBoolean = textOutputArg

#parse arguments if they exist
if(anyArguments):
    parser = argparse.ArgumentParser(description="Converts CSV to formatted text for PIL.", add_help=False)

    inputGroup = parser.add_argument_group("Input")
    inputGroup.add_argument("--pil_csv", required=True, help="Path to PIL csv file")
    inputGroup = parser.add_argument_group("Make text output")
    inputGroup.add_argument("--text_output", action="store_true", help="Makes an output text file instead of printing to console. Default false")
    helpGroup = parser.add_argument_group("Help")
    helpGroup.add_argument("-h", "--help", action="help", help="Displays this help message and exits.")
    args = parser.parse_args()
    setArgs(args.pil_csv, args.text_output)

#function that reads and parses the file, filling the list with the formatted output.
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
                column = unidecode(column)
                if i == 0:  #for each new row have a specific start without an extra new line and bullet.
                    #reference for specific sections/labels
                    #**Pics or Text:**
                    #**Clips:**
                    #**Videos**
                    #**Articles/News/Other**
                    if column.__eq__("Pics or Text:") or column.__eq__("Clips:") or column.__eq__("Videos:") or column.__eq__("Articles/News/Other:"):
                        #need to pop first to remove the space + *
                        convertedFromCSVToOutput.pop() #this removes the bullet already created since the categories shouldn't be a bullet.
                        convertedFromCSVToOutput.append("**" + column.lstrip() + "**") #adding the double star formatting.
                    else: #otherwise no extra new line
                        convertedFromCSVToOutput.append(column.lstrip()) #lstrip removes leading spaces
                else:  #add entry for other parameters
                    convertedFromCSVToOutput.append("\n * ")
                    convertedFromCSVToOutput.append(column.lstrip()) #lstrip removes leading spaces
    #delete initial two newlines. Could do same behavior with a if statement checking index but I did it this way to learn how to delete from front of a list.
    del convertedFromCSVToOutput[0]
    del convertedFromCSVToOutput[0]

#single file creation. Will overwrite the file if it already exists.
def createOutputFile():
    file = open("pil_script_output.txt", "w")
    file.write(''.join(convertedFromCSVToOutput)) 
    file.close()

#code that starts the processes. Depending on arguments will perform different functions
if(anyArguments): #if no arguments it will skip and run the tests but not running anything in here.
    readIdFile(PILCSVFilepath)
    if(textOutputBoolean):
        createOutputFile()
    else:
        print(''.join(convertedFromCSVToOutput))
else:
    print("test time")
