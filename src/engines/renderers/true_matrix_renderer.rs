use crate::core::matrix::MatrixBackend;
use rand::Rng;

struct RainColumn {
    x: i32,
    y: f32,
    speed: f32,
    length: usize,
}

pub struct TrueMatrixRenderer {
    columns: Vec<RainColumn>,
}

impl TrueMatrixRenderer {
    pub fn new(width: u32, height: u32) -> Self {
        let mut rng = rand::thread_rng();
        let mut columns = Vec::new();
        for x in (0..width as i32).step_by(4) {
            columns.push(RainColumn {
                x,
                y: rng.gen_range(-(height as f32)..0.0),
                speed: rng.gen_range(0.8..2.5),
                length: rng.gen_range(6..15),
            });
        }
        Self { columns }
    }

    pub fn render(&mut self, matrix: &mut dyn MatrixBackend) {
        let h = matrix.height() as f32;
        let mut rng = rand::thread_rng();

        for col in &mut self.columns {
            col.y += col.speed;
            if col.y - col.length as f32 >= h {
                col.y = 0.0;
            }

            let head_y = col.y as i32;
            for i in 0..col.length {
                let py = head_y - i as i32;
                if py >= 0 && py < h as i32 {
                    if i == 0 {
                        // Bright leading head pixel
                        matrix.set_pixel(col.x, py, 200, 255, 200);
                    } else {
                        // Green trailing trail
                        let fade = 255 - ((i as f32 / col.length as f32) * 200.0) as u8;
                        matrix.set_pixel(col.x, py, 0, fade, 0);
                    }
                }
            }
        }
    }
}
