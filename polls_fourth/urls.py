from django.conf.urls import patterns, url

from polls_fourth import views


urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name = 'index'),
    url(r'^(?P<poll_id>\d+)/vote/$', views.vote, name = 'vote'),
)
