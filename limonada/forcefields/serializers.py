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

# third-party

from django.urls import reverse
from rest_framework.serializers import HyperlinkedModelSerializer, SerializerMethodField, SlugRelatedField, StringRelatedField

from .models import Forcefield
from homepage.serializers import ReferenceSerializer, FileField, UrlField

class ForcefieldSerializer(HyperlinkedModelSerializer):
    """
    Serializer for the Forcefield model, converting instances to JSON representations.
    Provides detailed information about force fields used in membrane simulations.

    Fields:
    - **name**: The name of the force field.
    - **details**: URL to access detailed information about the force field.
    
    Meta:
    - **model**: The model associated with this serializer (Forcefield).
    - **fields**: List of fields to include in the JSON representation (name, details).
    """
    
    details = UrlField(read_only=True, source='url')
    
    class Meta:
        model = Forcefield
        fields = [ 'name', 'details' ]

class FfListSerializer(HyperlinkedModelSerializer):
    """
    Serializer for detailed representation of the Forcefield model, providing force field data in JSON format.

    Fields:
    - name: Name of the force field.
    - details: URL to access detailed metadata about the force field.
    - software: Name of the primary software associated with the force field.
    - type: Type categorization of the force field (e.g., atomistic, coarse-grained).
    - forcefield_file: URL to download the force field parameter file.
    - parameters_file: URL to download the molecular dynamics parameters file.

    Methods:
    - get_software(forcefield): Retrieves the name of the first software associated with the force field.

    Meta:
    - model: Associated model (Forcefield).
    - fields: List of exposed fields in the JSON representation.
    """
    
    details = UrlField(read_only=True, source='url')
    software = SerializerMethodField(read_only=True)
    type = StringRelatedField(read_only=True, source='get_forcefield_type_display')
    forcefield_file = FileField(read_only=True, source='ff_file')
    parameters_file = FileField(read_only=True, source='mdp_file')
    
    class Meta:
        model = Forcefield
        fields = [ 'name', 'details', 'software', 'type', 'forcefield_file', 'parameters_file' ]
    
    def get_software(self, forcefield):
        return "" if getattr(forcefield, 'prefetched_softwares', None) == None else forcefield.prefetched_softwares[0].name
    
class FfDetailsSerialize(HyperlinkedModelSerializer):
    """
    Serializer for comprehensive details of the Forcefield model, including additional descriptive and reference data in JSON format.

    Fields:
    - name: Name of the force field.
    - type: Type categorization of the force field (e.g., atomistic, coarse-grained).
    - forcefield_file: URL to download the force field parameter file.
    - parameters_file: URL to download the molecular dynamics parameters file.
    - software: List of names of software associated with the force field.
    - description: Detailed description providing additional information about the force field.
    - references: List of references related to the force field, each providing bibliographic data.

    Meta:
    - model: Associated model (Forcefield).
    - fields: List of exposed fields in the JSON representation.
    """
    
    type = StringRelatedField(read_only=True, source='get_forcefield_type_display')
    forcefield_file = FileField(read_only=True, source='ff_file')
    parameters_file = FileField(read_only=True, source='mdp_file')
    software = StringRelatedField(read_only=True, many=True)
    references = ReferenceSerializer(read_only=True, many=True, source='reference')
    
    class Meta:
        model = Forcefield
        fields = [ 'name', 'type', 'forcefield_file', 'parameters_file', 'software', 'description', 'references' ]