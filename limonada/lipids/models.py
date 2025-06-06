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
import re
import shutil

# third-party
import requests

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.db import models
from django.db.models.signals import m2m_changed, pre_delete, pre_save
from django.dispatch.dispatcher import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.utils.formats import localize
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.core.files.base import ContentFile


# Django apps
from limonada.functions import delete_file

# local Django
from .functions import residuetypes


_UNSAVED_ITPFILE = 'unsaved_itpfile'
_UNSAVED_GROFILE = 'unsaved_grofile'


def validate_name(value):
    """Validation of the lipid short name format

    This function checks that lipid short names are 4 alphanumeric characters long and uppercase.
    It also check that the chosen name is not usually used for other biomolecule residues.

    Parameters
    ----------
    value : string
        defines the lipid short name
    """
    if len(value) != 4 or not re.match(r'[0-9A-Z]{4}', value):
        raise ValidationError(_('Invalid name'),
                              code='invalid',
                              params={'value': value})
    residues = residuetypes() # dict of residue names from residuetypes.dat
    if value in residues.keys():
        raise ValidationError(_('%s is usually used for a protein residue name' % value),
                              code='invalid',
                              params={'value': value})


def validate_lmid(value):
    """Validation of the lipid LMID field

    The LMID must start by LM or by LI. To start by LM, the LMID must exist in LipidMaps.

    Parameters
    ----------
    value : string
        defines the lipid LMID
    """
    if value[:2] == 'LM':
        try:
            lm_response = requests.get('http://www.lipidmaps.org/rest/compound/lm_id/%s/all/json' % value)
            lm_data_raw = lm_response.json()
            if lm_data_raw == []:
                raise ValidationError(_('Invalid LMID'),
                                      code='invalid',
                                      params={'value': value})
        except ValidationError:
            raise ValidationError(_('Invalid LMID'),
                                  code='invalid',
                                  params={'value': value})
    elif value[:2] != 'LI':
        raise ValidationError(_('Invalid LMID'),
                              code='invalid',
                              params={'value': value})


def validate_file_extension(value):
    """Valdiation of formats accepted for the lipid picture

    Parameters
    ----------
    value : ImageField()
    """
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.png', '.jpg']
    if ext not in valid_extensions:
        raise ValidationError(u'File not supported!')


def validate_img_size(value):
    """The lipid picture size should not exceed 1MB

    Parameters
    ----------
    value : ImageField()
    """
    filesize = value.size
    if filesize > 1048576:
        raise ValidationError("The maximum file size that can be uploaded is 1MB")
    #else:
    #    return value


def img_path(instance, filename):
    """The lipid picture is uploaded to the "media/lipids" directory and named accoding it's LMID.
    This function returns the path to this new location.
    If a file already exist at this location with one of the two permitted extension, it is removed.

    Parameters
    ----------
    instance : instance of the lipid model 
    filename : name of the uploaded file

    Returns
    -------
    filepath 
    """
    ext = os.path.splitext(filename)[1]
    filepath = 'lipids/{0}{1}'.format(instance.lmid, ext)
    valid_extensions = ['.png', '.jpg']
    for ext in valid_extensions:
        imgpath = 'lipids/{0}{1}'.format(instance.lmid, ext)
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, imgpath)):
            os.remove(os.path.join(settings.MEDIA_ROOT, imgpath))
    return filepath


def validate_file_size(value):
    """The lipid topology and structure files should not exceed 200KB

    Parameters
    ----------
    value : FileField()
    """
    filesize = value.size
    if filesize > 209715:
        raise ValidationError("The maximum file size that can be uploaded is 200KB")
    #else:
    #    return value


def file_path(instance, filename):
    """The lipid topology and structure files are uploaded to the
    "topologies/{software}/{forcefield}/{lipid}" directory and named accoding the LMID.
    This function returns the path to this new location.
    If a file already exist at this location with one of the two permitted extension, it is removed.

    Parameters
    ----------
    instance : instance of the lipid model 
    filename : name of the uploaded file

    Returns
    -------
    filepath 
    """
    ext = os.path.splitext(filename)[1]
    version = unidecode(instance.version).replace(' ', '_')
    forcefield = unidecode(instance.forcefield.name).replace(' ', '_')
    # ex.: topologies/Gromacs/Martini/POPC/version/POPC.{itp,gro} (we assume gromacs for now)
    filepath = 'topologies/{0}/{1}/{2}/{3}/{2}{4}'.format(instance.software.all()[0].name, forcefield,
                                                          instance.lipid.name, version, ext)
    if os.path.isfile(os.path.join(settings.MEDIA_ROOT, filepath)):
        os.remove(os.path.join(settings.MEDIA_ROOT, filepath))
    return filepath


