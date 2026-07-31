use crate::core::matrix::MatrixBackend;
use crate::core::theme::get_theme_info;
use image::{Rgb, RgbImage};
use rusttype::{Font, Scale};

pub struct BaseRenderer {
    font: Font<'static>,
}

impl BaseRenderer {
    pub fn new() -> Self {
        // Default built-in font fallback
        let font_data = include_bytes!("../../../fonts/PressStart2P.ttf");
        let font = Font::try_from_bytes(font_data as &[u8]).expect("Error loading built-in font");
        Self { font }
    }

    pub fn render_text(
        &self,
        matrix: &mut dyn MatrixBackend,
        text: &str,
        theme_id: i32,
        size: u32,
        offset_x: i32,
        offset_y: i32,
        color1_override: Option<(u8, u8, u8)>,
        color2_override: Option<(u8, u8, u8)>,
    ) {
        let theme = get_theme_info(theme_id);
        let primary = color1_override.unwrap_or(theme.primary_color);
        let secondary = color2_override.unwrap_or(theme.secondary_color);

        let scale = Scale::uniform(8.0 * size as f32);
        let v_metrics = self.font.v_metrics(scale);

        let glyphs: Vec<_> = self.font.layout(text, scale, rusttype::point(0.0, v_metrics.ascent)).collect();
        let text_width = glyphs
            .iter()
            .rev()
            .next()
            .map(|g| g.position().x + g.unpositioned().h_metrics().advance_width)
            .unwrap_or(0.0) as i32;
        let text_height = (v_metrics.ascent - v_metrics.descent) as i32;

        let start_x = (matrix.width() as i32 - text_width) / 2 + offset_x;
        let start_y = (matrix.height() as i32 - text_height) / 2 + offset_y;

        // Render shadow/outline with secondary color
        if secondary != (0, 0, 0) {
            for glyph in &glyphs {
                if let Some(bb) = glyph.pixel_bounding_box() {
                    glyph.draw(|x, y, v| {
                        if v > 0.5 {
                            let px = start_x + bb.min.x + x as i32 + 1;
                            let py = start_y + bb.min.y + y as i32 + 1;
                            matrix.set_pixel(px, py, secondary.0, secondary.1, secondary.2);
                        }
                    });
                }
            }
        }

        // Render main text with primary color
        for glyph in &glyphs {
            if let Some(bb) = glyph.pixel_bounding_box() {
                glyph.draw(|x, y, v| {
                    if v > 0.5 {
                        let px = start_x + bb.min.x + x as i32;
                        let py = start_y + bb.min.y + y as i32;
                        matrix.set_pixel(px, py, primary.0, primary.1, primary.2);
                    }
                });
            }
        }
    }
}
