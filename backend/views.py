from .models import Survivor, LastLocation, Item, Reports
from .serializers import SurvivorSerializer, LastLocationSerializer, ReportsSerializer
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
from .services.reportinfected import FlagInfected
from .services.tradeitems import Trader

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
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class SurvivorDetail(APIView):

    def get(self, request, pk, format=None):
        survivor = get_object_or_404(Survivor, pk=pk)
        serializer = SurvivorSerializer(survivor)
        return Response(serializer.data)


class LastLocationUpdate(APIView):

    def get(self, request, pk, format=None):
        survivor = get_object_or_404(Survivor, pk=pk)
        last_location = get_object_or_404(LastLocation, pk=survivor.last_location_id)
        serializer = LastLocationSerializer(last_location)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        survivor = get_object_or_404(Survivor, pk=pk)
        if survivor.infected == False:
            last_location = get_object_or_404(LastLocation, pk=survivor.last_location_id)
            serializer = LastLocationSerializer(last_location, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        else:
            raise Exception("Zombie invasion! Permission denied!")


class ReportInfected(APIView, FlagInfected):

    def get(self, request, pk_reporter, pk_reported, format=None):
        survivor = get_object_or_404(Survivor, pk=pk_reported)
        serializer = SurvivorSerializer(survivor)
        return Response(serializer.data)

    def patch(self, request, pk_reporter, pk_reported, format=None):
        reporter = get_object_or_404(Survivor, pk=pk_reporter)
        reported = get_object_or_404(Survivor, pk=pk_reported)
        data = self.report_infected(request, reporter, reported)
        if data:
            serializer = SurvivorSerializer(reported, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class TradeItems(APIView, Trader):

    def get(self, request, pk_sur_1, pk_sur_2, format=None):
        survivor_1 = get_object_or_404(Survivor, pk=pk_sur_1)
        survivor_2 = get_object_or_404(Survivor, pk=pk_sur_2)
        serializer_1 = SurvivorSerializer(survivor_1)
        serializer_2 = SurvivorSerializer(survivor_2)
        data = ((serializer_1.data), (serializer_2.data))
        return Response(data)

    def patch(self, request, pk_sur_1, pk_sur_2, format=None):
        survivor_1 = get_object_or_404(Survivor, pk=pk_sur_1)
        survivor_2 = get_object_or_404(Survivor, pk=pk_sur_2)
        trade = self.trade_items(request, survivor_1, survivor_2)
        if trade:
            serializer_1 = SurvivorSerializer(survivor_1)
            serializer_2 = SurvivorSerializer(survivor_2)
            data = ((serializer_1.data), (serializer_2.data))
            return Response(data)
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
