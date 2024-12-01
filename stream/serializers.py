from rest_framework import serializers
from .models import *


class StreamSerializer(serializers.ModelSerializer):
    hls_url = serializers.SerializerMethodField()
    class Meta:
        model = Stream
        fields = ['id', 'ip_address', 'username', 'password', 'place', 'hls_url']

    def get_hls_url(self, obj):
        # Construct the HLS URL
        return f"/streams/{obj.ip_address}/stream.m3u8"