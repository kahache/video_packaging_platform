__author__ = "The One & Only Javi"
__version__ = "1.0.0"
__start_date__ = "25th July 2020"
__end_date__ = "5th August 2020"
__maintainer__ = "me"
__email__ = "little_kh@hotmail.com"
__requirements__ = "Bento4 tools, subprocess"
__status__ = "Production"
__description__ = """
This is the Video Operations module.
It can extract metadata, fragment, encrypt and transcode into MPEG-DASH
It's a dumb module, it doesn't work with databases. It only needs the Bento4
binaries.
"""

import os
import subprocess
import sys
import json
from database import *
import ntpath
import string
import secrets
import base64


class Video_ops:
    """ Contains individual methods, in order to process a video file """

    def video_ingest(input_file):
        os.chdir(bin_dir)
        Video_ops.export_into_json(input_file)
        """ Export the Video metadata into a JSON """
        # try:
        #     subprocess.check_output("./mp4info {} --format json > out.json".
        #                             format(input_file), shell=True)
        # except subprocess.CalledProcessError as e:
        #     output = (
        #         "ERROR - Corrupted or wrong file, please review the file. "
        #         "Details:"
        #         + '\n' + '\n', e)
        #     return output
        #     raise
        """ Check the metadata and search for video tracks """
        with open('out.json') as f:
            data = json.load(f)
            items = data.get('tracks')
            video_found_flag = 0
            for item in items:
                if item.get('type') == 'Video':
                    video_found_flag = 1
                    video_track_number = (item.get('id'))
                    os.chdir(working_dir)
                    """When a video track is found, return the Track ID and
                    put file into storage"""
                    return Video_ops.export_into_json(input_file)
                    # try:
                    #     subprocess.check_output(
                    #         "mv {}".format(input_file) + " {}".
                    #         format(storage_dir), shell=True)
                    #     file_name = ntpath.basename(input_file)
                    #     # DATABASE - we add 1 as confirmation process went
                    #     # good!
                    #     output = ("OK - File " + input_file +
                    #               " has been processed and moved to storage",
                    #               video_track_number, 1)
                    #     return output
                    # except subprocess.CalledProcessError as e:
                    #     output = (
                    #         "\nERROR - can't move the file to storage\n\n", e)
                    #     return output
                    #     raise
            if video_found_flag == 0:
                output = (
                    "ERROR - An error has been occured, file doesn't contain "
                    "an audio track ")
                return output

    def video_fragment(input_file):
        """
        Fragments the video. Step needed for future processes.
        It will also rename + move the file into storage/folder
        with encrypted name.
        """
        # First, generation of encrypted folder/file name
        output_code = ''.join(secrets.choice(string.ascii_uppercase +
                                             string.digits) for _ in range(6))
        output_file_path = \
            output_dir + output_code + "/" + output_code + ".mp4"
        os.chdir(output_dir)
        os.mkdir(output_code, mode=0o0755)
        os.chdir(bin_dir)
        """Then the video fragmentation process uses its output as name
        encryption"""
        fragment_custom_command = ("./mp4fragment " + str(input_file) + " " +
                                   output_file_path)
        try:
            subprocess.check_output(fragment_custom_command, shell=True)
            output = ("OK - File " + input_file +
                      " has been fragmented and is ready to encrypt\n\n",
                      output_file_path, 1)
            return output
        except subprocess.CalledProcessError as e:
            output = ("\nERROR - can't fragment the video file" +
                      input_file + "\n\n", e)
            return output
            raise
        os.chdir(working_dir)

    def video_encrypt(video_track_number, key, kid, input_file):
        """
        It encrypts the video track of a video file, using AES CBCS encryption
        with a KEY and KID given.
        """
        # First, translation of the keys into Base64 + naming of the output
        os.chdir(bin_dir)
        string1 = (key + "==")
        video_key = (base64.b64decode(string1).hex())
        string2 = (kid + "==")
        video_kid = (base64.b64decode(string2).hex())
        output_file_path = (os.path.splitext(input_file)[0]) + "_enc.mp4"
        # Then, encryption is launched
        encrypt_custom_command = ("./mp4encrypt --method MPEG-CBCS --key " +
                                  str(video_track_number) + ":" + video_key +
                                  ":random " + "--property " +
                                  str(
                                      video_track_number) + ":KID:" +
                                  video_kid +
                                  " " + input_file + " " + output_file_path)
        try:
            subprocess.check_output(encrypt_custom_command, shell=True)
            output = ("\nOK - File" + input_file +
                      " has been encrypted with key:" + key + "kid:" + kid,
                      output_file_path, 1)
            return output
        except subprocess.CalledProcessError as e:
            output = ("\nERROR - can't encrypt the video file" +
                      input_file + "\n\n", e)
            return output
            raise
        os.chdir(working_dir)

    def video_dash(input_file):
        """ Simple transcoding from the input video into a MPEG-DASH output """
        os.chdir(bin_dir)
        path, file = os.path.split(input_file)
        dash_custom_command = ("./mp4dash " + input_file + " -o " +
                               path + "/dash/")
        try:
            subprocess.check_output(dash_custom_command, shell=True)
            dash_output = path + "/dash/stream.mpd"
            list_dict = Video_ops.splitall(dash_output)
            dash_url = ("http://localhost:8080/" + list_dict[-3] + "/" +
                        list_dict[-2] + "/" + list_dict[-1])
            output = ("OK - File" + input_file + " has been processed into " +
                      dash_output, dash_output, dash_url, 1)
            return output
        except subprocess.CalledProcessError as e:
            output = ("\nERROR - can't generate the mpd file" +
                      input_file + "\n\n", e)
            return output
            raise
        os.chdir(working_dir)

    def splitall(path):
        """ Simple path splitting for last URL output """
        allparts = []
        while 1:
            parts = os.path.split(path)
            if parts[0] == path:  # sentinel for absolute paths
                allparts.insert(0, parts[0])
                break
            elif parts[1] == path:  # sentinel for relative paths
                allparts.insert(0, parts[1])
                break
            else:
                path = parts[0]
                allparts.insert(0, parts[1])
        return allparts

    def export_into_json(input_file):
        """ Export the Video metadata into a JSON """
        try:
            subprocess.check_output("./mp4info {} --format json > out.json".
                                    format(input_file), shell=True)
        except subprocess.CalledProcessError as e:
            output = (
                "ERROR - Corrupted or wrong file, please review the file. "
                "Details:"
                + '\n' + '\n', e)
            return output
            raise
    def move_into_storage(input_file):
        try:
            subprocess.check_output(
                "mv {}".format(input_file) + " {}".
                format(storage_dir), shell=True)
            file_name = ntpath.basename(input_file)
            # DATABASE - we add 1 as confirmation process went
            # good!
            output = ("OK - File " + input_file +
                      " has been processed and moved to storage",
                      video_track_number, 1)
            return output
        except subprocess.CalledProcessError as e:
            output = (
                "\nERROR - can't move the file to storage\n\n", e)
            return output
            raise


# We define the folders as variables
working_dir = os.getcwd()
bin_dir = os.getcwd() + "/../bin"
storage_dir = os.getcwd() + "/../storage/"
output_dir = os.getcwd() + "/../output/"

# For the future:
# Further this exercise, we should consider a file normalisation function
