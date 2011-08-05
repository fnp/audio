# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Audiobook.source_file'
        db.alter_column('archive_audiobook', 'source_file', self.gf('django.db.models.fields.files.FileField')(max_length=255))


    def backwards(self, orm):
        
        # Changing field 'Audiobook.source_file'
        db.alter_column('archive_audiobook', 'source_file', self.gf('django.db.models.fields.files.FileField')(max_length=100))


    models = {
        'archive.audiobook': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Audiobook'},
            'artist': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'conductor': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'date': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'encoded_by': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['archive.Project']"}),
            'source_file': ('django.db.models.fields.files.FileField', [], {'max_length': '255'}),
            'source_sha1': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'translator': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255'})
        },
        'archive.project': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Project'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'db_index': 'True'}),
            'sponsors': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['archive']
