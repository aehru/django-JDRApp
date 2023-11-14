from django.conf import settings
from django.db import models

class Campaign(models.Model):
    master = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    universe = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.universe}), mastered by {self.master}"

class Character(models.Model):
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    alias = models.CharField(max_length=25, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
