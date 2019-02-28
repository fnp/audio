# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Audiobook.part_name'
        db.add_column(u'archive_audiobook', 'part_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Audiobook.index'
        db.add_column(u'archive_audiobook', 'index',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Audiobook.parts_count'
        db.add_column(u'archive_audiobook', 'parts_count',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Audiobook.part_name'
        db.delete_column(u'archive_audiobook', 'part_name')

        # Deleting field 'Audiobook.index'
        db.delete_column(u'archive_audiobook', 'index')

        # Deleting field 'Audiobook.parts_count'
        db.delete_column(u'archive_audiobook', 'parts_count')


    models = {
        u'archive.audiobook': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Audiobook'},
            'artist': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'conductor': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'date': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'encoded_by': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'mp3_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'mp3_published': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'mp3_published_tags': ('jsonfield.fields.JSONField', [], {'null': 'True'}),
            'mp3_status': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True'}),
            'mp3_tags': ('jsonfield.fields.JSONField', [], {'null': 'True'}),
            'mp3_task': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'ogg_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'ogg_published': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'ogg_published_tags': ('jsonfield.fields.JSONField', [], {'null': 'True'}),
            'ogg_status': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True'}),
            'ogg_tags': ('jsonfield.fields.JSONField', [], {'null': 'True'}),
            'ogg_task': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'part_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'parts_count': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['archive.Project']"}),
            'source_file': ('django.db.models.fields.files.FileField', [], {'max_length': '255'}),
            'source_sha1': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'translator': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255'})
        },
        u'archive.project': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Project'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'db_index': 'True'}),
            'sponsors': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['archive']