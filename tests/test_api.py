import pytest
from flask import json
import os

def test_api_settings_get(test_client):
    """Test retrieving settings via GET request."""
    response = test_client.get('/api/settings')
    assert response.status_code == 200
    data = response.get_json()
    
    assert 'brightness_limit' in data
    assert 'rotation' in data
    assert 'clock_theme' in data

def test_api_settings_post_valid(test_client):
    """Test saving settings via POST request with valid data."""
    payload = {
        'brightness_limit': 65,
        'clock_theme': 21,
        'format_24h': False,
        'rotation': 'clock,gifs,weather',
        'fighter_interval_sec': 120
    }
    response = test_client.post('/api/settings', json=payload)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data.get('status') == 'success'
    
    # Verify the config was actually updated
    from api.server import config
    assert config.matrix_brightness == 65
    assert config.time_theme == 21
    assert config.time_24h == False
    assert config.idle_rotation == ['clock', 'gifs', 'weather']
    assert config.idle_fighter_interval == 120

def test_api_settings_post_missing_data(test_client):
    """Test POSTing to settings with empty or missing payload."""
    response = test_client.post('/api/settings', json={})
    assert response.status_code == 400
    assert response.get_json().get('message') == 'No data provided'

    # Request without json content-type should also fail gracefully
    response = test_client.post('/api/settings', data='not json')
    assert response.status_code in (400, 415)

def test_api_reboot(test_client, monkeypatch):
    """Test system reboot endpoint."""
    import subprocess
    reboot_called = False
    def mock_popen(command, shell=True):
        nonlocal reboot_called
        if "reboot" in command:
            reboot_called = True
    monkeypatch.setattr(subprocess, "Popen", mock_popen)
    
    response = test_client.post('/api/system/reboot')
    assert response.status_code == 200
    assert response.get_json().get('status') == 'success'
    assert reboot_called

def test_api_shutdown(test_client, monkeypatch):
    """Test system shutdown endpoint."""
    import subprocess
    shutdown_called = False
    def mock_popen(command, shell=True):
        nonlocal shutdown_called
        if "shutdown" in command or "poweroff" in command:
            shutdown_called = True
    monkeypatch.setattr(subprocess, "Popen", mock_popen)
    
    response = test_client.post('/api/system/shutdown')
    assert response.status_code == 200
    assert response.get_json().get('status') == 'success'
    assert shutdown_called

def test_api_fonts_get(test_client, monkeypatch):
    """Test fonts listing API."""
    def mock_listdir(path):
        return ['font1.ttf', 'font2.bdf', 'font3.otf', 'image.png', 'script.sh']
    monkeypatch.setattr(os, "listdir", mock_listdir)
    
    response = test_client.get('/api/fonts')
    assert response.status_code == 200
    fonts = response.get_json()
    assert 'font1.ttf' in fonts
    assert 'font2.bdf' in fonts
    assert 'font3.otf' in fonts
    assert 'image.png' not in fonts

def test_api_system_info(test_client, monkeypatch):
    """Test system info endpoint."""
    import sys
    from unittest.mock import MagicMock
    
    mock_psutil = MagicMock()
    mock_psutil.cpu_percent.return_value = 10.0
    mock_psutil.virtual_memory.return_value = MagicMock(used=1024*1024*100, total=1024*1024*1024, percent=10.0)
    mock_psutil.disk_usage.return_value = MagicMock(free=1024**3 * 50, total=1024**3 * 100, percent=50.0)
    sys.modules['psutil'] = mock_psutil
    
    def mock_run(*args, **kwargs):
        class MockResult:
            stdout = "mocked output"
            returncode = 0
        return MockResult()
    import subprocess
    monkeypatch.setattr(subprocess, "run", mock_run)
    
    response = test_client.get('/api/system_info')
    assert response.status_code == 200
    data = response.get_json()
    assert 'temperature_c' in data

def test_api_wifi(test_client, monkeypatch):
    """Test WiFi connection endpoint."""
    def mock_run(*args, **kwargs):
        class MockResult:
            returncode = 0
            stderr = ""
        return MockResult()
    import subprocess
    monkeypatch.setattr(subprocess, "run", mock_run)
    
    response = test_client.post('/api/wifi', json={'ssid': 'TestNet', 'password': 'pass'})
    assert response.status_code == 200
    assert response.get_json().get('status') == 'success'


def test_api_message(test_client):
    """Test sending a message to matrix."""
    response = test_client.post('/api/message', json={'message': 'Hello World', 'color': '#ff0000'})
    assert response.status_code == 200

def test_api_clock(test_client):
    """Test setting clock duration override."""
    response = test_client.post('/api/clock', json={'duration': 60})
    assert response.status_code == 200

def test_api_playlists(test_client, monkeypatch):
    """Test playlist routes."""
    def mock_listdir(path):
        return ['mario.gif', 'sonic.gif']
    monkeypatch.setattr(os, "listdir", mock_listdir)
    
    res = test_client.get('/api/playlists')
    assert res.status_code == 200
    
    res = test_client.get('/api/sprites/playlists')
    assert res.status_code == 200
    
    res = test_client.post('/api/playlists/save', json={'selected': 'mario.gif'})
    assert res.status_code == 200
    
    res = test_client.post('/api/sprites/playlists/save', json={'selected': 'ryu'})
    assert res.status_code == 200
