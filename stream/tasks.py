from celery import shared_task
import subprocess
import os
import signal
from .models import Stream


@shared_task
def start_stream(rtsp_url, output_path):
    os.makedirs(os.path.dirname(output_path),exist_ok=True)
    command = [
        "ffmpeg", "-i", rtsp_url, "-c:v", "libx264", "-preset", "veryfast", "-f", "hls", output_path
    ]

    try:
        subprocess.run(command, check=True)
        return {"status": "success", "output": output_path}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": str(e)}
    

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