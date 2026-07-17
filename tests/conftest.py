import pytest
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.server import app, set_app_instance
from core.config import Config

class MockMatrix:
    def __init__(self):
        self.brightness = 0

class MockMatrixWrapper:
    def __init__(self):
        self.matrix = MockMatrix()

class MockAppInstance:
    def __init__(self, config):
        self.config = config
        self.mw = MockMatrixWrapper()

@pytest.fixture
def mock_config(tmp_path):
    # Provide a clean, isolated config
    conf_file = tmp_path / "conf.ini"
    conf = Config(config_file=str(conf_file))
    conf.matrix_brightness = 50
    conf.matrix_rows = 32
    conf.matrix_cols = 64
    conf.matrix_chain = 1
    conf.matrix_parallel = 1
    conf.matrix_mapping = "regular"
    conf.matrix_rgb_sequence = "RGB"
    conf.matrix_pwm_bits = 11
    conf.matrix_pwm_lsb_nanoseconds = 130
    conf.idle_rotation = ['clock', 'date']
    conf.time_theme = 18
    # Add other defaults to ensure stability
    return conf

@pytest.fixture
def test_client(mock_config):
    # Setup the application instance mock
    app_instance = MockAppInstance(mock_config)
    set_app_instance(app_instance)
    
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
