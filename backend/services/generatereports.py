from ..models import Survivor, Item, Reports

class GenerateReports():

    def generate_reports(self):
        if not Reports.objects.all().exists():
            reports = Reports.objects.create()
        else:
            reports = Reports.objects.get()
        all_survivors = Survivor.objects.all().count()
        infected = Survivor.objects.filter(infected=True).count()
        not_infected = Survivor.objects.filter(infected=False).count()
        waters_not_infected = Item.objects.filter(name="Water", inventory__survivor__infected=False).count()
        foods_not_infected = Item.objects.filter(name="Foods", inventory__survivor__infected=False).count()
        medications_not_infected = Item.objects.filter(name="Medication", inventory__survivor__infected=False).count()
        ammunitions_not_infected = Item.objects.filter(name="Ammunition", inventory__survivor__infected=False).count()
        waters_infected = Item.objects.filter(name="Water", inventory__survivor__infected=True)
        foods_infected = Item.objects.filter(name="Foods", inventory__survivor__infected=True)
        medications_infected = Item.objects.filter(name="Medication", inventory__survivor__infected=True)
        ammunitions_infected = Item.objects.filter(name="Ammunition", inventory__survivor__infected=True)
        # i. Percentage of infected survivors.
        per_infected = (infected/all_survivors) * 100
        reports.per_infected = per_infected
        # ii. Percentage of non-infected survivors.
        per_not_infected = (not_infected/all_survivors) * 100
        reports.per_not_infected = per_not_infected
        # iii. Average amount of each kind of resource by survivor (e.g. 5 waters per survivor)
        average_water = waters_not_infected/not_infected
        average_food = foods_not_infected/not_infected
        average_medication = medications_not_infected/not_infected
        average_ammunition = ammunitions_not_infected/not_infected
        reports.average_water = average_water
        reports.average_food = average_food
        reports.average_medication = average_medication
        reports.average_ammunition = average_ammunition
        # iv. Points lost because of infected survivor.
        water_points = 0
        food_points = 0
        medication_points = 0
        ammunition_points = 0
        for water in waters_infected:
            water_points += water.points
        for food in foods_infected:
            food_points += food.points
        for medication in medications_infected:
            medication_points += medication.points
        for ammunition in ammunitions_infected:
            ammunition_points += ammunition.points
        lost_points = water_points + food_points + medication_points + ammunition_points
        reports.lost_points = lost_points
        reports.save()
        return reports
