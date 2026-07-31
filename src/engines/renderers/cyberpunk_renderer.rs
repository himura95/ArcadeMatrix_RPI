use crate::core::matrix::MatrixBackend;
use rand::Rng;

struct Particle {
    x: f32,
    y: f32,
    speed: f32,
    color: (u8, u8, u8),
}

pub struct CyberpunkRenderer {
    particles: Vec<Particle>,
}

impl CyberpunkRenderer {
    pub fn new(width: u32, height: u32) -> Self {
        let mut rng = rand::thread_rng();
        let mut particles = Vec::new();
        for _ in 0..25 {
            particles.push(Particle {
                x: rng.gen_range(0.0..width as f32),
                y: rng.gen_range(0.0..height as f32),
                speed: rng.gen_range(0.5..2.0),
                color: if rng.gen_bool(0.5) {
                    (0, 255, 255)
                } else {
                    (255, 0, 128)
                },
            });
        }
        Self { particles }
    }

    pub fn render(&mut self, matrix: &mut dyn MatrixBackend) {
        let w = matrix.width() as f32;
        let h = matrix.height() as f32;
        let mut rng = rand::thread_rng();

        for p in &mut self.particles {
            p.y += p.speed;
            if p.y >= h {
                p.y = 0.0;
                p.x = rng.gen_range(0.0..w);
            }
            matrix.set_pixel(p.x as i32, p.y as i32, p.color.0, p.color.1, p.color.2);
        }
    }
}
