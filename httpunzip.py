import struct, urllib2, zipfile, argparse

def get_centdir(url, endrec):
    req = urllib2.Request(url)
    req.add_header("Range","bytes=%s-%s" % (endrec[zipfile._ECD_OFFSET], endrec[zipfile._ECD_OFFSET]+endrec[zipfile._ECD_SIZE]))
    f = urllib2.urlopen(req)
    data = f.read()
    centdir_dict = {}
    total = 0
    while total < endrec[zipfile._ECD_SIZE]:
        centdir = data[total:total+zipfile.sizeCentralDir]
        centdir = struct.unpack(zipfile.structCentralDir, centdir)
        fn_start = total + zipfile.sizeCentralDir
        fn_end = fn_start + centdir[zipfile._CD_FILENAME_LENGTH]
        filename = data[fn_start:fn_end]
        total = (fn_end + centdir[zipfile._CD_EXTRA_FIELD_LENGTH] + centdir[zipfile._CD_COMMENT_LENGTH])
        centdir_dict[filename] = list(centdir)
    return centdir_dict

def get_endrec(url):
    req = urllib2.Request(url)   
    req.add_header("Range","bytes=-%s" % (zipfile.sizeEndCentDir))
    f = urllib2.urlopen(req)
    data = f.read()
    
    if data[0:4] == zipfile.stringEndArchive and data[-2:] == "\000\000":
        return list(struct.unpack(zipfile.structEndArchive, data))
    
def list_files(url, details=False):
    endrec = get_endrec(url)
    centdir = get_centdir(url, endrec)
    if details:
        return centdir
    else:
        centdir.keys()

def http_unzip(url, files):
    print files
    
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-l', '--list', action="store_true", dest="list", help='List files in remote archive.')
    parser.add_argument('files', metavar='FILE', nargs='*')
    group = parser.add_argument_group('required arguments')
    group.add_argument('-u', '--url', action="store", dest="url", required=True, help='The URL of the target zip or jar file.', metavar='URL')
    args = parser.parse_args()
        
    if args.list:
        print list_files(args.url, details=True)
    elif args.files:
        http_unzip(args.url, args.files)


#http_unzip('http://palm.cdnetworks.net/rom/pre2/p201r0d11242010/wrep201rod/webosdoctorp102ueuna-wr.jar')