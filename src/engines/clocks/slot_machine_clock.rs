use crate::core::matrix::MatrixBackend;

pub struct SlotMachineClock {
    reel_offset: f32,
}

impl SlotMachineClock {
    pub fn new() -> Self {
        Self { reel_offset: 0.0 }
    }

    pub fn render(&mut self, matrix: &mut dyn MatrixBackend) {
        self.reel_offset = (self.reel_offset + 1.0) % 16.0;

        // Draw 3 slot machine reels
        for reel in 0..3 {
            let rx = (reel * 16) + 8;
            for y in 0..matrix.height() as i32 {
                matrix.set_pixel(rx, y, 255, 215, 0);
            }
        }
    }
}
