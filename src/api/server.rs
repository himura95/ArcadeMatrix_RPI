use crate::api::ota::{get_version, handle_update};
use crate::core::config::Config;
use actix_files::Files;
use actix_web::{get, post, web, App, HttpResponse, HttpServer, Responder};
use serde_json::json;
use std::sync::Arc;
use sysinfo::System;

struct AppState {
    config: Arc<Config>,
}

#[get("/api/fonts")]
async fn api_fonts() -> impl Responder {
    let mut fonts = Vec::new();
    if let Ok(entries) = std::fs::read_dir("fonts") {
        for entry in entries.flatten() {
            if let Ok(name) = entry.file_name().into_string() {
                if name.ends_with(".ttf") || name.ends_with(".otf") || name.ends_with(".bdf") {
                    fonts.push(name);
                }
            }
        }
    }
    HttpResponse::Ok().json(fonts)
}

#[get("/api/settings")]
async fn get_settings(data: web::Data<AppState>) -> impl Responder {
    let s = data.config.settings.read();
    HttpResponse::Ok().json(json!({
        "brightness_limit": s.matrix_brightness,
        "color_depth": 24,
        "rotation": s.idle_rotation.join(","),
        "clock_offset_x": s.time_offset_x,
        "clock_offset_y": s.time_offset_y,
        "date_offset_x": s.date_offset_x,
        "date_offset_y": s.date_offset_y,
        "weather_offset_x": s.weather_offset_x,
        "weather_offset_y": s.weather_offset_y,
        "clock_size": s.time_size,
        "clock_font": s.time_font,
        "clock_theme": s.time_theme,
        "clock_color_1": s.clock_color_1,
        "clock_color_2": s.clock_color_2,
        "format_24h": s.time_24h,
        "date_size": s.date_size,
        "date_font": s.date_font,
        "date_theme": s.date_theme,
        "date_format": s.date_format,
        "date_color_1": s.date_color_1,
        "date_color_2": s.date_color_2,
        "night_mode_enabled": s.standby_enabled,
        "turn_off_at": s.standby_turn_off,
        "wake_up_at": s.standby_wake_up,
        "matrix_brightness_night": s.standby_night_brightness,
        "matrix_power": data.config.matrix_power.load(std::sync::atomic::Ordering::Relaxed),
        "matrix_brightness": s.matrix_brightness,
        "matrix_slowdown": s.matrix_slowdown,
        "matrix_rows": s.matrix_rows,
        "matrix_cols": s.matrix_cols,
        "matrix_chain": s.matrix_chain,
        "matrix_parallel": s.matrix_parallel,
        "matrix_mapping": s.matrix_mapping,
        "matrix_rgb_sequence": s.matrix_rgb_sequence,
        "matrix_pwm_bits": s.matrix_pwm_bits,
        "matrix_pwm_lsb_nanoseconds": s.matrix_pwm_lsb_nanoseconds,
        "mqtt_enabled": s.mqtt_enabled,
        "mqtt_broker": s.mqtt_broker,
        "mqtt_port": s.mqtt_port,
        "mqtt_user": s.mqtt_user,
        "clock_duration_sec": s.idle_clock_duration_sec,
        "date_duration_sec": s.idle_date_duration_sec,
        "weather_duration_sec": s.idle_weather_duration_sec,
        "gifs_count": s.idle_gifs_count,
        "sprite_count": s.idle_sprite_count,
        "fighter_interval_sec": s.idle_fighter_interval,
        "weather_api_key": s.weather_api_key,
        "weather_city": s.weather_city,
        "weather_lang": s.weather_lang,
    }))
}

