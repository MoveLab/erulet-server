# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Track'
        db.create_table(u'appulet_track', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('name_oc', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('name_es', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('name_ca', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('name_fr', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
        ))
        db.send_create_signal(u'appulet', ['Track'])

        # Adding model 'Step'
        db.create_table(u'appulet_step', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('absolute_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('track', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='steps', null=True, to=orm['appulet.Track'])),
            ('order', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')()),
            ('longitude', self.gf('django.db.models.fields.FloatField')()),
            ('altitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('precision', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'appulet', ['Step'])

        # Adding model 'Reference'
        db.create_table(u'appulet_reference', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('name_oc', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('name_es', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('name_ca', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('name_fr', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('html_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('highlight', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='references', null=True, to=orm['appulet.Highlight'])),
        ))
        db.send_create_signal(u'appulet', ['Reference'])

        # Adding model 'ReferenceImage'
        db.create_table(u'appulet_referenceimage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reference', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['appulet.Reference'])),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal(u'appulet', ['ReferenceImage'])

        # Adding model 'Route'
        db.create_table(u'appulet_route', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('id_route_based_on', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['appulet.Route'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='routes', null=True, to=orm['auth.User'])),
            ('description_oc', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description_es', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description_ca', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description_fr', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description_en', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('short_description_oc', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('short_description_es', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('short_description_ca', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('short_description_fr', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('short_description_en', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('local_carto', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('name_oc', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('name_es', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('name_ca', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('name_fr', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('reference', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['appulet.Reference'], unique=True, null=True, blank=True)),
            ('track', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['appulet.Track'], unique=True, null=True, blank=True)),
            ('upload_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('gpx_track', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('gpx_waypoints', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('gpx_pois', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('official', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'appulet', ['Route'])

        # Adding model 'Highlight'
        db.create_table(u'appulet_highlight', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='highlights', null=True, to=orm['auth.User'])),
            ('name_oc', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('name_es', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('name_ca', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('name_fr', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('long_text_oc', self.gf('django.db.models.fields.CharField')(max_length=2000, blank=True)),
            ('long_text_es', self.gf('django.db.models.fields.CharField')(max_length=2000, blank=True)),
            ('long_text_ca', self.gf('django.db.models.fields.CharField')(max_length=2000, blank=True)),
            ('long_text_fr', self.gf('django.db.models.fields.CharField')(max_length=2000, blank=True)),
            ('long_text_en', self.gf('django.db.models.fields.CharField')(max_length=2000, blank=True)),
            ('media', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('radius', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
            ('step', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='highlights', null=True, to=orm['appulet.Step'])),
            ('order', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'appulet', ['Highlight'])

        # Adding model 'InteractiveImage'
        db.create_table(u'appulet_interactiveimage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('image_file', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('highlight', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='interactive_images', null=True, to=orm['appulet.Highlight'])),
        ))
        db.send_create_signal(u'appulet', ['InteractiveImage'])

        # Adding model 'Box'
        db.create_table(u'appulet_box', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('interactive_image', self.gf('django.db.models.fields.related.ForeignKey')(related_name='boxes', to=orm['appulet.InteractiveImage'])),
            ('message_oc', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('message_es', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('message_ca', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('message_fr', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('message_en', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('max_y', self.gf('django.db.models.fields.IntegerField')()),
            ('max_x', self.gf('django.db.models.fields.IntegerField')()),
            ('min_y', self.gf('django.db.models.fields.IntegerField')()),
            ('min_x', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'appulet', ['Box'])

        # Adding model 'Rating'
        db.create_table(u'appulet_rating', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('rating', self.gf('django.db.models.fields.IntegerField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ratings', to=orm['auth.User'])),
            ('time', self.gf('django.db.models.fields.DateTimeField')()),
            ('highlight', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['appulet.Highlight'], null=True, blank=True)),
            ('route', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='ratings', null=True, to=orm['appulet.Route'])),
        ))
        db.send_create_signal(u'appulet', ['Rating'])


    def backwards(self, orm):
        # Deleting model 'Track'
        db.delete_table(u'appulet_track')

        # Deleting model 'Step'
        db.delete_table(u'appulet_step')

        # Deleting model 'Reference'
        db.delete_table(u'appulet_reference')

        # Deleting model 'ReferenceImage'
        db.delete_table(u'appulet_referenceimage')

        # Deleting model 'Route'
        db.delete_table(u'appulet_route')

        # Deleting model 'Highlight'
        db.delete_table(u'appulet_highlight')

        # Deleting model 'InteractiveImage'
        db.delete_table(u'appulet_interactiveimage')

        # Deleting model 'Box'
        db.delete_table(u'appulet_box')

        # Deleting model 'Rating'
        db.delete_table(u'appulet_rating')


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
            'min_y': ('django.db.models.fields.IntegerField', [], {}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'})
        },
        u'appulet.highlight': {
            'Meta': {'object_name': 'Highlight'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'highlights'", 'null': 'True', 'to': u"orm['auth.User']"}),
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
            'type': ('django.db.models.fields.IntegerField', [], {}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'})
        },
        u'appulet.interactiveimage': {
            'Meta': {'object_name': 'InteractiveImage'},
            'highlight': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'interactive_images'", 'null': 'True', 'to': u"orm['appulet.Highlight']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_file': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'})
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
            'highlight': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'references'", 'null': 'True', 'to': u"orm['appulet.Highlight']"}),
            'html_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_ca': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'name_es': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'name_oc': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'})
        },
        u'appulet.referenceimage': {
            'Meta': {'object_name': 'ReferenceImage'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'reference': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['appulet.Reference']"})
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
            'reference': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['appulet.Reference']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'short_description_ca': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'short_description_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'short_description_es': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'short_description_fr': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'short_description_oc': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'track': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['appulet.Track']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'upload_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'})
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
            'track': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'steps'", 'null': 'True', 'to': u"orm['appulet.Track']"}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'})
        },
        u'appulet.track': {
            'Meta': {'object_name': 'Track'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_ca': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'name_es': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'name_oc': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'})
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