# -*- coding: utf-8; Mode: python; tab-width: 4; indent-tabs-mode: nil; -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
"""
Tests pour l'API des Topologies
"""

from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework import status

from lipids.models import Lipid, Topology
from forcefields.models import Forcefield, Software
from homepage.models import Reference  # si vous utilisez ce modèle dans les références des forcefields/topologies


#
# Tests pour l'endpoint list des Topologies
#

class ManyNullFieldAPITopolListTestCase(APITestCase):
    def setUp(self):
        user = User.objects.create(
            username='testuser', first_name='Test', last_name='User',
            email='test@example.com', password='testpassword'
        )
        
        forcefield = Forcefield.objects.create(id=1, curator=user, name='ForceFieldTest')
        lipid = Lipid.objects.create(name='DMDG', lmid='LTEST', curator=user)
        
        Topology.objects.create(
            id=1,
            forcefield=forcefield,
            lipid=lipid,
            curator=user,
            version='2.0'
        )
        Topology.objects.create(
            id=2,
            forcefield=forcefield,
            lipid=lipid,
            curator=user,
            version='3.1'
        )

    def tearDown(self):
        User.objects.all().delete()
        Forcefield.objects.all().delete()
        Lipid.objects.all().delete()
        Topology.objects.all().delete()

    def test_topol_list(self):
        url = reverse('api-toplist')
        response = self.client.get(url)
        
        # check the status_code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # check json structure
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['results']), 2)
        
        # check if names are valids 
        names = tuple(map(lambda x: x['name'], response.data['results']))
        
        self.assertTrue('2.0_DMDG' in names)
        self.assertTrue('3.1_DMDG' in names)
        
        # check other fields
        t1, t2 = None, None
        
        t1 = response.data['results'][0]
        t2 = response.data['results'][1]
        
        if response.data['results'][1]['name'] == '2.0_LipidTest':
            t1, t2 = t2, t1
            
        self.assertEqual(t1['details'], 'http://testserver/api/v1/topologies/1/')
        self.assertEqual(t1['forcefield']['name'], 'ForceFieldTest')
        self.assertEqual(t1['forcefield']['details'], 'http://testserver/api/v1/forcefields/1/')
        self.assertEqual(t1['lipid']['name'], 'DMDG')
        self.assertEqual(t1['lipid']['details'], 'http://testserver/api/v1/lipids/ltest/')
        self.assertEqual(t1['software'], '')
        self.assertEqual(t1['gro_file'], '')
        self.assertEqual(t1['itp_file'], '')
        
        self.assertEqual(t2['details'], 'http://testserver/api/v1/topologies/2/')
        self.assertEqual(t2['forcefield']['name'], 'ForceFieldTest')
        self.assertEqual(t2['forcefield']['details'], 'http://testserver/api/v1/forcefields/1/')
        self.assertEqual(t2['lipid']['name'], 'DMDG')
        self.assertEqual(t2['lipid']['details'], 'http://testserver/api/v1/lipids/ltest/')
        self.assertEqual(t2['software'], '')
        self.assertEqual(t2['gro_file'], '')
        self.assertEqual(t2['itp_file'], '')

class FilledFieldAPITopolListTestCase(APITestCase):
    def setUp(self):
        user = User.objects.create(
            username='testuser2', first_name='Test2', last_name='User2',
            email='test2@example.com', password='testpassword'
        )
        
        software = Software.objects.create(name='Gromacs', version='2020')
        
        forcefield = Forcefield.objects.create(id=1, curator=user, name='Test FF')
        forcefield.software.add(software)
        
        lipid = Lipid.objects.create(name='POPC', com_name='POPC', lmid='POP1', curator=user)
        
        topol = Topology.objects.create(
            id=1,
            forcefield=forcefield,
            lipid=lipid,
            version='v1.0',
            gro_file='topologies/popc.gro',
            itp_file='topologies/popc.itp',
            description='Topology for POPC',
            curator=user
        )
        
        topol.software.add(software)

    def tearDown(self):
        User.objects.all().delete()
        Forcefield.objects.all().delete()
        Software.objects.all().delete()
        Lipid.objects.all().delete()
        Topology.objects.all().delete()

    def test_topol_list(self):
        url = reverse('api-toplist')
        response = self.client.get(url)
        
        # check the status_code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # check json structure
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)
        
        # check other fields
        topol = response.data['results'][0]
        
        self.assertTrue(topol['name'])
        self.assertTrue(topol['details'].startswith('http://testserver/api/v1/topologies/'))
        
        self.assertEqual(topol['forcefield']['name'], 'Test FF')
        self.assertTrue(topol['forcefield']['details'].startswith('http://testserver/api/v1/forcefields/'))
        self.assertEqual(topol['lipid']['name'], 'POPC - POPC')
        self.assertTrue(topol['lipid']['details'].startswith('http://testserver/api/v1/lipids/'))
        self.assertEqual(topol['software'], 'Gromacs')
        self.assertEqual(topol['gro_file'], 'http://testserver/media/topologies/popc.gro')
        self.assertEqual(topol['itp_file'], 'http://testserver/media/topologies/popc.itp')


