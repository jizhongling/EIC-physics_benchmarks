#!/usr/bin/env python3

import json
from junitparser import TestCase, TestSuite, JUnitXml, Skipped, Error, IntAttr, FloatAttr


# Create the new element by subclassing Element or one of its child class,
## and add custom attributes to it.
#class MyTestCase(TestCase):
#    foo = Attr()

# Add the custom attribute
#TestCase.id = IntAttr('id')
TestCase.efficiency = FloatAttr('efficiency')
#TestCase.custom = Attr('custom')
#case = TestCase()
#case.id = 123
#case.rate = 0.95
#case.custom = 'foobar'

# After looking at two different python libraries (junit-xml and junitparser)
# junitparser looks the most robust
# https://github.com/weiwei/junitparser 

def merge_results():
    results = None;
    with open("results/dvcs/dvcs_tests.json","r") as f: 
        results = json.load(f)

    # Create suite and add cases
    suite = TestSuite('dvcs')
    suite.add_property('energy', '10-on-100')

    for tname,tres in results.items():
        for ttype, tval in tres.items():
            # Create cases
            case1 = TestCase(tname)
            case1.time = 1.0
            case1.efficiency = tval
            case1.classname = ttype
            suite.add_testcase(case1)

    xml = JUnitXml()
    xml.add_testsuite(suite)
    xml.write('results/dvcs/dvcs_report.xml',pretty=True)


#test code for junit-xml:
#from junit_xml import TestSuite, TestCase
#    test_cases =  []
#        print(test_name)
#        print(test_res)
#        for test_type, test_val in test_res.items():
#           test_cases.append(TestCase(test_name, "dvcs.dvcs_tests.{}".format(test_type), 10, str(test_val), 'I am stderr!'))
#    ts = TestSuite("my test suite", test_cases)
#    # pretty printing is on by default but can be disabled using prettyprint=False
#    print(TestSuite.to_xml_string([ts]))
#    # you can also write the XML to a file and not pretty print it
#    with open('results/dvcs/dvcs_report.xml', 'w') as f:
#        TestSuite.to_file(f, [ts], prettyprint=True)

if __name__ == "__main__":
    # execute only if run as a script
    merge_results()
