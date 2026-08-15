// content.js - Deezer detection (regular DOM, no shadow roots)

let lastSentTrack = '';
let lastSentTime = 0;

function parseTime(str) {
  if (!str) return 0;
  const parts = str.trim().split(':');
  if (parts.length === 2) return parseInt(parts[0]) * 60 + parseInt(parts[1]);
  if (parts.length === 3) return parseInt(parts[0]) * 3600 + parseInt(parts[1]) * 60 + parseInt(parts[2]);
  return 0;
}

function detectNowPlaying() {
  try {
    const titleEl = document.querySelector('[data-testid="item_title"]');
    const artistEl = document.querySelector('[data-testid="item_subtitle"]');
    const elapsedEl = document.querySelector('[data-testid="elapsed_time"]');
    const remainingEl = document.querySelector('[data-testid="remaining_time"]');
    const progressEl = document.querySelector('[data-testid="progress_bar"]');

    if (!titleEl || !titleEl.textContent?.trim()) return null;

    const title = titleEl.textContent.trim();
    const artist = artistEl?.textContent?.trim() || '';

    const elapsed = parseTime(elapsedEl?.textContent);
    const remaining = parseTime(remainingEl?.textContent);
    const duration = parseInt(progressEl?.getAttribute('aria-valuemax')) || (elapsed + remaining) || 0;

    return { title, artist, elapsed, duration, source: 'deezer' };
  } catch (e) {
    console.error('[DeezerExt] detect error:', e);
    return null;
  }
}

function sendToBackground(track) {
  if (!track || !track.title) return;

  const signature = `${track.artist} - ${track.title}`;
  const now = Date.now();

  if (signature === lastSentTrack && (now - lastSentTime) < 500) return;

  chrome.runtime.sendMessage({ action: 'nowPlaying', track }, (response) => {
    if (response) {
      console.log('[DeezerExt] Sent:', track.title, '|', track.artist, '|', track.elapsed + 's/' + track.duration + 's');
      lastSentTrack = signature;
      lastSentTime = now;
    }
  });
}

// Poll every seconds
setInterval(() => {
  const result = detectNowPlaying();
  if (result) sendToBackground(result);
}, 500);

// Initial check after 1s
setTimeout(() => {
  const result = detectNowPlaying();
  if (result) sendToBackground(result);
}, 500);
