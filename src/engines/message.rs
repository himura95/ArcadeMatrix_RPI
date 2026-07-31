use crate::core::matrix::MatrixBackend;
use crate::engines::renderers::BaseRenderer;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MessagePayload {
    pub text: String,
    pub color: String,
    pub size: u32,
    pub direction: String,
    pub speed: u32,
    pub timeout_seconds: u32,
}

pub struct MessageEngine {
    base_renderer: BaseRenderer,
    offset_x: i32,
}

impl MessageEngine {
    pub fn new() -> Self {
        Self {
            base_renderer: BaseRenderer::new(),
            offset_x: 64,
        }
    }

    pub fn render(&mut self, matrix: &mut dyn MatrixBackend, payload: &MessagePayload) {
        self.offset_x -= 1;
        if self.offset_x < -200 {
            self.offset_x = matrix.width() as i32;
        }

        let color = crate::core::theme::parse_hex_color(&payload.color);

        self.base_renderer.render_text(
            matrix,
            &payload.text,
            0,
            payload.size,
            self.offset_x,
            0,
            Some(color),
            None,
        );
    }
}
