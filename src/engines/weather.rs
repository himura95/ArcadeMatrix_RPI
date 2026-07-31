use crate::core::config::Config;
use crate::core::matrix::MatrixBackend;
use crate::engines::renderers::BaseRenderer;
use serde::Deserialize;
use std::time::{Duration, Instant};
use tracing::error;

#[derive(Deserialize)]
struct WeatherMain {
    temp: f32,
}

#[derive(Deserialize)]
struct WeatherApiResponse {
    main: WeatherMain,
}

pub struct WeatherEngine {
    base_renderer: BaseRenderer,
    cached_temp: String,
    last_fetch: Option<Instant>,
}

impl WeatherEngine {
    pub fn new() -> Self {
        Self {
            base_renderer: BaseRenderer::new(),
            cached_temp: "--°C".to_string(),
            last_fetch: None,
        }
    }

    pub fn render(&mut self, matrix: &mut dyn MatrixBackend, config: &Config) {
        let (api_key, city) = {
            let s = config.settings.read();
            (s.weather_api_key.clone(), s.weather_city.clone())
        };

        if !api_key.is_empty() && !city.is_empty() {
            let should_fetch = self
                .last_fetch
                .map(|t| t.elapsed() > Duration::from_secs(1800))
                .unwrap_or(true);

            if should_fetch {
                self.fetch_weather(&api_key, &city);
            }
        }

        let s = config.settings.read();
        self.base_renderer.render_text(
            matrix,
            &self.cached_temp,
            0,
            2,
            s.weather_offset_x,
            s.weather_offset_y,
            None,
            None,
        );
    }

    fn fetch_weather(&mut self, api_key: &str, city: &str) {
        let url = format!(
            "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric",
            city, api_key
        );

        self.last_fetch = Some(Instant::now());

        if let Ok(resp) = reqwest::blocking::get(&url) {
            if let Ok(json) = resp.json::<WeatherApiResponse>() {
                self.cached_temp = format!("{:.0}°C", json.main.temp);
            }
        }
    }
}
