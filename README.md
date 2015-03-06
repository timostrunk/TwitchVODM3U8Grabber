# TwitchVODM3U8Grabber
Downloads and completes the m3u8 playlist for the new Twitch VOD format, which still misses an official API.
The downloaded playlist can be rendered into a complete video using ffmpeg.

This project is a direct implementation of the efforts of:
https://github.com/fonsleenaars/twitch-hls-vods

Thanks to fonsleenaars for documenting it so accurately.

## Requirements
1. pycurl
2. python2 or python3
3. ffmpeg to compile download and merge the video

## Standalone Usage

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

## Usage as a python library
    from TwitchVODM3U8Grabber import TwitchVODM3UGrabber

    quality = "Medium"
    vid = 1234567
    with open("out.m3u8",'w') as out:
        TwitchVODM3UGrabber.get_completed_m3u_playlist(vid,quality,out)

"out" can be any streamlike with a write function, vid is integer, quality is a video quality string. ("Low","Medium","High","Mobile",...)

