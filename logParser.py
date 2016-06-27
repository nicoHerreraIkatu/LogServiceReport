# -*- coding: UTF-8 -*-
import rest
import re
import unittest
import argparse
import sys
from __init__ import TestCase, TestSuite


class TestSuiteTests(unittest.TestCase):
    
    def test_emerg(self):
        lines= restLog.get()[1]['lines']
        pattern_emerg = re.compile("(?P<month>(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (?P<day> ?[1-9]?[0-9]).*(?P<error>\[emerg\]).*)")
        pattern_error = re.compile("(?P<month>(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (?P<day> ?[1-9]?[0-9]).*(?P<error>\[err\]).*)")
        
        i=0
        test_cases= []
        for line in lines:
            test_cases.append(TestCase(line, '', '','', ''))
            if pattern_emerg.findall(line):
                test_cases[i].add_failure_info('Emerg')
            elif pattern_error.findall(line):
                test_cases[i].add_error_info('Error')
            i+=1
        ts = [TestSuite("InfoLog", test_cases)]
        print(TestSuite.to_xml_string(ts))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    #--baseURL=http://{BLGW_IP}/
    parser.add_argument('--baseURL', help ="BLGW IP")
    
    parser.add_argument('unittest_args', nargs='*')
    
    args = parser.parse_args()
    
    restLog = rest.Rest(args.baseURL +'a/read/serviceErrorHistory')
    
    # Now set the sys.argv to the unittest_args (leaving sys.argv[0] alone)
    sys.argv[1:] = args.unittest_args
    unittest.main()
