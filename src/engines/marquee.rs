use crate::core::matrix::MatrixBackend;
use image::RgbImage;

pub struct MarqueeEngine;

impl MarqueeEngine {
    pub fn new() -> Self {
        Self
    }

    pub fn render(&self, matrix: &mut dyn MatrixBackend, image: &RgbImage) {
        matrix.draw_image(image, 0, 0);
    }
}