#[post("/api/settings")]
async fn post_settings(
    data: web::Data<AppState>,
    body: web::Json<serde_json::Value>,
) -> impl Responder {
    let mut s = data.config.settings.write();

    // Matrix settings
    if let Some(v) = body.get("brightness_limit").and_then(|v| v.as_u64()) {
        s.matrix_brightness = v as u32;
        data.config
            .matrix_brightness
            .store(v as u32, std::sync::atomic::Ordering::Relaxed);
    }
    if let Some(v) = body.get("matrix_slowdown").and_then(|v| v.as_u64()) {
        s.matrix_slowdown = v as u32;
    }

    // Clock settings
    if let Some(v) = body.get("clock_theme").and_then(|v| v.as_i64()) {
        s.time_theme = v as i32;
    }
    if let Some(v) = body.get("clock_font").and_then(|v| v.as_str()) {
        s.time_font = v.to_string();
    }
    if let Some(v) = body.get("clock_size").and_then(|v| v.as_u64()) {
        s.time_size = v as u32;
    }
    if let Some(v) = body.get("clock_color_1").and_then(|v| v.as_str()) {
        s.clock_color_1 = v.to_string();
    }
    if let Some(v) = body.get("clock_color_2").and_then(|v| v.as_str()) {
        s.clock_color_2 = v.to_string();
    }
    if let Some(v) = body.get("clock_offset_x").and_then(|v| v.as_i64()) {
        s.time_offset_x = v as i32;
    }
    if let Some(v) = body.get("clock_offset_y").and_then(|v| v.as_i64()) {
        s.time_offset_y = v as i32;
    }
    if let Some(v) = body.get("format_24h").and_then(|v| v.as_bool()) {
        s.time_24h = v;
    }

    // Date settings
    if let Some(v) = body.get("date_theme").and_then(|v| v.as_i64()) {
        s.date_theme = v as i32;
    }
    if let Some(v) = body.get("date_font").and_then(|v| v.as_str()) {
        s.date_font = v.to_string();
    }
    if let Some(v) = body.get("date_size").and_then(|v| v.as_u64()) {
        s.date_size = v as u32;
    }
    if let Some(v) = body.get("date_format").and_then(|v| v.as_str()) {
        s.date_format = v.to_string();
    }
    if let Some(v) = body.get("date_color_1").and_then(|v| v.as_str()) {
        s.date_color_1 = v.to_string();
    }
    if let Some(v) = body.get("date_color_2").and_then(|v| v.as_str()) {
        s.date_color_2 = v.to_string();
    }
    if let Some(v) = body.get("date_offset_x").and_then(|v| v.as_i64()) {
        s.date_offset_x = v as i32;
    }
    if let Some(v) = body.get("date_offset_y").and_then(|v| v.as_i64()) {
        s.date_offset_y = v as i32;
    }

    // Weather settings
    if let Some(v) = body.get("weather_api_key").and_then(|v| v.as_str()) {
        s.weather_api_key = v.to_string();
    }
    if let Some(v) = body.get("weather_city").and_then(|v| v.as_str()) {
        s.weather_city = v.to_string();
    }
    if let Some(v) = body.get("weather_lang").and_then(|v| v.as_str()) {
        s.weather_lang = v.to_string();
    }
    if let Some(v) = body.get("weather_offset_x").and_then(|v| v.as_i64()) {
        s.weather_offset_x = v as i32;
    }
    if let Some(v) = body.get("weather_offset_y").and_then(|v| v.as_i64()) {
        s.weather_offset_y = v as i32;
    }

    // Rotation & Idle settings
    if let Some(v) = body.get("rotation").and_then(|v| v.as_str()) {
        s.idle_rotation = v
            .split(',')
            .map(|item| item.trim().to_string())
            .filter(|item| !item.is_empty())
            .collect();
    }
    if let Some(v) = body.get("clock_duration_sec").and_then(|v| v.as_u64()) {
        s.idle_clock_duration_sec = v as u32;
    }
    if let Some(v) = body.get("date_duration_sec").and_then(|v| v.as_u64()) {
        s.idle_date_duration_sec = v as u32;
    }
    if let Some(v) = body.get("weather_duration_sec").and_then(|v| v.as_u64()) {
        s.idle_weather_duration_sec = v as u32;
    }
    if let Some(v) = body.get("gifs_count").and_then(|v| v.as_u64()) {
        s.idle_gifs_count = v as u32;
    }
    if let Some(v) = body.get("sprite_count").and_then(|v| v.as_u64()) {
        s.idle_sprite_count = v as u32;
    }

    // Standby / Night mode
    if let Some(v) = body.get("night_mode_enabled").and_then(|v| v.as_bool()) {
        s.standby_enabled = v;
    }
    if let Some(v) = body.get("turn_off_at").and_then(|v| v.as_str()) {
        s.standby_turn_off = v.to_string();
    }
    if let Some(v) = body.get("wake_up_at").and_then(|v| v.as_str()) {
        s.standby_wake_up = v.to_string();
    }
    if let Some(v) = body.get("matrix_brightness_night").and_then(|v| v.as_u64()) {
        s.standby_night_brightness = v as u32;
    }

    // MQTT settings
    if let Some(v) = body.get("mqtt_enable").and_then(|v| v.as_bool()) {
        s.mqtt_enabled = v;
    }
    if let Some(v) = body.get("mqtt_broker").and_then(|v| v.as_str()) {
        s.mqtt_broker = v.to_string();
    }
    if let Some(v) = body.get("mqtt_port").and_then(|v| v.as_u64()) {
        s.mqtt_port = v as u16;
    }
    if let Some(v) = body.get("mqtt_user").and_then(|v| v.as_str()) {
        s.mqtt_user = v.to_string();
    }
    if let Some(v) = body.get("mqtt_pass").and_then(|v| v.as_str()) {
        s.mqtt_pass = v.to_string();
    }

    drop(s);
    data.config.save();
    data.config
        .reload_flag
        .store(true, std::sync::atomic::Ordering::Relaxed);

    HttpResponse::Ok().json(json!({"status": "success"}))
}

