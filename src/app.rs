use crate::api::run_server;
use crate::core::config::Config;
use crate::core::matrix::{MatrixBackend, MockMatrix};
use crate::engines::clock::ClockEngine;
use crate::engines::message::{MessageEngine, MessagePayload};

use std::net::UdpSocket;
use std::sync::Arc;
use tracing::info;

fn get_local_ip() -> String {
    if let Ok(socket) = UdpSocket::bind("0.0.0.0:0") {
        if socket.connect("8.8.8.8:80").is_ok() {
            if let Ok(addr) = socket.local_addr() {
                return addr.ip().to_string();
            }
        }
    }
    "127.0.0.1".to_string()
}

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
        let local_ip = get_local_ip();
        info!("ArcadeMatrix RPi IP Address: {}", local_ip);

        let config_clone = Arc::clone(&self.config);
        std::thread::spawn(move || {
            let sys = actix_web::rt::System::new();
            if let Err(e) = sys.block_on(run_server(config_clone, 8080)) {
                tracing::error!("API Server crashed: {}", e);
            }
        });

        let mut matrix = MockMatrix::new(64, 32);
        let mut clock_engine = ClockEngine::new(64, 32);
        let mut message_engine = MessageEngine::new();

        // Display startup IP Address banner on DMD matrix
        let startup_payload = MessagePayload {
            text: format!("IP: {}", local_ip),
            color: "#00ffc8".to_string(),
            size: 1,
            direction: "left".to_string(),
            speed: 30,
            timeout_seconds: 4,
        };

        let start_time = std::time::Instant::now();
        while start_time.elapsed() < std::time::Duration::from_secs(4) {
            matrix.clear();
            message_engine.render(&mut matrix, &startup_payload);
            matrix.update();
            tokio::time::sleep(std::time::Duration::from_millis(30)).await;
        }

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
