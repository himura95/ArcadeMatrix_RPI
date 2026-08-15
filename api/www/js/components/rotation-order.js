const ROTATION_ITEMS = [
  { value: 'clock', label: 'Clock' },
  { value: 'date', label: 'Date' },
  { value: 'weather', label: 'Weather' },
  { value: 'crypto', label: 'Crypto' },
  { value: 'stocks', label: 'Stocks' },
  { value: 'countdown', label: 'Countdown' },
  { value: 'gifs', label: 'GIFs' },
  { value: 'youtube', label: 'YouTube' },
  { value: 'music', label: 'Music' },
];

const ROTATION_EMOJI = {
  clock: '🕒', date: '📅', weather: '☁️', crypto: '📈', stocks: '📊',
  countdown: '⏱️', gifs: '🎬', youtube: '📺', music: '🎵',
};

let rotationOrder = [];
let rotationEnabled = new Set();
let dragSrcIndex = null;

export function initRotationOrder() {
  buildRotationList();
  bindDragEvents();
}

export function setRotationFromConfig(rotationStr) {
  const arr = (rotationStr || '').split(',').map(s => s.trim()).filter(Boolean);
  if (arr.length > 0) {
    rotationOrder = arr;
    rotationEnabled = new Set(arr);
  } else {
    rotationOrder = ROTATION_ITEMS.map(i => i.value);
    rotationEnabled = new Set(rotationOrder);
  }
  buildRotationList();
}

function buildRotationList() {
  const container = document.getElementById('rotation-order-list');
  if (!container) return;
  container.innerHTML = '';
  rotationOrder.forEach((value, index) => {
    const emoji = ROTATION_EMOJI[value] || '📺';
    const itemDef = ROTATION_ITEMS.find(d => d.value === value);
    const label = itemDef ? itemDef.label : value;
    const enabled = rotationEnabled.has(value);
    const div = document.createElement('div');
    div.className = 'rot-item' + (enabled ? '' : ' rot-disabled');
    div.dataset.value = value;
    div.dataset.index = index;
    div.innerHTML = `
      <span class="rot-handle">⠿</span>
      <input type="checkbox" ${enabled ? 'checked' : ''} data-value="${value}">
      <span class="rot-label">${emoji} ${label}</span>
    `;
    const cb = div.querySelector('input[type="checkbox"]');
    cb.addEventListener('change', () => {
      if (cb.checked) {
        rotationEnabled.add(value);
        div.classList.remove('rot-disabled');
      } else {
        rotationEnabled.delete(value);
        div.classList.add('rot-disabled');
      }
    });
    container.appendChild(div);
  });
}

function bindDragEvents() {
  const container = document.getElementById('rotation-order-list');
  if (!container) return;
  container.addEventListener('mousedown', onDragStart);
  container.addEventListener('touchstart', onDragStart, { passive: false });
  document.addEventListener('mouseup', onDragEnd);
  document.addEventListener('touchend', onDragEnd);
  document.addEventListener('mousemove', onDragMove);
  document.addEventListener('touchmove', onDragMove, { passive: false });
}

function onDragStart(e) {
  const item = e.target.closest('.rot-item');
  if (!item || e.target.type === 'checkbox') return;
  dragSrcIndex = parseInt(item.dataset.index);
  item.classList.add('dragging');
}

function onDragMove(e) {
  if (dragSrcIndex === null) return;
  e.preventDefault();
  const container = document.getElementById('rotation-order-list');
  if (!container) return;
  const point = e.touches ? e.touches[0] : e;
  const elements = document.elementsFromPoint(point.clientX, point.clientY);
  let targetItem = null;
  for (const el of elements) {
    if (el && el.classList.contains('rot-item') && !el.classList.contains('dragging')) {
      targetItem = el;
      break;
    }
  }
  container.querySelectorAll('.rot-item').forEach(i => i.classList.remove('drag-over'));
  if (targetItem) {
    targetItem.classList.add('drag-over');
    const targetIndex = parseInt(targetItem.dataset.index);
    if (!isNaN(dragSrcIndex) && !isNaN(targetIndex) && dragSrcIndex !== targetIndex) {
      const tmp = rotationOrder[dragSrcIndex];
      rotationOrder[dragSrcIndex] = rotationOrder[targetIndex];
      rotationOrder[targetIndex] = tmp;
      dragSrcIndex = targetIndex;
      buildRotationList();
    }
  }
}

function onDragEnd() {
  if (dragSrcIndex === null) return;
  document.querySelectorAll('.dragging, .drag-over').forEach(el => {
    el.classList.remove('dragging', 'drag-over');
  });
  dragSrcIndex = null;
}

export function getRotationString() {
  return rotationOrder
    .filter(v => rotationEnabled.has(v))
    .join(',');
}
