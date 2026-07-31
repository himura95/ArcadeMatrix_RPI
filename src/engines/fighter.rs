use crate::core::matrix::MatrixBackend;
use byteorder::{LittleEndian, ReadBytesExt};
use image::{Rgb, RgbImage};
use std::fs::File;
use std::io::BufReader;
use std::path::Path;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum FighterState {
    Walk,
    Attack,
    Hit,
    Win,
}

pub struct FighterSprite {
    pub width: u32,
    pub height: u32,
    pub frames: Vec<RgbImage>,
}

impl FighterSprite {
    pub fn load_fgt<P: AsRef<Path>>(path: P) -> Option<Self> {
        let file = File::open(path).ok()?;
        let mut reader = BufReader::new(file);

        let width = reader.read_u16::<LittleEndian>().ok()? as u32;
        let height = reader.read_u16::<LittleEndian>().ok()? as u32;
        let frame_count = reader.read_u16::<LittleEndian>().ok()? as usize;

        let mut frames = Vec::new();
        let pixel_count = (width * height) as usize;

        for _ in 0..frame_count {
            let mut img = RgbImage::new(width, height);
            for i in 0..pixel_count {
                let bgr565 = reader.read_u16::<LittleEndian>().ok()?;
                let r = (((bgr565 >> 11) & 0x1F) as u32 * 255 / 31) as u8;
                let g = (((bgr565 >> 5) & 0x3F) as u32 * 255 / 63) as u8;
                let b = ((bgr565 & 0x1F) as u32 * 255 / 31) as u8;

                let x = (i as u32) % width;
                let y = (i as u32) / width;
                img.put_pixel(x, y, Rgb([r, g, b]));
            }
            frames.push(img);
        }

        Some(Self {
            width,
            height,
            frames,
        })
    }
}

pub struct FighterEngine {
    pub p1_state: FighterState,
    pub p2_state: FighterState,
    pub p1_x: i32,
    pub p2_x: i32,
    pub frame_idx: usize,
}

impl FighterEngine {
    pub fn new(width: u32) -> Self {
        Self {
            p1_state: FighterState::Walk,
            p2_state: FighterState::Walk,
            p1_x: 4,
            p2_x: (width as i32) - 20,
            frame_idx: 0,
        }
    }

    pub fn render(&mut self, matrix: &mut dyn MatrixBackend, p1: &FighterSprite, p2: &FighterSprite) {
        if !p1.frames.is_empty() {
            let frame = &p1.frames[self.frame_idx % p1.frames.len()];
            matrix.draw_image(frame, self.p1_x, (matrix.height() as i32) - (p1.height as i32));
        }

        if !p2.frames.is_empty() {
            let frame = &p2.frames[self.frame_idx % p2.frames.len()];
            matrix.draw_image(frame, self.p2_x, (matrix.height() as i32) - (p2.height as i32));
        }

        self.frame_idx += 1;
    }
}
