from celery import shared_task
import signal
from django.conf import settings
import os
import subprocess
from .models import Stream

from celery import shared_task
import subprocess
import os
from django.conf import settings

@shared_task
def start_stream(rtsp_url, output_path):
    try:
        # Ensure the output path exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # FFmpeg command to convert RTSP to HLS
        command = [
            'ffmpeg',
            '-i', rtsp_url,         # Input RTSP stream URL
            '-c:v', 'libx264',       # Video codec
            '-c:a', 'aac',           # Audio codec
            '-f', 'hls',             # Format HLS
            '-hls_time', '10',       # Segment duration in seconds
            '-hls_list_size', '6',   # Keep 6 segments in the playlist
            '-hls_wrap', '10',       # Loop the playlist after 10 segments
            '-start_number', '1',    # Start numbering from 1
            output_path              # Output path for the HLS files
        ]
        
        # Run FFmpeg command
        subprocess.run(command, check=True)

        return f"Stream saved to {output_path}"

    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        return f"Error converting stream: {e}"

      

@shared_task
def stop_stream(task_id):
    try:
        # Find the stream by the task_id (assuming it's stored in the Stream model)
        stream = Stream.objects.get(task_id=task_id)

        # Check if the process is running (based on the pid in the Stream model)
        if stream.pid:
            os.kill(stream.pid, signal.SIGTERM)     # Gracefully terminate the FFmpeg process

            stream.is_active = False    # Mark the stream as inactive
            stream.save()

            return f"Stream {stream.id} stopped successfully."
        else:
            return f"Stream {stream.id} does not have a valid PID."
    except Stream.DoesNotExist:
        return f"No stream found with task_id {task_id}"