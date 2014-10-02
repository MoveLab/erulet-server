# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Box.uuid'
        db.delete_column(u'appulet_box', 'uuid')

        # Deleting field 'Route.uuid'
        db.delete_column(u'appulet_route', 'uuid')

        # Deleting field 'InteractiveImage.uuid'
        db.delete_column(u'appulet_interactiveimage', 'uuid')

        # Deleting field 'Highlight.uuid'
        db.delete_column(u'appulet_highlight', 'uuid')

        # Deleting field 'Step.uuid'
        db.delete_column(u'appulet_step', 'uuid')

        # Deleting field 'Reference.uuid'
        db.delete_column(u'appulet_reference', 'uuid')

        # Deleting field 'Track.uuid'
        db.delete_column(u'appulet_track', 'uuid')


    def backwards(self, orm):
        # Adding field 'Box.uuid'
        db.add_column(u'appulet_box', 'uuid',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=40, blank=True),
                      keep_default=False)

        # Adding field 'Route.uuid'
        db.add_column(u'appulet_route', 'uuid',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=40, blank=True),
                      keep_default=False)

        # Adding field 'InteractiveImage.uuid'
        db.add_column(u'appulet_interactiveimage', 'uuid',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=40, blank=True),
                      keep_default=False)

        # Adding field 'Highlight.uuid'
        db.add_column(u'appulet_highlight', 'uuid',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=40, blank=True),
                      keep_default=False)

        # Adding field 'Step.uuid'
        db.add_column(u'appulet_step', 'uuid',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=40, blank=True),
                      keep_default=False)

        # Adding field 'Reference.uuid'
        db.add_column(u'appulet_reference', 'uuid',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=40, blank=True),
                      keep_default=False)

        # Adding field 'Track.uuid'
        db.add_column(u'appulet_track', 'uuid',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=40, blank=True),
                      keep_default=False)


    models = {
        u'appulet.box': {
            'Meta': {'object_name': 'Box'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interactive_image': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'boxes'", 'to': u"orm['appulet.InteractiveImage']"}),
            'max_x': ('django.db.models.fields.IntegerField', [], {}),
            'max_y': ('django.db.models.fields.IntegerField', [], {}),
            'message_ca': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'message_en': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'message_es': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'message_fr': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'message_oc': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'min_x': ('django.db.models.fields.IntegerField', [], {}),
            'min_y': ('django.db.models.fields.IntegerField', [], {})
        },
        u'appulet.highlight': {
            'Meta': {'object_name': 'Highlight'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'highlights'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_text_ca': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'blank': 'True'}),
            'long_text_en': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'blank': 'True'}),
            'long_text_es': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'blank': 'True'}),
            'long_text_fr': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'blank': 'True'}),
            'long_text_oc': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'blank': 'True'}),
            'media': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name_ca': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name_es': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name_oc': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'radius': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'step': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'highlights'", 'null': 'True', 'to': u"orm['appulet.Step']"}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        u'appulet.interactiveimage': {
            'Meta': {'object_name': 'InteractiveImage'},
            'highlight': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'interactive_images'", 'null': 'True', 'to': u"orm['appulet.Highlight']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_file': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'})
        },
        u'appulet.rating': {
            'Meta': {'object_name': 'Rating'},
            'highlight': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['appulet.Highlight']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rating': ('django.db.models.fields.IntegerField', [], {}),
            'route': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ratings'", 'null': 'True', 'to': u"orm['appulet.Route']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ratings'", 'to': u"orm['auth.User']"})
        },
        u'appulet.reference': {
            'Meta': {'object_name': 'Reference'},
            'general': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'highlight': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'references'", 'null': 'True', 'to': u"orm['appulet.Highlight']"}),
            'html_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_ca': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'name_es': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'name_oc': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'appulet.route': {
            'Meta': {'object_name': 'Route'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'routes'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'description_ca': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description_es': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description_fr': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description_oc': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'gpx_pois': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'gpx_track': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'gpx_waypoints': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_route_based_on': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['appulet.Route']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'local_carto': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name_ca': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'name_es': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'name_oc': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'official': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reference': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['appulet.Reference']", 'unique': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'short_description_ca': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'short_description_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'short_description_es': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'short_description_fr': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'short_description_oc': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'track': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['appulet.Track']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'upload_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'appulet.step': {
            'Meta': {'object_name': 'Step'},
            'absolute_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'altitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'precision': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'track': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'steps'", 'null': 'True', 'to': u"orm['appulet.Track']"})
        },
        u'appulet.track': {
            'Meta': {'object_name': 'Track'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_ca': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'name_es': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'name_oc': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['appulet']