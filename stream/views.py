from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Stream
from .serializers import StreamSerializer
from .tasks import start_stream
from celery.result import AsyncResult
from django.conf import settings



class StreamAPIView(viewsets.ModelViewSet):
    queryset = Stream.objects.all()
    serializer_class = StreamSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            # Extract data for RTSP to HLS conversion
            ip_address = serializer.data.get('ip_address')
            username = serializer.data.get('username')
            password = serializer.data.get('password')

            # Construct RTSP URL
            rtsp_url = f"rtsp://{username}:{password}@{ip_address}"
            output_path = f"{settings.MEDIA_ROOT}/streams/{ip_address}/stream.m3u8"

            # Start the Celery task
            start_stream.delay(rtsp_url, output_path)

            # Return the HLS URL as part of the response
            hls_url = f"{settings.MEDIA_URL}streams/{ip_address}/stream.m3u8"

            return Response(
                {"message": "Stream process initiated.", "hls_url": hls_url},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Restart stream if RTSP details are updated
            if "ip_address" in serializer.validated_data or "username" in serializer.validated_data or "password" in serializer.validated_data:
                ip_address = serializer.data.get('ip_address')
                username = serializer.data.get('username')
                password = serializer.data.get('password')

                # RTSP URL and output path
                rtsp_url = f"rtsp://{username}:{password}@{ip_address}"
                output_path = f"/streams/{ip_address}/stream.m3u8"

                # Start the Celery Task
                start_stream.delay(rtsp_url, output_path)
                
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Stop the Celery task (if it's running)
        if instance.task_id:
            # Use the Celery to revoke or terminate the task
            task_result = AsyncResult(instance.task_id)

            if task_result.state == "PENDING" or task_result.state == "STARTED":
                # Terminate the task if it's running
                stop_stream.delay(instance.task_id)
                instance.is_active = False
                instance.save()

                return Response(
                    {"message": "Stream stopped and task terminated successfully."},
                    status=status.HTTP_204_NO_CONTENT
                )
            else:
                return Response(
                    {"error": "No active task found to stop."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"error": "No active stream found to stop."},
                status=status.HTTP_400_BAD_REQUEST
            )