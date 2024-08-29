from django.db import models
import datetime

# Create your models here.
class Game(models.Model):
    white_player = models.CharField(max_length=64)
    black_player = models.CharField(max_length=64)
    result = models.CharField(max_length=16)
    date = models.DateField(default=datetime.date.today)

    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f'{self.white_player} vs {self.black_player}: {self.result}'