class ManyNullFieldAPITopolDetailTestCase(APITestCase):
    def setUp(self):
        user = User.objects.create(
            username='testuser', first_name='Test', last_name='User',
            email='test@example.com', password='testpassword'
        )
        
        forcefield = Forcefield.objects.create(id=1, curator=user, name='ForceFieldTest')
        lipid = Lipid.objects.create(name='DMDG', lmid='ltest', curator=user)
        
        Topology.objects.create(
            id=1,
            forcefield=forcefield,
            lipid=lipid,
            curator=user,
            version='2.0'
        )

    def tearDown(self):
        User.objects.all().delete()
        Forcefield.objects.all().delete()
        Lipid.objects.all().delete()
        Topology.objects.all().delete()

    def test_topol_detail(self):
        url = reverse('api-topdetail', kwargs={'pk': 1})
        response = self.client.get(url)
        
        # check the status_code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # check json structure
        expected_keys = {
            'name', 'lipid', 'forcefield', 'software', 
            'version', 'gro_file', 'itp_file', 'description', 'references'
        }
        self.assertEqual(set(response.data.keys()), expected_keys)
        
        # check other fields
        self.assertEqual(response.data['name'], '2.0_DMDG')
        self.assertEqual(response.data['version'], '2.0')
        self.assertEqual(response.data['gro_file'], '')
        self.assertEqual(response.data['itp_file'], '')
        self.assertEqual(response.data['description'], '')
    
        self.assertEqual(response.data['forcefield']['name'], 'ForceFieldTest')
        self.assertEqual(response.data['forcefield']['details'], 'http://testserver/api/v1/forcefields/1/')
        
        self.assertEqual(response.data['lipid']['name'], 'DMDG')
        self.assertEqual(response.data['lipid']['details'], 'http://testserver/api/v1/lipids/ltest/')
        
        self.assertEqual(response.data['software'], [])
        self.assertEqual(response.data['references'], [])

class FilledFieldAPITopolDetailTestCase(APITestCase):
    def setUp(self):
        user = User.objects.create(
            username='testuser2', first_name='Test2', last_name='User2',
            email='test2@example.com', password='testpassword'
        )
        
        software = Software.objects.create(name='Gromacs', version='2020')
        
        forcefield = Forcefield.objects.create(id=1, curator=user, name='Test FF')
        forcefield.software.add(software)
        
        lipid = Lipid.objects.create(name='POPC', com_name='POPC', lmid='pop1', curator=user)
        
        topol = Topology.objects.create(
            id=1,
            forcefield=forcefield,
            lipid=lipid,
            curator=user,
            version='v1.0',
            gro_file='topologies/popc.gro',
            itp_file='topologies/popc.itp',
            description='Topology for POPC'
        )
        topol.software.add(software)

    def tearDown(self):
        User.objects.all().delete()
        Forcefield.objects.all().delete()
        Software.objects.all().delete()
        Lipid.objects.all().delete()
        Topology.objects.all().delete()

    def test_topol_detail(self):
        url = reverse('api-topdetail', kwargs={'pk': 1})
        response = self.client.get(url)
        
        # check the status_code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # check json structure
        expected_keys = {
            'name', 'lipid', 'forcefield', 'software', 
            'version', 'gro_file', 'itp_file', 'description', 'references'
        }
        self.assertEqual(set(response.data.keys()), expected_keys)
        
        # check other fields
        self.assertEqual(response.data['name'], 'v1.0_POPC')
        self.assertEqual(response.data['version'], 'v1.0')
        self.assertEqual(response.data['gro_file'], 'http://testserver/media/topologies/popc.gro')
        self.assertEqual(response.data['itp_file'], 'http://testserver/media/topologies/popc.itp')
        self.assertEqual(response.data['description'], 'Topology for POPC')
        self.assertEqual(response.data['forcefield']['name'], 'Test FF')
        self.assertEqual(response.data['forcefield']['details'], 'http://testserver/api/v1/forcefields/1/')
        self.assertEqual(response.data['lipid']['name'], 'POPC - POPC')
        self.assertTrue(response.data['lipid']['details'].startswith('http://testserver/api/v1/lipids/'))
        self.assertEqual(response.data['software'], ['Gromacs 2020'])
        self.assertEqual(response.data['references'], [])