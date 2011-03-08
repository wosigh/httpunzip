#!/usr/bin/env python

import argparse
from __init__ import *

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-l', '--list', action="store_true", dest="list", help='List files in remote archive.')
    parser.add_argument('-p', '--path', action="store", dest="targetpath", help='Target path for extracted files.')
    parser.add_argument('files', metavar='FILE', nargs='*')
    group = parser.add_argument_group('required arguments')
    group.add_argument('-u', '--url', action="store", dest="url", required=True, help='The URL of the target zip or jar file.', metavar='URL')
    args = parser.parse_args()
        
    if args.list:
        for f in list_files(args.url, details=False):
            print f
    elif args.files:
        http_unzip(args.url, args.files, args.targetpath)