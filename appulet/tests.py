from django.test import TestCase
from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from appulet.models import *
from django.db.models import Max
import pytz
from django.core.files.uploadedfile import SimpleUploadedFile


def create_general_reference():
    return Reference.objects.create(general=True)


def create_route():
    return Route.objects.create()


def create_route_with_reference():
    this_reference = Reference.objects.create()
    this_route = Route()
    this_route.reference = this_reference
    this_route.save()
    return this_route


def create_route_with_map():
    this_route = Route()
    this_route.save()
    this_map = Map(type=0)
    this_map.map_file = SimpleUploadedFile('test_map.txt', 'just a test')
    this_map.route = this_route
    this_map.save()
    return this_route


def create_general_map():
    this_map = Map(type=1)
    this_map.map_file = SimpleUploadedFile('test_map.txt', 'just a test')
    this_map.save()
    return this_map


class GetGeneralReferencesTests(TestCase):
    def test_no_references(self):
        """
        If no general references in database, view should return message stating this
        """
        fake_unix_time = int(datetime.now().strftime('%s'))
        response = self.client.get(reverse('get_general_reference_files_width_last_updated', kwargs={'max_width': 10, 'last_updated_unix_time_utc': fake_unix_time}))
        self.assertContains(response, 'There are no general references in the database')

    def test_no_new_modifications(self):
        """
        If no modifications since last update, view should return message stating this.
        """
        create_general_reference()
        fake_unix_time_in_future = int((datetime.now() + timedelta(days=30)).strftime('%s'))
        response = self.client.get(reverse('get_general_reference_files_width_last_updated', kwargs={'max_width': 10, 'last_updated_unix_time_utc': fake_unix_time_in_future}))
        self.assertContains(response, 'There have been no changes since your last update')


class GetRouteContentTests(TestCase):
    def test_no_route(self):
        """
        If route does not exist, view should return message stating this
        """
        create_route()
        non_existent_route_id = Route.objects.all().aggregate(Max('id'))['id__max'] + 1
        fake_unix_time = int(datetime.now().strftime('%s'))
        response = self.client.get(reverse('get_route_content_files_width_last_updated', kwargs={'route_id': non_existent_route_id, 'max_width': 10, 'last_updated_unix_time_utc': fake_unix_time}))
        self.assertContains(response, 'Route does not exist')

    def test_no_content(self):
        """
        If no content in route, view should return message stating this.
        """
        this_route = create_route()
        fake_unix_time_in_future = int((datetime.now() + timedelta(days=30)).strftime('%s'))
        response = self.client.get(reverse('get_route_content_files_width_last_updated', kwargs={'route_id': this_route.id, 'max_width': 10, 'last_updated_unix_time_utc': fake_unix_time_in_future}))
        self.assertContains(response, 'There is no content in this route')

    def test_no_new_modifications(self):
        """
        If no modifications since last update, view should return message stating this.
        """
        this_route = create_route_with_reference()
        fake_unix_time_in_future = int((datetime.now() + timedelta(days=30)).strftime('%s'))
        response = self.client.get(reverse('get_route_content_files_width_last_updated', kwargs={'route_id': this_route.id, 'max_width': 10, 'last_updated_unix_time_utc': fake_unix_time_in_future}))
        self.assertContains(response, 'There have been no changes since your last update')


class GetRouteMapTests(TestCase):
    def test_no_route(self):
        """
        If route does not exist, view should return message stating this
        """
        create_route()
        non_existent_route_id = Route.objects.all().aggregate(Max('id'))['id__max'] + 1
        fake_unix_time = int(datetime.now().strftime('%s'))
        response = self.client.get(reverse('get_route_map_last_updated', kwargs={'route_id': non_existent_route_id,'last_updated_unix_time_utc': fake_unix_time}))
        self.assertContains(response, 'Route does not exist')

    def test_no_map(self):
        """
        If no map for route, view should return message stating this.
        """
        this_route = create_route()
        fake_unix_time_in_future = int((datetime.now() + timedelta(days=30)).strftime('%s'))
        response = self.client.get(reverse('get_route_map_last_updated', kwargs={'route_id': this_route,'last_updated_unix_time_utc': fake_unix_time_in_future}))
        self.assertContains(response, 'This route has no map')

    def test_no_new_modifications(self):
        """
        If no modifications since last update, view should return message stating this.
        """
        this_route = create_route_with_map()
        fake_unix_time_in_future = int((datetime.now() + timedelta(days=30)).strftime('%s'))
        response = self.client.get(reverse('get_route_map_last_updated', kwargs={'route_id': this_route.id,'last_updated_unix_time_utc': fake_unix_time_in_future}))
        self.assertContains(response, 'There have been no changes since your last update')

    def test_serve_map(self):
        """
        If no modifications since last update, view should return message stating this.
        """
        this_route = create_route_with_map()
        response = self.client.get(reverse('get_route_map', kwargs={'route_id': this_route.id}))
        self.assertEquals(response.status_code, 302) and self.assertEquals(response['content-type'], 'application/zip')


class GetGeneralMapTests(TestCase):
    def test_no_map(self):
        """
        If no general map, view should return message stating this.
        """
        response = self.client.get(reverse('get_general_map'))
        self.assertContains(response, 'No general maps on server')

    def test_no_new_modifications(self):
        """
        If no modifications since last update, view should return message stating this.
        """
        this_map = create_general_map()
        fake_unix_time_in_future = int((datetime.now() + timedelta(days=30)).strftime('%s'))
        response = self.client.get(reverse('get_general_map_last_updated', kwargs={'last_updated_unix_time_utc': fake_unix_time_in_future}))
        self.assertContains(response, 'There have been no changes since your last update')

    def test_serve_map(self):
        """
        If no modifications since last update, view should return message stating this.
        """
        this_map = create_general_map()
        response = self.client.get(reverse('get_general_map'))
        self.assertEquals(response.status_code, 302) and self.assertEquals(response['content-type'], 'application/zip')
