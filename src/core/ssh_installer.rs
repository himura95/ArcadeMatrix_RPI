use std::net::TcpStream;
use ssh2::Session;

pub fn install_sync_script(target_ip: &str, matrix_ip: &str) -> Result<String, String> {
    let tcp = TcpStream::connect(format!("{}:22", target_ip))
        .map_err(|e| format!("Failed to connect to {}: {}", target_ip, e))?;

    let mut sess = Session::new().map_err(|e| format!("SSH session error: {}", e))?;
    sess.set_tcp_stream(tcp);
    sess.handshake().map_err(|e| format!("SSH handshake failed: {}", e))?;

    // Try default credentials: root / recalboxroot or linux
    if sess.userauth_password("root", "recalboxroot").is_err() {
        sess.userauth_password("root", "linux")
            .map_err(|_| "SSH authentication failed with root passwords (recalboxroot/linux)".to_string())?;
    }

    let script_content = format!(
        r#"#!/bin/bash
MQTT_BROKER="{}"
echo "Configuring Recalbox/Batocera MQTT sync to $MQTT_BROKER..."
"#,
        matrix_ip
    );

    let mut channel = sess.channel_session().map_err(|e| format!("Failed to open channel: {}", e))?;
    channel.exec(&format!("cat > /recalbox/share/recalbox_setup_mqtt.sh << 'EOF'\n{}\nEOF\nbash /recalbox/share/recalbox_setup_mqtt.sh", script_content))
        .map_err(|e| format!("Command execution failed: {}", e))?;

    Ok(format!("Sync script installed successfully on {}!", target_ip))
}
