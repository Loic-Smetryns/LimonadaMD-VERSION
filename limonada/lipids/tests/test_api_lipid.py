from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from lipids.models import Lipid

class ManyNullFieldAPILipidListTestCase(APITestCase):
    def setUp(self):
        user = User.objects.create(
            username='testuser', first_name='Test', last_name='User',
            email='test@example.com', password='testpassword'
        )

        Lipid.objects.create(name='DMDG', lmid='LTEST1', curator=user, com_name='A')
        Lipid.objects.create(name='POPC', lmid='LTEST2', curator=user, com_name='B')

    def tearDown(self):
        User.objects.all().delete()
        Lipid.objects.all().delete()

    def test_lipid_list(self):
        url = reverse('api-liplist')
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

        # check if names are valid
        names = tuple(map(lambda x: x['name'], response.data['results']))

        self.assertTrue('DMDG' in names)
        self.assertTrue('POPC' in names)

        # check other fields
        l1, l2 = None, None

        l1 = response.data['results'][0]
        l2 = response.data['results'][1]

        if response.data['results'][1]['name'] == 'DMDG':
            l1, l2 = l2, l1

        self.assertEqual(l1['details'], 'http://testserver/api/v1/lipids/ltest1/')
        self.assertEqual(l1['lipid_maps_id'], 'LTEST1')
        self.assertEqual(l1['common_name'], 'A')
        self.assertEqual(l1['systematic_name'], '')

        self.assertEqual(l2['details'], 'http://testserver/api/v1/lipids/ltest2/')
        self.assertEqual(l2['lipid_maps_id'], 'LTEST2')
        self.assertEqual(l2['common_name'], 'B')
        self.assertEqual(l2['systematic_name'], '')

class FilledFieldAPILipidListTestCase(APITestCase):
    def setUp(self):
        user = User.objects.create(
            username='testuser2', first_name='Test2', last_name='User2',
            email='test2@example.com', password='testpassword'
        )

        Lipid.objects.create(
            name='POPC', com_name='POPC', lmid='POP1', sys_name='Systematic Name', curator=user
        )

    def tearDown(self):
        User.objects.all().delete()
        Lipid.objects.all().delete()

    def test_lipid_list(self):
        url = reverse('api-liplist')
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
        lipid = response.data['results'][0]

        self.assertTrue(lipid['name'])
        self.assertTrue(lipid['details'].startswith('http://testserver/api/v1/lipids/'))
        self.assertEqual(lipid['lipid_maps_id'], 'POP1')
        self.assertEqual(lipid['common_name'], 'POPC')
        self.assertEqual(lipid['systematic_name'], 'Systematic Name')

class ManyNullFieldAPILipidDetailTestCase(APITestCase):
    def setUp(self):
        user = User.objects.create(
            username='testuser', first_name='Test', last_name='User',
            email='test@example.com', password='testpassword'
        )

        Lipid.objects.create(name='DMDG', lmid='ltest', curator=user)

    def tearDown(self):
        User.objects.all().delete()
        Lipid.objects.all().delete()

    def test_lipid_detail(self):
        url = reverse('api-lipdetail', kwargs={'slug': 'ltest'})
        response = self.client.get(url)

        # check the status_code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check json structure
        expected_keys = {
            'name', 'lipid_maps_id', 'pubchem_cid', 'common_name', 'systematic_name',
            'iupac_name', 'formula', 'category', 'main_class', 'sub_class', 'class_lvl_4', 'img'
        }
        self.assertEqual(set(response.data.keys()), expected_keys)

        # check other fields
        self.assertEqual(response.data['name'], 'DMDG')
        self.assertEqual(response.data['lipid_maps_id'], 'ltest')
        self.assertEqual(response.data['pubchem_cid'], '')
        self.assertEqual(response.data['common_name'], '')
        self.assertEqual(response.data['systematic_name'], '')
        self.assertEqual(response.data['iupac_name'], '')
        self.assertEqual(response.data['formula'], '')
        self.assertEqual(response.data['category'], '')
        self.assertEqual(response.data['main_class'], '')
        self.assertEqual(response.data['sub_class'], '')
        self.assertEqual(response.data['class_lvl_4'], '')
        self.assertEqual(response.data['img'], '')

class FilledFieldAPILipidDetailTestCase(APITestCase):
    def setUp(self):
        user = User.objects.create(
            username='testuser2', first_name='Test2', last_name='User2',
            email='test2@example.com', password='testpassword'
        )

        Lipid.objects.create(
            name='POPC', com_name='POPC', lmid='pop1', sys_name='Systematic Name',
            iupac_name='IUPAC Name', formula='C42H82NO8P', core='Category',
            main_class='Main Class', sub_class='Sub Class', l4_class='Class Lvl 4',
            pubchem_cid='12345', img='lipids/popc.png', curator=user
        )

    def tearDown(self):
        User.objects.all().delete()
        Lipid.objects.all().delete()

    def test_lipid_detail(self):
        url = reverse('api-lipdetail', kwargs={'slug': 'pop1'})
        response = self.client.get(url)

        # check the status_code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check json structure
        expected_keys = {
            'name', 'lipid_maps_id', 'pubchem_cid', 'common_name', 'systematic_name',
            'iupac_name', 'formula', 'category', 'main_class', 'sub_class', 'class_lvl_4', 'img'
        }
        self.assertEqual(set(response.data.keys()), expected_keys)

        # check other fields
        self.assertEqual(response.data['name'], 'POPC')
        self.assertEqual(response.data['lipid_maps_id'], 'pop1')
        self.assertEqual(response.data['pubchem_cid'], '12345')
        self.assertEqual(response.data['common_name'], 'POPC')
        self.assertEqual(response.data['systematic_name'], 'Systematic Name')
        self.assertEqual(response.data['iupac_name'], 'IUPAC Name')
        self.assertEqual(response.data['formula'], 'C42H82NO8P')
        self.assertEqual(response.data['category'], 'Category')
        self.assertEqual(response.data['main_class'], 'Main Class')
        self.assertEqual(response.data['sub_class'], 'Sub Class')
        self.assertEqual(response.data['class_lvl_4'], 'Class Lvl 4')
        self.assertTrue(response.data['img'].startswith('http://testserver/media/lipids/popc.png'))
