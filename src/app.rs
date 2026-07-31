use crate::api::run_server;
use crate::core::config::Config;
use crate::core::matrix::{MatrixBackend, MockMatrix};
use crate::engines::clock::ClockEngine;

use std::sync::Arc;
use tracing::info;

pub struct ArcadeMatrixApp {
    pub config: Arc<Config>,
}

impl ArcadeMatrixApp {
    pub fn new() -> Self {
        let config = Arc::new(Config::new("conf.ini"));
        Self { config }
    }

    pub async fn run(&self) -> std::io::Result<()> {
        info!("Starting ArcadeMatrix RPi v{}", env!("CARGO_PKG_VERSION"));

        let config_clone = Arc::clone(&self.config);
        std::thread::spawn(move || {
            let sys = actix_web::rt::System::new();
            if let Err(e) = sys.block_on(run_server(config_clone, 8080)) {
                tracing::error!("API Server crashed: {}", e);
            }
        });

        let mut matrix = MockMatrix::new(64, 32);
        let mut clock_engine = ClockEngine::new(64, 32);

        loop {
            if self
                .config
                .matrix_power
                .load(std::sync::atomic::Ordering::Relaxed)
            {
                matrix.clear();
                clock_engine.render(&mut matrix, &self.config);
                matrix.update();
            } else {
                matrix.clear();
                matrix.update();
            }

            tokio::time::sleep(std::time::Duration::from_millis(50)).await;
        }
    }
}
