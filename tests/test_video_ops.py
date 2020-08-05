import os
import subprocess
import sys
import json
from test_database import *
import ntpath
import string
import secrets
import base64
import unittest


# further this exercise, we should consider a file normalisation function
class test_video_ops(unittest.TestCase):

    def setUp(self):
        #
        # CREAR DIRECTORIOS DE PRUEBA
        #
        self.bin_dir = (os.getcwd() + "/../bin")
        self.working_dir = os.getcwd()
        self.storage_dir = os.getcwd() + "/../storage/"
        self.input_file1 = os.getcwd() + "/TEST_VIDEOS/BigBuckBunny.mp4"
        self.input_file2 = os.getcwd() + "/TEST_VIDEOS/BigBuckBunny_10sec.mp4"
        self.input_file3 = os.getcwd() + "/TEST_VIDEOS/BigBuckBunny_10sec_frag.mp4"
        self.input_file4 = os.getcwd() + "/TEST_VIDEOS/BigBuckBunny_10sec_frag.mp4"
        # #4 = os.getcwd() + ""
        self.output_dir = os.getcwd() + "/../output/"
        self.key = "hyN9IKGfWKdAwFaE5pm0qg"
        self.kid = "oW5AK5BW43HzbTSKpiu3SQ"
        self.video_track_number = 2

    def test_video_ingest(self):
        os.chdir(self.bin_dir)
        """ Export the Video metadata into a JSON """
        try:
            subprocess.check_output("./mp4info {} --format json > out.json".
                                    format(self.input_file1), shell=True)
        except subprocess.CalledProcessError as e:
            output = ("ERROR - Corrupted or wrong file, please review the file. Details:"
                      + '\n' + '\n', e)
            return output
        """ Check the metadata and search for video tracks """
        with open('out.json') as f:
            data = json.load(f)
            items = data.get('tracks')
            video_found_flag = 0
            for item in items:
                if item.get('type') == 'Video':
                    video_found_flag = 1
                    video_track_number = (item.get('id'))
                    os.chdir(self.working_dir)
                    """ When a video track is found, return the Track ID and put file into storage """
                    try:
                        subprocess.check_output("mv {}".format(self.input_file1) + " {}".
                                                format(self.storage_dir), shell=True)
                        file_name = ntpath.basename(self.input_file1)
                        # DATABASE - we add 1 as confirmation process went good!
                        output = ("OK - File " + self.input_file1 +
                                  " has been processed and moved to storage", video_track_number, 1)
                        return output
                    except subprocess.CalledProcessError as e:
                        output = ("\nERROR - can't move the file to storage\n\n", e)
                        return output
                        raise
            if video_found_flag == 0:
                output = ("ERROR - An error has been occured, file doesn't contain an audio track ")
                return output

    def test_video_fragment(self):
        output_code = ''.join(secrets.choice(string.ascii_uppercase +
                                             string.digits) for _ in range(6))
        output_file_path = self.output_dir + output_code + "/" + output_code + ".mp4"
        os.chdir(self.output_dir)
        os.mkdir(output_code, mode=0o0755)
        os.chdir(self.bin_dir)
        """ Then the video fragmentation process uses its output as name encryption """
        fragment_custom_command = ("./mp4fragment " + str(self.input_file2) + " " +
                                   output_file_path)
        try:
            # subprocess.check_output(fragment_custom_command, shell=True)
            output = ("OK - File " + str(self.input_file2) + " has been fragmented and is ready to encrypt\n\n",
                      str(output_file_path), 1)
            return output
        except subprocess.CalledProcessError as e:
            output = ("\nERROR - can't fragment the video file" +
                      self.input_file2 + "\n\n", e)
            return output
            raise
        os.chdir(working_dir)

    def test_video_encrypt(self):
        os.chdir(self.bin_dir)
        string1 = (self.key + "==")
        video_key = (base64.b64decode(string1).hex())
        string2 = (self.kid + "==")
        video_kid = (base64.b64decode(string2).hex())
        output_file_path = (os.path.splitext(self.input_file3)[0]) + "_enc.mp4"
        encrypt_custom_command = ("./mp4encrypt --method MPEG-CBCS --key " +
                                  str(self.video_track_number) + ":" + video_key +
                                  ":random " + "--property " +
                                  str(self.video_track_number) + ":KID:" + video_kid +
                                  " " + str(self.input_file3) + " " + output_file_path)
        try:
            subprocess.check_output(encrypt_custom_command, shell=True)
            output = ("\nOK - File" + str(self.input_file3) +
                      " has been encrypted with key:" + self.key + "kid:" + self.kid,
                      output_file_path, 1)
            return output
        except subprocess.CalledProcessError as e:
            output = ("\nERROR - can't encrypt the video file" +
                      self.input_file3 + "\n\n", e)
            return output
            raise
        os.chdir(working_dir)

    def test_video_dash(self):
        os.chdir(self.bin_dir)
        path, file = os.path.split(self.input_file4)
        dash_custom_command = ("./mp4dash " + self.input_file4 + " -o " +
                               path + "/dash/")
        try:
            subprocess.check_output(dash_custom_command, shell=True)
            dash_output = path + "/dash/stream.mpd"
            output = ("OK - File" + self.input_file4 + " has been processed into " +
                      dash_output, dash_output, 1)
            return output
        except subprocess.CalledProcessError as e:
            output = ("\nERROR - can't generate the mpd file" +
                      self.input_file4 + "\n\n", e)
            return output
            raise
        os.chdir(self.working_dir)


if __name__ == '__main__':
    unittest.main()
