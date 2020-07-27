import os
import subprocess
import sys
import json
#import mp4utils
from database import *
import ntpath
import string
import secrets

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

def video_ingestion(input_file):
    #input_file = "/Users/javierbrines/Documents/Rakuten/video_packaging_platform/BigBuckBunny.mp4"
    print(input_file)
    os.chdir(bin_dir)
    subprocess.run("./mp4info {} --format json > out.json".format(input_file),
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    with open('out.json') as f:
        data = json.load(f)
        items = data.get('tracks')
        for item in items:
            if item.get('type') == 'Video':
                video_track = (item.get('id'))
    #            print(video_track)
                #print(type(video_track))
                os.chdir(working_dir)
                subprocess.run("mv {} storage/".format(input_file),
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                 shell=True)
                file_name=ntpath.basename(input_file)
                Database.insert(input_file,None,(storage_dir+"/"+file_name),
                video_track,"Ingested",None,None,None,None,None)
            else:
                print("Error: file {} doesn't contain a video track".format(input_file))
                #turn this into return
                #OPTIONAL - we erase the input_file
                #subprocess.run("rm {}".format(input_file),
                #stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                # shell=True)



            #    Database.insert("BigBuckBunny.mp4",1,"/Users/javierbrines/Documents/Rakuten/video_packaging_platform/BigBuckBunny.mp4",video_track,"Ingested",'NULL','NULL','NULL','NULL')
            #else:

#def encrypt():
#    video_track_number()
#    input_file = "/Users/javierbrines/Documents/Rakuten/video_packaging_platform/fragmentao.mp4"
#    output_file = "/Users/javierbrines/Downloads/prueba_encripted_script.mp4"
    #key = "hyN9IKGfWKdAwFaE5pm0qg"
    #kid = "oW5AK5BW43HzbTSKpiu3SQ"
    #video_track = "2"


def fragment(row_name,input_content_id):
    #AÑADIR CHECK DE QUE NO ESTÁ FRAGMENTADO + IF/ELSE
    file_for_fragment=(Database.view_one_row(row_name,input_content_id))
    #print(file_for_fragment)
#    prueba=ntpath.normpath(file_for_fragment)
#    print(prueba)
    output_file="/Users/javierbrines/Downloads/prueba_fragmentado.mp4"
    output_code=''.join(secrets.choice(string.ascii_uppercase +
     string.digits) for _ in range(6))
    output_file_path=output_dir+"/"+output_code+"/"+output_code+".mp4"
    os.chdir(output_dir)
    os.mkdir(output_code, mode=0o0755)
    os.chdir(bin_dir)
    fragment_custom_command = ("./mp4fragment " + str(file_for_fragment) + " " + output_file_path)
    print(fragment_custom_command)
    subprocess.run(fragment_custom_command,
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    os.chdir(working_dir)
    Database.update('status','Fragmented',str(input_content_id))
    #Database.update('output_file_path',str(output_file_path),str(input_content_id))

def encrypt(input_file,output_file):
    fragment_custom_command = ("./mp4fragment " + input_file + " " + output_file)
    encrypt_custom_command = ("./bin/mp4encrypt --method MPEG-CBCS --key "+
     str(video_track) +":random:random "+ input_file + " " + output_file)
    #print(fragment_custom_command)
    #subprocess.run(encrypt_custom_command,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    Database.update('status','Encrypted','1')

Database.__init__()
#print(Database.view())
#video_track_number()
working_dir = os.getcwd()
bin_dir=os.getcwd()+"/bin"
storage_dir=os.getcwd()+"/storage"
file="/Users/javierbrines/Documents/Rakuten/video_packaging_platform/BigBuckBunny.mp4"
output_dir=os.getcwd()+"/output"
#video_ingestion(file)
#print(Database.view())
fragment("file_path",15)
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


#buffer_file = '/Users/javierbrines/Documents/Rakuten/video_packaging_platform/buffer.txt'

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
