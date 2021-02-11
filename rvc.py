 #  #
######
 #  #    Robust Video Compress  --  by Manuel Fischer
######
 #  #

import sys, os
import subprocess

USAGE = """-- Robust Video Compress --

USAGE: rvc <directory>"

The script creates a subdirectory inside <directory> that is called
compressed. All files in <directory> get compressed with ffmpeg.

If the execution was stopped, the script can be reexecuted with the
same parameters to continue. It rembembers to redo files by simply
storing an empty file in the filesystem to mark that a file is not
completed.

The script is based on ffmpeg and ffprobe, keep sure that you have
installed these programs
"""

__doc__ = """Robust Video Compress (RVC)
Robust script to compress video files in a directory

You need to install ffmpeg and ffprobe
"""

#FFMPEG_OPTS = "-hwaccel cuda" # find out acceleration methods with just ffmpeg -hwaccels
#FFMPEG_OPTS = "-hwaccel vulkan" # not really doing anything on my machine
FFMPEG_OPTS = ""

#FFMPEG_OPTS += " -hide_banner -loglevel error"
FFMPEG_SILENT_OPTS = "-v quiet -stats"
FFMPEG_OPTS += FFMPEG_SILENT_OPTS

def cmd(command):
    print(f"[ |{command}]")
    process = subprocess.run(command)
    print(f"[/|{command}] = {process.returncode}")
    process.check_returncode()
    
    #if result != 0: raise SystemError(f"Command failed with exit code {result}")

def video_duration(file):
    pipe = subprocess.Popen(f"ffprobe -i {file}", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    text = pipe.communicate()[1].decode("utf-8")
    pos = text.find("Duration: ")
    pos2 = text.find(",", pos+10)
    return text[pos+10 : pos2]
    

def compress(input, output):
    output_incomplete = output+".incomplete"
    if os.path.exists(output) \
       and not os.path.exists(output_incomplete):
        # do not compress again
        print(f"{output} already compressed")
    else:
        with open(output_incomplete, "w"): pass # create empty output_incomplete file
        print(f"Duration: {video_duration(input)}")
        cmd(f"ffmpeg {FFMPEG_OPTS} -i {input} -vcodec h264 -acodec aac {output}")
        os.remove(output_incomplete)
        
    input_size = os.path.getsize(input)
    output_size = os.path.getsize(output)
    print(f"Ratio of files {output_size:12}/{input_size:<12} = {(output_size/input_size)*100:#5.2f} %")
    input_dur = video_duration(input)
    output_dur = video_duration(output)
    if input_dur != output_dur:
        print(f"Warning, durations differ: in {input_dur}, out {output_dur}")
    

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(USAGE)
    else:
        dir = sys.argv[1]
        subdir = os.path.join(dir, "compressed")
        print("Compressed video files show up in", subdir)
        print("Do not run this command multiple times at once")
        try: os.mkdir(subdir)
        except FileExistsError: pass

        for f in os.listdir(dir):
            if os.path.isfile(os.path.join(dir, f)):
                compress(os.path.join(dir, f), os.path.join(subdir, f))
