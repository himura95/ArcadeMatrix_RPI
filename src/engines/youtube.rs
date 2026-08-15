use crate::api::youtube::YouTubeProvider;
use crate::core::config::Config;
use crate::core::matrix::MatrixBackend;
use crate::engines::renderers::BaseRenderer;
use std::collections::HashMap;
use std::time::{Duration, Instant};

#[derive(Clone, Debug)]
pub struct CachedChannel {
    channel: String,
    title: String,
    subscribers: u64,
    videos: u64,
    views: u64,
    last_fetch: Instant,
    has_data: bool,
}

pub struct YouTubeEngine {
    base_renderer: BaseRenderer,
    cache: HashMap<String, CachedChannel>,
    current_index: usize,
    last_switch: Instant,
    scroll_offset: f32,
    scroll_text: String,
    scroll_text_width: i32,
    last_font: String,
}

impl YouTubeEngine {
    pub fn new() -> Self {
        Self {
            base_renderer: BaseRenderer::new(),
            cache: HashMap::new(),
            current_index: 0,
            last_switch: Instant::now(),
            scroll_offset: 0.0,
            scroll_text: String::new(),
            scroll_text_width: 0,
            last_font: String::new(),
        }
    }

    fn fetch_channel(&mut self, api_key: &str, channel: &str, ttl_min: u64) -> (String, u64, u64, u64, bool) {
        let now = Instant::now();
        let ttl_secs = (if ttl_min > 0 { ttl_min } else { 1 }) * 60;

        if let Some(c) = self.cache.get(channel) {
            if c.has_data && now.duration_since(c.last_fetch).as_secs() < ttl_secs {
                return (c.title.clone(), c.subscribers, c.videos, c.views, true);
            }
        }

        match YouTubeProvider::fetch_channel_stats(api_key, channel) {
            Some((title, subs, vids, views)) => {
                self.cache.insert(
                    channel.to_string(),
                    CachedChannel {
                        channel: channel.to_string(),
                        title: title.clone(),
                        subscribers: subs,
                        videos: vids,
                        views,
                        last_fetch: now,
                        has_data: true,
                    },
                );
                (title, subs, vids, views, true)
            }
            None => {
                if let Some(c) = self.cache.get(channel) {
                    if c.has_data {
                        return (c.title.clone(), c.subscribers, c.videos, c.views, true);
                    }
                }
                (String::new(), 0, 0, 0, false)
            }
        }
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

    fn format_number_fr(count: u64) -> String {
        if count >= 1_000_000 {
            format!("{} M", count / 1_000_000)
        } else if count >= 1_000 {
            format!("{} K", count / 1_000)
        } else {
            format!("{}", count)
        }
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

    fn draw_youtube_logo(matrix: &mut dyn MatrixBackend, icon_x: i32, icon_y: i32, icon_size: i32) {
        for y in 0..8 {
            for x in 0..8 {
                let is_outer = x == 0 || x == 7 || y == 0 || y == 7;
                let is_triangle =
                    y == 2 && x >= 2 && x <= 4
                        || y == 3 && x >= 2 && x <= 5
                        || y == 4 && x >= 2 && x <= 5
                        || y == 5 && x >= 2 && x <= 4;
                if is_outer || is_triangle {
                    matrix.set_pixel(
                        icon_x + x as i32 * icon_size,
                        icon_y + y as i32 * icon_size,
                        255, 0, 0,
                    );
                    if icon_size > 1 {
                        for dy in 1..icon_size {
                            for dx in 1..icon_size {
                                matrix.set_pixel(
                                    icon_x + x as i32 * icon_size + dx,
                                    icon_y + y as i32 * icon_size + dy,
                                    255, 0, 0,
                                );
                            }
                        }
                    }
                }
            }
        }
    }

    pub fn render(&mut self, matrix: &mut dyn MatrixBackend, config: &Config) {
        let (channels, ttl_min, api_key, duration_sec, font_name) = {
            let s = config.settings.read();
            (s.youtube_channels.clone(), s.youtube_cache_ttl_min, s.youtube_api_key.clone(), s.youtube_duration_sec, s.youtube_font.clone())
        };

        if channels.is_empty() || api_key.is_empty() {
            return;
        }

        // Reload font from disk if the config font changes
        if font_name != self.last_font {
            self.base_renderer = BaseRenderer::from_font_path(&font_name);
            self.last_font = font_name;
            self.scroll_offset = 0.0;
            self.scroll_text = String::new();
            self.scroll_text_width = 0;
        }

        let dur = if duration_sec > 0 { duration_sec } else { 5 };
        let channel = &channels[self.current_index % channels.len()];
        let (title, subs, vids, views, success) = self.fetch_channel(&api_key, channel, ttl_min as u64);

        let width = matrix.width() as i32;
        let height = matrix.height() as i32;

        let top_h = (height / 2).max(16);
        let bot_h = height - top_h;

        let icon_size = if height >= 64 { 3 } else { 2 };
        let icon_w = 8 * icon_size;
        let icon_x = 6;
        let icon_y = (top_h as i32 - icon_w as i32) / 2;

        Self::draw_youtube_logo(matrix, icon_x, icon_y, icon_size as i32);

        let name_max_w = width - icon_x - icon_w - 10;
        let max_scale_top = if height >= 64 { 2.0 } else { 1.0 };
        let name_scale = Self::compute_adaptive_scale(&title, name_max_w, max_scale_top, 0.75, &self.base_renderer);
        let name_th = self.text_height(name_scale);
        let name_y = (top_h as i32 - name_th) / 2;
        self.draw_text_at(matrix, &title, icon_x + icon_w + 6, name_y, (255, 255, 255), name_scale);

        // Divider
        for x in 4..(width - 4) {
            matrix.set_pixel(x, top_h as i32, 40, 40, 40);
        }

        // Bottom line: scrolling stats
        let bot_y_base = top_h as i32 + 4;

        if !success {
            self.draw_text_at(matrix, "Chargement...", 6, bot_y_base, (180, 180, 180), 1.0);
            return;
        }

        let sub_str = Self::format_number_fr(subs);
        let vid_str = Self::format_number_fr(vids);
        let view_str = Self::format_number_fr(views);
        let new_scroll_text = format!("{} abonnes  |  {} videos  |  {} vues", sub_str, vid_str, view_str);

        // Update scroll text when channel changes
        if self.scroll_text != new_scroll_text {
            self.scroll_text = new_scroll_text;
            self.scroll_offset = width as f32;
            self.scroll_text_width = 0;
        }

        let avail_height = bot_h as i32 - 8;
        let bot_scale = Self::compute_adaptive_scale_by_height(avail_height, 4.0, 1.0, &self.base_renderer);

        // Compute text width on first frame
        if self.scroll_text_width == 0 {
            self.scroll_text_width = self.text_width(&self.scroll_text, bot_scale);
        }

        // Continuous scroll loop
        self.scroll_offset -= 1.0;
        if self.scroll_offset < -(self.scroll_text_width as f32) {
            self.scroll_offset = width as f32;
        }

        let bot_th = self.text_height(bot_scale);
        let y_pos = bot_y_base + (bot_h as i32 - bot_th as i32) / 2;

        let font = self.base_renderer.font();
        let (pixels_by_char, _, _) = font.get_pixel_map(&self.scroll_text, bot_scale);
        for char_pixels in &pixels_by_char {
            for (gx, gy) in char_pixels {
                let px = self.scroll_offset as i32 + gx;
                let py = y_pos + gy;
                if px >= 0 && px < width && py >= 0 && py < height {
                    matrix.set_pixel(px, py, 255, 215, 0);
                }
            }
        }

        // Switch channel after duration
        if self.last_switch.elapsed() > Duration::from_secs(dur as u64) {
            self.current_index = (self.current_index + 1) % channels.len();
            self.last_switch = Instant::now();
            self.scroll_offset = 0.0;
            self.scroll_text = String::new();
            self.scroll_text_width = 0;
        }
    }
}
