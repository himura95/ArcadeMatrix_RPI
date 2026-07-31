use parking_lot::Mutex;
use std::collections::HashSet;
use std::fs::{self, File};
use std::io::Write;
use std::path::{Path, PathBuf};
use tracing::{error, info};

pub struct DmdCache {
    cache_dir: PathBuf,
    negative_cache: Mutex<HashSet<String>>,
}

impl DmdCache {
    pub fn new<P: AsRef<Path>>(cache_dir: P) -> Self {
        let path = cache_dir.as_ref().to_path_buf();
        let _ = fs::create_dir_all(&path);
        Self {
            cache_dir: path,
            negative_cache: Mutex::new(HashSet::new()),
        }
    }

    pub fn get_marquee_path(&self, system: &str, game: &str) -> Option<PathBuf> {
        let key = format!("{}/{}", system, game);
        if self.negative_cache.lock().contains(&key) {
            return None;
        }

        let local_filename = format!("{}_{}.png", system, game);
        let local_path = self.cache_dir.join(&local_filename);

        if local_path.exists() {
            return Some(local_path);
        }

        // Attempt download from GitHub Pixelcade repository
        let url = format!(
            "https://raw.githubusercontent.com/alinke/pixelcade-media/main/marquees/{}/{}.png",
            system, game
        );

        match reqwest::blocking::get(&url) {
            Ok(resp) if resp.status().is_success() => {
                if let Ok(bytes) = resp.bytes() {
                    let tmp_path = self.cache_dir.join(format!("{}.tmp", local_filename));
                    if let Ok(mut file) = File::create(&tmp_path) {
                        if file.write_all(&bytes).is_ok()
                            && fs::rename(&tmp_path, &local_path).is_ok()
                        {
                            info!("Downloaded marquee for {}", key);
                            return Some(local_path);
                        }
                    }
                }
            }
            _ => {
                self.negative_cache.lock().insert(key);
            }
        }

        None
    }
}
