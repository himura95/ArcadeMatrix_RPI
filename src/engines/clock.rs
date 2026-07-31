use crate::core::config::Config;
use crate::core::matrix::MatrixBackend;
use crate::engines::clocks::*;
use crate::engines::renderers::*;
use chrono::Local;

pub struct ClockEngine {
    base_renderer: BaseRenderer,
    cyberpunk: CyberpunkRenderer,
    flip: FlipRenderer,
    true_matrix: TrueMatrixRenderer,
    pong: PongClock,
    tetris: TetrisClock,
    tetris_gb: TetrisClock,
    word: WordClock,
    binary: BinaryClock,
    pacman: PacmanClock,
    versus: VersusClock,
    slot_machine: SlotMachineClock,
}

impl ClockEngine {
    pub fn new(w: u32, h: u32) -> Self {
        Self {
            base_renderer: BaseRenderer::new(),
            cyberpunk: CyberpunkRenderer::new(w, h),
            flip: FlipRenderer::new(),
            true_matrix: TrueMatrixRenderer::new(w, h),
            pong: PongClock::new(w, h),
            tetris: TetrisClock::new(false),
            tetris_gb: TetrisClock::new(true),
            word: WordClock::new(),
            binary: BinaryClock::new(),
            pacman: PacmanClock::new(),
            versus: VersusClock::new(),
            slot_machine: SlotMachineClock::new(),
        }
    }

    pub fn render(&mut self, matrix: &mut dyn MatrixBackend, config: &Config) {
        let settings = config.settings.read();
        let now = Local::now();

        let time_str = if settings.time_24h {
            now.format("%H:%M").to_string()
        } else {
            now.format("%I:%M").to_string()
        };

        let hours = now.format("%H").to_string().parse::<u32>().unwrap_or(0);
        let minutes = now.format("%M").to_string().parse::<u32>().unwrap_or(0);
        let seconds = now.format("%S").to_string().parse::<u32>().unwrap_or(0);

        match settings.time_theme {
            18 => self.cyberpunk.render(matrix),
            21 => self.true_matrix.render(matrix),
            22 => self.pong.update_and_render(matrix, hours, minutes),
            23 => self.tetris.render(matrix, &time_str),
            24 => self.word.render(matrix, hours, minutes),
            25 => self.binary.render(matrix, hours, minutes, seconds),
            26 => self.pacman.render(matrix),
            27 => self.versus.render(matrix, hours, minutes),
            28 => self.slot_machine.render(matrix),
            29 => self.tetris_gb.render(matrix, &time_str),
            _ => self.base_renderer.render_text(
                matrix,
                &time_str,
                settings.time_theme,
                settings.time_size,
                settings.time_offset_x,
                settings.time_offset_y,
                None,
                None,
            ),
        }
    }
}
