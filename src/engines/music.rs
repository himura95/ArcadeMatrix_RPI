use crate::core::config::Config;
use crate::core::matrix::MatrixBackend;
use crate::engines::renderers::BaseRenderer;
use reqwest::blocking::Client;
use serde::{Deserialize, Serialize};
use std::time::{Duration, Instant};

fn parse_hex_color(hex: &str) -> Option<(u8, u8, u8)> {
    let s = hex.trim_start_matches('#');
    if s.len() == 6 {
        let r = u8::from_str_radix(&s[0..2], 16).ok()?;
        let g = u8::from_str_radix(&s[2..4], 16).ok()?;
        let b = u8::from_str_radix(&s[4..6], 16).ok()?;
        Some((r, g, b))
    } else {
        None
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct NowPlaying {
    artist: String,
    title: String,
    elapsed: u64,
    duration: u64,
    playing: bool,
}

pub struct MusicEngine {
    base_renderer: BaseRenderer,
    last_font: String,
    music_server_url: String,
    last_music_info: Option<NowPlaying>,
    last_fetch: Instant,
    // Scroll state for artist line
    artist_scroll_offset: f32,
    artist_scroll_text: String,
    artist_scroll_width: i32,
    // Scroll state for title line
    title_scroll_offset: f32,
    title_scroll_text: String,
    title_scroll_width: i32,
}

impl MusicEngine {
    pub fn new() -> Self {
        Self {
            base_renderer: BaseRenderer::new(),
            last_font: String::new(),
            music_server_url: String::new(),
            last_music_info: None,
            last_fetch: Instant::now(),
            artist_scroll_offset: 0.0,
            artist_scroll_text: String::new(),
            artist_scroll_width: 0,
            title_scroll_offset: 0.0,
            title_scroll_text: String::new(),
            title_scroll_width: 0,
        }
    }

    fn fetch_now_playing(&mut self, client: &Client, url: &str) -> Option<NowPlaying> {
        // Only fetch every 2 seconds to avoid excessive polling
        if self.last_fetch.elapsed() < Duration::from_secs(2) {
            tracing::debug!("MusicEngine: cache hit, last_music_info={:?}", self.last_music_info.is_some());
            return self.last_music_info.clone();
        }
        let endpoint = if url.ends_with("/nowplaying") {
            url.to_string()
        } else {
            format!("{}/nowplaying", url)
        };
        tracing::info!("MusicEngine: fetching from {}", endpoint);
        self.last_fetch = Instant::now();

        match client.get(&endpoint).timeout(Duration::from_secs(5)).send() {
            Ok(response) => {
                if response.status().is_success() {
                    if let Ok(json) = response.json::<serde_json::Value>() {
                        tracing::info!("MusicEngine: received JSON: {}", json);
                        // Check if we have a "playing" field or just the data
                        if let Some(playing) = json.get("playing") {
                            if !playing.as_bool().unwrap_or(false) {
                                tracing::info!("MusicEngine: playing=false, returning empty");
                                return Some(NowPlaying {
                                    artist: String::new(),
                                    title: String::new(),
                                    elapsed: 0,
                                    duration: 0,
                                    playing: false,
                                });
                            }
                        }

                        // If we have a "artist" field, it's the full structure
                        if let (Some(artist), Some(title)) = (
                            json.get("artist").and_then(|v| v.as_str()),
                            json.get("title").and_then(|v| v.as_str()),
                        ) {
                            let elapsed = json.get("elapsed").and_then(|v| v.as_u64()).unwrap_or(0);
                            let duration = json.get("duration").and_then(|v| v.as_u64()).unwrap_or(0);
                            
                            tracing::info!("MusicEngine: got track {} - {}", artist, title);
                            return Some(NowPlaying {
                                artist: artist.to_string(),
                                title: title.to_string(),
                                elapsed,
                                duration,
                                playing: true,
                            });
                        }
                    }
                } else {
                    tracing::warn!("MusicEngine: HTTP status {}", response.status());
                }
            }
            Err(e) => {
                tracing::warn!("MusicEngine: fetch error: {}", e);
                return self.last_music_info.clone();
            }
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

    fn draw_scrolling_text(
        &self,
        matrix: &mut dyn MatrixBackend,
        text: &str,
        start_x: i32,
        start_y: i32,
        color: (u8, u8, u8),
        scale: f32,
        width: i32,
        scroll_offset: &mut f32,
        scroll_text: &mut String,
        scroll_width: &mut i32,
    ) {
        let font = self.base_renderer.font();
        let text_width = self.text_width(text, scale);

        // Reset scroll state if text changed
        if *scroll_text != text {
            *scroll_text = text.to_string();
            *scroll_width = text_width;
            *scroll_offset = width as f32;
        }

        if text_width <= width {
            // Text fits, center it
            let centered_x = start_x + (width - text_width) / 2;
            self.draw_text_at(matrix, text, centered_x, start_y, color, scale);
            return;
        }

        // Scroll: move left by 1 pixel per frame
        *scroll_offset -= 1.0;
        if *scroll_offset < -(text_width as f32) {
            *scroll_offset = width as f32;
        }

        let (pixels_by_char, _, _) = font.get_pixel_map(text, scale);
        for char_pixels in pixels_by_char {
            for (gx, gy) in char_pixels {
                let px = start_x + *scroll_offset as i32 + gx;
                let py = start_y + gy;
                if px >= start_x && px < (start_x + width) && py >= 0 && py < matrix.height() as i32 {
                    matrix.set_pixel(px, py, color.0, color.1, color.2);
                }
            }
        }
    }

    pub fn render(&mut self, matrix: &mut dyn MatrixBackend, config: &Config) {
        let (enabled, url, duration_sec, font_name, artist_color, title_color, time_color, bar_bg_color, bar_fg_color) = {
            let s = config.settings.read();
            (
                s.music_enabled,
                s.music_server_url.clone(),
                s.music_duration_sec,
                s.music_font.clone(),
                s.music_artist_color.clone(),
                s.music_title_color.clone(),
                s.music_time_color.clone(),
                s.music_bar_bg_color.clone(),
                s.music_bar_fg_color.clone(),
            )
        };

        if url.is_empty() || !enabled {
            return;
        }

        // Reload font from disk if the config font changes
        if font_name != self.last_font {
            self.base_renderer = BaseRenderer::from_font_path(&font_name);
            self.last_font = font_name;
        }

        let client = Client::new();
        let now_playing = self.fetch_now_playing(&client, &url);

        // Update last known info only if valid (non-empty title)
        if let Some(ref info) = now_playing {
            if info.title.is_empty() {
                self.last_music_info = None;
            } else {
                self.last_music_info = Some(info.clone());
            }
        }

        matrix.clear();

        let width = matrix.width() as i32;
        let height = matrix.height() as i32;

        if !now_playing.as_ref().is_some_and(|p| p.playing) {
            self.draw_text_at(
                matrix,
                "En attente de musique...",
                0,
                (height / 2) as i32,
                (255, 255, 255),
                1.0,
            );
            return;
        }

        let info = now_playing.unwrap();

        if info.artist.is_empty() && info.title.is_empty() {
            self.draw_text_at(
                matrix,
                "En attente de musique...",
                0,
                (height / 2) as i32,
                (255, 255, 255),
                1.0,
            );
            return;
        }

        // Layout: 3 lines
        // Line 1: Artist (scrolling full width, centered if fits)
        // Line 2: Title (scrolling full width, centered if fits)
        // Line 3: Time text above full-width progress bar
        let line_height = height / 3;

        // Parse colors
        let acolor = parse_hex_color(&artist_color).unwrap_or((255, 255, 255));
        let tcolor = parse_hex_color(&title_color).unwrap_or((200, 200, 200));
        let mcolor = parse_hex_color(&time_color).unwrap_or((255, 255, 255));
        let bbg = parse_hex_color(&bar_bg_color).unwrap_or((60, 60, 60));
        let bfg = parse_hex_color(&bar_fg_color).unwrap_or((255, 215, 0));

        // Compute scales
        let text_scale = Self::compute_adaptive_scale_by_height(line_height - 2, 3.0, 0.75, &self.base_renderer);
        let text_th = self.text_height(text_scale);

        // Line 1: Artist (full width)
        let artist_y = (line_height / 2) as i32 - text_th / 2;
        let artist_text = info.artist.clone();
        let mut a_off = self.artist_scroll_offset;
        let mut a_txt = self.artist_scroll_text.clone();
        let mut a_wid = self.artist_scroll_width;
        self.draw_scrolling_text(
            matrix,
            &artist_text,
            0,
            artist_y,
            acolor,
            text_scale,
            width,
            &mut a_off,
            &mut a_txt,
            &mut a_wid,
        );
        self.artist_scroll_offset = a_off;
        self.artist_scroll_text = a_txt;
        self.artist_scroll_width = a_wid;

        // Line 2: Title (full width)
        let title_y = line_height + (line_height / 2) as i32 - text_th / 2;
        let title_text = info.title.clone();
        let mut t_off = self.title_scroll_offset;
        let mut t_txt = self.title_scroll_text.clone();
        let mut t_wid = self.title_scroll_width;
        self.draw_scrolling_text(
            matrix,
            &title_text,
            0,
            title_y,
            tcolor,
            text_scale,
            width,
            &mut t_off,
            &mut t_txt,
            &mut t_wid,
        );
        self.title_scroll_offset = t_off;
        self.title_scroll_text = t_txt;
        self.title_scroll_width = t_wid;

        // Line 3: Time text + progress bar (full width)
        let bar_section_y = line_height * 2;
        let bar_height = 8;
        let bar_y = bar_section_y + (line_height / 2) as i32 - bar_height / 2 - text_th / 2 - 2;

        // Format time text as "elapsed / duration"
        let time_text = format!("{} / {}", Self::format_time(info.elapsed), Self::format_time(info.duration));
        let time_width = self.text_width(&time_text, text_scale);
        let time_x = (width - time_width) / 2;
        self.draw_text_at(matrix, &time_text, time_x, bar_section_y, mcolor, text_scale);

        // Progress bar (full width)
        let bar_y = bar_section_y + text_th + 2;
        let progress_percent = if info.duration > 0 {
            (info.elapsed as f64 / info.duration as f64).min(1.0)
        } else {
            0.0
        };
        let filled_width = (width as f64 * progress_percent) as i32;

        // Bar background
        for x in 0..width {
            for y in bar_y..(bar_y + bar_height) {
                matrix.set_pixel(x, y, bbg.0, bbg.1, bbg.2);
            }
        }

        // Bar filled portion
        for x in 0..filled_width {
            for y in bar_y..(bar_y + bar_height) {
                matrix.set_pixel(x, y, bfg.0, bfg.1, bfg.2);
            }
        }
    }

    fn format_time(seconds: u64) -> String {
        let min = seconds / 60;
        let sec = seconds % 60;
        format!("{:02}:{:02}", min, sec)
    }
}