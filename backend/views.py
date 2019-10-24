from .models import Survivor, LastLocation
from .serializers import SurvivorSerializer, LastLocationSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'survivors': reverse('snippet-list', request=request, format=format)
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
        last_location = self.get_last_location(survivor.last_location_id)
        serializer = LastLocationSerializer(last_location, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportInfected(APIView):
    def get_reporter(self, pk_reporter):
        import ipdb; ipdb.set_trace()
        try:
            return Survivor.objects.get(pk=pk_reporter)
        except Survivor.DoesNotExist:
            raise Http404

    def get_reported(self, pk_reported):
        try:
            return LastLocation.objects.get(pk=pk_reported)
        except LastLocation.DoesNotExist:
            raise Http404
