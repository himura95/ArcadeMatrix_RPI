use std::fs;
use tempfile::NamedTempFile;

#[test]
fn test_default_config() {
    let settings = arcadematrix::core::config::ConfigSettings::default();
    assert_eq!(settings.matrix_rows, 32);
    assert_eq!(settings.matrix_cols, 64);
    assert_eq!(settings.time_24h, true);
    assert_eq!(settings.time_font, "PressStart2P.ttf");
}
