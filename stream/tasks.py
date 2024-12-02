from celery import shared_task
import signal
from django.conf import settings
import os
import subprocess
from .models import Stream

@shared_task
def start_stream(rtsp_url, output_path):
    full_output_path = os.path.join(settings.MEDIA_ROOT, output_path)
    os.makedirs(os.path.dirname(full_output_path), exist_ok=True)

    command = [
        "ffmpeg", "-i", rtsp_url,
        "-c:v", "libx264", "-preset", "veryfast", "-f", "hls",
        full_output_path
    ]
    try:
        subprocess.run(command, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr.decode()}")
      

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