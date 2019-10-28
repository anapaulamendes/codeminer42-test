from .models import Survivor, LastLocation
from .serializers import SurvivorSerializer, LastLocationSerializer, ReportsSerializer
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
from .services.reportinfected import FlagInfected
from .services.tradeitems import Trader
from .services.generatereports import GenerateReports

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

    def patch(self, request, pk, format=None):
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
        flagger = FlagInfected(request.data["infected"], reporter, reported)
        data = flagger.perform()
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


class ViewReports(APIView, GenerateReports):

    def get(self, request, format=None):
        generate = GenerateReports()
        reports = generate.generate_reports()
        serializer = ReportsSerializer(reports)
        return Response(serializer.data)
