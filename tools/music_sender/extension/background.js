// background.js - MV3 service worker for ArcadeMatrix Music Sender

const DEFAULT_SERVER_URL = 'http://192.168.1.18:8085';
const CHECK_INTERVAL_MS = 500;

let lastSentTrack = '';
let lastSentTime = 0;

// Load config from storage
async function loadConfig() {
  try {
    const result = await chrome.storage.local.get(['serverUrl']);
    return {
      serverUrl: result.serverUrl || DEFAULT_SERVER_URL,
      interval: CHECK_INTERVAL_MS
    };
  } catch {
    return { serverUrl: DEFAULT_SERVER_URL, interval: CHECK_INTERVAL_MS };
  }
}

// Initialize on install
chrome.runtime.onInstalled.addListener(() => {
  console.log('ArcadeMatrix Music Sender installed');
  chrome.alarms.create('musicCheck', { periodInMinutes: 1 });
});

// Listen for messages from popup and content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'updateConfig') {
    chrome.storage.local.set({ serverUrl: request.config.serverUrl });
    sendResponse({ success: true });
  } else if (request.action === 'nowPlaying') {
    (async () => {
      const config = await loadConfig();
      await sendTrackData(request.track, config.serverUrl);
      sendResponse({ success: true });
    })();
    return true; // async response
  }
});