@python_2_unicode_compatible
class Lipid(models.Model):

    name = models.CharField(max_length=4,
                            validators=[validate_name],
                            unique=True)
    lmid = models.CharField(max_length=20,
                            validators=[validate_lmid],
                            unique=True)
    com_name = models.CharField(max_length=200,
                                unique=True)
    search_name = models.CharField(max_length=300)
    sys_name = models.CharField(max_length=200,
                                blank=True)
    iupac_name = models.CharField(max_length=500,
                                  blank=True)
    formula = models.CharField(max_length=30,
                               blank=True)
    core = models.CharField(max_length=200)
    main_class = models.CharField(max_length=200)
    sub_class = models.CharField(max_length=200)
    l4_class = models.CharField(max_length=200,
                                blank=True)
    pubchem_cid = models.CharField(max_length=50,
                                   blank=True)
    img = models.ImageField(upload_to=img_path,
                            validators=[validate_file_extension,
                                        validate_img_size],
                            null=True)
    curator = models.ForeignKey(User,
                                on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.search_name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.lmid.lower()) if self.lmid else (slugify(self.name) if self.name else str(self.id))
        super(Lipid, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('lipdetail', args=[str(self.slug)])
    
    @property
    def formated_com_name(self):
        return f"{self.name} - {self.com_name}" if self.com_name != '' else self.name
    
    @property
    def url(self):
        return reverse('api-lipdetail', kwargs={'slug': self.slug})


@python_2_unicode_compatible
class TopologyResidue(models.Model):

    name = models.CharField(max_length=6,
                            unique=True)

    def __str__(self):
        return self.name


class ResidueList(models.Model):

    topology = models.ForeignKey('lipids.Topology',
                                 on_delete=models.CASCADE)
    residue = models.ForeignKey(TopologyResidue,
                                on_delete=models.CASCADE)
    position = models.PositiveIntegerField()

    def clone(self, topol):
        clone = ResidueList(
            topology=topol,
            residue=self.residue,
            position=self.position
        )
        clone.save()
        
        return clone

    def __str__(self):
        return self.residue.name


@python_2_unicode_compatible
class Topology(models.Model):

    software = models.ManyToManyField('forcefields.Software')
    forcefield = models.ForeignKey('forcefields.Forcefield',
                                   on_delete=models.CASCADE)
    lipid = models.ForeignKey(Lipid,
                              on_delete=models.CASCADE)
    itp_file = models.FileField(upload_to=file_path,
                                validators=[validate_file_size])
    gro_file = models.FileField(upload_to=file_path,
                                validators=[validate_file_size])
    version = models.CharField(max_length=30,
                               help_text='YearAuthor')
    head = models.CharField(max_length=10)
    residues = models.ManyToManyField(TopologyResidue,
                                      through=ResidueList)
    #5thdigit ?
    description = models.TextField(blank=True)
    reference = models.ManyToManyField('homepage.Reference')
    date = models.DateField(auto_now=True)
    curator = models.ForeignKey(User, on_delete=models.CASCADE)
    
    t_version = models.IntegerField(default=1)
    root_version = models.ForeignKey('lipids.Topology', null=True, blank=True, on_delete=models.DO_NOTHING)

    def __str__(self):
        return '%s_%s' % (self.lipid.name, self.version)

    def get_absolute_url(self):
        return reverse('topdetail', args=[str(self.pk)])
    
    @property
    def name(self):
        return f"{self.version}_{self.lipid.name}"
    
    @property
    def url(self):
        return reverse('api-topdetail', kwargs={'pk': self.id})
    
    def clone(self):
        topol_clone = Topology(
            forcefield=self.forcefield,
            lipid=self.lipid,
            version=self.version,
            head=self.head,
            description=self.description,
            date=self.date,
            curator=self.curator
        )
        topol_clone.save()
        
        topol_clone.root_version = self.root_version if self.root_version else self
        
        last_version = Topology.objects.filter(
            root_version=topol_clone.root_version
        ).order_by('-t_version').first()
        
        topol_clone.t_version = last_version.t_version + 1 if last_version else 2
        
        for res in self.residuelist_set.all():
            res.clone(topol_clone)
        
        topol_clone.software.set(self.software.all())
        topol_clone.reference.set(self.reference.all())
        
        if self.itp_file:
            topol_clone.itp_file=topol_clone.root_version.itp_file.name[:-4]+"_"+str(topol_clone.t_version)+topol_clone.root_version.itp_file.name[-4:]
            shutil.copy2(self.itp_file.path, topol_clone.itp_file.path)
        
        if self.gro_file:
            topol_clone.gro_file=topol_clone.root_version.gro_file.name[:-4]+"_"+str(topol_clone.t_version)+topol_clone.root_version.gro_file.name[-4:]
            shutil.copy2(self.gro_file.path, topol_clone.gro_file.path)
        
        topol_clone.save()
    
        
        return topol_clone


@python_2_unicode_compatible
class TopComment(models.Model):

    topology = models.ForeignKey('lipids.Topology',
                                 on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s %s %s %s' % (self.user.username, self.topology.lipid.name, self.topology.version,
                                localize(self.date))


@receiver(pre_delete, sender=Lipid)
def delete_file_pre_delete_lip(sender, instance, *args, **kwargs):
    if instance.img:
        delete_file(instance.img.path)


@receiver(pre_delete, sender=Topology)
def delete_file_pre_delete_top(sender, instance, *args, **kwargs):
    if instance.itp_file:
        delete_file(instance.itp_file.path)
    if instance.gro_file:
        delete_file(instance.gro_file.path)


@receiver(pre_save, sender=Topology)
def skip_saving_file(sender, instance, **kwargs):
    if not instance.pk and not hasattr(instance, _UNSAVED_GROFILE):
        setattr(instance, _UNSAVED_ITPFILE, instance.itp_file)
        instance.itp_file = None
        setattr(instance, _UNSAVED_GROFILE, instance.gro_file)
        instance.gro_file = None


@receiver(m2m_changed, sender=Topology.software.through)
def save_file_on_m2m(sender, instance, action, **kwargs):
    """ The directory where the topology files will be saved involve in its path the name of the software
        familly with which it can be used. For the Topology table, software is a ManyToMany field that
        can only be saved once the Topology instance has an id.
    """
    if action == 'post_add' and hasattr(instance, _UNSAVED_ITPFILE) and hasattr(instance, _UNSAVED_GROFILE):
        instance.itp_file = getattr(instance, _UNSAVED_ITPFILE)
        instance.gro_file = getattr(instance, _UNSAVED_GROFILE)
        instance.save()
        instance.__dict__.pop(_UNSAVED_ITPFILE)
        instance.__dict__.pop(_UNSAVED_GROFILE)
