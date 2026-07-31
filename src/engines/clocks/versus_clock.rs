use crate::core::matrix::MatrixBackend;

pub struct VersusClock;

impl VersusClock {
    pub fn new() -> Self {
        Self
    }

    pub fn render(&self, matrix: &mut dyn MatrixBackend, hours: u32, minutes: u32) {
        let w = matrix.width() as i32;

        // Player 1 Health Bar (Hours)
        let p1_health = ((hours % 12) as f32 / 12.0 * (w / 2 - 4) as f32) as i32;
        for x in 2..(2 + p1_health) {
            for y in 1..4 {
                matrix.set_pixel(x, y, 255, 215, 0);
            }
        }

        // Player 2 Health Bar (Minutes)
        let p2_health = ((minutes as f32 / 60.0) * (w / 2 - 4) as f32) as i32;
        for x in (w - 2 - p2_health)..(w - 2) {
            for y in 1..4 {
                matrix.set_pixel(x, y, 220, 20, 60);
            }
        }

        // VS Logo in center
        let center_x = w / 2;
        matrix.set_pixel(center_x - 1, 2, 255, 0, 0);
        matrix.set_pixel(center_x + 1, 2, 0, 0, 255);
    }
}
