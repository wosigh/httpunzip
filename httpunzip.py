import struct, urllib2, zipfile, io, shutil, argparse

def get_file(url, zinfo):
    z_end = zinfo.header_offset + zipfile.sizeFileHeader + len(zinfo.extra) + zinfo.compress_size
    req = urllib2.Request(url)
    req.add_header("Range","bytes=%s-%s" % (zinfo.header_offset, z_end))
    f = urllib2.urlopen(req)
    data = f.read()
    tmp = io.StringIO(data)
    z = zipfile.ZipExtFile(fileobj=tmp, zipinfo=zinfo)
    target = file("test.png", "wb")
    shutil.copyfileobj(z, target)
    z.close()
    target.close()
    

def get_centdir(url, endrec):
    req = urllib2.Request(url)
    req.add_header("Range","bytes=%s-%s" % (endrec[zipfile._ECD_OFFSET],
                                            endrec[zipfile._ECD_OFFSET]+endrec[zipfile._ECD_SIZE]))
    f = urllib2.urlopen(req)
    data = f.read()
    centdir_dict = {}
    total = 0
    #concat = endrec[zipfile._ECD_LOCATION] - endrec[zipfile._ECD_SIZE] - endrec[zipfile._ECD_OFFSET]
    while total < endrec[zipfile._ECD_SIZE]:
        centdir = data[total:total+zipfile.sizeCentralDir]
        centdir = struct.unpack(zipfile.structCentralDir, centdir)
        fn_start = total + zipfile.sizeCentralDir
        fn_end = fn_start + centdir[zipfile._CD_FILENAME_LENGTH]
        filename = data[fn_start:fn_end]
        x = zipfile.ZipInfo(filename)
        extra_end = fn_end + centdir[zipfile._CD_EXTRA_FIELD_LENGTH]
        x.extra = data[fn_end:extra_end]
        x.header_offset = centdir[zipfile._CD_LOCAL_HEADER_OFFSET]
        (x.create_version, x.create_system, x.extract_version, x.reserved,
            x.flag_bits, x.compress_type, t, d,
            x.CRC, x.compress_size, x.file_size) = centdir[1:12]
        x.volume, x.internal_attr, x.external_attr = centdir[15:18]
        x._raw_time = t
        x.date_time = ( (d>>9)+1980, (d>>5)&0xF, d&0x1F,
                                 t>>11, (t>>5)&0x3F, (t&0x1F) * 2 )
        x._decodeExtra()
        #x.header_offset = x.header_offset + concat
        x.filename = x._decodeFilename()
        total = (fn_end + centdir[zipfile._CD_EXTRA_FIELD_LENGTH] + centdir[zipfile._CD_COMMENT_LENGTH])
        centdir_dict[filename] = x
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

def http_unzip(url, filenames):
    endrec = get_endrec(url)
    centdir = get_centdir(url, endrec)
    for fn in filenames:
        get_file(url, centdir[fn])
        #tmp = io.StringIO()
        #print centdir[fn]
    
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