#[post("/api/clock")]
async fn post_clock(
    data: web::Data<AppState>,
    body: web::Json<serde_json::Value>,
) -> impl Responder {
    if let Some(theme) = body.get("clock_theme").and_then(|v| v.as_i64()) {
        let mut s = data.config.settings.write();
        s.time_theme = theme as i32;
        drop(s);
        data.config.save();
        data.config
            .reload_flag
            .store(true, std::sync::atomic::Ordering::Relaxed);
    }
    HttpResponse::Ok().json(json!({"status": "success"}))
}

#[post("/api/message")]
async fn post_message(
    data: web::Data<AppState>,
    body: web::Json<serde_json::Value>,
) -> impl Responder {
    *data.config.message_payload.lock() = Some(body.into_inner());
    *data.config.force_engine.lock() = Some("message".to_string());
    HttpResponse::Ok().json(json!({"status": "success"}))
}

#[get("/api/playlists")]
async fn get_playlists() -> impl Responder {
    let mut playlists = serde_json::Map::new();
    let gifs_dir = std::path::Path::new("gifs");
    if let Ok(entries) = std::fs::read_dir(gifs_dir) {
        for entry in entries.flatten() {
            if entry.path().is_dir() {
                let path_str = entry.path().to_string_lossy().to_string();
                let mut count = 0;
                if let Ok(files) = std::fs::read_dir(entry.path()) {
                    count = files
                        .flatten()
                        .filter(|f| {
                            let name = f.file_name().to_string_lossy().to_string().to_lowercase();
                            name.ends_with(".gif") && !name.starts_with("._")
                        })
                        .count();
                }
                playlists.insert(
                    path_str.clone(),
                    json!({
                        "path": path_str,
                        "count": count
                    }),
                );
            }
        }
    }
    HttpResponse::Ok().json(playlists)
}

#[get("/api/playlists/selected")]
async fn get_selected_playlists(data: web::Data<AppState>) -> impl Responder {
    let s = data.config.settings.read();
    HttpResponse::Ok().json(json!({
        "playlists": s.selected_gifs
    }))
}

#[post("/api/playlists/save")]
async fn save_selected_playlists(
    data: web::Data<AppState>,
    body: web::Json<serde_json::Value>,
) -> impl Responder {
    if let Some(arr) = body.get("playlists").and_then(|v| v.as_array()) {
        let selected: Vec<String> = arr
            .iter()
            .filter_map(|v| v.as_str().map(|s| s.to_string()))
            .collect();
        let mut s = data.config.settings.write();
        s.selected_gifs = selected;
        drop(s);
        data.config.save();
    }
    HttpResponse::Ok().json(json!({"status": "success"}))
}

