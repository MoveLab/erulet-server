from django.test import TestCase
from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from appulet.models import *
from django.db.models import Max
import pytz


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
