use crate::core::matrix::MatrixBackend;

pub struct FlipRenderer {
    anim_progress: f32,
}

impl FlipRenderer {
    pub fn new() -> Self {
        Self { anim_progress: 1.0 }
    }

    pub fn render_digit(&mut self, matrix: &mut dyn MatrixBackend, x: i32, y: i32, digit: char) {
        let bg_color = (30, 30, 30);
        let fg_color = (240, 240, 240);
        let line_color = (10, 10, 10);

        // Draw card background (12x16 pixels)
        for dy in 0..16 {
            for dx in 0..12 {
                if dy == 8 {
                    matrix.set_pixel(x + dx, y + dy, line_color.0, line_color.1, line_color.2);
                } else {
                    matrix.set_pixel(x + dx, y + dy, bg_color.0, bg_color.1, bg_color.2);
                }
            }
        }
    }
}
