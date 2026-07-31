#![recursion_limit = "256"]

mod api;
mod app;
mod core;
mod engines;

use app::ArcadeMatrixApp;
use tracing_subscriber::FmtSubscriber;

#[tokio::main]
async fn main() -> std::io::Result<()> {
    let subscriber = FmtSubscriber::builder()
        .with_max_level(tracing::Level::INFO)
        .finish();
    tracing::subscriber::set_global_default(subscriber)
        .expect("setting default subscriber failed");

    let app = ArcadeMatrixApp::new();
    app.run().await
}
