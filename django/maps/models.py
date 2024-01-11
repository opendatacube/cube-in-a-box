from django.db import models

class BoundingBox(models.Model):
    lat = models.FloatField()
    long = models.FloatField()
    # Outros campos conforme necessário

    def __str__(self):
        return f"{self.latitude}, {self.longitude}"
