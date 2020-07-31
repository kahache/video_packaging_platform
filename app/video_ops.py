import os
import subprocess
import sys
import json
from database import *
import ntpath
import string
import secrets
import base64

#further this exercise, we should consider a file normalisation function
class Video_ops:
    
    def video_ingest(input_file):
        os.chdir(bin_dir)
        try:
            subprocess.check_output("./mp4info {} --format json > out.json".
                                    format(input_file), shell=True)
        except subprocess.CalledProcessError as e:
            output=("ERROR - Corrupted or wrong file, please review the file. Details:"
                        +'\n'+'\n', e)
            return output
            raise
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
                        subprocess.check_output("mv {}".format(input_file)+" {}".
                                                format(storage_dir),shell=True)
                        file_name=ntpath.basename(input_file)
                        #DATABASE - we add 1 as confirmation process went good!
                        output=("OK - File "+input_file+
                                    " has been processed and moved to storage\n\n",1)
                        return output
                    except subprocess.CalledProcessError as e:
                        output=("\nERROR - can't move the file to storage\n\n",e)
                        return output
                        raise
            if video_found_flag == 0:
                output=("ERROR - An error has been occured, file doesn't contain an audio track ")
                return output
        #OPTIONAL - we erase the input_file
        #subprocess.run("rm {}".format(input_file),stdout=subprocess.DEVNULL,
        #stderr=subprocess.DEVNULL,shell=True)


    def video_fragment(input_file):
        #PENSAR QUE PASA SI YA ESTÁ FRAGMENTADO (evitar duplicados)
        output_file="/Users/javierbrines/Downloads/prueba_fragmentado.mp4"
        output_code=''.join(secrets.choice(string.ascii_uppercase +
                    string.digits) for _ in range(6))
        output_file_path=output_dir+output_code+"/"+output_code+".mp4"
        os.chdir(output_dir)
        os.mkdir(output_code, mode=0o0755)
        os.chdir(bin_dir)
        fragment_custom_command = ("./mp4fragment " + str(input_file) + " " +
                                    output_file_path)
        try:
            subprocess.check_output(fragment_custom_command,shell=True)
            output=("OK - File "+file+
                        " has been fragmented and is ready to encrypt\n\n",output_file_path,1)
            return output
        except subprocess.CalledProcessError as e:
            output=("\nERROR - can't fragment the video file"+
                        input_file+"\n\n",e)
            return output
            raise
        os.chdir(working_dir)

    def video_encrypt(video_track_number,key,kid,input_file):
        os.chdir(bin_dir)
        string1=(key+"==")
        video_key=(base64.b64decode(string1).hex())
        string2=(kid+"==")
        video_kid=(base64.b64decode(string2).hex())
        output_file_path=(os.path.splitext(input_file)[0])+"_enc.mp4"
        encrypt_custom_command = ("./mp4encrypt --method MPEG-CBCS --key " +
                                str(video_track_number) + ":" + video_key +
                                ":random " + "--property " + str(video_track_number) +
                                 ":KID:" + video_kid + " " + input_file +  " " +
                                  output_file_path)
        try:
            subprocess.check_output(encrypt_custom_command,shell=True)
            output=("\nOK - File" + input_file + " has been encrypted with key:" +
                    key + "kid:"+kid+ "\n\n",output_file_path,1)
            return output
        except subprocess.CalledProcessError as e:
            output=("\nERROR - can't encrypt the video file"+
                    input_file + "\n\n",e)
            return output
            raise
        os.chdir(working_dir)
        #subprocess.run(encrypt_custom_command,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        os.chdir(working_dir)

    def video_dash(input_file):
        os.chdir(bin_dir)
        path, file = os.path.split(input_file)
        dash_custom_command = ("./mp4dash " + input_file +" -o "+
                                path +"/dash/")
        try:
            subprocess.check_output(dash_custom_command,shell=True)
            output=("\nOK - File" + input_file + " has been processed into " + path + "/dash/stream.mpd" + "\n\n",1)
            return output
        except subprocess.CalledProcessError as e:
            output=("\nERROR - can't generate the mpd file"+
                    input_file + "\n\n",e)
            return output
            raise
        os.chdir(working_dir)

#We define the table we're going to use
db_name="video_files"
table_name="movie_files"
#Database.__init__(db_name,table_name)

#print(Database.view())
#video_track_number()
working_dir = os.getcwd()
bin_dir=os.getcwd()+"/../bin"
storage_dir=os.getcwd()+"/../storage/"
file="/Users/javierbrines/Documents/Rakuten/video_packaging_platform/BigBuckBunny.mp4"
output_dir=os.getcwd()+"/../output/"
#key="F1998AA4629FB47EFFE1A611659BD6A7"
#kid="59C3308F57ADA6AC1D9D34200C484369"
key="hyN9IKGfWKdAwFaE5pm0qg"
kid="oW5AK5BW43HzbTSKpiu3SQ"

#video_ingest(file)
#prueba=video_ingest(file)
#if (prueba[-1]) == 1:
#    Database.insert_one_row(table_name,"input_content_origin",file)
#    input_content_id=(Database.view_one_value("input_content_id",table_name,"input_content_origin",file))
#    print(input_content_id)
#    Database.update(table_name,"status","Ingested",str(input_content_id))
#else:
#    print(prueba)

#video_fragmentation
#input_content_id=18
#file_for_fragment=(Database.view_one_value("input_content_origin",table_name,"input_content_id",input_content_id))
#print(file_for_fragment)
#prueba=video_fragment(file_for_fragment)
#if (prueba[-1]) == 1:
#    Database.update(table_name,"status","Fragmented",str(input_content_id))
#    AÑADIR PATH SI CAMBIA?
#    print(Database.view_one_value("input_content_id",table_name,"input_content_origin",file))
#else:
#    print(prueba)

#input_content_id=10;
#video_track_number=(Database.view_one_value("video_track_number",table_name,"input_content_id",input_content_id))
#file_to_encrypt=(Database.view_one_value("output_file_path",table_name,"input_content_id",input_content_id))
#video_encrypt(video_track_number,key,kid,file_to_encrypt)


input_file="/Users/javierbrines/Documents/Rakuten/video_packaging_platform/app/../output/KCXP3G/KCXP3G.mp4"
#print(Database.view())
#fragment("origin_file_path",3)
#video_encrypt(video_track_number,key,kid,input_file)
prueba=Video_ops.video_encrypt(2,key,kid,input_file)
if (prueba[-1]) == 1:
    print(prueba)
else:
    print(prueba)

#DASH
#archivo_de_prueba="/Users/javierbrines/Documents/Rakuten/video_packaging_platform/app/../output/KCXP3G/KCXP3G.mp4"
#salida="/archivo/larguisimo/asiodhoia/salida.mpd"
#prueba=Video_ops.video_dash(archivo_de_prueba)
#if (prueba[-1]) == 1:
#    print(prueba)
#else:
#    print(prueba)
