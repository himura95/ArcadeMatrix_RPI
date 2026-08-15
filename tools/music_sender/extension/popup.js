// popup.js - Popup script for ArcadeMatrix Music Sender

document.addEventListener('DOMContentLoaded', function() {
  const serverIp = document.getElementById('server-ip');
  const serverPort = document.getElementById('server-port');
  const saveBtn = document.getElementById('save-btn');
  const testBtn = document.getElementById('test-btn');

  // Load saved configuration
  chrome.storage.local.get(['serverUrl'], function(result) {
    if (result.serverUrl) {
      const url = new URL(result.serverUrl);
      serverIp.value = url.hostname;
      serverPort.value = url.port || '8085';
    }
  });

  // Save configuration
  saveBtn.addEventListener('click', function() {
    const ip = serverIp.value.trim();
    const port = serverPort.value.trim() || '8085';
    
    if (!ip) {
      alert('Please enter a valid IP address');
      return;
    }
    
    const serverUrl = `http://${ip}:${port}`;
    
    // Save to storage
    chrome.storage.local.set({serverUrl: serverUrl}, function() {
      // Send to background script
      chrome.runtime.sendMessage({
        action: 'updateConfig',
        config: { serverUrl: serverUrl }
      });
      
      alert('Configuration saved!');
    });
  });

  // Test connection
  testBtn.addEventListener('click', function() {
    const ip = serverIp.value.trim();
    const port = serverPort.value.trim() || '8085';
    
    if (!ip) {
      alert('Please enter a valid IP address');
      return;
    }
    
    const testUrl = `http://${ip}:${port}/health`;
    
    const controller = new AbortController();
    setTimeout(() => controller.abort(), 3000);
    fetch(testUrl, { signal: controller.signal })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'ok') {
          alert('Connection successful!');
        } else {
          alert('Connection failed - server not responding');
        }
      })
      .catch(error => {
        console.error('Test error:', error);
        alert('Connection failed - check IP and port');
      });
  });
});