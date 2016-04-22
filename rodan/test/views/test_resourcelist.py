from rest_framework.test import APITestCase
from rest_framework import status
from rodan.models import Resource, ResourceList
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
from model_mommy import mommy


class ResourceListViewTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.test_project = mommy.make('rodan.Project')
        self.test_resourcetype = mommy.make('rodan.ResourceType')
        self.test_resources = mommy.make(
            'rodan.Resource', _quantity=5,
            project=self.test_project,
            resource_type=self.test_resourcetype
        )
        self.client.force_authenticate(user=self.test_superuser)

    def test_create_successfully(self):
        rl_obj = {
            'resources': map(lambda x: "http://localhost:8000/resource/{0}/".format(x.uuid), self.test_resources),
            "name": "test resource list"
        }
        response = self.client.post("/resourcelists/", rl_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        rl_uuid = response.data['uuid']
        rl = ResourceList.objects.get(uuid=rl_uuid)
        self.assertEqual(rl.project, self.test_project)
        self.assertEqual(rl.resource_type, self.test_resourcetype)
        self.assertEqual(rl.resources.count(), 5)
        resources = rl.resources.all()
        self.assertEqual(resources[0], self.test_resources[0])
        self.assertEqual(resources[1], self.test_resources[1])
        self.assertEqual(resources[2], self.test_resources[2])
        self.assertEqual(resources[3], self.test_resources[3])
        self.assertEqual(resources[4], self.test_resources[4])

    def test_create_conflict_project(self):
        p2 = mommy.make('rodan.Project')
        r2 = mommy.make('rodan.Resource',
                        project=p2,
                        resource_type=self.test_resourcetype)
        rl_obj = {
            'resources': map(lambda x: "http://localhost:8000/resource/{0}/".format(x.uuid), self.test_resources+[r2]),
            "name": "test resource list"
        }
        response = self.client.post("/resourcelists/", rl_obj, format='json')
        anticipated_message = {'resources': ["All Resources should belong to the same Project."]}

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)

    def test_create_conflict_resourcetype(self):
        rt2 = mommy.make('rodan.ResourceType')
        r2 = mommy.make('rodan.Resource',
                        project=self.test_project,
                        resource_type=rt2)
        rl_obj = {
            'resources': map(lambda x: "http://localhost:8000/resource/{0}/".format(x.uuid), self.test_resources+[r2]),
            "name": "test resource list"
        }
        response = self.client.post("/resourcelists/", rl_obj, format='json')
        anticipated_message = {'resources': ["All Resources should have the same ResourceType."]}

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)

    def test_patch_conflict_project(self):
        rl_obj = {
            'resources': map(lambda x: "http://localhost:8000/resource/{0}/".format(x.uuid), self.test_resources),
            "name": "test resource list"
        }
        response = self.client.post("/resourcelists/", rl_obj, format='json')
        assert response.status_code == status.HTTP_201_CREATED, 'This should pass'
        rl_uuid = response.data['uuid']

        rt2 = mommy.make('rodan.ResourceType')
        r2 = mommy.make('rodan.Resource',
                        project=self.test_project,
                        resource_type=rt2)
        rl_obj = {
            'resources': map(lambda x: "http://localhost:8000/resource/{0}/".format(x.uuid), self.test_resources+[r2]),
        }
        response = self.client.patch("/resourcelist/{0}/".format(rl_uuid), rl_obj, format='json')
        anticipated_message = {'resources': ["All Resources should have the same ResourceType."]}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)

    def test_patch_conflict_resourcetype(self):
        rl_obj = {
            'resources': map(lambda x: "http://localhost:8000/resource/{0}/".format(x.uuid), self.test_resources),
            "name": "test resource list"
        }
        response = self.client.post("/resourcelists/", rl_obj, format='json')
        assert response.status_code == status.HTTP_201_CREATED, 'This should pass'
        rl_uuid = response.data['uuid']

        p2 = mommy.make('rodan.Project')
        r2 = mommy.make('rodan.Resource',
                        project=p2,
                        resource_type=self.test_resourcetype)
        rl_obj = {
            'resources': map(lambda x: "http://localhost:8000/resource/{0}/".format(x.uuid), self.test_resources+[r2]),
        }
        response = self.client.patch("/resourcelist/{0}/".format(rl_uuid), rl_obj, format='json')
        anticipated_message = {'resources': ["All Resources should belong to the same Project."]}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)

    def test_create_empty_resourcelist(self):
        rl_obj = {
            'resources': [],
            "name": "test resource list"
        }
        response = self.client.post("/resourcelists/", rl_obj, format='json')
        anticipated_message = {'resources': ["This list may not be empty."]}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)

    def test_patch_empty_resourcelist(self):
        rl_obj = {
            'resources': map(lambda x: "http://localhost:8000/resource/{0}/".format(x.uuid), self.test_resources),
            "name": "test resource list"
        }
        response = self.client.post("/resourcelists/", rl_obj, format='json')
        assert response.status_code == status.HTTP_201_CREATED, 'This should pass'
        rl_uuid = response.data['uuid']

        rl_obj = {
            'resources': []
        }
        response = self.client.patch("/resourcelist/{0}/".format(rl_uuid), rl_obj, format='json')
        anticipated_message = {'resources': ["This list may not be empty."]}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)