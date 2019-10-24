from django.db import models
from django.db.models import signals


class Item(models.Model):
    name = models.CharField("Name", max_length=20)
    points = models.PositiveIntegerField("Points")
    quantity = models.PositiveIntegerField("Quantity", default=0)

    def __str__(self):
        return self.name


class Inventory(models.Model):
    items = models.ManyToManyField(Item)


class LastLocation(models.Model):
    latitude = models.DecimalField("Latitude", max_digits=50, decimal_places=30)
    longitude = models.DecimalField("Longitude", max_digits=50, decimal_places=30)


class Survivor(models.Model):
    name = models.CharField("Name", max_length=100)
    age = models.PositiveIntegerField("Age")
    gender = models.CharField("Gender", max_length=25)
    last_location = models.ForeignKey(LastLocation, null=True, on_delete=models.CASCADE)
    inventory = models.ForeignKey(Inventory, null=True, on_delete=models.CASCADE)
    infected = models.BooleanField("Infected", default=False)
    reported_infected = models.PositiveIntegerField("Reported Infected", default=0)

    def __str__(self):
        return self.name

def survivor_post_save(signal, instance, sender, **kwargs):
    inventory = Inventory.objects.create()
    water = Item.objects.create(name="Water", points=4, quantity=0)
    food = Item.objects.create(name="Food", points=3, quantity=0)
    medication = Item.objects.create(name="Medication", points=2, quantity=0)
    ammunition = Item.objects.create(name="Ammunition", points=1, quantity=0)
    for item in [water, food, medication, ammunition]:
        inventory.items.add(item)
    instance.inventory_id = inventory.id
    instance.save()

signals.post_save.connect(survivor_post_save, sender=Survivor)
