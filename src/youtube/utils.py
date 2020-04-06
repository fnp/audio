import subprocess
from tempfile import NamedTemporaryFile


def video_from_image(img_path, duration, fps=25):
    tmp = NamedTemporaryFile(prefix='image', suffix='.mkv', delete=False)
    tmp.close()
    subprocess.run(
        ['ffmpeg', '-y', '-framerate', f'1/{duration}',  '-i', img_path, '-c:v', 'libx264', '-vf', f'fps={fps},format=yuv420p', tmp.name], check=True)
    return tmp.name


def cut_video(video_path, duration):
    tmp = NamedTemporaryFile(prefix='cut', suffix='.mkv', delete=False)
    tmp.close()
    subprocess.run(
        ['ffmpeg', '-y', '-i', video_path, '-t', str(duration), tmp.name], check=True)
    return tmp.name


def concat_videos(paths):
    filelist = NamedTemporaryFile(prefix='concat', suffix='.txt')
    for path in paths:
        filelist.write(f"file '{path}'\n".encode('utf-8'))
    filelist.flush()

    output = NamedTemporaryFile(prefix='concat', suffix='.mkv', delete=False)
    output.close()
        
    subprocess.run(
        ['ffmpeg', '-y', '-safe', '0', '-f', 'concat', '-i', filelist.name, '-c', 'copy', output.name],
        check=True)

    filelist.close()
    return output.name


def mux(channels, output_path=None):
    if not output_path:
        output = NamedTemporaryFile(prefix='concat', suffix='.mkv', delete=False)
        output.close()
        output_path = output.name
    args = ['ffmpeg']
    for c in channels:
        args.extend(['-i', c])
    args.extend(['-shortest', '-y', output_path])
    subprocess.run(args, check=True)
    return output_path


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
