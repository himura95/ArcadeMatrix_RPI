use crate::core::config::Config;
use rumqttc::{Client, Event, MqttOptions, Packet, QoS};
use std::sync::Arc;
use std::time::Duration;
use tracing::{error, info};

pub fn start_mqtt_client(config: Arc<Config>) {
    let (enabled, broker, port, user, pass) = {
        let s = config.settings.read();
        (
            s.mqtt_enabled,
            s.mqtt_broker.clone(),
            s.mqtt_port,
            s.mqtt_user.clone(),
            s.mqtt_pass.clone(),
        )
    };

    if !enabled {
        return;
    }

    std::thread::spawn(move || {
        let mut mqttoptions = MqttOptions::new("arcadematrix_rpi", broker, port);
        mqttoptions.set_keep_alive(Duration::from_secs(5));

        if !user.is_empty() {
            mqttoptions.set_credentials(user, pass);
        }

        let (client, mut connection) = Client::new(mqttoptions, 10);

        if let Err(e) = client.subscribe("recalbox/emulation/game", QoS::AtMostOnce) {
            error!("Failed to subscribe to Recalbox MQTT topic: {}", e);
            return;
        }

        for notification in connection.iter() {
            match notification {
                Ok(Event::Incoming(Packet::Publish(publish))) => {
                    if let Ok(payload) = String::from_utf8(publish.payload.to_vec()) {
                        info!("MQTT Recalbox game payload: {}", payload);
                        // Trigger marquee download / engine switch in config
                        *config.force_engine.lock() = Some("marquee".to_string());
                        config
                            .reload_flag
                            .store(true, std::sync::atomic::Ordering::Relaxed);
                    }
                }
                Err(e) => {
                    error!("MQTT connection error: {}", e);
                    std::thread::sleep(Duration::from_secs(5));
                }
                _ => {}
            }
        }
    });
}
