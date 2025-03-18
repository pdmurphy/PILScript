# PILScriptTest
from PILScript import *
import unittest

testFilePath = "resources/PILScriptTestFile.csv"
testComparisonPath = "resources/testComparisonFile.txt"

class TestPILScript(unittest.TestCase):

    #def setUp(self):
    #	print("setup")

    #def tearDown(self):
    #	print("teardown")

    def test_categories(self):
        print("Testing categories")
        readIdFile(testFilePath)
        #print(convertedFromCSVToOutput)
        #print(''.join(convertedFromCSVToOutput))
        self.assertEqual('**Pics or Text:**', convertedFromCSVToOutput[0], "should be **Pics or Text:**")
        self.assertEqual('**Clips:**', convertedFromCSVToOutput[21], "**Clips:**")
        self.assertEqual('**Videos:**', convertedFromCSVToOutput[40], "should be **Videos:**")
        self.assertEqual('**Articles/News/Other:**', convertedFromCSVToOutput[43], "should be **Articles/News/Other:**")
        self.assertEqual('Pics or Text:', convertedFromCSVToOutput[65], "should be Pics or Text:") #shouldnt be bolded by *s

    def test_curly_quotes(self):
        print("Testing curly apostraphe and curly quotes")
        self.assertEqual("Broken apostraphe test. 'this didn't work before'", convertedFromCSVToOutput[55], "should be Broken apostraphe test. 'this didn't work before'")
        self.assertEqual("quote broken test \"abcdefg\"", convertedFromCSVToOutput[59], "should be quote broken test \"abcdefg\"")

    def test_full_output(self):
    	print("Testing full output")
    	with open(testComparisonPath, 'r') as file:
    		file_content = file.read()
    		self.assertEqual(file_content, ''.join(convertedFromCSVToOutput), file_content)


    def end_of_test(self):
        print("COMPLETE: Testing complete")    

def suite():
    """
        Gather all the tests from this module in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestPILScript))
    return test_suite

mySuit = suite()

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(mySuit)
#   unittest.main()
