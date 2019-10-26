from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^survivors/$', views.SurvivorList.as_view(), name='survivor_list'),
    url(r'^survivors/(?P<pk>[^/]+)/$', views.SurvivorDetail.as_view(), name='survivor_detail'),
    url(r'^survivors/(?P<pk>[^/]+)/last-location$', views.LastLocationUpdate.as_view(), name='last_location_update'),
    url(r'^survivors/(?P<pk_reporter>[^/]+)/report-infected/(?P<pk_reported>[^/]+)$', views.ReportInfected.as_view(), name='report_infected'),
]
