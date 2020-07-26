import os
import subprocess
import sys
import json
#import mp4utils
from database import *

#def upload():
    #    subprocess.call('mv '+file_name+' storage/',shell=True)
        #subprocess.run('./bin/mp4info storage/BigBuckBunny.mp4 --format json| grep Video -B1 | cut -d ":" -f 2 | cut -d "," -f 1 | head -1',shell=True)
        #print(video_track)
        #order = "'./bin/mp4info storage/BigBuckBunny.mp4 | grep Video -B1 | head -1 | sed 's/[^0-9]*//g'""
#        video_track = subprocess.run('./bin/mp4info storage/BigBuckBunny.mp4 | grep Video -B1 | head -1 | sed 's/[^0-9]*//g',shell=True)
#    subprocess.run('./bin/mp4info storage/BigBuckBunny.mp4 --format json| grep Video -B1 | cut -d ":" -f 2 | cut -d "," -f 1 | head -1 >> buffer.txt',shell=True)
#mp4utils.Bento4Command.options.exec_dir = "/Users/javierbrines/Documents/Rakuten/video_packaging_platform"
#exec_dir = "/Users/javierbrines/Documents/Rakuten/video_packaging_platform/"
#result = mp4utils.Mp4Info('--format json',"BigBuckBunny.mp4","/Users/javierbrines/Documents/Rakuten/video_packaging_platform")
#mp4utils.Mp4Info('',"/Users/javierbrines/Documents/Rakuten/video_packaging_platform/BigBuckBunny.mp4")

def video_track_number():
    input_file = "/Users/javierbrines/Documents/Rakuten/video_packaging_platform/BigBuckBunny.mp4"
    subprocess.run("./mp4info {} --format json > out.json".format(input_file),stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    with open('out.json') as f:
        data = json.load(f)
        items = data.get('tracks')
        for item in items:
            if item.get('type') == 'Video':
                video_track = (item.get('id'))
                #print(type(video_track))
                Database.insert("BigBuckBunny.mp4",1,"/Users/javierbrines/Documents/Rakuten/video_packaging_platform/BigBuckBunny.mp4",video_track,"Ingested",'NULL','NULL','NULL','NULL')

#def encrypt():
#    video_track_number()
    input_file = "/Users/javierbrines/Documents/Rakuten/video_packaging_platform/fragmentao.mp4"
    output_file = "/Users/javierbrines/Downloads/prueba_encripted_script.mp4"
    #key = "hyN9IKGfWKdAwFaE5pm0qg"
    #kid = "oW5AK5BW43HzbTSKpiu3SQ"
    #video_track = "2"


def fragment(input_file,output_file,otra_cosa):
    #fragment_custom_command = ("./mp4fragment " + input_file + " " + output_file)
    Database.update('status','Ingested','1')

def encrypt(input_file,output_file):
    encrypt_custom_command = ("./mp4encrypt --method MPEG-CBCS --key "+ str(video_track) +":random:random "+ input_file + " " + output_file)
    #print(fragment_custom_command)
    #subprocess.run(encrypt_custom_command,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
Database.__init__()
print(Database.view())
#video_track_number()
fragment("archivo","cosa","otra_cosa")
#encrypt()



#print(result)
#        print_output(order)

#def print_output(order):
#    original = sys.stdout
#    sys.stdout = open(buffer_file, 'w')
#    command = os.popen(order)
#    print(command.read())
#    print(command.close())
#    sys.stdout = original
#    output_file = open(buffer_file, "r")
#    data = output_file.read()


buffer_file = '/Users/javierbrines/Documents/Rakuten/video_packaging_platform/buffer.txt'

# Store the reference, in case you want to show things again in standard output
#old_stdout = sys.stdout
# This variable will store everything that is sent to the standard output
#result = StringIO()
#sys.stdout = result
# Here we can call anything we like, like external modules, and everything that they will send to standard output will be stored on "result"
#upload()
# Redirect again the std output to screen
#sys.stdout = old_stdout
# Then, get the stdout like a string and process it!
#result_string = result.getvalue()
#print(result_string)
#print("./mp4encrypt --map"+result_string+":prueba:prueba")
#upload()
#print(result_string)
