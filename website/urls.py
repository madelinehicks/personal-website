from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'website.views.content'),
#    url(r'^tinymce/', include('tinymce.urls')),
    url(r'log/', 'website.views.fb_log'),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'etsy/', 'website.views.etsy'),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'trade/', 'website.views.trade'),
    url(r'routes/', 'website.views.route_lookup'),
    url(r'item/(?P<type_id>.*)/$', 'website.views.item_lookup'),
)
