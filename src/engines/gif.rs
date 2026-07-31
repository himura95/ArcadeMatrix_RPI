use crate::core::matrix::MatrixBackend;
use gif::Decoder;
use image::{Rgb, RgbImage};
use std::fs::File;
use std::path::{Path, PathBuf};

pub struct GifEngine {
    current_gif_path: Option<PathBuf>,
    frames: Vec<RgbImage>,
    frame_index: usize,
}

impl GifEngine {
    pub fn new() -> Self {
        Self {
            current_gif_path: None,
            frames: Vec::new(),
            frame_index: 0,
        }
    }

    pub fn load_gif<P: AsRef<Path>>(&mut self, path: P) -> bool {
        let file = match File::open(&path) {
            Ok(f) => f,
            Err(_) => return false,
        };

        let mut decoder = match Decoder::new(file) {
            Ok(d) => d,
            Err(_) => return false,
        };

        let mut frames = Vec::new();
        while let Ok(Some(frame)) = decoder.read_next_frame() {
            let width = frame.width as u32;
            let height = frame.height as u32;
            let mut img = RgbImage::new(width, height);

            for (i, pixel) in frame.buffer.chunks_exact(4).enumerate() {
                let x = (i as u32) % width;
                let y = (i as u32) / width;
                img.put_pixel(x, y, Rgb([pixel[0], pixel[1], pixel[2]]));
            }
            frames.push(img);
        }

        if !frames.is_empty() {
            self.current_gif_path = Some(path.as_ref().to_path_buf());
            self.frames = frames;
            self.frame_index = 0;
            true
        } else {
            false
        }
    }

    pub fn render_next_frame(&mut self, matrix: &mut dyn MatrixBackend) {
        if self.frames.is_empty() {
            return;
        }

        let img = &self.frames[self.frame_index];
        matrix.draw_image(img, 0, 0);

        self.frame_index = (self.frame_index + 1) % self.frames.len();
    }
}
