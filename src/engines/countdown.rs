use crate::core::config::Config;
use crate::core::matrix::MatrixBackend;
use crate::engines::renderers::BaseRenderer;
use std::time::{Duration, Instant};

#[derive(Clone, Debug)]
struct CountdownEvent {
    title: String,
    target: String,
    time_format: String,
}

pub struct CountdownEngine {
    base_renderer: BaseRenderer,
    current_index: usize,
    last_switch: Instant,
    last_font: String,
}

impl CountdownEngine {
    pub fn new() -> Self {
        Self {
            base_renderer: BaseRenderer::new(),
            current_index: 0,
            last_switch: Instant::now(),
            last_font: String::new(),
        }
    }

    fn parse_events(raw: &[String]) -> Vec<CountdownEvent> {
        raw.iter()
            .filter_map(|entry| {
                let parts: Vec<&str> = entry.splitn(3, '|').collect();
                if parts.len() >= 2 {
                    let title = parts[0].trim().to_string();
                    let target = parts[1].trim().to_string();
                    let time_format = if parts.len() >= 3 && !parts[2].trim().is_empty() {
                        parts[2].trim().to_string()
                    } else {
                        "auto".to_string()
                    };
                    if !title.is_empty() && !target.is_empty() {
                        return Some(CountdownEvent { title, target, time_format });
                    }
                }
                None
            })
            .collect()
    }

    fn compute_remaining(target_date: &str, time_format: &str) -> String {
        let now = chrono::Local::now();
        let target = match Self::parse_date(target_date) {
            Some(dt) => dt,
            None => return format!("Erreur: {}", target_date),
        };

        if target <= now {
            return "Atteint !".to_string();
        }

        let diff = target.signed_duration_since(now);
        let total_secs = diff.num_seconds();

        match time_format {
            "hms" => {
                let hours = total_secs / 3600;
                let minutes = (total_secs % 3600) / 60;
                let seconds = total_secs % 60;
                format!("{:02}:{:02}:{:02}", hours, minutes, seconds)
            }
            "nights" => {
                let nights = total_secs / 86400;
                format!("{} nuit{}", nights, if nights == 1 { "" } else { "s" })
            }
            _ => {
                let days = total_secs / 86400;
                let hours = (total_secs % 86400) / 3600;
                let minutes = (total_secs % 3600) / 60;
                if days > 0 {
                    format!("{}j {:02}h {:02}min", days, hours, minutes)
                } else if hours > 0 {
                    format!("{:02}h {:02}min", hours, minutes)
                } else {
                    format!("{:02}min", minutes)
                }
            }
        }
    }

    fn parse_date(date_str: &str) -> Option<chrono::DateTime<chrono::Local>> {
        let cleaned = date_str.trim();
        if let Ok(dt) = chrono::NaiveDate::parse_from_str(cleaned, "%Y-%m-%d") {
            return dt.and_hms_opt(0, 0, 0)
                .and_then(|ndt| ndt.and_local_timezone(chrono::Local).earliest());
        }
        if let Ok(dt) = chrono::NaiveDateTime::parse_from_str(cleaned, "%Y-%m-%d %H:%M") {
            return dt.and_local_timezone(chrono::Local).earliest();
        }
        if let Ok(dt) = chrono::NaiveDateTime::parse_from_str(cleaned, "%Y-%m-%d %H:%M:%S") {
            return dt.and_local_timezone(chrono::Local).earliest();
        }
        if let Ok(dt) = chrono::NaiveDateTime::parse_from_str(cleaned, "%d/%m/%Y-%H:%M") {
            return dt.and_local_timezone(chrono::Local).earliest();
        }
        if let Ok(dt) = chrono::NaiveDateTime::parse_from_str(cleaned, "%d/%m/%Y-%H:%M:%S") {
            return dt.and_local_timezone(chrono::Local).earliest();
        }
        None
    }

    fn draw_text_at(
        &self,
        matrix: &mut dyn MatrixBackend,
        text: &str,
        start_x: i32,
        start_y: i32,
        color: (u8, u8, u8),
        scale: f32,
    ) -> i32 {
        let font = self.base_renderer.font();
        let (pixels_by_char, text_width, _) = font.get_pixel_map(text, scale);

        for char_pixels in pixels_by_char {
            for (gx, gy) in char_pixels {
                let px = start_x + gx;
                let py = start_y + gy;
                if px >= 0 && px < matrix.width() as i32 && py >= 0 && py < matrix.height() as i32 {
                    matrix.set_pixel(px, py, color.0, color.1, color.2);
                }
            }
        }
        text_width
    }

    fn text_width(&self, text: &str, scale: f32) -> i32 {
        let font = self.base_renderer.font();
        let (_, tw, _) = font.get_pixel_map(text, scale);
        tw
    }

