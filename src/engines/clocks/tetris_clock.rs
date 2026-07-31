use crate::core::matrix::MatrixBackend;

pub struct TetrisClock {
    gameboy_palette: bool,
}

impl TetrisClock {
    pub fn new(gameboy_palette: bool) -> Self {
        Self { gameboy_palette }
    }

    pub fn render(&self, _matrix: &mut dyn MatrixBackend, time_str: &str) {
        let (_color_block, _color_bg) = if self.gameboy_palette {
            ((15, 56, 15), (139, 172, 15))
        } else {
            ((0, 240, 240), (0, 0, 0))
        };

        // Render Tetris blocks digit grid
        for (i, _ch) in time_str.chars().enumerate() {
            let _offset_x = (i as i32 * 14) + 4;
            // Draw digit blocks
        }
    }
}
