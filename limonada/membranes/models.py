# -*- coding: utf-8; Mode: python; tab-width: 4; indent-tabs-mode:nil; -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
#    Limonada is accessible at https://limonada.univ-reims.fr/
#    Copyright (C) 2016-2020 - The Limonada Team (see the AUTHORS file)
#
#    This file is part of Limonada.
#
#    Limonada is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Limonada is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Limonada.  If not, see <http://www.gnu.org/licenses/>.

# standard library
from __future__ import unicode_literals
from unidecode import unidecode
import os

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.utils.formats import localize
from django.urls import reverse
from django.core.files.base import ContentFile

# Django apps
from limonada.functions import delete_file


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.gro', '.pdb']
    if ext not in valid_extensions:
        raise ValidationError(u'File not supported!')


def validate_otherfile_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.zip']
    if ext not in valid_extensions:
        raise ValidationError(u'File not supported!')


def validate_mem_size(value):
    filesize = value.size
    if filesize > 104857600:
        raise ValidationError("The maximum file size that can be uploaded is 100MB")
    else:
        return value


def validate_other_size(value):
    filesize = value.size
    if filesize > 5242880:
        raise ValidationError("The maximum file size that can be uploaded is 5MB")
    else:
        return value


def directory_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    name = unidecode(instance.name).replace(' ', '_')
    filepath = 'membranes/LIM{0}_{1}{2}'.format(instance.id, name, ext)
    if os.path.isfile(os.path.join(settings.MEDIA_ROOT, filepath)):
        os.remove(os.path.join(settings.MEDIA_ROOT, filepath))
    return filepath


@python_2_unicode_compatible
class MembraneTopol(models.Model):

    name = models.CharField(max_length=100)
    search_name = models.CharField(max_length=100,
                                   blank=True)
    membrane = models.ForeignKey('Membrane',
                                 null=True,
                                 on_delete=models.CASCADE)
    lipids = models.ManyToManyField('lipids.Lipid',
                                    through='TopolComposition')
    temperature = models.PositiveIntegerField()
    equilibration = models.PositiveIntegerField()
    mem_file = models.FileField(upload_to=directory_path,
                                help_text='.pdb and .gro files are supported',
                                validators=[validate_file_extension,
                                            validate_mem_size],
                                blank=True,
                                null=True)
    compo_file = models.FileField(upload_to=directory_path,
                                  blank=True,
                                  null=True)
    other_file = models.FileField(upload_to=directory_path,
                                  validators=[validate_otherfile_extension,
                                              validate_other_size],
                                  help_text='Use a zip file containing these files',
                                  blank=True,
                                  null=True)
    software = models.ForeignKey('forcefields.Software',
                                 on_delete=models.CASCADE)
    forcefield = models.ForeignKey('forcefields.Forcefield',
                                   on_delete=models.CASCADE)
    nb_lipids = models.PositiveIntegerField(null=True, default=0)
    description = models.TextField(blank=True)
    prot = models.ManyToManyField('membranes.MembraneProt',
                                  blank=True)
    reference = models.ManyToManyField('homepage.Reference')
    date = models.DateField(auto_now=True)
    curator = models.ForeignKey(User,
                                on_delete=models.CASCADE)
    doi = models.ManyToManyField('membranes.MembraneDoi',  # This file is used to add doi link for Zenodo
                                 blank=True)
    
    version = models.IntegerField(default=1)
    root_version = models.ForeignKey('membranes.MembraneTopol', blank=True, null=True, on_delete=models.DO_NOTHING)
    
    @property
    def tags(self):
        if self.membrane is None:
            return []
        return self.membrane.tag.all()
    
    @property
    def lipid_species_count(self):
        if self.membrane is None:
            return 0
        return self.membrane.nb_liptypes
    
    @property
    def url(self):
        return reverse('api-memdetail', kwargs={'pk': self.id})
    
    # salt []

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.id is None:
            saved_mem_file = self.mem_file
            self.mem_file = None
            saved_other_file = self.other_file
            self.other_file = None
            super(MembraneTopol, self).save(*args, **kwargs)
            self.mem_file = saved_mem_file
            self.other_file = saved_other_file
        super(MembraneTopol, self).save(*args, **kwargs)
        
    def clone(self):
        mem_clone = MembraneTopol(
            pk=None,
            name=self.name,
            search_name=self.search_name,
            temperature=self.temperature,
            equilibration=self.equilibration,
            software_id=self.software_id,
            forcefield_id=self.forcefield_id,
            nb_lipids=self.nb_lipids,
            description=self.description,
            date=self.date,
            curator_id=self.curator_id,
            membrane=self.membrane
        )
        
        mem_clone.save()
        
        clone_file_prefix = f"membranes/LIM{mem_clone.pk}"
        
        def clone_file(file, file_out):
            if file :
                clone_file = os.path.join(clone_file_prefix, file.name[14:])
                
                file_out.save(clone_file, ContentFile(file.read()), save=True)
            
        clone_file(self.mem_file, mem_clone.mem_file)
        clone_file(self.compo_file, mem_clone.compo_file)
        clone_file(self.other_file, mem_clone.other_file)
        
        for composition in self.topolcomposition_set.all():
            composition.clone(mem_clone)
        
        mem_clone.prot.set(self.prot.all())
        mem_clone.reference.set(self.reference.all())
        mem_clone.doi.set(self.doi.all())
        
        mem_clone.root_version = self.root_version if self.root_version else self
        
        last_version = MembraneTopol.objects.filter(
            root_version=mem_clone.root_version
        ).order_by('-version').first()
        
        mem_clone.version = last_version.version + 1 if last_version else 2
        
        mem_clone.save()
        
        return mem_clone

