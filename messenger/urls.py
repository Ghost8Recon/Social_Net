from django.conf.urls import url

from messenger import views


urlpatterns = [
    url(r'^$', views.inbox, name='inbox'),
    url(r'^send/$', views.send, name='send_message'),
    url(r'^delete/$', views.delete, name='delete_message'),
    url(r'^check/$', views.check, name='check_message'),
    url(r'^create_album/$', views.create_album, name='create_album'),
    url(r'^(?P<username>[^/]+)/$', views.messages, name='messages'),
    url(r'^(?P<album_id>[0-9]+)/$', views.detail, name='detail'),
]