// Send track data to the server
async function sendTrackData(track, serverUrl) {
  if (!track || !track.title) return;

  const signature = `${track.artist} - ${track.title}`;
  const now = Date.now();

  // Avoid sending same track too frequently
  if (signature === lastSentTrack && (now - lastSentTime) < 500) return;

  const payload = {
    artist: track.artist || '',
    title: track.title,
    elapsed: track.elapsed || 0,
    duration: track.duration || 0
  };

  try {
    const resp = await fetch(serverUrl + '/nowplaying', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await resp.json();
    console.log('Track sent:', data);
    lastSentTrack = signature;
    lastSentTime = now;
  } catch (e) {
    console.error('Send error:', e);
  }
}

// Inject detection script into a tab (MAIN world to access page's context)
async function injectAndCheck(tabId, detectorFn) {
  try {
    const results = await chrome.scripting.executeScript({
      target: { tabId },
      func: detectorFn,
      world: 'MAIN'
    });
    return results[0]?.result;
  } catch (e) {
    console.error('Inject error:', e.message);
    return null;
  }
}

// ====== DETECTORS ======

// Deezer Web - MAIN world injection
function detectDeezer() {
  return function () {
    function parseTime(str) {
      if (!str) return 0;
      const parts = str.trim().split(':');
      if (parts.length === 2) return parseInt(parts[0]) * 60 + parseInt(parts[1]);
      if (parts.length === 3) return parseInt(parts[0]) * 3600 + parseInt(parts[1]) * 60 + parseInt(parts[2]);
      return 0;
    }
    try {
      // Deezer uses Web Audio API, not <audio> element
      // Try to find track info in Deezer's global state
      const globalKeys = ['ZePlayer', 'player', '__DEEZER__', 'ZP', 'ZPApp'];
      for (const key of globalKeys) {
        if (window[key]) {
          const obj = window[key];
          const track = findTrackInObj(obj);
          if (track) return track;
        }
      }

      // Direct selectors from Deezer player DOM (regular DOM, no shadow roots)
      const titleEl = document.querySelector('[data-testid="item_title"]');
      const artistEl = document.querySelector('[data-testid="item_subtitle"]');
      const elapsedEl = document.querySelector('[data-testid="elapsed_time"]');
      const remainingEl = document.querySelector('[data-testid="remaining_time"]');
      const progressEl = document.querySelector('[data-testid="progress_bar"]');

      if (titleEl && titleEl.textContent?.trim()) {
        const elapsed = parseTime(elapsedEl?.textContent);
        const remaining = parseTime(remainingEl?.textContent);
        const duration = parseInt(progressEl?.getAttribute('aria-valuemax')) || (elapsed + remaining) || 0;
        return {
          title: titleEl.textContent.trim(),
          artist: artistEl?.textContent?.trim() || '',
          elapsed, duration, source: 'deezer-dom'
        };
      }

      // Last resort: check meta tags
      const metaTitle = document.querySelector('meta[property="og:title"]');
      const metaArtist = document.querySelector('meta[property="og:artist"]') ||
                        document.querySelector('meta[property="music:musician"]');
      if (metaTitle) {
        return {
          title: metaTitle.content.trim(),
          artist: metaArtist ? metaArtist.content.trim() : '',
          elapsed: 0, duration: 0, source: 'deezer-meta'
        };
      }
    } catch (e) {
      console.error('[Deezer] detect error:', e);
    }
    return null;
  };
}

function findTrackInObj(obj, depth = 0) {
  if (!obj || typeof obj !== 'object' || depth > 6) return null;
  if (obj.title && typeof obj.title === 'string' && obj.title.length > 0) {
    return {
      title: obj.title,
      artist: obj.artist?.name || obj.contributor?.name || '',
      elapsed: obj.elapsed || obj.current || 0,
      duration: obj.duration || 0,
      source: 'deezer-global'
    };
  }
  for (const key of Object.keys(obj)) {
    try {
      const result = findTrackInObj(obj[key], depth + 1);
      if (result) return result;
    } catch(e) {}
  }
  return null;
}

// Spotify Web
function detectSpotify() {
  return function () {
    try {
      // Check audio element
      const audio = document.querySelector('audio');
      if (audio && !audio.paused) {
        const metaTitle = document.querySelector('meta[property="og:title"]');
        const metaArtist = document.querySelector('meta[property="music:musician"]');
        if (metaTitle) {
          return {
            title: metaTitle.content.trim(),
            artist: metaArtist ? metaArtist.content.trim() : '',
            elapsed: Math.floor(audio.currentTime),
            duration: Math.floor(audio.duration),
            source: 'spotify'
          };
        }
      }

      // Fallback: main player selectors
      const titleEl = document.querySelector('[data-testid="nowplaying-title"]') ||
                      document.querySelector('[class*="trackName"]');
      const artistEl = document.querySelector('[data-testid="nowplaying-artists"]') ||
                       document.querySelector('[class*="artistName"]');

      if (titleEl && artistEl) {
        return {
          title: titleEl.textContent.trim(),
          artist: artistEl.textContent.trim(),
          elapsed: 0, duration: 0, source: 'spotify'
        };
      }

      // Check for now-playing-bar
      const bar = document.querySelector('[data-testid="now-playing-bar"]');
      if (bar) {
        const title = bar.querySelector('a[href*="/track/"]')?.textContent?.trim() || '';
        const artist = bar.querySelector('a[href*="/artist/"]')?.textContent?.trim() || '';
        if (title) return { title, artist, elapsed: 0, duration: 0, source: 'spotify' };
      }
    } catch (e) {
      // ignore
    }
    return null;
  };
}

// YouTube Music
function detectYouTubeMusic() {
  return function () {
    try {
      const audio = document.querySelector('audio');
      if (audio && !audio.paused) {
        const metaTitle = document.querySelector('meta[property="og:title"]');
        const metaArtist = document.querySelector('meta[property="og:site_name"]');
        if (metaTitle) {
          return {
            title: metaTitle.content.trim(),
            artist: metaArtist ? metaArtist.content.trim() : '',
            elapsed: Math.floor(audio.currentTime),
            duration: Math.floor(audio.duration),
            source: 'youtube'
          };
        }
      }

      const titleEl = document.querySelector('yt-formatted-string[id="title"]') ||
                      document.querySelector('ytmusic-player-bar #title');
      if (titleEl) {
        const artistEl = document.querySelector('a[href*="/channel/"]');
        return {
          title: titleEl.textContent.trim(),
          artist: artistEl?.textContent?.trim() || '',
          elapsed: 0, duration: 0, source: 'youtube'
        };
      }
    } catch (e) {
      // ignore
    }
    return null;
  };
}

// Generic HTML5 audio detector
function detectGenericAudio() {
  return function () {
    try {
      const audios = document.querySelectorAll('audio');
      for (const audio of audios) {
        if (!audio.paused && audio.duration > 10 && audio.currentTime > 0) {
          const ogTitle = document.querySelector('meta[property="og:title"]')?.content;
          const ogArtist = document.querySelector('meta[property="og:artist"]')?.content ||
                          document.querySelector('meta[property="music:musician"]')?.content;
          return {
            title: ogTitle || document.title || 'Unknown',
            artist: ogArtist || '',
            elapsed: Math.floor(audio.currentTime),
            duration: Math.floor(audio.duration),
            source: 'generic'
          };
        }
      }
    } catch (e) {
      // ignore
    }
    return null;
  };
}

// Main check routine
async function checkForMusic() {
  const config = await loadConfig();

  try {
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tabs.length) return;

    const tab = tabs[0];

    // Get URL - may be empty for chrome:// pages
    let url = '';
    try {
      // Try to get URL from tab
      url = tab.url || '';
    } catch (e) {
      // Can't read URL (chrome:// etc.)
      return;
    }

    // Check if URL matches known music sites
    const lowerUrl = url.toLowerCase();
    const isMusicSite = lowerUrl.includes('deezer.com') ||
                        lowerUrl.includes('spotify.com') ||
                        lowerUrl.includes('music.youtube.com') ||
                        lowerUrl.includes('youtube.com');

    if (!isMusicSite) {
      return;
    }

    console.log('Checking music site:', url);

    // Order detectors by site
    const detectors = [];
    if (lowerUrl.includes('deezer.com')) {
      detectors.push(detectDeezer);
    }
    if (lowerUrl.includes('spotify.com')) {
      detectors.push(detectSpotify);
    }
    if (lowerUrl.includes('youtube.com')) {
      detectors.push(detectYouTubeMusic);
    }
    // Always add generic detector as fallback
    detectors.push(detectGenericAudio);

    for (const detector of detectors) {
      const result = await injectAndCheck(tab.id, detector());
      console.log('Detector result:', result);
      if (result && result.title) {
        console.log('Detected:', result);
        await sendTrackData(result, config.serverUrl);
        return;
      }
    }

    console.log('No music detected on:', url);
  } catch (e) {
    console.error('Check error:', e);
  }
}

// Use chrome.alarms for periodic checks
chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === 'musicCheck') {
    await checkForMusic();
  }
});

// Also check on tab updates (faster response)
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.active) {
    await checkForMusic();
  }
});

// Check on tab activation
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  await checkForMusic();
});

// Run initial check
checkForMusic();