class TopolComposition(models.Model):

    UPPER = 'UP'
    LOWER = 'LO'
    LEAFLET_CHOICES = ((UPPER, 'Upper leaflet'),
                       (LOWER, 'Lower leaflet'))
    for i in range(50):
        LEAFLET_CHOICES += (('UP%d' % (i+2), 'Upper leaflet %d' % (i+2)),
                            ('LO%d' % (i+2), 'Lower leaflet %d' % (i+2)))
    LEAFLET_CHOICES += ((('UNK', 'Not in leaflet')),)

    membrane = models.ForeignKey(MembraneTopol,
                                 on_delete=models.CASCADE)
    lipid = models.ForeignKey('lipids.Lipid',
                              on_delete=models.CASCADE)
    topology = models.ForeignKey('lipids.Topology',
                                 on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    side = models.CharField(max_length=4,
                            choices=LEAFLET_CHOICES,
                            default=UPPER)
    
    def clone(self, mem_topol):
        comp_clone = TopolComposition.objects.create(
            membrane=mem_topol,
            lipid=self.lipid,
            topology=self.topology,
            number=self.number,
            side=self.side
        )
        
        comp_clone.save()
        return comp_clone


@python_2_unicode_compatible
class MembraneProt(models.Model):

    prot = models.CharField(max_length=30,
                            unique=True)

    def __str__(self):
        return self.prot


@python_2_unicode_compatible
class MembraneDoi(models.Model):

    doi = models.CharField(max_length=50)

    def __str__(self):
        return self.doi


@python_2_unicode_compatible
class Membrane(models.Model):

    name = models.CharField(max_length=100, unique=True)
    lipids = models.ManyToManyField('lipids.Lipid',
                                    through='Composition')
    tag = models.ManyToManyField('membranes.MembraneTag',
                                 blank=True)
    nb_liptypes = models.PositiveIntegerField(null=True)

    def clone(self):
        mem_clone = Membrane.objects.create(
            name=self.name,
            nb_liptypes=self.nb_liptypes
        )
        
        mem_clone.tag.set(self.tag.all())
        
        mem_clone.save()
        
        return mem_clone

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class MembraneTag(models.Model):

    tag = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.tag


class Composition(models.Model):

    UPPER = 'UP'
    LOWER = 'LO'
    LEAFLET_CHOICES = ((UPPER, 'Upper leaflet'),
                       (LOWER, 'Lower leaflet'))
    for i in range(50):
        LEAFLET_CHOICES += (('UP%d' % (i+2), 'Upper leaflet %d' % (i+2)),
                            ('LO%d' % (i+2), 'Lower leaflet %d' % (i+2)))
    LEAFLET_CHOICES += ((('UNK', 'Not in leaflet')),)

    membrane = models.ForeignKey(Membrane,
                                 on_delete=models.CASCADE)
    lipid = models.ForeignKey('lipids.Lipid',
                              on_delete=models.CASCADE)
    number = models.DecimalField(max_digits=7, decimal_places=4)
    side = models.CharField(max_length=4,
                            choices=LEAFLET_CHOICES,
                            default=UPPER)


@python_2_unicode_compatible
class MemComment(models.Model):

    membrane = models.ForeignKey(MembraneTopol,
                                 on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s %s %s' % (self.user.username, self.membrane.name, localize(self.date))


@receiver(pre_delete, sender=MembraneTopol)
def delete_file_pre_delete_mem(sender, instance, *args, **kwargs):
    if instance.mem_file:
        delete_file(instance.mem_file.path)
    if instance.compo_file:
        delete_file(instance.compo_file.path)
    if instance.other_file:
        delete_file(instance.other_file.path)
