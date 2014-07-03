from django.conf.urls import patterns, include, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^polls/', include('polls_third_attempt.urls', namespace = 'polls_third_attempt')),
    url(r'^admin/', include(admin.site.urls)),
)
