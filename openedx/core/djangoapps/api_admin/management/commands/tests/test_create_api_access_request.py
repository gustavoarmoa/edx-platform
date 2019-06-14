import ddt
from django.core.management import call_command
from django.test import TestCase
from student.tests.factories import UserFactory
from openedx.core.djangoapps.api_admin.models import (
    ApiAccessConfig,
    ApiAccessRequest,
)
from django.core.management.base import CommandError
from mock import patch

from openedx.core.djangoapps.api_admin.management.commands import create_api_access_request


@ddt.ddt
class TestCreateApiAccessRequest(TestCase):
    """ Test create_api_access_request command """

    @classmethod
    def setUpClass(cls):
        super(TestCreateApiAccessRequest, cls).setUpClass()
        cls.command = 'create_api_access_request'
        cls.user = UserFactory()

    def assert_models_exist(self, expect_request_exists, expect_config_exists):
        #import pdb; pdb.set_trace()
        self.assertEquals(
            ApiAccessRequest.objects.filter(user=self.user).exists(),
            expect_request_exists
        )
        self.assertEquals(
            ApiAccessConfig.objects.filter(enabled=True).exists(),
            expect_config_exists
        )

    @ddt.data(False, True)
    def test_create_api_access_request(self, create_config):
        self.assert_models_exist(False, False)

        call_command(self.command, self.user.username, create_config=create_config)

        self.assert_models_exist(True, create_config)

    def test_user_not_found(self):
        with self.assertRaisesRegex(CommandError, r'User .*? not found'):
            call_command(self.command, 'not-a-user-notfound-nope')

    @patch('openedx.core.djangoapps.api_admin.models.ApiAccessRequest.objects.create')
    def test_api_request_error(self, mocked_method):
        mocked_method.side_effect = Exception()

        self.assert_models_exist(False, False)

        with self.assertRaisesRegex(CommandError, r'Unable to create ApiAccessRequest .*'):
            call_command(self.command, self.user.username)

        self.assert_models_exist(False, False)

    @patch('openedx.core.djangoapps.api_admin.models.ApiAccessConfig.objects.get_or_create')
    def test_api_config_error(self, mocked_method):
        mocked_method.side_effect = Exception()
        self.assert_models_exist(False, False)

        with self.assertRaisesRegex(CommandError, r'Unable to create ApiAccessConfig\. .*'):
            call_command(self.command, self.user.username, create_config=True)

        self.assert_models_exist(True, False)
