"""Test module for NFTestENV"""

from nftest.NFTestENV import NFTestENV


def test_nftest_env_load(monkeypatch):
    """Tests loading of values from environment"""
    test_out_directory = "random/directory_output"
    test_temp_directory = "random/directory_temp"
    test_init_directory = "random/directory_init"
    test_log_level = "random_log_level"
    test_log_file = "random/log.log"

    monkeypatch.setenv("NFT_OUTPUT", test_out_directory)
    monkeypatch.setenv("NFT_TEMP", test_temp_directory)
    monkeypatch.setenv("NFT_INIT", test_init_directory)
    monkeypatch.setenv("NFT_LOG_LEVEL", test_log_level)
    monkeypatch.setenv("NFT_LOG", test_log_file)

    # Clear any existing singleton value
    NFTestENV._instances.pop(NFTestENV, None)
    nftest_env = NFTestENV()

    assert NFTestENV in NFTestENV._instances

    assert nftest_env.NFT_OUTPUT == test_out_directory
    assert nftest_env.NFT_TEMP == test_temp_directory
    assert nftest_env.NFT_INIT == test_init_directory
    assert nftest_env.NFT_LOG_LEVEL == test_log_level
    assert nftest_env.NFT_LOG == test_log_file


def test_singleton():
    """Tests singleton pattern"""
    nftest_env1 = NFTestENV()
    nftest_env2 = NFTestENV()

    assert id(nftest_env1) == id(nftest_env2)

    NFTestENV._instances.pop(NFTestENV, None)
    nftest_env3 = NFTestENV()

    assert id(nftest_env1) != id(nftest_env3)
