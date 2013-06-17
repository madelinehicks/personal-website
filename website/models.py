from django.db import models
from django.contrib import admin
from django.template.defaultfilters import slugify
#from tinymce.models import HTMLField

class Post(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=200)
    url = models.SlugField(blank=True)
    #content = HTMLField()
    content = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.url:
            self.url = slugify(self.title)
        super(Post, self).save(*args, **kwargs)


    
class Tag(models.Model):
    tag = models.CharField(max_length=50)
    post = models.ForeignKey(Post, related_name='tags')
    
admin.site.register(Tag)
admin.site.register(Post)