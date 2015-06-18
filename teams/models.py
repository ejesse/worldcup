from django.db import models

# Create your models here.

class Team(models.Model):

    full_name = models.CharField(max_length=100, unique=True)
    three_letter_name = models.CharField(max_length=3, unique=True)

    def save(self, force_insert=False, force_update=False, using=None,
        update_fields=None):
        self.three_letter_name = self.three_letter_name.upper()
        return models.Model.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    def __unicode__(self):
        return u'%s' % (self.full_name)

    def __str__(self):
        return self.__unicode__()