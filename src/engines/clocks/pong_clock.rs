use crate::core::matrix::MatrixBackend;

pub struct PongClock {
    ball_x: f32,
    ball_y: f32,
    dx: f32,
    dy: f32,
    p1_y: f32,
    p2_y: f32,
}

impl PongClock {
    pub fn new(w: u32, h: u32) -> Self {
        Self {
            ball_x: w as f32 / 2.0,
            ball_y: h as f32 / 2.0,
            dx: 1.2,
            dy: 0.8,
            p1_y: h as f32 / 2.0,
            p2_y: h as f32 / 2.0,
        }
    }

    pub fn update_and_render(
        &mut self,
        matrix: &mut dyn MatrixBackend,
        _hours: u32,
        _minutes: u32,
    ) {
        let w = matrix.width() as f32;
        let h = matrix.height() as f32;

        self.ball_x += self.dx;
        self.ball_y += self.dy;

        if self.ball_y <= 0.0 || self.ball_y >= h - 1.0 {
            self.dy = -self.dy;
        }

        if self.ball_x <= 2.0 || self.ball_x >= w - 3.0 {
            self.dx = -self.dx;
        }

        // Draw dotted center line
        for y in (0..h as i32).step_by(2) {
            matrix.set_pixel((w / 2.0) as i32, y, 100, 100, 100);
        }

        // Draw paddles
        for dy in -2..=2 {
            matrix.set_pixel(
                1,
                (self.ball_y as i32 + dy).clamp(0, h as i32 - 1),
                255,
                255,
                255,
            );
            matrix.set_pixel(
                (w - 2.0) as i32,
                (self.ball_y as i32 + dy).clamp(0, h as i32 - 1),
                255,
                255,
                255,
            );
        }

        // Draw ball
        matrix.set_pixel(self.ball_x as i32, self.ball_y as i32, 255, 255, 0);
    }
}
