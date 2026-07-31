use crate::core::matrix::MatrixBackend;

pub struct PacmanClock {
    pacman_x: f32,
    direction: f32,
}

impl PacmanClock {
    pub fn new() -> Self {
        Self { pacman_x: 0.0, direction: 1.0 }
    }

    pub fn render(&mut self, matrix: &mut dyn MatrixBackend) {
        let w = matrix.width() as f32;
        self.pacman_x += self.direction * 1.5;

        if self.pacman_x >= w {
            self.pacman_x = 0.0;
        }

        let px = self.pacman_x as i32;
        let py = (matrix.height() / 2) as i32;

        // Draw Pacman
        for dy in -3..=3 {
            for dx in -3..=3 {
                if dx * dx + dy * dy <= 9 {
                    matrix.set_pixel(px + dx, py + dy, 255, 255, 0);
                }
            }
        }

        // Draw dots
        for x in (0..w as i32).step_by(6) {
            if x > px {
                matrix.set_pixel(x, py, 255, 184, 82);
            }
        }
    }
}
