use arcadematrix::core::config::Config;
use arcadematrix::core::matrix::{MatrixBackend, MockMatrix};
use arcadematrix::engines::clock::ClockEngine;
use arcadematrix::engines::date::DateEngine;
use arcadematrix::engines::fighter::FighterEngine;
use arcadematrix::engines::message::{MessageEngine, MessagePayload};
use tempfile::NamedTempFile;

#[test]
fn test_clock_engine_render_themes() {
    let temp_file = NamedTempFile::new().unwrap();
    let config = Config::new(temp_file.path());
    let mut matrix = MockMatrix::new(64, 32);
    let mut clock_engine = ClockEngine::new(64, 32);

    // Test rendering all 30 themes without panics
    for theme_id in 0..30 {
        config.settings.write().time_theme = theme_id;
        matrix.clear();
        clock_engine.render(&mut matrix, &config);
    }
}

#[test]
fn test_date_engine_render() {
    let temp_file = NamedTempFile::new().unwrap();
    let config = Config::new(temp_file.path());
    let mut matrix = MockMatrix::new(64, 32);
    let mut date_engine = DateEngine::new();

    matrix.clear();
    date_engine.render(&mut matrix, &config);
}

#[test]
fn test_message_payload_json() {
    let json_data = serde_json::json!({
        "text": "Hello World",
        "color": "#00ff00",
        "size": 2,
        "direction": "left",
        "speed": 5,
        "timeout_seconds": 10
    });

    let payload: MessagePayload = serde_json::from_value(json_data).unwrap();
    assert_eq!(payload.text, "Hello World");
    assert_eq!(payload.color, "#00ff00");
    assert_eq!(payload.size, 2);
}

#[test]
fn test_fighter_engine_initialization() {
    let engine = FighterEngine::new(64);
    assert_eq!(engine.p1_x, 4);
    assert_eq!(engine.p2_x, 44);
}
