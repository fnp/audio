# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Audiobook.publishing_tags'
        db.delete_column('archive_audiobook', 'publishing_tags')

        # Deleting field 'Audiobook.published_tags'
        db.delete_column('archive_audiobook', 'published_tags')

        # Deleting field 'Audiobook.publish_wait'
        db.delete_column('archive_audiobook', 'publish_wait')

        # Deleting field 'Audiobook.published'
        db.delete_column('archive_audiobook', 'published')

        # Deleting field 'Audiobook.publishing'
        db.delete_column('archive_audiobook', 'publishing')

        # Adding field 'Audiobook.mp3_status'
        db.add_column('archive_audiobook', 'mp3_status', self.gf('django.db.models.fields.SmallIntegerField')(null=True), keep_default=False)

        # Adding field 'Audiobook.mp3_task'
        db.add_column('archive_audiobook', 'mp3_task', self.gf('django.db.models.fields.CharField')(max_length=64, null=True), keep_default=False)

        # Adding field 'Audiobook.mp3_tags'
        db.add_column('archive_audiobook', 'mp3_tags', self.gf('jsonfield.fields.JSONField')(null=True), keep_default=False)

        # Adding field 'Audiobook.mp3_published_tags'
        db.add_column('archive_audiobook', 'mp3_published_tags', self.gf('jsonfield.fields.JSONField')(null=True), keep_default=False)

        # Adding field 'Audiobook.mp3_published'
        db.add_column('archive_audiobook', 'mp3_published', self.gf('django.db.models.fields.DateTimeField')(null=True), keep_default=False)

        # Adding field 'Audiobook.ogg_status'
        db.add_column('archive_audiobook', 'ogg_status', self.gf('django.db.models.fields.SmallIntegerField')(null=True), keep_default=False)

        # Adding field 'Audiobook.ogg_task'
        db.add_column('archive_audiobook', 'ogg_task', self.gf('django.db.models.fields.CharField')(max_length=64, null=True), keep_default=False)

        # Adding field 'Audiobook.ogg_tags'
        db.add_column('archive_audiobook', 'ogg_tags', self.gf('jsonfield.fields.JSONField')(null=True), keep_default=False)

        # Adding field 'Audiobook.ogg_published_tags'
        db.add_column('archive_audiobook', 'ogg_published_tags', self.gf('jsonfield.fields.JSONField')(null=True), keep_default=False)

        # Adding field 'Audiobook.ogg_published'
        db.add_column('archive_audiobook', 'ogg_published', self.gf('django.db.models.fields.DateTimeField')(null=True), keep_default=False)


    def backwards(self, orm):
        
        # Adding field 'Audiobook.publishing_tags'
        db.add_column('archive_audiobook', 'publishing_tags', self.gf('jsonfield.fields.JSONField')(null=True), keep_default=False)

        # Adding field 'Audiobook.published_tags'
        db.add_column('archive_audiobook', 'published_tags', self.gf('jsonfield.fields.JSONField')(null=True), keep_default=False)

        # Adding field 'Audiobook.publish_wait'
        db.add_column('archive_audiobook', 'publish_wait', self.gf('django.db.models.fields.DateTimeField')(null=True), keep_default=False)

        # Adding field 'Audiobook.published'
        db.add_column('archive_audiobook', 'published', self.gf('django.db.models.fields.DateTimeField')(null=True), keep_default=False)

        # Adding field 'Audiobook.publishing'
        db.add_column('archive_audiobook', 'publishing', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Deleting field 'Audiobook.mp3_status'
        db.delete_column('archive_audiobook', 'mp3_status')

        # Deleting field 'Audiobook.mp3_task'
        db.delete_column('archive_audiobook', 'mp3_task')

        # Deleting field 'Audiobook.mp3_tags'
        db.delete_column('archive_audiobook', 'mp3_tags')

        # Deleting field 'Audiobook.mp3_published_tags'
        db.delete_column('archive_audiobook', 'mp3_published_tags')

        # Deleting field 'Audiobook.mp3_published'
        db.delete_column('archive_audiobook', 'mp3_published')

        # Deleting field 'Audiobook.ogg_status'
        db.delete_column('archive_audiobook', 'ogg_status')

        # Deleting field 'Audiobook.ogg_task'
        db.delete_column('archive_audiobook', 'ogg_task')

        # Deleting field 'Audiobook.ogg_tags'
        db.delete_column('archive_audiobook', 'ogg_tags')

        # Deleting field 'Audiobook.ogg_published_tags'
        db.delete_column('archive_audiobook', 'ogg_published_tags')

        # Deleting field 'Audiobook.ogg_published'
        db.delete_column('archive_audiobook', 'ogg_published')


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
