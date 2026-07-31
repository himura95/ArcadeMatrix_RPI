use crate::core::config::Config;
use crate::core::matrix::MatrixBackend;
use crate::engines::renderers::BaseRenderer;
use chrono::Local;

pub struct DateEngine {
    base_renderer: BaseRenderer,
}

impl DateEngine {
    pub fn new() -> Self {
        Self {
            base_renderer: BaseRenderer::new(),
        }
    }

    pub fn render(&mut self, matrix: &mut dyn MatrixBackend, config: &Config) {
        let settings = config.settings.read();
        let now = Local::now();
        let date_str = now.format(&settings.date_format).to_string();

        self.base_renderer.render_text(
            matrix,
            &date_str,
            settings.date_theme,
            settings.date_size,
            settings.date_offset_x,
            settings.date_offset_y,
            None,
            None,
        );
    }
}
