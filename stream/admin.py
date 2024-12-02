from django.contrib import admin
from .models import Stream

# Customizing the admin interface for the Stream model
class StreamAdmin(admin.ModelAdmin):
    list_display = ('id', 'ip_address', 'username', 'place', 'is_active', 'hls_url')
    list_filter = ('is_active',)  # Allows filtering by active status
    search_fields = ('ip_address', 'place', 'username')  # Enables search by ip_address, place, and username
    ordering = ('-id',)  # Orders the streams by ID in descending order
    readonly_fields = ('hls_url',)  # Makes the hls_url field read-only in the admin panel
    
    def hls_url(self, obj):
        # This method generates the HLS URL for the stream in the admin panel
        return f"http://127.0.0.1:8000/media/streams/{obj.ip_address}/stream.m3u8"
    hls_url.short_description = 'HLS Stream URL'  # Add a label for this method in the admin interface

# Register the Stream model and the custom admin interface
admin.site.register(Stream, StreamAdmin)
