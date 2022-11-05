import mock
from NFTestCase import NFTestCase

@mock.patch('nftest.NFTestCase.NFTestCase', wraps=NFTestCase)