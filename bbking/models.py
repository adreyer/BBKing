from django.db  import models


class WordFilter(models.Model):
    name = models.CharField(max_length=40)
    base_re = models.CharField(max_length=500)
    base_replace = models.CharField(max_length=500)
    active = models.BooleanField(default=True)
    ignore_case = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)

    def __str__(self):
        return self.name
