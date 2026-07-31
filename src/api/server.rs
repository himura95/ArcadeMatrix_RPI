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
    if let Some(v) = body.get("brightness_limit").and_then(|v| v.as_u64()) {
        s.matrix_brightness = v as u32;
        data.config
            .matrix_brightness
            .store(v as u32, std::sync::atomic::Ordering::Relaxed);
    }
    if let Some(v) = body.get("clock_theme").and_then(|v| v.as_i64()) {
        s.time_theme = v as i32;
    }
    drop(s);
    data.config.save();
    data.config
        .reload_flag
        .store(true, std::sync::atomic::Ordering::Relaxed);
    HttpResponse::Ok().json(json!({"status": "success"}))
}

#[get("/api/system_info")]
async fn api_system_info() -> impl Responder {
    let mut sys = System::new_all();
    sys.refresh_all();

    let cpu_load = sys.global_cpu_usage();
    let ram_used = sys.used_memory() / (1024 * 1024);
    let ram_total = sys.total_memory() / (1024 * 1024);

    let temp = match sysinfo::Components::new_with_refreshed_list()
        .iter()
        .next()
        .map(|c| c.temperature())
    {
        Some(t) => t,
        None => 42.0,
    };

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
