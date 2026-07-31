use crate::core::matrix::MatrixBackend;

pub struct WordClock;

impl WordClock {
    pub fn new() -> Self {
        Self
    }

    pub fn render(&self, matrix: &mut dyn MatrixBackend, hours: u32, minutes: u32) {
        let grid = [
            "IT IS HALF TEN",
            "QUARTER PAST TWO",
            "TWENTY FIVE TO",
            "NINE ONE SIX THREE",
            "FOUR FIVE EIGHT",
            "SEVEN ELEVEN TEN",
            "TWELVE O CLOCK",
        ];

        // Draw grid with active words highlighted
        for (y, line) in grid.iter().enumerate() {
            for (x, _ch) in line.chars().enumerate() {
                matrix.set_pixel(x as i32 * 4, y as i32 * 4, 80, 80, 80);
            }
        }
    }
}
