from django.conf import settings
from django.http import Http404
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from pymongo import DESCENDING
from topic_tracking.model import DiscoveredResource
from topic_tracking.topic_management.topic_manager import TopicManager
from topic_tracking.util.http import detect_header_encoding
from topic_tracking.util.similarity.model_query import ModelQueryBuilder
from topic_tracking.util.xml import decode_html
from topic_tracking_web.services.es import get_es, get_es_main_index
from topic_tracking_web.services.mongo import get_resource_collection, \
    get_stories_collection, get_topics_collection
from topic_tracking_web.services.processing import get_processing_service_client
from urllib2 import HTTPRedirectHandler
import logging
import time
import urllib2


logger = logging.getLogger('web')


resource_collection = get_resource_collection()
story_collection = get_stories_collection()
topic_collection = get_topics_collection()

es = get_es()
main_index = get_es_main_index()

processing_service_client = get_processing_service_client()

MAX_CLAUSES = 20
MAX_ENTITY_CLAUSES = 10
ENTITY_BOOST = 10
TERM_BOOST = 1
query_builder = ModelQueryBuilder(MAX_CLAUSES, MAX_ENTITY_CLAUSES, ENTITY_BOOST, TERM_BOOST)
MIN_SIMILARITY = 0.5
topic_manager = TopicManager(story_collection, topic_collection, \
    es, main_index, query_builder, MIN_SIMILARITY)


time_intervals = []
now = int(time.time())
hour = 3600
day = hour * 24
week = day * 7
month = week * 4
time_intervals.append(('one hour ago', now - hour, now))
time_intervals.append(('one day ago', now - day, now - hour))
time_intervals.append(('one week ago', now - week, now - day))
time_intervals.append(('one month ago', now - month, now - week))
time_intervals.append(('two months ago', now - month * 2, now - month))
time_intervals.append(('three months ago', now - month * 3, now - month * 2))
time_intervals.append(('four months ago', now - month * 4, now - month * 3))
time_intervals.append(('five months ago', now - month * 5, now - month * 4))
time_intervals.append(('six months ago', now - month * 6, now - month * 5))
time_intervals.append(('earlier than six months', 0, now - month * 7))


MAX_STORIES_ALL = 20
MAX_STORIES_PER_INTERVAL = 3
MAX_RESOURCES_PER_STORY_BRIEF = 2
MAX_RESOURCES_PER_STORY_PAGE = 50
STORY_SORT = [('resource_count', DESCENDING)]


def index(request):
    s = 'salut'
    return render_to_response('index.html', {'s': s})


def stories_list(request):
    stories = story_collection.find_models(). \
        sort(STORY_SORT). \
        limit(MAX_STORIES_ALL)

    story_resources = []
    for story in stories:
        resources = resource_collection.find_models(
            {'story_id': story._id}, limit=MAX_RESOURCES_PER_STORY_BRIEF)
        story_resources.append((story, resources))

    d = {'story_resources': story_resources}

    return render_to_response('demo/stories/list.html', d, RequestContext(request))


def stories_show(request, id):
    story = story_collection.find_one_model(id)
    if story is None:
        raise Http404()

    resources = resource_collection.find_models({'story_id': story._id}). \
        limit(MAX_RESOURCES_PER_STORY_PAGE)

    d = {'story': story, 'resources': resources}

    return render_to_response('demo/stories/show.html', d, RequestContext(request))


def topics_list(request):
    topics = topic_collection.find_models(fields={'title', 'story_ids'})

    d = {'topics': topics}

    return render_to_response('demo/topics/list.html', d, RequestContext(request))


def topics_create(request):
    story = story_collection.find_one_model(request.POST['story_id'])
    if story is None:
        raise Http404()

    topic = topic_manager.create_from_story(story.title, story)

    return redirect('topic_tracking_web.demo.views.topics_show', topic._id)


def topics_show(request, id):
    topic = topic_collection.find_one_model(id)
    if topic is None:
        raise Http404()

    summaries = []
    for name, startTime, endTime in time_intervals:
        summaries.append((name, _build_interval_summary(topic, name, startTime, endTime)))

    d = {'topic': topic, 'summaries': summaries}

    return render_to_response('demo/topics/show.html', d, RequestContext(request))


def _build_interval_summary(topic, name, startTime, endTime):
    stories = topic_manager.get_summary(topic, startTime, endTime, MAX_STORIES_PER_INTERVAL)

    story_resources = []
    for story in stories:
        resources = resource_collection.find_models(
            {'story_id': story._id}, limit=MAX_RESOURCES_PER_STORY_BRIEF)
        story_resources.append((story, resources))

    return story_resources

















def bookmarklet_follow(request):
    uri = (request.GET['u'])
    title = (request.GET['t'])

    # url opener
    redirect_handler = HTTPRedirectHandler()
    redirect_handler.max_redirections = settings.CONFIG['url']['max_redirections']
    opener = urllib2.build_opener(redirect_handler)

    # web page loading
    handle = opener.open(uri)
    encoding = detect_header_encoding(handle.headers.dict)
    content = decode_html(handle.read(), encoding)
    handle.close()

    # build a resource
    discovered_resource = DiscoveredResource()
    discovered_resource.uri = uri
    discovered_resource.title = title
    discovered_resource.content = content

    # process the discovered resource
    resource = processing_service_client.process(discovered_resource)

    topic = topic_manager.create_from_features(resource.title, resource.terms, resource.entities)

    return redirect('topic_tracking_web.demo.views.topics_show', topic._id)
