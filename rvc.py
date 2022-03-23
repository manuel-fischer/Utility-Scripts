 #  #
######
 #  #    Robust Video Compress  --  by Manuel Fischer
######
 #  #

import sys, os
import subprocess

USAGE = """-- Robust Video Compress --

USAGE: rvc <directory> [:: <ext1>:<ext2>... ::] <ffmpeg-options> [-- <ffmpeg-output-opts>]"

The script creates a subdirectory inside <directory> that is called
compressed. All files in <directory> get compressed with ffmpeg.

If the execution was stopped, the script can be reexecuted with the
same parameters to continue. It rembembers to redo files by simply
storing an empty file in the filesystem to mark that a file is not
completed.

The script is based on ffmpeg and ffprobe, keep sure that you have
installed these programs

If some video files get ignored, edit the variable VIDEO_FILES
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
FFMPET_WARNING_OPTS = "-v warning -stats"
FFMPEG_OPTS += FFMPET_WARNING_OPTS

VIDEO_FILES = "mp4 m4v mov wmv avi flv webm mkv".lower().split()

IMAGE_FILES = "png gif".lower().split()

COMPRESS_FILES = VIDEO_FILES + IMAGE_FILES

USE_COMMA = True

def flt2str(flt, prec=3):
    s = f"{flt:.{prec}f}"
    if USE_COMMA:
        s = s.replace(".", ",")
    return s

def fltdiff2str(a, b):
    return f"{flt2str((b-a)*100/(a or 1), 2)}%"

def dur2str(dur):
    return dur

def dur2int(dur):
    return sum(float(e)*60**i for i, e in enumerate(dur.split(':')))

def durdiff2str(a, b):
    return fltdiff2str(dur2int(a), dur2int(b))


class CompressionLogger:
    def __init__(self, dir):
        self.dir = dir
    
    def __enter__(self):
        self.logger = None
        self.initialized = False
        return self

    def lazy_init(self):
        if not self.initialized:
            self.initialized = True
            self.logger = open(os.path.join(self.dir, "rvc.csv"), "wt")
            self.print("ifn;ofn;ifsz;ofsz;fsz%;idur;odur;dur%;ikfrm;okfrm;frm%")

    def print(self, *a, **kv):
        self.lazy_init()
        print(*a, **kv, file=self.logger)

    def print_stat(self,
                   input_fn, output_fn,
                   input_size, output_size,
                   input_dur, output_dur,
                   input_gop, output_gop):
        self.print(";".join((input_fn, output_fn,
                             str(input_size), str(output_size), fltdiff2str(input_size, output_size),
                             dur2str(input_dur), dur2str(output_dur), durdiff2str(input_dur, output_dur),
                             flt2str(input_gop), flt2str(output_gop), fltdiff2str(input_gop, output_gop)
                             )))

    def __exit__(self, *a, **kv):
        if self.logger: self.logger.close()



def ffmpeg_opts(file):
    # key frame interval, useful for static videos
    GOPSIZE = 100 # 25 fps -- 4 sec interval
    return "-x264opts keyint={GOPSIZE}:min-keyint={GOPSIZE}:scenecut=-1"

#ESCAPE_CHAR = "^" if os.name == "nt" else "\\"
def escape_filename(filename):
    #return filename.replace(" ", ESCAPE_CHAR + " ")
    if " " in filename:
        return f'"{filename}"'
    return filename

def cmd(command):
    print(f"[ |{command}]")
    process = subprocess.run(command)
    print(f"[/|{command}] = {process.returncode}")
    process.check_returncode()
    
    #if result != 0: raise SystemError(f"Command failed with exit code {result}")

def is_video_file(filename):
    name, ext = os.path.splitext(filename)
    assert not ext or ext[0] == "."
    return ext[1:] in VIDEO_FILES

def is_compress_file(filename):
    name, ext = os.path.splitext(filename)
    assert not ext or ext[0] == "."
    return ext[1:] in COMPRESS_FILES

def video_duration(file):
    pipe = subprocess.Popen(f"ffprobe -i {escape_filename(file)}", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    text = pipe.communicate()[1].decode("utf-8")
    pos = text.find("Duration: ")
    pos2 = text.find(",", pos+10)
    return text[pos+10 : pos2]

def key_frame_interval(file):
    # https://stackoverflow.com/questions/18085458/checking-keyframe-interval
    pipe = subprocess.Popen(f"ffprobe -loglevel error -select_streams v:0 -show_entries packet=pts_time,flags -of csv=print_section=0 {escape_filename(file)}",
    #pipe = subprocess.Popen(f"ffprobe -loglevel error -skip_frame nokey -select_streams v:0 -show_entries frame=pkt_pts_time -of csv=print_section=0 {file}",
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
#    text = pipe.communicate()[0].decode("utf-8")
#    frames = (float(line[:line.find(",")]) for line in text.split("\n") if "K" in line)
#
#    frames = iter(frames)
#    
#    num_keyframes = 0
#    last_frame = None
#    for frame in frames:
#        last_frame = frame
#        num_keyframes += 1
#    return last_frame / num_keyframes if last_frame is not None else 0.
    num_keyframes = 0
    last_frame = 0
    while num_keyframes < 100 and not pipe.poll():
        line = pipe.stdout.readline()
        if not line: break
        line = line.decode("utf-8").strip()
        if "K" in line:
            num_keyframes += 1
            try:
                last_frame = float(line[:line.find(",")])
            except ValueError:
                last_frame = 0
    pipe.terminate()

    return last_frame/(num_keyframes or 1)

def compress(log, input, output, ffmpeg_opts, ffmpeg_opts2):
    output_incomplete = output+".incomplete"
    if os.path.exists(output) \
       and not os.path.exists(output_incomplete):
        # do not compress again
        print(f"{output} already compressed")
    else:
        with open(output_incomplete, "w"): pass # create empty output_incomplete file
        print(f"Duration: {video_duration(input)}")
        if is_video_file(output):
            format_opts = "-vcodec h264 -acodec aac"
        else:
            format_opts = ""

            
        try:
            cmd(f"ffmpeg {FFMPEG_OPTS} {ffmpeg_opts} -i {escape_filename(input)} {format_opts} {ffmpeg_opts2} {escape_filename(output)}")
        except:
            import traceback
            traceback.print_exc()
            return
        else:
            os.remove(output_incomplete)
        
    input_size = os.path.getsize(input)
    output_size = os.path.getsize(output)
    print(f"Ratio of files {output_size:12}/{input_size:<12} = {(output_size/input_size)*100:#6.2f} %")
    input_dur = video_duration(input)
    output_dur = video_duration(output)
    if input_dur != output_dur:
        print(f"Warning, durations differ: in {input_dur}, out {output_dur}")

    input_gop = key_frame_interval(input)
    output_gop = key_frame_interval(output)
    print(f"Keyframe ratio (out/in): {output_gop:#6.2f}/{input_gop:<6.2f} = {(output_gop/(input_gop or 1))*100:#6.2f} %")

    log.print_stat(input, output,
                   input_size, output_size,
                   input_dur, output_dur,
                   input_gop, output_gop)
    

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(USAGE)
    else:
        dir = sys.argv[1]

        map_ext = {}

        opts = sys.argv[2:]
        if opts:
            if opts[0] == "::":
                opts = opts[1:]
                while opts:
                    opt, opts = opts[0], opts[1:]
                    if opt == "::": break
                    else:
                        old, new = opt.split(":")
                        map_ext[old] = new

        print(map_ext)
        
        try: split_pos = opts.index("--")
        except ValueError: split_pos = len(opts)
        ffmpeg_opts  = " ".join(opts[:split_pos])
        ffmpeg_opts2 = " ".join(opts[split_pos+1:])
        subdir = os.path.join(dir, "compressed")
        print("Compressed video files show up in", subdir)
        print("Do not run this command multiple times at once")
        try: os.mkdir(subdir)
        except FileExistsError: pass

        with CompressionLogger(dir) as log:
            for f in os.listdir(dir):
                if os.path.isfile(os.path.join(dir, f)):
                    if is_compress_file(f):
                        ifn = os.path.join(dir, f)
                        ofn = os.path.join(subdir, f)
                        off, ofx = os.path.splitext(ofn)
                        ofx = ofx[1:]
                        if ofx in map_ext:
                            print("extension replacement {ofx} -> {map_ext[ofx]}")
                            ofn = off + os.extsep + map_ext[ofx]
                        compress(log, ifn, ofn, ffmpeg_opts, ffmpeg_opts2)
                    else:
                        print(f"ignoring {f}, it is not a video file")
