use arcadematrix::core::config::Config;
use arcadematrix::core::dmd_cache::DmdCache;
use arcadematrix::core::matrix::{MatrixBackend, MockMatrix};
use arcadematrix::engines::clock::ClockEngine;
use arcadematrix::engines::date::DateEngine;
use arcadematrix::engines::fighter::{FighterEngine, FighterSprite};
use arcadematrix::engines::gif::GifEngine;
use arcadematrix::engines::marquee::MarqueeEngine;
use arcadematrix::engines::message::{MessageEngine, MessagePayload};
use image::RgbImage;
use tempfile::NamedTempFile;

#[test]
fn test_clock_engine_render_themes() {
    let temp_file = NamedTempFile::new().unwrap();
    let config = Config::new(temp_file.path());
    let mut matrix = MockMatrix::new(64, 32);
    let mut clock_engine = ClockEngine::new(64, 32);

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
fn test_message_engine() {
    let mut matrix = MockMatrix::new(64, 32);
    let mut engine = MessageEngine::new();
    let payload = MessagePayload {
        text: "Scrolling Message".to_string(),
        color: "#ff0000".to_string(),
        size: 1,
        direction: "left".to_string(),
        speed: 2,
        timeout_seconds: 5,
    };

    engine.render(&mut matrix, &payload);
}

#[test]
fn test_marquee_engine() {
    let mut matrix = MockMatrix::new(64, 32);
    let engine = MarqueeEngine::new();
    let img = RgbImage::new(64, 32);

    engine.render(&mut matrix, &img);
}

#[test]
fn test_gif_engine_init() {
    let mut gif_engine = GifEngine::new();
    let mut matrix = MockMatrix::new(64, 32);

    gif_engine.render_next_frame(&mut matrix);
    assert!(!gif_engine.load_gif("non_existent.gif"));
}

#[test]
fn test_fighter_engine_initialization() {
    let mut engine = FighterEngine::new(64);
    let mut matrix = MockMatrix::new(64, 32);
    let p1 = FighterSprite {
        width: 16,
        height: 16,
        frames: vec![],
    };
    let p2 = FighterSprite {
        width: 16,
        height: 16,
        frames: vec![],
    };

    engine.render(&mut matrix, &p1, &p2);
    assert_eq!(engine.p1_x, 4);
}

#[test]
fn test_dmd_cache_lookup() {
    let temp_dir = tempfile::tempdir().unwrap();
    let cache = DmdCache::new(temp_dir.path());
    assert!(cache
        .get_marquee_path("invalid_sys", "invalid_game")
        .is_none());
}
