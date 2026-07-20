import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config import Config


def test_config_defaults_when_file_missing(tmp_path):
    """No conf.ini at all -> pure hardcoded defaults, no crash."""
    conf_file = tmp_path / "does_not_exist.ini"
    conf = Config(config_file=str(conf_file))

    assert conf.matrix_width == 64
    assert conf.matrix_height == 32
    assert conf.matrix_brightness == 50
    assert conf.time_24h is True
    assert conf.standby_enabled is False
    assert conf.api_auth_enabled is False
    # A fresh install with no config file yet still gets a generated API token so that
    # enabling auth later doesn't require a reboot to generate one.
    assert isinstance(conf.api_token, str)


def test_config_computes_total_dimensions_from_chain_parallel(tmp_path):
    """matrix_width/height are COLS*CHAIN / ROWS*PARALLEL, not the raw per-panel values."""
    conf_file = tmp_path / "conf.ini"
    conf_file.write_text(
        "[MATRIX]\n"
        "ROWS=32\n"
        "COLS=64\n"
        "CHAIN=3\n"
        "PARALLEL=2\n"
    )
    conf = Config(config_file=str(conf_file))

    assert conf.matrix_cols == 64
    assert conf.matrix_rows == 32
    assert conf.matrix_width == 64 * 3
    assert conf.matrix_height == 32 * 2


def test_config_parses_idle_rotation_csv(tmp_path):
    conf_file = tmp_path / "conf.ini"
    conf_file.write_text(
        "[IDLE]\n"
        "ROTATION=clock, date ,weather\n"
    )
    conf = Config(config_file=str(conf_file))

    assert conf.idle_rotation == ["clock", "date", "weather"]


def test_config_malformed_values_fall_back_to_defaults(tmp_path):
    """get_int()/get_bool() must swallow bad values rather than raising."""
    conf_file = tmp_path / "conf.ini"
    conf_file.write_text(
        "[MATRIX]\n"
        "BRIGHTNESS=not-a-number\n"
        "[MQTT]\n"
        "ENABLED=maybe\n"
    )
    conf = Config(config_file=str(conf_file))

    assert conf.matrix_brightness == 50   # default preserved, no crash
    assert conf.mqtt_enabled is False


def test_config_save_and_reload_round_trip(tmp_path):
    conf_file = tmp_path / "conf.ini"
    conf = Config(config_file=str(conf_file))
    conf.matrix_brightness = 77
    conf.time_theme = 12
    conf.idle_rotation = ["clock", "gifs"]
    conf.standby_enabled = True
    conf.save()

    assert conf_file.exists()

    reloaded = Config(config_file=str(conf_file))
    assert reloaded.matrix_brightness == 77
    assert reloaded.time_theme == 12
    assert reloaded.idle_rotation == ["clock", "gifs"]
    assert reloaded.standby_enabled is True


def test_config_api_token_persists_across_reloads(tmp_path):
    conf_file = tmp_path / "conf.ini"
    first = Config(config_file=str(conf_file))
    token = first.api_token
    assert token  # auto-generated and saved on first load

    second = Config(config_file=str(conf_file))
    assert second.api_token == token  # not regenerated on every load
