use std::time::Duration;
use tracing::info;

pub struct YouTubeProvider;

impl YouTubeProvider {
    pub fn fetch_channel_stats(api_key: &str, channel_input: &str) -> Option<(String, u64, u64, u64)> {
        if api_key.is_empty() {
            tracing::warn!("[YouTube] API key is empty");
            return None;
        }

        let client = reqwest::blocking::Client::builder()
            .timeout(Duration::from_secs(10))
            .build()
            .ok()?;

        // Clean channel input: remove @ prefix if present
        let cleaned = channel_input.trim_start_matches('@').trim();

        // Step 1: Resolve channel ID if needed
        let channel_id = if cleaned.starts_with("UC") {
            cleaned.to_string()
        } else {
            match Self::resolve_channel_by_handle(&client, api_key, cleaned) {
                Some(id) => id,
                None => {
                    tracing::warn!("[YouTube] Could not resolve channel: {}", cleaned);
                    return None;
                }
            }
        };

        // Step 2: Fetch channel stats using the official API
        let url = format!(
            "https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={}&key={}",
            channel_id, api_key
        );

        let res = match client.get(&url).send() {
            Ok(r) => r,
            Err(e) => {
                tracing::warn!("[YouTube] Request failed: {}", e);
                return None;
            }
        };

        if !res.status().is_success() {
            let status = res.status();
            let body = res.text().unwrap_or_default();
            tracing::warn!("[YouTube] HTTP {}: {}", status, body);
            return None;
        }

        let json = match res.json::<serde_json::Value>() {
            Ok(j) => j,
            Err(e) => {
                tracing::warn!("[YouTube] JSON parse failed: {}", e);
                return None;
            }
        };

        // Step 3: Parse the response
        Self::parse_channel_response(&json)
    }

    fn resolve_channel_by_handle(
        client: &reqwest::blocking::Client,
        api_key: &str,
        handle: &str,
    ) -> Option<String> {
        // Try forHandle parameter first (works with @handle or plain handle)
        let handle_param = if handle.starts_with('@') {
            handle.to_string()
        } else {
            format!("@{}", handle)
        };

        let url = format!(
            "https://www.googleapis.com/youtube/v3/channels?part=id,snippet&forHandle={}&key={}",
            handle_param, api_key
        );

        if let Ok(res) = client.get(&url).send() {
            if res.status().is_success() {
                if let Ok(json) = res.json::<serde_json::Value>() {
                    if let Some(items) = json["items"].as_array() {
                        if let Some(first) = items.first() {
                            if let Some(id) = first["id"].as_str() {
                                return Some(id.to_string());
                            }
                        }
                    }
                }
            }
        }

        // Fallback: try as channel username via forUsername
        let url2 = format!(
            "https://www.googleapis.com/youtube/v3/channels?part=id,snippet&forUsername={}&key={}",
            handle, api_key
        );

        if let Ok(res) = client.get(&url2).send() {
            if res.status().is_success() {
                if let Ok(json) = res.json::<serde_json::Value>() {
                    if let Some(items) = json["items"].as_array() {
                        if let Some(first) = items.first() {
                            if let Some(id) = first["id"].as_str() {
                                return Some(id.to_string());
                            }
                        }
                    }
                }
            }
        }

        None
    }

    fn parse_channel_response(json: &serde_json::Value) -> Option<(String, u64, u64, u64)> {
        let items = json["items"].as_array()?;
        let item = items.first()?;

        let subscriber_count: u64 = item["statistics"]["subscriberCount"]
            .as_str()
            .and_then(|s| s.parse().ok())
            .unwrap_or(0);

        let video_count: u64 = item["statistics"]["videoCount"]
            .as_str()
            .and_then(|s| s.parse().ok())
            .unwrap_or(0);

        let view_count: u64 = item["statistics"]["viewCount"]
            .as_str()
            .and_then(|s| s.parse().ok())
            .unwrap_or(0);

        let title = item["snippet"]["title"]
            .as_str()
            .unwrap_or("Unknown")
            .to_string();

        info!("[YouTube] {} has {} subscribers, {} videos, {} views", title, subscriber_count, video_count, view_count);

        Some((title, subscriber_count, video_count, view_count))
    }
}