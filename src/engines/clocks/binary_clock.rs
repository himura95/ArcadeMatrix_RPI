use crate::core::matrix::MatrixBackend;

pub struct BinaryClock;

impl BinaryClock {
    pub fn new() -> Self {
        Self
    }

    pub fn render(&self, matrix: &mut dyn MatrixBackend, hours: u32, minutes: u32, seconds: u32) {
        let digits = [
            hours / 10, hours % 10,
            minutes / 10, minutes % 10,
            seconds / 10, seconds % 10,
        ];

        let active_color = (0, 255, 200);
        let inactive_color = (30, 30, 50);

        for (col, &val) in digits.iter().enumerate() {
            let cx = (col as i32 * 8) + 8;
            for bit in 0..4 {
                let is_on = (val >> bit) & 1 == 1;
                let cy = 24 - (bit as i32 * 6);
                let color = if is_on { active_color } else { inactive_color };
                matrix.set_pixel(cx, cy, color.0, color.1, color.2);
                matrix.set_pixel(cx + 1, cy, color.0, color.1, color.2);
            }
        }
    }
}
