# encoding: utf-8
import datetime
from hashlib import sha1
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


def sha1_file(f):
    sha = sha1()
    for piece in iter(lambda: f.read(1024*1024), ''):
        sha.update(piece)
    return sha.hexdigest()


class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Audiobook.source_sha1'
        db.add_column('archive_audiobook', 'source_sha1', self.gf('django.db.models.fields.CharField')(default='', max_length=40), keep_default=False)

        # Adding field 'Audiobook.translator'
        db.add_column('archive_audiobook', 'translator', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)

        if not db.dry_run:
            for obj in orm.Audiobook.objects.all():
                try:
                    f = open(obj.source_file.path)
                except ValueError, e:
                    print "Audiobook has no source file"
                    pass
                else:
                    obj.source_sha1 = sha1_file(f)
                    f.close()
                    obj.save()


    def backwards(self, orm):
        
        # Deleting field 'Audiobook.source_sha1'
        db.delete_column('archive_audiobook', 'source_sha1')

        # Deleting field 'Audiobook.translator'
        db.delete_column('archive_audiobook', 'translator')


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
