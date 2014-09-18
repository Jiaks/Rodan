from django.test import TestCase
from rodan.models.inputport import InputPort
from rodan.models.workflowjob import WorkflowJob
from rodan.models.outputport import OutputPort
from rodan.models.job import Job
from rodan.models.connection import Connection


class ConnectionTestCase(TestCase):
    fixtures = ['1_users', '2_initial_data']

    def setUp(self):
        self.test_inputport = InputPort.objects.get(uuid="dd35645a7a7845c5a72c9a856ccb920e")
        self.test_outputport = OutputPort.objects.get(uuid="bbdd13ddf05844aa8549e93e82ae4fd2")
        self.test_workflowjob1 = self.test_inputport.workflow_job
        self.test_workflowjob2 = self.test_outputport.workflow_job

        self.test_data = {
            "input_port": self.test_inputport,
            "output_port": self.test_outputport,
        }

    def test_save(self):
        connection = Connection(**self.test_data)
        connection.save()

        retr_conn = Connection.objects.get(**self.test_data)

        self.assertEqual(retr_conn.workflow, self.test_workflowjob1.workflow)
