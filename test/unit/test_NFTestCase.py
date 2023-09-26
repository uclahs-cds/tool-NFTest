# pylint: disable=W0212
''' Test module for NFTestCase '''
import mock
from types import SimpleNamespace
from nftest.NFTestCase import NFTestCase

@mock.patch('nftest.NFTestCase.NFTestCase', wraps=NFTestCase)
def test_combine_global(mock_case):
    ''' Tests for using global config parameters '''
    test_remove_temp = True
    test_temp_directory = 'global_temp_dir'
    test_clean_logs = True
    mock_case.return_value.remove_temp = None
    mock_case.return_value.temp_dir = None
    mock_case.return_value.clean_logs = None
    mock_case.return_value._global.remove_temp = test_remove_temp
    mock_case.return_value._global.temp_dir = test_temp_directory
    mock_case.return_value._global.clean_logs = test_clean_logs
    mock_case.return_value.combine_global = NFTestCase.combine_global

    case = mock_case()
    case.combine_global(case, case._global)
    assert case.remove_temp == test_remove_temp
    assert case.temp_dir == test_temp_directory
    assert case.clean_logs == test_clean_logs

@mock.patch('nftest.NFTestCase.selectors')
@mock.patch('nftest.NFTestCase.sp.Popen')
@mock.patch('nftest.NFTestCase.NFTestCase', wraps=NFTestCase)
def test_submit(mock_case, mock_sp, mock_selectors):
    ''' Tests for submission step '''
    test_stdout = 'hello world'

    mock_sp.return_value.__enter__ = lambda x: SimpleNamespace(**{'stdout': test_stdout, 'stderr': '', 'poll': lambda: True})
    mock_selectors.DefaultSelector.register.return_value = lambda x, y, z: None

    mock_case.return_value.params_file = ''
    mock_case.return_value.output_directory_param_name = ''
    mock_case.return_value._env.NFT_OUTPUT = ''
    mock_case.return_value.temp_dir = ''
    mock_case.return_value.nf_script = ''
    mock_case.return_value.submit = NFTestCase.submit

    case = mock_case()

    assert case.submit(case).stdout == test_stdout
