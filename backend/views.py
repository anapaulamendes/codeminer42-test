from .models import Survivor, LastLocation, Item, Reports
from .serializers import SurvivorSerializer, LastLocationSerializer, ReportsSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'survivors': reverse('survivor-list', request=request, format=format)
    })


class SurvivorList(APIView):
    def get(self, request, format=None):
        survivors = Survivor.objects.all()
        serializer = SurvivorSerializer(survivors, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = SurvivorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SurvivorDetail(APIView):
    def get_object(self, pk):
        try:
            return Survivor.objects.get(pk=pk)
        except Survivor.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        survivor = self.get_object(pk)
        serializer = SurvivorSerializer(survivor)
        return Response(serializer.data)

class LastLocationUpdate(APIView):
    def get_survivor(self, pk):
        try:
            return Survivor.objects.get(pk=pk)
        except Survivor.DoesNotExist:
            raise Http404

    def get_last_location(self, pk):
        try:
            return LastLocation.objects.get(pk=pk)
        except LastLocation.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        survivor = self.get_survivor(pk)
        last_location = self.get_last_location(survivor.last_location_id)
        serializer = LastLocationSerializer(last_location)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        survivor = self.get_survivor(pk)
        if survivor.infected == False:
            last_location = self.get_last_location(survivor.last_location_id)
            serializer = LastLocationSerializer(last_location, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise Exception("Zombie invasion! Permission denied!")


class ReportInfected(APIView):
    def get_reporter(self, pk_reporter):
        try:
            return Survivor.objects.get(pk=pk_reporter)
        except Survivor.DoesNotExist:
            raise Http404

    def get_reported(self, pk_reported):
        try:
            return Survivor.objects.get(pk=pk_reported)
        except Survivor.DoesNotExist:
            raise Http404

    def get(self, request, pk_reporter, pk_reported, format=None):
        survivor = self.get_reported(pk_reported)
        serializer = SurvivorSerializer(survivor)
        return Response(serializer.data)

    def patch(self, request, pk_reporter, pk_reported, format=None):
        reporter = self.get_reporter(pk_reporter)
        reported = self.get_reported(pk_reported)
        if reporter.infected == False:
            if reported.reported_infected < 2:
                if request.data["infected"] == True:
                    data = {
                        "infected": False,
                        "reported_infected": reported.reported_infected + 1
                    }
                else:
                    raise Exception("Flag as infected!")
            else:
                data = {
                    "infected": True,
                    "reported_infected": reported.reported_infected + 1
                }
            serializer = SurvivorSerializer(reported, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise Exception("Zombie invasion! Permission denied!")


class TradeItems(APIView):
    def get_survivor_1(self, pk_sur_1):
        try:
            return Survivor.objects.get(pk=pk_sur_1)
        except Survivor.DoesNotExist:
            raise Http404

    def get_survivor_2(self, pk_sur_2):
        try:
            return Survivor.objects.get(pk=pk_sur_2)
        except Survivor.DoesNotExist:
            raise Http404

    def get(self, request, pk_sur_1, pk_sur_2, format=None):
        survivor_1 = self.get_survivor_1(pk_sur_1)
        survivor_2 = self.get_survivor_2(pk_sur_2)
        serializer_1 = SurvivorSerializer(survivor_1)
        serializer_2 = SurvivorSerializer(survivor_2)
        data = ((serializer_1.data), (serializer_2.data))
        return Response(data)

    def patch(self, request, pk_sur_1, pk_sur_2, format=None):
        survivor_1 = self.get_survivor_1(pk_sur_1)
        survivor_2 = self.get_survivor_2(pk_sur_2)
        items = ["Water", "Food", "Medication", "Ammunition"]
        points_survivor_1 = 0
        points_survivor_2 = 0
        if survivor_1.infected == False and survivor_2.infected == False:
            for item_key in request.data[0]["survivor_1"]["trade_item"].keys():
                item_qt = survivor_1.inventory.items.get(name=item_key).quantity
                if item_qt - request.data[0]["survivor_1"]["trade_item"][item_key] >= 0:
                    item_points = survivor_1.inventory.items.get(name=item_key).points
                    points_survivor_1 += request.data[0]["survivor_1"]["trade_item"][item_key] * item_points
                else:
                    raise Exception("It isn't enough to trade! Permission denied!")
            for item_key in request.data[1]["survivor_2"]["trade_item"].keys():
                item_qt = survivor_2.inventory.items.get(name=item_key).quantity
                if item_qt - request.data[1]["survivor_2"]["trade_item"][item_key] >= 0:
                    item_points = survivor_2.inventory.items.get(name=item_key).points
                    points_survivor_2 += request.data[1]["survivor_2"]["trade_item"][item_key] * item_points
                else:
                    raise Exception("It isn't enough to trade! Permission denied!")
            if points_survivor_1 == points_survivor_2:
                for data in request.data:
                    if data["id"] == survivor_1.id:
                        for trade_item in data["survivor_1"]["trade_item"].keys():
                            for item in items:
                                if trade_item == item:
                                    trade_sur_1 = survivor_1.inventory.items.get(name=item)
                                    trade_sur_1.quantity -= data["survivor_1"]["trade_item"][item]
                                    trade_sur_1.save()
                                    trade_sur_2 = survivor_2.inventory.items.get(name=item)
                                    trade_sur_2.quantity += data["survivor_1"]["trade_item"][item]
                                    trade_sur_2.save()
                    else:
                        for trade_item in data["survivor_2"]["trade_item"].keys():
                            for item in items:
                                if trade_item == item:
                                    trade_sur_2 = survivor_2.inventory.items.get(name=item)
                                    trade_sur_2.quantity -= data["survivor_2"]["trade_item"][item]
                                    trade_sur_2.save()
                                    trade_sur_1 = survivor_1.inventory.items.get(name=item)
                                    trade_sur_1.quantity += data["survivor_2"]["trade_item"][item]
                                    trade_sur_1.save()
                serializer_1 = SurvivorSerializer(survivor_1)
                serializer_2 = SurvivorSerializer(survivor_2)
                data = ((serializer_1.data), (serializer_2.data))
                return Response(data)
            else:
                raise Exception("You must have the same amount of points to trade! Permission denied!")
        else:
            raise Exception("Zombie invasion! Permission denied!")


class ViewReports(APIView):

    def get(self, request, format=None):
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
        serializer = ReportsSerializer(reports)
        return Response(serializer.data)
