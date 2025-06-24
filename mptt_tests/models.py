from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class SubgroupUnit(MPTTModel):
    name = models.CharField(max_length=100)
    parent = TreeForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True, related_name='children'
    )
    
    class MPTTMeta:
        order_insertion_by = ['name']
    
    def __str__(self):
        return self.name


class Subgroup(models.Model):
    name = models.CharField(max_length=100)
    subgroup_unit = models.OneToOneField(SubgroupUnit, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_all_descendants(self):
        return self.subgroup_unit.get_descendants()

class Church(models.Model):
    name = models.CharField(max_length=100)
    node = models.ForeignKey('mptt_tests.SubgroupUnit', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_full_position(self):
        return self.node.get_ancestors(include_self=True)

class BasicUserSubgroupUnit(models.Model):
    subgroup_unit = models.ManyToManyField('mptt_tests.SubgroupUnit')

    class Meta:
        abstract = True

    def published_for(self):
        return self.subgroup_unit.all()

class Event(BasicUserSubgroupUnit):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name