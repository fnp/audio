import os
import shutil
import subprocess
from tempfile import NamedTemporaryFile
from django.conf import settings


FILE_CACHE = getattr(settings, 'FILE_CACHE', 'file_cache/')


def link_or_copy(src, dst):
    dstdir = os.path.dirname(dst)
    if not os.path.exists(dstdir):
        os.makedirs(dstdir)
    if os.path.exists(dst):
        os.unlink(dst)
        # FIXME: tiny window here when the temp path is not taken.
    try:
        os.link(src, dst)
    except OSError:
        shutil.copyfile(src, dst)


def process_to_file(cmdline, prefix='', suffix='', cache_key=None, output_path=None):
    if not output_path:
        tmp = NamedTemporaryFile(prefix=prefix, suffix=suffix, delete=False)
        tmp.close()
        output_path = tmp.name

    if cache_key:
        cache_path = FILE_CACHE + cache_key.replace('/', '__')

    if cache_key and os.path.exists(cache_path):
        link_or_copy(cache_path, output_path)
    else:
        # Actually run the processing.
        subprocess.run(cmdline + [output_path], check=True)
        if cache_key:
            link_or_copy(output_path, cache_path)

    return output_path


def video_from_image(img_path, duration, fps=25, cache=True):
    return process_to_file(
        ['ffmpeg', '-y', '-loop', '1', '-t', str(duration), '-i', img_path, '-c:v', 'libx264', '-vf', f'fps={fps},format=yuv420p'],
        'image-',
        '.mkv',
        f'video_from_image:{img_path}:{duration}:{fps}.mkv' if cache else None
    )


def cut_video(video_path, duration):
    return process_to_file(
        ['ffmpeg', '-y', '-i', video_path, '-t', str(duration), '-c', 'copy'],
        'cut-',
        '.mkv'
    )


def ffmpeg_concat(paths, suffix, copy=False):
    filelist = NamedTemporaryFile(prefix='concat-', suffix='.txt')
    for path in paths:
        filelist.write(f"file '{path}'\n".encode('utf-8'))
    filelist.flush()

    args = ['ffmpeg', '-y', '-safe', '0', '-f', 'concat', '-i', filelist.name]
    if copy:
        args += ['-c', 'copy']
    outname = process_to_file(args, 'concat-', suffix)

    filelist.close()
    return outname


def concat_videos(paths):
    return ffmpeg_concat(paths, '.mkv', copy=True)


def concat_audio(paths):
    return ffmpeg_concat(paths, '.flac')


def standardize_audio(p, cache=True):
    return process_to_file(
        ['ffmpeg', '-y', '-i', p, '-sample_fmt', 's16', '-acodec', 'flac', '-ac', '2', '-ar', '44100'],
        'standardize-', '.flac',
        f'standardize_audio:{p}.flac' if cache else None
    )


def standardize_video(p, cache=True):
    return process_to_file(
        ['ffmpeg', '-y', '-i', p],
        'standardize-', '.mkv',
        f'standardize_video:{p}.mkv' if cache else None
    )


def mux(channels, output_path=None):
    args = ['ffmpeg', '-y']
    for c in channels:
        args.extend(['-i', c])
    args.extend(['-c', 'copy'])
    return process_to_file(args, 'mux-', '.mkv', output_path=output_path)


def get_duration(path):
    return float(
        subprocess.run(
            [
                "ffprobe",
                "-i",
                path,
                "-show_entries",
                "format=duration",
                "-v",
                "quiet",
                "-of",
                "csv=p=0",
            ],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    )


def get_framerate(path):
    rates = subprocess.run(
            [
                "ffprobe",
                "-i",
                path,
                "-show_entries",
                "stream=r_frame_rate",
                "-v",
                "quiet",
                "-of",
                "csv=p=0",
            ],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip().split('\n')
    for rate in rates:
        a, b = rate.split('/')
        if b == '1':
            return int(a)
