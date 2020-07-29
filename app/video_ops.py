import os
import subprocess
import sys
import json
from database import *
import ntpath
import string
import secrets

#further this exercise, we should consider a file normalisation function
def video_ingestion(input_file):
    print(input_file)
    os.chdir(bin_dir)
    try:
        subprocess.check_output("./mp4info {} --format json > out.json".format(input_file), shell=True)
    #    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        print("\nOK - File"+input_file+" is a video file and is going to be processed!")
    except subprocess.CalledProcessError as e:
        print("\nERROR - Corrupted or wrong file, please review the file. Details are:")
        text_output=("An error has been occured"+'\n'+'\n', e)
        raise
        return text_output
    with open('out.json') as f:
        data = json.load(f)
        items = data.get('tracks')
        video_found_flag=0
        for item in items:
            if item.get('type') == 'Video':
                video_found_flag=1
                video_track = (item.get('id'))
                os.chdir(working_dir)
                try:
                    subprocess.check_output("mv {}".format(input_file)+" {}".format(storage_dir),
                    shell=True)
                    file_name=ntpath.basename(input_file)
                    text_output=("OK - File "+file+" has been processed and moved to storage")
                    return text_output
                except subprocess.CalledProcessError as e:
                    print("\nERROR - can't move the file to storage\n\n",e)
                    text_output=("ERROR - can't move the file to storage",e)
                    return text_output
                    raise
        if video_found_flag == 0:
            print("ERROR - File doesn't contain a video track")
            text_output=("ERROR - An error has been occured, file doesn't contain an audio track ")
            return text_output
#
#                print(text_output)
#                return text_output
#                break
#            else:
#                text_output="ERROR - Video file doesn't contain a valid video track"
#                print(text_output)
#                return text_output
#                break
#        print(video_found_flag)
#        print(video_track)
            #    Database.insert(input_file,None,(storage_dir+"/"+file_name),
            #    video_track,"Ingested",None,None,None,None,None)
    #        else:
    #            print("Error: file {} doesn't contain a video track".format(input_file))
                #turn this into return
                #OPTIONAL - we erase the input_file
                #subprocess.run("rm {}".format(input_file),
                #stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                # shell=True)


def fragment(row_name,input_content_id):
    #AÑADIR CHECK DE QUE NO ESTÁ FRAGMENTADO + IF/ELSE
    #PENSAR QUE PASA SI YA ESTÁ FRAGMENTADO (evitar duplicados)
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
    Database.update('output_file_path',str(output_file_path),str(input_content_id))

def encrypt(row_name,key,kid,input_content_id):
    file_to_encrypt=(Database.view_one_row(row_name,input_content_id))
    video_track=(Database.view_one_row("video_track_number",input_content_id))
    output_file=(Database.view_one_row("output_file_path",input_content_id))
    os.chdir(bin_dir)
    encrypt_custom_command = ("./mp4encrypt --method MPEG-CBCS --key " + str(video_track) + ":" + key + ":random " + "--property " + str(video_track) + ":KID:" + kid + " " + file_to_encrypt +  " " + output_file)
    print(encrypt_custom_command)
    subprocess.run(encrypt_custom_command,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    os.chdir(working_dir)
    #Database.update('status','Encrypted','1')

#We define the table we're going to use
db_name="video_files"
table_name="movie_files"
Database.__init__(db_name,table_name)

#print(Database.view())
#video_track_number()
working_dir = os.getcwd()
bin_dir=os.getcwd()+"/../bin"
storage_dir=os.getcwd()+"/../storage/"
file="/Users/javierbrines/Documents/Rakuten/video_packaging_platform/BigBuckBunny.mp4"
output_dir=os.getcwd()+"/output"
key="F1998AA4629FB47EFFE1A611659BD6A7"
kid="59C3308F57ADA6AC1D9D34200C484369"
video_ingestion(file)
#print(Database.view())
#fragment("origin_file_path",3)
#encrypt("output_file_path",key,kid,3)