    fn text_height(&self, scale: f32) -> i32 {
        let font = self.base_renderer.font();
        let (_, _, th) = font.get_pixel_map("X", scale);
        th
    }

    fn compute_adaptive_scale(text: &str, max_width: i32, max_scale: f32, min_scale: f32, base_renderer: &BaseRenderer) -> f32 {
        let font = base_renderer.font();
        let mut scale = max_scale;
        loop {
            let (_, tw, _) = font.get_pixel_map(text, scale);
            if tw <= max_width || scale <= min_scale {
                break;
            }
            scale -= 0.25;
        }
        scale
    }

    fn compute_adaptive_scale_by_height(max_height: i32, max_scale: f32, min_scale: f32, base_renderer: &BaseRenderer) -> f32 {
        let font = base_renderer.font();
        let mut scale = max_scale;
        loop {
            let (_, _, th) = font.get_pixel_map("X", scale);
            if th <= max_height || scale <= min_scale {
                break;
            }
            scale -= 0.25;
        }
        scale
    }

    fn draw_countdown_icon(matrix: &mut dyn MatrixBackend, icon_x: i32, icon_y: i32, icon_size: i32) {
        let icon = [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 1, 0, 0, 1],
            [1, 0, 1, 0, 0, 1, 0, 1],
            [1, 0, 1, 0, 0, 1, 0, 1],
            [1, 0, 0, 1, 1, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
        ];

        for (y, row) in icon.iter().enumerate() {
            for (x, &pixel) in row.iter().enumerate() {
                if pixel == 1 {
                    matrix.set_pixel(
                        icon_x + x as i32 * icon_size,
                        icon_y + y as i32 * icon_size,
                        0, 255, 255,
                    );
                    if icon_size > 1 {
                        for dy in 1..icon_size {
                            for dx in 1..icon_size {
                                matrix.set_pixel(
                                    icon_x + x as i32 * icon_size + dx,
                                    icon_y + y as i32 * icon_size + dy,
                                    0, 255, 255,
                                );
                            }
                        }
                    }
                }
            }
        }
    }

    pub fn render(&mut self, matrix: &mut dyn MatrixBackend, config: &Config) {
        let (events, duration_sec, font_name) = {
            let s = config.settings.read();
            (
                s.countdown_events.clone(),
                s.countdown_duration_sec,
                s.countdown_font.clone(),
            )
        };

        if events.is_empty() {
            return;
        }

        if font_name != self.last_font {
            self.base_renderer = BaseRenderer::from_font_path(&font_name);
            self.last_font = font_name;
        }

        let dur = if duration_sec > 0 { duration_sec } else { 15 };
        let parsed = Self::parse_events(&events);

        if parsed.is_empty() {
            return;
        }

        let event = &parsed[self.current_index % parsed.len()];
        let remaining = Self::compute_remaining(&event.target, &event.time_format);

        let width = matrix.width() as i32;
        let height = matrix.height() as i32;

        let top_h = (height / 2).max(16);
        let bot_h = height - top_h;

        let icon_size = if height >= 64 { 3 } else { 2 };
        let icon_w = 8 * icon_size;
        let icon_x = 6;
        let icon_y = (top_h as i32 - icon_w as i32) / 2;

        Self::draw_countdown_icon(matrix, icon_x, icon_y, icon_size as i32);

        // Title
        let name_max_w = width - icon_x - icon_w - 10;
        let max_scale_top = if height >= 64 { 2.0 } else { 1.0 };
        let name_scale = Self::compute_adaptive_scale(&event.title, name_max_w, max_scale_top, 0.75, &self.base_renderer);
        let name_th = self.text_height(name_scale);
        let name_y = (top_h as i32 - name_th) / 2;
        self.draw_text_at(matrix, &event.title, icon_x + icon_w + 6, name_y, (255, 255, 255), name_scale);

        // Divider
        for x in 4..(width - 4) {
            matrix.set_pixel(x, top_h as i32, 40, 40, 40);
        }

        // Bottom: static remaining time
        let bot_y_base = top_h as i32 + 4;
        let avail_height = bot_h as i32 - 8;
        let rem_scale = Self::compute_adaptive_scale_by_height(avail_height, 4.0, 1.0, &self.base_renderer);
        let rem_center_x = (width - self.text_width(&remaining, rem_scale)) / 2;
        let rem_y = bot_y_base + (avail_height - self.text_height(rem_scale) as i32) / 2;
        self.draw_text_at(matrix, &remaining, rem_center_x, rem_y, (255, 255, 0), rem_scale);

        // Switch event after duration
        if self.last_switch.elapsed() > Duration::from_secs(dur as u64) {
            self.current_index = (self.current_index + 1) % parsed.len();
            self.last_switch = Instant::now();
        }
    }
}
