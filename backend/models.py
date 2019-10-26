from django.db import models
from django.db.models import signals


class Item(models.Model):
    name = models.CharField("Name", max_length=20)
    points = models.PositiveIntegerField("Points")
    quantity = models.PositiveIntegerField("Quantity", default=0)

    def __str__(self):
        return self.name


    class Meta:
        ordering = ["-points",]


class Inventory(models.Model):
    items = models.ManyToManyField(Item)


class LastLocation(models.Model):
    latitude = models.DecimalField("Latitude", max_digits=50, decimal_places=30, default=0)
    longitude = models.DecimalField("Longitude", max_digits=50, decimal_places=30, default=0)


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

def survivor_pre_save(signal, instance, sender, **kwargs):
    if instance.inventory_id is not None:
        items = []
        for item in instance.inventory.items.all():
            items.append(item.name)
        if not "Water" in items:
            water = Item.objects.create(name="Water", points=4, quantity=0)
            instance.inventory.items.add(water)
        if not "Food" in items:
            food = Item.objects.create(name="Food", points=3)
            instance.inventory.items.add(food)
        if not "Medication" in items:
            medication = Item.objects.create(name="Medication", points=2)
            instance.inventory.items.add(medication)
        if not "Ammunition" in items:
            ammunition = Item.objects.create(name="Ammunition", points=1)
            instance.inventory.items.add(ammunition)
        if instance.infected == True or instance.reported_infected > 0:
            instance.delete()
            raise Exception("Impossible to register zoombies!")

signals.pre_save.connect(survivor_pre_save, sender=Survivor)
