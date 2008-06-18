from django.db import models
from django.utils.translation import ugettext as _
from django.core import urlresolvers

class Menu(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    base_url = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Admin:
        pass
 
    def __unicode__(self):
        return _("%s" % self.name)
 
    def save(self):
        """
        Re-order all items at from 10 upwards, at intervals of 10.
        This makes it easy to insert new items in the middle of
        existing items without having to manually shuffle
        them all around.
        """
        super(Menu, self).save()
 
        current = 10
        for item in MenuItem.objects.filter(menu=self).order_by('order'):
            item.order = current
            item.save()
            current += 10
 
class MenuItem(models.Model):
    menu = models.ForeignKey(Menu, edit_inline=models.TABULAR, num_in_admin=3, num_extra_on_change=3)
    order = models.IntegerField(core=True)
    url_name = models.CharField(max_length=100, help_text='URL Name for Reverse Lookup, eg comments.comment_was_posted', blank=True, null=True, core=True)
    view_path = models.CharField(max_length=100, help_text='Python Path to View to Render, eg django.contrib.admin.views.main.index', blank=True, null=True, core=True)
    link_url = models.CharField(max_length=100, help_text='URL or URI to the content, eg /about/ or http://foo.com/', blank=True, null=True, core=True)
    title = models.CharField(max_length=100, core=True)
    login_required = models.BooleanField(blank=True, null=True, core=True)
    staff_required = models.BooleanField(blank=True, null=True, core=True)
 
    def __unicode__(self):
        return _("%s %s. %s" % (self.menu.slug, self.order, self.title))

    def get_absolute_url(self):
        if self.url_name:
            return urlresolvers.reverse(self.url_name)
        elif self.view_path:
            return urlresolvers.reverse(self.view_path)
        elif self.link_url:
            return self.link_url