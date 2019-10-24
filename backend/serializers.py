from rest_framework import serializers
from .models import Item, Inventory, LastLocation, Survivor


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['name', 'points', 'quantity']


class InventorySerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, read_only=True)


    class Meta:
        model = Inventory
        fields = ['items']


class LastLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LastLocation
        fields = ['latitude', 'longitude']


class SurvivorSerializer(serializers.ModelSerializer):
    last_location = LastLocationSerializer(many=False, read_only=True)
    inventory = InventorySerializer(many=False, read_only=True)


    class Meta:
        model = Survivor
        fields = ['id', 'name', 'age', 'gender', 'last_location', 'inventory', 'infected', 'reported_infected']