#[post("/api/playlists/play")]
async fn play_selected_playlists(
    data: web::Data<AppState>,
    body: web::Json<serde_json::Value>,
) -> impl Responder {
    if let Some(arr) = body.get("playlists").and_then(|v| v.as_array()) {
        let selected: Vec<String> = arr
            .iter()
            .filter_map(|v| v.as_str().map(|s| s.to_string()))
            .collect();
        let mut s = data.config.settings.write();
        s.selected_gifs = selected;
        drop(s);
        data.config.save();
        *data.config.force_engine.lock() = Some("gifs".to_string());
    }
    HttpResponse::Ok().json(json!({"status": "success"}))
}

#[get("/api/system_info")]
async fn api_system_info() -> impl Responder {
    let mut sys = System::new_all();
    sys.refresh_all();

    let cpu_load = sys.global_cpu_usage();
    let ram_used = sys.used_memory() / (1024 * 1024);
    let ram_total = sys.total_memory() / (1024 * 1024);

    let temp = sysinfo::Components::new_with_refreshed_list()
        .iter()
        .next()
        .map(|c| c.temperature())
        .unwrap_or(42.0);

    HttpResponse::Ok().json(json!({
        "cpu_load": cpu_load,
        "ram_used_mb": ram_used,
        "ram_total_mb": ram_total,
        "ram_percent": (ram_used as f32 / ram_total as f32 * 100.0) as u32,
        "disk_free_gb": 10.5,
        "disk_total_gb": 16.0,
        "disk_percent": 35,
        "temperature_c": temp,
    }))
}

#[post("/api/system/reboot")]
async fn api_reboot() -> impl Responder {
    tokio::spawn(async {
        tokio::time::sleep(std::time::Duration::from_secs(1)).await;
        let _ = tokio::process::Command::new("sudo")
            .arg("reboot")
            .status()
            .await;
    });
    HttpResponse::Ok().json(json!({"status": "success", "message": "Rebooting..."}))
}

#[post("/api/system/shutdown")]
async fn api_shutdown() -> impl Responder {
    tokio::spawn(async {
        tokio::time::sleep(std::time::Duration::from_secs(1)).await;
        let _ = tokio::process::Command::new("sudo")
            .args(["shutdown", "now"])
            .status()
            .await;
    });
    HttpResponse::Ok().json(json!({"status": "success", "message": "Shutting down..."}))
}

#[post("/api/system/power")]
async fn api_power(
    data: web::Data<AppState>,
    body: web::Json<serde_json::Value>,
) -> impl Responder {
    if let Some(state) = body.get("state").and_then(|v| v.as_bool()) {
        data.config
            .matrix_power
            .store(state, std::sync::atomic::Ordering::Relaxed);
        data.config
            .reload_flag
            .store(true, std::sync::atomic::Ordering::Relaxed);
    }
    let p = data
        .config
        .matrix_power
        .load(std::sync::atomic::Ordering::Relaxed);
    HttpResponse::Ok().json(json!({"status": "success", "matrix_power": p}))
}

pub async fn run_server(config: Arc<Config>, port: u16) -> std::io::Result<()> {
    let state = web::Data::new(AppState { config });

    HttpServer::new(move || {
        App::new()
            .app_data(state.clone())
            .service(api_fonts)
            .service(get_settings)
            .service(post_settings)
            .service(post_clock)
            .service(post_message)
            .service(get_playlists)
            .service(get_selected_playlists)
            .service(save_selected_playlists)
            .service(play_selected_playlists)
            .service(api_system_info)
            .service(api_reboot)
            .service(api_shutdown)
            .service(api_power)
            .service(get_version)
            .service(handle_update)
            .service(Files::new("/", "api/www").index_file("index.html"))
    })
    .bind(("0.0.0.0", port))?
    .run()
    .await
}
