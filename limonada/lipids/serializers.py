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

from rest_framework.serializers import HyperlinkedModelSerializer, SerializerMethodField, StringRelatedField

from .models import Topology, Lipid
from forcefields.serializers import ForcefieldSerializer
from homepage.serializers import FileField, UrlField, ReferenceSerializer

class LipidSerializer(HyperlinkedModelSerializer):
    """
    Serializer for the Lipid model, providing a JSON representation of lipid details.

    Fields:
    - name: Formatted common name of the lipid.
    - details: URL to detailed information about the lipid.

    Meta:
    - model: Associated model (Lipid).
    - fields: List of fields to include in the JSON representation.
    """
    
    name = StringRelatedField(read_only=True, source='formated_com_name')
    details = UrlField(read_only=True, source='url')
    
    class Meta:
        model = Lipid
        fields = [ 'name', 'details' ]

class TopolListSerializer(HyperlinkedModelSerializer):
    """
    Serializer for listing Topology model instances, converting them to JSON representations.
    Includes essential fields and relationships for topology listings.

    Fields:
    - name: Name of the topology.
    - details: URL to topology details.
    - forcefield: Detailed information about the force field used.
    - lipid: Detailed information about the associated lipid.
    - software: Name of the software used (retrieved via method).
    - gro_file: URL to the GRO file.
    - itp_file: URL to the ITP file.

    Methods:
    - get_software(forcefield): Retrieves the name of the first associated software.

    Meta:
    - model: Associated model (Topology).
    - fields: List of fields to include in the JSON representation.
    """
    
    name = StringRelatedField(read_only=True)
    details = UrlField(read_only=True, source='url')
    forcefield = ForcefieldSerializer(read_only=True)
    lipid = LipidSerializer(read_only=True)
    software = SerializerMethodField(read_only=True)
    gro_file = FileField(read_only=True)
    itp_file = FileField(read_only=True)
    
    class Meta:
        model = Topology
        fields = [ 'name', 'details', 'forcefield', 'lipid', 'software', 'gro_file', 'itp_file' ]
    
    def get_software(self, forcefield):
        return forcefield.software.first().name if forcefield.software.first() != None else ''
    
class TopolDetailsSerializer(HyperlinkedModelSerializer):
    """
    Serializer for detailed representation of the Topology model, providing comprehensive topology details in JSON format.

    Fields:
    - name: Name of the topology.
    - lipid: Detailed information about the associated lipid.
    - forcefield: Detailed information about the force field used.
    - software: List of software names used.
    - version: Version of the topology.
    - gro_file: URL to the GRO file.
    - itp_file: URL to the ITP file.
    - description: Description of the topology.
    - references: References related to the topology.

    Meta:
    - model: Associated model (Topology).
    - fields: List of fields to include in the JSON representation.
    """
    
    name = StringRelatedField(read_only=True)
    lipid = LipidSerializer(read_only=True)
    forcefield = ForcefieldSerializer(read_only=True)
    software = StringRelatedField(read_only=True, many=True)
    gro_file = FileField(read_only=True)
    itp_file = FileField(read_only=True)
    references = ReferenceSerializer(read_only=True, many=True, source='reference')
    
    class Meta:
        model = Topology
        fields = [ 'name', 'lipid', 'forcefield', 'software', 'version', 'gro_file', 'itp_file', 'description', 'references' ]
        
class LipidListSerializer(HyperlinkedModelSerializer):
    """
    Serializer for listing Lipid model instances, converting them to JSON representations.
    Includes essential fields for lipid listings.

    Fields:
    - details: URL to detailed information about the lipid.
    - lipid_maps_id: Lipid Maps ID of the lipid.
    - common_name: Common name of the lipid.
    - systematic_name: Systematic name of the lipid.

    Meta:
    - model: Associated model (Lipid).
    - fields: List of fields to include in the JSON representation.
    """
    
    details = UrlField(read_only=True, source='url')
    lipid_maps_id = StringRelatedField(read_only=True, source='lmid')
    common_name = StringRelatedField(read_only=True, source='com_name')
    systematic_name = StringRelatedField(read_only=True, source='sys_name')
    
    class Meta:
        model = Lipid
        fields = [ 'name', 'details', 'lipid_maps_id', 'common_name', 'systematic_name' ]
        
class LipidDetailsSerializer(HyperlinkedModelSerializer):
    """
    Serializer for detailed representation of the Lipid model, providing comprehensive lipid details in JSON format.

    Fields:
    - lipid_maps_id: Lipid Maps ID of the lipid.
    - common_name: Common name of the lipid.
    - systematic_name: Systematic name of the lipid.
    - category: Category of the lipid.
    - class_lvl_4: Level 4 classification of the lipid.
    - img: URL to the image of the lipid.

    Meta:
    - model: Associated model (Lipid).
    - fields: List of fields to include in the JSON representation.
    """
    
    lipid_maps_id = StringRelatedField(read_only=True, source='lmid')
    common_name = StringRelatedField(read_only=True, source='com_name')
    systematic_name = StringRelatedField(read_only=True, source='sys_name')
    category = StringRelatedField(read_only=True, source='core')
    class_lvl_4 = StringRelatedField(read_only=True, source='l4_class')
    img = FileField(read_only=True)
    
    class Meta:
        model = Lipid
        fields = [ 
            'name', 'lipid_maps_id', 'pubchem_cid', 'common_name', 'systematic_name', 'iupac_name',
            'formula', 'category', 'main_class', 'sub_class', 'class_lvl_4', 'img'
        ]