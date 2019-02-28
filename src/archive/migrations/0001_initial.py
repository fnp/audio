# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Project'
        db.create_table('archive_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128, db_index=True)),
            ('sponsors', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('archive', ['Project'])

        # Adding model 'Audiobook'
        db.create_table('archive_audiobook', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('artist', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('conductor', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('encoded_by', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('date', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['archive.Project'])),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=255)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('published_tags', self.gf('jsonfield.fields.JSONField')(null=True)),
            ('mp3_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True)),
            ('ogg_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True)),
            ('publishing_tags', self.gf('jsonfield.fields.JSONField')(null=True)),
            ('publish_wait', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('publishing', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('published', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('archive', ['Audiobook'])


    def backwards(self, orm):
        
        # Deleting model 'Project'
        db.delete_table('archive_project')

        # Deleting model 'Audiobook'
        db.delete_table('archive_audiobook')


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
            'ogg_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['archive.Project']"}),
            'publish_wait': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'published': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'published_tags': ('jsonfield.fields.JSONField', [], {'null': 'True'}),
            'publishing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'publishing_tags': ('jsonfield.fields.JSONField', [], {'null': 'True'}),
            'source_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
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
