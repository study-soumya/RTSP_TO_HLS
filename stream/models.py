from django.db import models



class Stream(models.Model):
    ip_address = models.GenericIPAddressField()
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    place = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    task_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.ip_address} - {self.place}"