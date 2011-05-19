from django.conf import settings
from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
    url(r'^demo/$', 'topic_tracking_web.demo.views.index'),
    url(r'^demo/stories/$', 'topic_tracking_web.demo.views.stories_list'),
    url(r'^demo/stories/(?P<id>[A-Za-z0-9-_]+)/$', 'topic_tracking_web.demo.views.stories_show'),
    url(r'^demo/topics/$', 'topic_tracking_web.demo.views.topics_list'),
    url(r'^demo/topics/(?P<id>[A-Za-z0-9-_]+)/$', 'topic_tracking_web.demo.views.topics_show'),
    url(r'^demo/topics_create/$', 'topic_tracking_web.demo.views.topics_create'),
    url(r'^demo/follow/$', 'topic_tracking_web.demo.views.bookmarklet_follow'),
)

if settings.DEBUG:
    _media_url = settings.MEDIA_URL
    if _media_url.startswith('/'):
        _media_url = _media_url[1:]
        urlpatterns += patterns('',
            url(r'^%s(?P<path>.*)$' % _media_url,
            'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}))
    del(_media_url)
