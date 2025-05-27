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

from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

from forcefields.models import Forcefield, Software
from homepage.models import Reference

class ManyNullFieldAPIFfListTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='testuser', first_name='Test', last_name='User', email='test@example.com',
            password='testpassword'
        )

        self.software = Software.objects.create(name='Gromacs', version='5.0')

        self.forcefield = Forcefield.objects.create(
            id=1, name='Test FF', curator=self.user
        )

        self.forcefield.software.add(self.software)

    def tearDown(self):
        User.objects.all().delete()
        Software.objects.all().delete()
        Forcefield.objects.all().delete()

    def test_ff_list(self):
        url = reverse('api-fflist')
        response = self.client.get(url)

        # check the status_code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check json structure
        self.assertEqual(len(response.data), 4)
        self.assertTrue('count' in response.data.keys())
        self.assertTrue('next' in response.data.keys())
        self.assertTrue('previous' in response.data.keys())
        self.assertTrue('results' in response.data.keys())

        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)

        # check fields
        ff_data = response.data['results'][0]

        self.assertEqual(ff_data['name'], 'Test FF')
        self.assertEqual(ff_data['details'], 'http://testserver/api/v1/forcefields/1/')
        self.assertEqual(ff_data['software'], 'Gromacs')
        self.assertEqual(ff_data['type'], 'All atom')
        self.assertEqual(ff_data['forcefield_file'], '')
        self.assertEqual(ff_data['parameters_file'], '')
        
class FilledFieldAPIFfListTestCase(APITestCase):

    def setUp(self):
        user = User.objects.create(
            username='testuser', first_name='Test', last_name='User', email='test@example.com',
            password='testpassword'
        )

        software1 = Software.objects.create(name='Gromacs', version='5.0')
        software2 = Software.objects.create(name='Gromacs', version='20')

        forcefield = Forcefield.objects.create(
            id=1, name='Test FF', 
            curator=user, 
            forcefield_type='CG', 
            description='Test description',
            ff_file='forcefields/Gromacs/Charmm27.ff.zip', 
            mdp_file='forcefields/Gromacs/Charmm27.par.zip'
        )

        forcefield.software.add(software1, software2)

        reference = Reference.objects.create(title="Test Reference", year=2001, curator=user)
        forcefield.reference.add(reference)

    def tearDown(self):
        User.objects.all().delete()
        Software.objects.all().delete()
        Forcefield.objects.all().delete()
        Reference.objects.all().delete()

    def test_ff_list(self):
        url = reverse('api-fflist')
        response = self.client.get(url)

        # check the status_code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check json structure
        self.assertEqual(len(response.data), 4)
        self.assertTrue('count' in response.data.keys())
        self.assertTrue('next' in response.data.keys())
        self.assertTrue('previous' in response.data.keys())
        self.assertTrue('results' in response.data.keys())

        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)

        # check fields
        ff_data = response.data['results'][0]

        self.assertEqual(ff_data['name'], 'Test FF')
        self.assertEqual(ff_data['details'], 'http://testserver/api/v1/forcefields/1/')
        self.assertEqual(ff_data['software'], 'Gromacs')
        self.assertEqual(ff_data['type'], 'Coarse grained')
        self.assertEqual(ff_data['forcefield_file'], 'http://testserver/media/forcefields/Gromacs/Charmm27.ff.zip')
        self.assertEqual(ff_data['parameters_file'], 'http://testserver/media/forcefields/Gromacs/Charmm27.par.zip')
        
class ManyNullFieldAPIFfDetailTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='testuser', first_name='Test', last_name='User', email='test@example.com',
            password='testpassword'
        )

        self.software = Software.objects.create(name='Gromacs', version='5.0')

        self.forcefield = Forcefield.objects.create(
            id=1, name='Test FF', curator=self.user,
            ff_file='forcefields/Gromacs/Charmm27.ff.zip'
        )

        self.forcefield.software.add(self.software)

    def tearDown(self):
        User.objects.all().delete()
        Software.objects.all().delete()
        Forcefield.objects.all().delete()

    def test_ff_detail(self):
        url = reverse('api-ffdetail', kwargs={'pk': self.forcefield.id})
        response = self.client.get(url)

        # check the status_code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check json structure
        self.assertEqual(len(response.data), 7)
        self.assertTrue('name' in response.data.keys())
        self.assertTrue('type' in response.data.keys())
        self.assertTrue('forcefield_file' in response.data.keys())
        self.assertTrue('parameters_file' in response.data.keys())
        self.assertTrue('software' in response.data.keys())
        self.assertTrue('description' in response.data.keys())
        self.assertTrue('references' in response.data.keys())

        # check fields
        ff_data = response.data

        self.assertEqual(ff_data['name'], 'Test FF')
        self.assertEqual(ff_data['type'], 'All atom')
        self.assertEqual(ff_data['forcefield_file'], 'http://testserver/media/forcefields/Gromacs/Charmm27.ff.zip')
        self.assertEqual(ff_data['parameters_file'], '')
        self.assertEqual(ff_data['software'], ['Gromacs 5.0'])
        self.assertEqual(ff_data['description'], '')
        self.assertEqual(ff_data['references'], [])

class FilledFieldAPIFfDetailTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='testuser', first_name='Test', last_name='User', email='test@example.com',
            password='testpassword'
        )

        self.software1 = Software.objects.create(name='Gromacs', version='5.0')
        self.software2 = Software.objects.create(name='Gromacs', version='20')

        self.forcefield = Forcefield.objects.create(
            id=1, name='Test FF', curator=self.user,
            forcefield_type='CG', description='Test description',
            ff_file='forcefields/Gromacs/Charmm27.ff.zip',
            mdp_file='forcefields/Gromacs/Charmm27.par.zip'
        )

        self.forcefield.software.add(self.software1, self.software2)

        self.reference = Reference.objects.create(title="Test Reference", year=2023, curator=self.user)
        self.forcefield.reference.add(self.reference)

    def tearDown(self):
        User.objects.all().delete()
        Software.objects.all().delete()
        Forcefield.objects.all().delete()
        Reference.objects.all().delete()

    def test_ff_detail(self):
        url = reverse('api-ffdetail', kwargs={'pk': self.forcefield.id})
        response = self.client.get(url)

        # check the status_code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check json structure
        self.assertEqual(len(response.data), 7)
        self.assertTrue('name' in response.data.keys())
        self.assertTrue('type' in response.data.keys())
        self.assertTrue('forcefield_file' in response.data.keys())
        self.assertTrue('parameters_file' in response.data.keys())
        self.assertTrue('software' in response.data.keys())
        self.assertTrue('description' in response.data.keys())
        self.assertTrue('references' in response.data.keys())

        # check fields
        ff_data = response.data

        self.assertEqual(ff_data['name'], 'Test FF')
        self.assertEqual(ff_data['type'], 'Coarse grained')
        self.assertEqual(ff_data['forcefield_file'], 'http://testserver/media/forcefields/Gromacs/Charmm27.ff.zip')
        self.assertEqual(ff_data['parameters_file'], 'http://testserver/media/forcefields/Gromacs/Charmm27.par.zip')
        self.assertEqual(sorted(ff_data['software']), sorted(['Gromacs 5.0', 'Gromacs 20']))
        self.assertEqual(ff_data['description'], 'Test description')
        self.assertEqual(len(ff_data['references']), 1)
        self.assertEqual(ff_data['references'][0]['title'], 'Test Reference')
        self.assertEqual(ff_data['references'][0]['year'], 2023)