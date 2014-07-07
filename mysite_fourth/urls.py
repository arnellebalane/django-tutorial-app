from django.conf.urls import patterns, include, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^polls/', include('polls_fourth.urls', namespace = 'polls')),
    url(r'^admin/', include(admin.site.urls)),
)
