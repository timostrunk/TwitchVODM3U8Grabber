#!/usr/bin/env python

"""
The MIT License (MIT)

Copyright (c) 2015 Timo Strunk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import print_function

import ast

try:
    from StringIO import StringIO as CURL_IO_OBJ
    from StringIO import StringIO 
except ImportError:
    from io import BytesIO as CURL_IO_OBJ
    from io import StringIO 
import pycurl


class M3UINDEXParser(object):
    """
        Parses a Twitch index M3U and stores just the name of the streams and
        the stream URLS.
        Use is like this:
        m3up = M3UINDEXParser()
        m3up.parse(StringIO(playlist))
        mym3u_url = m3up.get_url_for("Medium")
    """
    def __init__(self):
        self.streams = {}
    
    """
        parse takes a streamlike object and returns nothing.
    """
    def parse(self,infile):
        skipline = 0
        next_stream = None
        for line in infile:
            if 'EXT-X-MEDIA' in line:
                skipline = 1
                splitargs = line.split(',')
                for arg in splitargs:
                    splitarg = arg.split('=')
                    if splitarg[0] == 'NAME':
                        next_stream = splitarg[1].replace('"','')
                continue
            if 'EXT-X-STREAM-INF' in line:
                continue
            if skipline == 1:
                skipline = 0
                url = line[:-1]
                self.streams[next_stream] = url
                next_stream = None

    """
        Debug routine to just get the stream urls
    """
    def dump_to_stdout(self):
        for key,url in self.streams.items():
            print(key,url)                 
    
    """
        After picking a quality (that is a NAME tag in the Index url
        this returns the stream.
    """
    def get_url_for(self,quality):
        return self.streams[quality.title()]


"""
Main class, use like this:
    Open the past broadcasts page and the check the stream url.
    Check the available qualities.
    
    Call:
    TwitchVODM3UGrabber(video_id,"Medium",outstream)
    video_id is the integer of the video url, "Medium" is the quality string.
"""
class TwitchVODM3UGrabber(object):
    BASE_API_URL="https://api.twitch.tv/api/vods/%d/access_token"
    M3U_BASE_URL ="http://usher.twitch.tv/vod/%d?nauthsig=%s&nauth=%s"
    
    """
        Takes a streamlike content M3U and replaces all lines starting with
        index- with:
        url/index-
        
        Returns the file line by line
        Use this function to convert a M3U from relative to absolute.
    """
    @staticmethod
    def M3UCONTENTRelativeToAbsolute(infile,url):
        for line in infile:
            if line.startswith('index-'):
                line = "%s/%s"%(url,line)
            yield line[:-1]

    """
        Just a standard curl url to string routine
    """
    @staticmethod
    def get_url_contents(url): 
        buf = CURL_IO_OBJ()
    
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buf)
        c.perform()
    
        body = buf.getvalue()
        buf.close()
        body = body.decode('iso-8859-1')
        return body

    """
        The main workflow method, annotations inside
    """
    @classmethod
    def get_completed_m3u_playlist(cls,vid,quality,outstream):
        #1. We get the API url:
        API_URL=cls.BASE_API_URL%vid
        #2. We download the contents to get the sig and token values:
        first_stage = cls.get_url_contents(API_URL)
        video_info = ast.literal_eval(first_stage)
        #3. We use the sig and token values to get the m3u8 url (and get it):
        M3U_URL = cls.M3U_BASE_URL %(vid,video_info["sig"],video_info["token"])        
        playlist = cls.get_url_contents(M3U_URL)
        playlist = cls.get_url_contents(M3U_URL)
        #4. We get the video url for our chosen quality:
        m3up = M3UINDEXParser()
        m3up.parse(StringIO(playlist))
        mym3u_url = m3up.get_url_for("Medium")
        lastslash = mym3u_url.rfind('/')
        mym3u_base = mym3u_url[0:lastslash]
        #5. We get the actual M3U8 file with the video content links:
        mym3u = cls.get_url_contents(mym3u_url)
        #6. We convert the relative links in said M3U8 to absolute links to
        #   obtain FFMPEG compatibility:
        for line in cls.M3UCONTENTRelativeToAbsolute(StringIO(mym3u),mym3u_base):
            outstream.write(line+'\n')
        
        
if __name__ == '__main__':
    import os,sys
    if len(sys.argv) < 4:
        print("""
            
            Usage: %s 1234567 Medium myplaylist.m3u8
            
    1234567: video id of the stream to be downloaded
    Medium: Quality of the stream (Usually, Low Mobile Medium High)
    myplaylist.m3u8 file to be written to.
    
    You can obtain the video id by clicking on past_broadcasts and then clicking
    Copy Link Location of the video you would like to download.
    
    The video URL will look like this:
    
     http://www.twitch.tv/mybroadcaster/v/12345678
                                          ^^^^^^^^
                                          VIDEO_ID                
                                        
                                        
    This playlist downloader only supports urls with a v before the ID.
              """ %(os.path.basename(__file__)))
        exit()
    vid = int(sys.argv[1])
    quality = sys.argv[2]
    outfile = sys.argv[3]
    if os.path.exists(outfile):
        print("Output file %s already exists. Please delete it before."%outfile)
        exit()
    with open(outfile,'w') as out:
        TwitchVODM3UGrabber.get_completed_m3u_playlist(vid,quality,out)
    print ("Playlist written to %s"%outfile)
    print ('Encode with: <ffmpeg -i "%s" -bsf:a aac_adtstoasc -c copy output.mp4>'%(outfile))
