# TwitchVODM3U8Grabber
Downloads and completes the m3u8 playlist for the new Twitch VOD format, which still misses an official API.

## Requirements
1. pycurl
2. python2 or python3
3. ffmpeg to compile download and merge the video

## Usage

    TwitchVODM3U8Grabber.py 1234567 Medium myplaylist.m3u8

    1234567: video id of the stream to be downloaded
    Medium: Quality of the stream (Usually, Low Mobile Medium High)
    myplaylist.m3u8 file to be written to.

    You can obtain the video id by clicking on past_broadcasts and then clicking
    Copy Link Location of the video you would like to download.

    The video URL will look like this:

     http://www.twitch.tv/mybroadcaster/v/12345678
                                          ^^^^^^^^
                                          VIDEO_ID
