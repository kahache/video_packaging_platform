#!/bin/bash
#__author__ = "Ka Hache a.k.a. The One & Only Javi"
#__version__ = "1.0.0"
#__start_date__ = "10/05/2015"
#__end_date__ = "14/05/2015"
#__maintainer__ = "me"
#__email__ = "little_kh@hotmail.com.com"
#__status__ = "In production"
#__description__ = "Simple downloader for files contained in a text file"

FILE="public_test_video_list.txt"

for LINE in `cat $FILE` 
	do
	wget $LINE	
done
