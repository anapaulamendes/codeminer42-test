from ..models import Survivor, Item, Reports


class GenerateReports:
    def __init__(self):
        self.all_survivors = Survivor.objects.all().count()
        self.infected = Survivor.objects.filter(infected=True).count()
        self.not_infected = Survivor.objects.filter(infected=False).count()

    def get_or_create_report(self):
        if not Reports.objects.all().exists():
            reports = Reports.objects.create()
        else:
            reports = Reports.objects.get()
        return reports

    def percentage_of_infected_survivors(self):
        return (self.infected/self.all_survivors) * 100

    def percentage_of_non_infected_survivors(self):
        return (self.not_infected/self.all_survivors) * 100

    def average_amount_of_resource_by_survivor(self, name):
        item_quantity = 0
        items = Item.objects.filter(name=name, inventory__survivor__infected=False)
        for item in items:
            item_quantity += item.quantity
        return item_quantity/self.not_infected

    def points_lost_for_infected_survivors(self):
        lost_points = 0
        names = ["Water", "Food", "Medication", "Ammunition"]
        for name in names:
            item_points = 0
            items = Item.objects.filter(name=name, inventory__survivor__infected=True)
            for item in items:
                item_points += (item.points * item.quantity)
            lost_points += item_points
        return lost_points

    def generate_reports(self):
        reports = self.get_or_create_report()
        reports.per_infected = self.percentage_of_infected_survivors()
        reports.per_not_infected = self.percentage_of_non_infected_survivors()
        reports.average_water = self.average_amount_of_resource_by_survivor("Water")
        reports.average_food = self.average_amount_of_resource_by_survivor("Food")
        reports.average_medication = self.average_amount_of_resource_by_survivor("Medication")
        reports.average_ammunition = self.average_amount_of_resource_by_survivor("Ammunition")
        reports.lost_points = self.points_lost_for_infected_survivors()
        reports.save()
        return reports
