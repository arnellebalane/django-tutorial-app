from django.conf.urls import patterns, url, include
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^polls/', include('polls_remake.urls', namespace = 'polls_remake')),
    url(r'^admin/', include(admin.site.urls)),
)