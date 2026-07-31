from django.db import models


class Food(models.Model):
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    image = models.ImageField(upload_to='food_images/')
    description = models.TextField()

    def __str__(self):
        return self.name
