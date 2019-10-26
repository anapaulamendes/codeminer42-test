from rest_framework import serializers
from .models import Item, Inventory, LastLocation, Survivor


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'points', 'quantity']


class InventorySerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True)


    class Meta:
        model = Inventory
        fields = ['id', 'items']


class LastLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LastLocation
        fields = ['id', 'latitude', 'longitude']


class SurvivorSerializer(serializers.ModelSerializer):
    last_location = LastLocationSerializer(many=False)
    inventory = InventorySerializer(many=False)


    class Meta:
        model = Survivor
        fields = ['id', 'name', 'age', 'gender', 'last_location', 'inventory', 'infected', 'reported_infected']

    def validate_items(self, item, survivor, last_location, inventory):
        if item.name == "Water":
            item.points = 4
        elif item.name == "Food":
            item.points = 3
        elif item.name == "Medication":
            item.points = 2
        elif item.name == "Ammunition":
            item.points = 1
        else:
            survivor.delete()
            last_location.delete()
            inventory.delete()
            item.delete()
            raise Exception("Wrong item!")

    def create(self, validated_data):
        last_location_data = validated_data.pop('last_location')
        items_data = validated_data.pop('inventory')
        survivor = Survivor.objects.create(**validated_data)
        last_location = LastLocation.objects.create(**last_location_data)
        inventory = Inventory.objects.create()
        for item_data in items_data['items']:
            item = Item.objects.create(**item_data)
            self.validate_items(item, survivor, last_location, inventory)
            item.save()
            inventory.items.add(item)
        survivor.last_location_id = last_location.id
        survivor.inventory_id = inventory.id
        survivor.save()
        return survivor
