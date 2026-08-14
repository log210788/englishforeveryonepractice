/* ==========================================================================
   Teacher Lewis's Practice Book - Interactive Audio Studio & Workbook Engine
   ========================================================================== */

let currentPageNum = 1;
let isStudioMode = false;
let activeTool = 'select'; // 'select' | 'add-audio' | 'add-text'

// Annotations Store: Keyed by page number e.g. annotationsData[12] = [ { id, type, top, left, ... } ]
let annotationsData = {};

// Audio Registry (loaded from audio_index.json)
let audioIndex = {};

// Audio Player Deck State
let currentAudio = null;
let activeAudioPinId = null;
let playbackSpeed = 1.0;
let isMuted = false;

// Currently Selected Element for Modal Editing
let editingPin = null;
let modalAudioPreview = null;

// DOM Elements
const pageSelect = document.getElementById('pageSelect');
const prevPageBtn = document.getElementById('prevPageBtn');
const nextPageBtn = document.getElementById('nextPageBtn');
const pageImage = document.getElementById('pageImage');
const overlayLayer = document.getElementById('overlayLayer');
const bookCanvas = document.getElementById('bookCanvas');

// Header & Mode Controls
const toggleModeBtn = document.getElementById('toggleModeBtn');
const modeBtnText = document.getElementById('modeBtnText');
const studioSubToolbar = document.getElementById('studioSubToolbar');
const exportJsonBtn = document.getElementById('exportJsonBtn');
const importJsonBtn = document.getElementById('importJsonBtn');
const importFileInput = document.getElementById('importFileInput');
const gradeBtn = document.getElementById('gradeBtn');
const scoreBadge = document.getElementById('scoreBadge');

// Studio Toolbar Tools
const toolSelectBtn = document.getElementById('toolSelectBtn');
const toolAddAudioBtn = document.getElementById('toolAddAudioBtn');
const toolAddTextBtn = document.getElementById('toolAddTextBtn');
const clearPageBtn = document.getElementById('clearPageBtn');
const savePageBtn = document.getElementById('savePageBtn');

// Top Audio Player Deck
const audioTrackSelect = document.getElementById('audioTrackSelect');
const audioPlayBtn = document.getElementById('audioPlayBtn');
const audioStopBtn = document.getElementById('audioStopBtn');
const audioProgress = document.getElementById('audioProgress');
const audioTimeDisplay = document.getElementById('audioTimeDisplay');
const audioSpeedBtn = document.getElementById('audioSpeedBtn');
const audioVolumeBtn = document.getElementById('audioVolumeBtn');

// Modal Elements
const audioModalBackdrop = document.getElementById('audioModalBackdrop');
const modalCloseBtn = document.getElementById('modalCloseBtn');
const modalCancelBtn = document.getElementById('modalCancelBtn');
const modalSaveBtn = document.getElementById('modalSaveBtn');
const modalDeleteBtn = document.getElementById('modalDeleteBtn');

const modalUnitSelect = document.getElementById('modalUnitSelect');
const modalTrackFilter = document.getElementById('modalTrackFilter');
const modalTrackSelect = document.getElementById('modalTrackSelect');
const modalPreviewBtn = document.getElementById('modalPreviewBtn');
const modalPinLabel = document.getElementById('modalPinLabel');
const modalIconStyle = document.getElementById('modalIconStyle');
const modalPinColor = document.getElementById('modalPinColor');

// 1. Initialize Workbook Application
async function initWorkbook() {
  populatePageSelector();
  await loadAudioIndex();
  loadStoredAnnotations();
  setupEventListeners();
  loadPage(currentPageNum);
  setupMascot();
}

// Populate Page Selector Dropdown (Pages 1 to 176)
function populatePageSelector() {
  pageSelect.innerHTML = '';
  for (let pNum = 1; pNum <= 176; pNum++) {
    const opt = document.createElement('option');
    opt.value = pNum;
    opt.textContent = `Page ${pNum}`;
    pageSelect.appendChild(opt);
  }
}

// Fetch Audio Index JSON
async function loadAudioIndex() {
  try {
    const res = await fetch('audio_index.json');
    if (res.ok) {
      audioIndex = await res.json();
    }
  } catch (err) {
    console.warn('audio_index.json not found, constructing default fallback index.', err);
    // Construct default unit mapping
    for (let u = 1; u <= 48; u++) {
      audioIndex[u] = [];
    }
  }
}

// Load Annotations from LocalStorage or Default
function loadStoredAnnotations() {
  const saved = localStorage.getItem('workbook_custom_annotations');
  if (saved) {
    try {
      annotationsData = JSON.parse(saved);
    } catch (e) {
      console.error('Failed to parse saved annotations', e);
      annotationsData = {};
    }
  }
}

// Save Annotations to LocalStorage
function persistAnnotations() {
  localStorage.setItem('workbook_custom_annotations', JSON.stringify(annotationsData));
}

// 2. Load Page and Render Clean View / Placed Pins
function loadPage(pageNum) {
  currentPageNum = pageNum;
  pageSelect.value = pageNum;

  prevPageBtn.disabled = (pageNum <= 1);
  nextPageBtn.disabled = (pageNum >= 176);

  const padNum = String(pageNum).padStart(3, '0');
  pageImage.src = `images/page_${padNum}.png`;

  stopAudioTrack();

  // Render Page Overlays from custom annotations store
  renderPageOverlays(pageNum);
  updateAudioDeckOptions();
}

// Render custom audio pins and text boxes for the current page
function renderPageOverlays(pageNum) {
  overlayLayer.innerHTML = '';
  const items = annotationsData[pageNum] || [];

  items.forEach(item => {
    if (item.type === 'audio') {
      const pinEl = createAudioPinElement(item);
      overlayLayer.appendChild(pinEl);
    } else if (item.type === 'input') {
      const inputEl = createTextBoxElement(item);
      overlayLayer.appendChild(inputEl);
    }
  });
}

// Helper: Calculate default unit for a given page number
function getUnitForPage(pageNum) {
  // Estimated unit ranges for Level 1 Practice Book (~48 units across 176 pages)
  const unit = Math.min(48, Math.max(1, Math.ceil(pageNum / 3.6)));
  return String(unit);
}

// 3. Create Audio Pin DOM Element
function createAudioPinElement(item) {
  const wrapper = document.createElement('div');
  wrapper.className = `audio-pin-wrapper ${item.color || 'cyan'} ${activeAudioPinId === item.id ? 'active-playing' : ''}`;
  wrapper.style.top = `${item.top}%`;
  wrapper.style.left = `${item.left}%`;
  wrapper.dataset.id = item.id;
  wrapper.dataset.type = 'audio';

  const iconClass = getIconClass(item.iconStyle);
  const labelText = item.label || item.audioFile || 'Audio Pin';

  wrapper.innerHTML = `
    <div class="audio-pin-btn" title="Click to play audio (${labelText})">
      <i class="${iconClass}"></i>
    </div>
    ${labelText ? `<span class="audio-pin-badge">${labelText}</span>` : ''}
    <div class="pin-edit-handle" title="Edit Audio Settings"><i class="fa-solid fa-gear"></i></div>
  `;

  // Click Action in Study Mode vs Studio Mode
  wrapper.addEventListener('click', (e) => {
    if (e.target.closest('.pin-edit-handle')) {
      e.stopPropagation();
      openAudioModal(item);
      return;
    }

    if (isStudioMode) {
      if (activeTool === 'select') {
        openAudioModal(item);
      }
    } else {
      // Play Audio in Study Mode
      playAudioPinTrack(item);
    }
  });

  makeDraggable(wrapper, item);
  return wrapper;
}

function getIconClass(style) {
  switch (style) {
    case 'play': return 'fa-solid fa-play';
    case 'speaker': return 'fa-solid fa-volume-high';
    case 'music': return 'fa-solid fa-music';
    case 'headphones':
    default: return 'fa-solid fa-headphones';
  }
}

// 4. Create Text Input Box DOM Element
function createTextBoxElement(item) {
  const wrapper = document.createElement('div');
  wrapper.className = 'text-box-wrapper';
  wrapper.style.top = `${item.top}%`;
  wrapper.style.left = `${item.left}%`;
  wrapper.style.width = `${item.width || 20}%`;
  wrapper.style.height = `${item.height || 4}%`;
  wrapper.dataset.id = item.id;
  wrapper.dataset.type = 'input';

  const inputEl = document.createElement('input');
  inputEl.type = 'text';
  inputEl.className = 'custom-text-input';
  inputEl.value = item.userAnswer || '';
  inputEl.placeholder = isStudioMode ? 'Text input...' : '...';
  inputEl.disabled = isStudioMode; // Disabled typing while in Studio edit mode to allow drag

  inputEl.addEventListener('input', (e) => {
    item.userAnswer = e.target.value;
    persistAnnotations();
  });

  wrapper.appendChild(inputEl);

  if (isStudioMode) {
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'box-delete-btn';
    deleteBtn.innerHTML = '&times;';
    deleteBtn.title = 'Delete Text Box';
    deleteBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      removeAnnotationItem(currentPageNum, item.id);
    });
    wrapper.appendChild(deleteBtn);
  }

  makeDraggable(wrapper, item);
  return wrapper;
}

// 5. Drag & Drop Engine (Relative Percentage Coordinates)
function makeDraggable(element, item) {
  let isDragging = false;
  let startX, startY;
  let initialLeft, initialTop;

  element.addEventListener('mousedown', (e) => {
    if (!isStudioMode || activeTool !== 'select') return;
    if (e.target.tagName === 'INPUT' || e.target.closest('.modal-backdrop')) return;

    isDragging = true;
    startX = e.clientX;
    startY = e.clientY;

    const rect = bookCanvas.getBoundingClientRect();
    initialLeft = parseFloat(element.style.left) || 0;
    initialTop = parseFloat(element.style.top) || 0;

    element.classList.add('is-dragging');
    showCoordTooltip(element);

    const onMouseMove = (moveEvent) => {
      if (!isDragging) return;
      const deltaX = moveEvent.clientX - startX;
      const deltaY = moveEvent.clientY - startY;

      const deltaLeftPct = (deltaX / rect.width) * 100;
      const deltaTopPct = (deltaY / rect.height) * 100;

      const newLeft = Math.max(0, Math.min(95, initialLeft + deltaLeftPct));
      const newTop = Math.max(0, Math.min(95, initialTop + deltaTopPct));

      element.style.left = `${newLeft.toFixed(2)}%`;
      element.style.top = `${newTop.toFixed(2)}%`;

      item.left = parseFloat(newLeft.toFixed(2));
      item.top = parseFloat(newTop.toFixed(2));

      updateCoordTooltip(element, newTop.toFixed(2), newLeft.toFixed(2));
    };

    const onMouseUp = () => {
      if (isDragging) {
        isDragging = false;
        element.classList.remove('is-dragging');
        hideCoordTooltip(element);
        persistAnnotations();
      }
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
    };

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  });
}

function showCoordTooltip(el) {
  let tooltip = el.querySelector('.coord-tooltip');
  if (!tooltip) {
    tooltip = document.createElement('span');
    tooltip.className = 'coord-tooltip';
    el.appendChild(tooltip);
  }
  updateCoordTooltip(el, parseFloat(el.style.top), parseFloat(el.style.left));
}

function updateCoordTooltip(el, top, left) {
  const tooltip = el.querySelector('.coord-tooltip');
  if (tooltip) {
    tooltip.textContent = `y:${top}%, x:${left}%`;
  }
}

function hideCoordTooltip(el) {
  const tooltip = el.querySelector('.coord-tooltip');
  if (tooltip) tooltip.remove();
}

// 6. Click-to-Place Pin on Canvas (Add Audio / Add Text Tool)
bookCanvas.addEventListener('click', (e) => {
  if (!isStudioMode) return;
  if (activeTool === 'select') return;
  if (e.target.closest('.audio-pin-wrapper') || e.target.closest('.text-box-wrapper')) return;

  const rect = bookCanvas.getBoundingClientRect();
  const clickX = e.clientX - rect.left;
  const clickY = e.clientY - rect.top;

  const leftPct = parseFloat(((clickX / rect.width) * 100).toFixed(2));
  const topPct = parseFloat(((clickY / rect.height) * 100).toFixed(2));

  if (activeTool === 'add-audio') {
    const newItem = {
      id: 'audio_' + Date.now(),
      type: 'audio',
      top: topPct,
      left: leftPct,
      unit: getUnitForPage(currentPageNum),
      audioFile: '',
      label: 'New Audio',
      iconStyle: 'headphones',
      color: 'cyan'
    };

    addAnnotationItem(currentPageNum, newItem);
    openAudioModal(newItem);
  } else if (activeTool === 'add-text') {
    const newItem = {
      id: 'input_' + Date.now(),
      type: 'input',
      top: topPct,
      left: leftPct,
      width: 25,
      height: 4,
      userAnswer: ''
    };

    addAnnotationItem(currentPageNum, newItem);
  }
});

function addAnnotationItem(pageNum, item) {
  if (!annotationsData[pageNum]) annotationsData[pageNum] = [];
  annotationsData[pageNum].push(item);
  persistAnnotations();
  renderPageOverlays(pageNum);
  updateAudioDeckOptions();
}

function removeAnnotationItem(pageNum, id) {
  if (!annotationsData[pageNum]) return;
  annotationsData[pageNum] = annotationsData[pageNum].filter(item => item.id !== id);
  persistAnnotations();
  renderPageOverlays(pageNum);
  updateAudioDeckOptions();
}

// 7. Audio Settings Inspector Modal
function openAudioModal(item) {
  editingPin = item;

  // Populate Unit Selector (1 to 48)
  modalUnitSelect.innerHTML = '';
  for (let u = 1; u <= 48; u++) {
    const opt = document.createElement('option');
    opt.value = String(u);
    opt.textContent = `Unit ${u}`;
    if (String(u) === String(item.unit || getUnitForPage(currentPageNum))) {
      opt.selected = true;
    }
    modalUnitSelect.appendChild(opt);
  }

  modalPinLabel.value = item.label || '';
  modalIconStyle.value = item.iconStyle || 'headphones';
  modalPinColor.value = item.color || 'cyan';
  modalTrackFilter.value = '';

  updateModalTrackDropdown();
  audioModalBackdrop.classList.remove('hidden');
}

function closeAudioModal() {
  if (modalAudioPreview) {
    modalAudioPreview.pause();
    modalAudioPreview = null;
  }
  modalPreviewBtn.innerHTML = `<i class="fa-solid fa-play"></i> Preview`;
  audioModalBackdrop.classList.add('hidden');
  editingPin = null;
}

function updateModalTrackDropdown() {
  const unit = modalUnitSelect.value;
  const filter = modalTrackFilter.value.trim().toLowerCase();
  modalTrackSelect.innerHTML = '';

  const files = audioIndex[unit] || [];
  let matchingFiles = files;

  if (filter) {
    matchingFiles = files.filter(f => f.toLowerCase().includes(filter));
  }

  if (matchingFiles.length === 0) {
    const opt = document.createElement('option');
    opt.value = '';
    opt.textContent = 'No matching audio files in this unit';
    modalTrackSelect.appendChild(opt);
    modalTrackSelect.disabled = true;
  } else {
    modalTrackSelect.disabled = false;
    matchingFiles.forEach(file => {
      const opt = document.createElement('option');
      opt.value = file;
      opt.textContent = file;
      if (editingPin && editingPin.audioFile === file) {
        opt.selected = true;
      }
      modalTrackSelect.appendChild(opt);
    });
  }
}

// Modal Event Listeners
modalUnitSelect.addEventListener('change', updateModalTrackDropdown);
modalTrackFilter.addEventListener('input', updateModalTrackDropdown);

modalPreviewBtn.addEventListener('click', () => {
  const unit = modalUnitSelect.value;
  const file = modalTrackSelect.value;
  if (!file) return;

  if (modalAudioPreview && !modalAudioPreview.paused) {
    modalAudioPreview.pause();
    modalAudioPreview = null;
    modalPreviewBtn.innerHTML = `<i class="fa-solid fa-play"></i> Preview`;
    return;
  }

  const audioPath = `audio/${unit}/${file}`;
  modalAudioPreview = new Audio(audioPath);
  modalAudioPreview.play().then(() => {
    modalPreviewBtn.innerHTML = `<i class="fa-solid fa-pause"></i> Playing...`;
  }).catch(err => {
    alert(`Could not load audio file: ${audioPath}`);
    modalPreviewBtn.innerHTML = `<i class="fa-solid fa-play"></i> Preview`;
  });

  modalAudioPreview.onended = () => {
    modalPreviewBtn.innerHTML = `<i class="fa-solid fa-play"></i> Preview`;
  };
});

modalSaveBtn.addEventListener('click', () => {
  if (!editingPin) return;

  editingPin.unit = modalUnitSelect.value;
  editingPin.audioFile = modalTrackSelect.value;
  editingPin.label = modalPinLabel.value.trim() || modalTrackSelect.value;
  editingPin.iconStyle = modalIconStyle.value;
  editingPin.color = modalPinColor.value;

  persistAnnotations();
  renderPageOverlays(currentPageNum);
  updateAudioDeckOptions();
  closeAudioModal();
});

modalDeleteBtn.addEventListener('click', () => {
  if (!editingPin) return;
  removeAnnotationItem(currentPageNum, editingPin.id);
  closeAudioModal();
});

modalCloseBtn.addEventListener('click', closeAudioModal);
modalCancelBtn.addEventListener('click', closeAudioModal);

// 8. Persistent Audio Deck Engine
function updateAudioDeckOptions() {
  const items = (annotationsData[currentPageNum] || []).filter(i => i.type === 'audio');
  audioTrackSelect.innerHTML = '';

  if (items.length === 0) {
    const opt = document.createElement('option');
    opt.value = '';
    opt.textContent = 'No audio pins placed on this page';
    audioTrackSelect.appendChild(opt);
    audioTrackSelect.disabled = true;
    audioPlayBtn.disabled = true;
    audioStopBtn.disabled = true;
    audioProgress.disabled = true;
  } else {
    audioTrackSelect.disabled = false;
    audioPlayBtn.disabled = false;
    audioStopBtn.disabled = false;
    audioProgress.disabled = false;

    items.forEach((pin, idx) => {
      const opt = document.createElement('option');
      opt.value = pin.id;
      opt.textContent = `${idx + 1}. ${pin.label || pin.audioFile || 'Audio Track'}`;
      audioTrackSelect.appendChild(opt);
    });
  }
}

function playAudioPinTrack(pin) {
  if (!pin || !pin.audioFile) {
    alert('Please assign an audio file to this pin in Studio Mode!');
    return;
  }

  const audioPath = `audio/${pin.unit}/${pin.audioFile}`;
  
  if (currentAudio && activeAudioPinId === pin.id) {
    if (!currentAudio.paused) {
      currentAudio.pause();
      updatePlayButtonUI(false);
      return;
    } else {
      currentAudio.play();
      updatePlayButtonUI(true);
      return;
    }
  }

  stopAudioTrack();

  activeAudioPinId = pin.id;
  audioTrackSelect.value = pin.id;

  const audio = new Audio(audioPath);
  currentAudio = audio;
  audio.playbackRate = playbackSpeed;
  audio.muted = isMuted;

  audio.addEventListener('loadedmetadata', () => {
    audioProgress.max = audio.duration;
    updateTimeDisplay(audio.currentTime, audio.duration);
  });

  audio.addEventListener('timeupdate', () => {
    audioProgress.value = audio.currentTime;
    updateTimeDisplay(audio.currentTime, audio.duration);
  });

  audio.addEventListener('ended', () => {
    stopAudioTrack();
  });

  audio.play().then(() => {
    updatePlayButtonUI(true);
    highlightActivePin(pin.id);
  }).catch(err => {
    console.error(`Failed to play track: ${audioPath}`, err);
    alert(`Could not play audio track: ${audioPath}`);
    stopAudioTrack();
  });
}

function highlightActivePin(pinId) {
  document.querySelectorAll('.audio-pin-wrapper').forEach(el => {
    if (el.dataset.id === pinId) {
      el.classList.add('active-playing');
    } else {
      el.classList.remove('active-playing');
    }
  });
}

function stopAudioTrack() {
  if (currentAudio) {
    currentAudio.pause();
    currentAudio.currentTime = 0;
    currentAudio = null;
  }
  activeAudioPinId = null;
  audioProgress.value = 0;
  audioTimeDisplay.textContent = '0:00 / 0:00';
  updatePlayButtonUI(false);
  highlightActivePin(null);
}

function updatePlayButtonUI(isPlaying) {
  if (isPlaying) {
    audioPlayBtn.innerHTML = `<i class="fa-solid fa-pause"></i>`;
    audioPlayBtn.classList.add('playing');
    audioPlayBtn.title = 'Pause Track';
  } else {
    audioPlayBtn.innerHTML = `<i class="fa-solid fa-play"></i>`;
    audioPlayBtn.classList.remove('playing');
    audioPlayBtn.title = 'Play Track';
  }
}

function updateTimeDisplay(current, duration) {
  if (isNaN(duration) || !duration) {
    audioTimeDisplay.textContent = formatTime(current) + ' / 0:00';
  } else {
    audioTimeDisplay.textContent = formatTime(current) + ' / ' + formatTime(duration);
  }
}

function formatTime(secs) {
  const m = Math.floor(secs / 60);
  const s = Math.floor(secs % 60);
  return `${m}:${s < 10 ? '0' : ''}${s}`;
}

// 9. Mode Switcher & Tools
function setupEventListeners() {
  pageSelect.addEventListener('change', (e) => loadPage(Number(e.target.value)));
  prevPageBtn.addEventListener('click', () => { if (currentPageNum > 1) loadPage(currentPageNum - 1); });
  nextPageBtn.addEventListener('click', () => { if (currentPageNum < 176) loadPage(currentPageNum + 1); });

  // Keyboard Arrows Page Navigation
  document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;
    if (e.key === 'ArrowLeft' && currentPageNum > 1) {
      loadPage(currentPageNum - 1);
    } else if (e.key === 'ArrowRight' && currentPageNum < 176) {
      loadPage(currentPageNum + 1);
    }
  });

  // Mode Switcher Button
  toggleModeBtn.addEventListener('click', () => {
    isStudioMode = !isStudioMode;
    if (isStudioMode) {
      toggleModeBtn.classList.add('active');
      modeBtnText.textContent = 'Exit Studio Mode';
      studioSubToolbar.classList.remove('hidden');
      bookCanvas.classList.add('studio-active');
      setActiveTool('select');
    } else {
      toggleModeBtn.classList.remove('active');
      modeBtnText.textContent = 'Authoring Studio';
      studioSubToolbar.classList.add('hidden');
      bookCanvas.classList.remove('studio-active');
    }
    renderPageOverlays(currentPageNum);
  });

  // Studio Tools Selection
  toolSelectBtn.addEventListener('click', () => setActiveTool('select'));
  toolAddAudioBtn.addEventListener('click', () => setActiveTool('add-audio'));
  toolAddTextBtn.addEventListener('click', () => setActiveTool('add-text'));

  // Clear Page Action
  clearPageBtn.addEventListener('click', () => {
    if (confirm(`Are you sure you want to clear all audio pins and text boxes on Page ${currentPageNum}?`)) {
      annotationsData[currentPageNum] = [];
      persistAnnotations();
      renderPageOverlays(currentPageNum);
      updateAudioDeckOptions();
    }
  });

  // Save Page Action
  savePageBtn.addEventListener('click', async () => {
    persistAnnotations();
    
    // Try sending to local save endpoint if available
    try {
      const res = await fetch('/api/save_annotations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(annotationsData)
      });
      if (res.ok) {
        alert(`✓ Page ${currentPageNum} annotations saved successfully to disk & local storage!`);
        return;
      }
    } catch (e) {
      // Local server not present, standard local storage save
    }
    alert(`✓ Page ${currentPageNum} annotations saved successfully to browser local memory!`);
  });

  // Export & Import JSON Actions
  exportJsonBtn.addEventListener('click', exportAnnotationsJson);
  importJsonBtn.addEventListener('click', () => importFileInput.click());
  importFileInput.addEventListener('change', importAnnotationsJson);

  // Audio Deck Player Controls
  audioPlayBtn.addEventListener('click', () => {
    const selectedId = audioTrackSelect.value;
    if (!selectedId) return;
    const items = annotationsData[currentPageNum] || [];
    const targetPin = items.find(i => i.id === selectedId);
    if (targetPin) playAudioPinTrack(targetPin);
  });

  audioStopBtn.addEventListener('click', stopAudioTrack);

  audioTrackSelect.addEventListener('change', () => {
    stopAudioTrack();
    const selectedId = audioTrackSelect.value;
    const items = annotationsData[currentPageNum] || [];
    const targetPin = items.find(i => i.id === selectedId);
    if (targetPin) playAudioPinTrack(targetPin);
  });

  audioProgress.addEventListener('input', (e) => {
    if (currentAudio) {
      currentAudio.currentTime = Number(e.target.value);
    }
  });

  audioSpeedBtn.addEventListener('click', () => {
    if (playbackSpeed === 1.0) playbackSpeed = 0.8;
    else if (playbackSpeed === 0.8) playbackSpeed = 1.2;
    else if (playbackSpeed === 1.2) playbackSpeed = 1.5;
    else playbackSpeed = 1.0;

    audioSpeedBtn.textContent = `${playbackSpeed.toFixed(1)}x`;
    if (currentAudio) {
      currentAudio.playbackRate = playbackSpeed;
    }
  });

  audioVolumeBtn.addEventListener('click', () => {
    isMuted = !isMuted;
    if (currentAudio) {
      currentAudio.muted = isMuted;
    }
    audioVolumeBtn.innerHTML = isMuted 
      ? `<i class="fa-solid fa-volume-xmark"></i>` 
      : `<i class="fa-solid fa-volume-high"></i>`;
  });
}

function setActiveTool(tool) {
  activeTool = tool;
  toolSelectBtn.classList.toggle('active', tool === 'select');
  toolAddAudioBtn.classList.toggle('active', tool === 'add-audio');
  toolAddTextBtn.classList.toggle('active', tool === 'add-text');

  bookCanvas.dataset.activeTool = tool;
}

// Export Annotations JSON
function exportAnnotationsJson() {
  const jsonStr = JSON.stringify(annotationsData, null, 2);
  const blob = new Blob([jsonStr], { type: 'application/json' });
  const url = URL.createObjectURL(blob);

  const a = document.createElement('a');
  a.href = url;
  a.download = `workbook_custom_annotations.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// Import Annotations JSON
function importAnnotationsJson(e) {
  const file = e.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (event) => {
    try {
      const data = JSON.parse(event.target.result);
      if (typeof data === 'object' && data !== null) {
        annotationsData = data;
        persistAnnotations();
        loadPage(currentPageNum);
        alert('✓ Custom annotations imported successfully!');
      } else {
        alert('Invalid JSON structure format.');
      }
    } catch (err) {
      alert('Error parsing uploaded JSON file: ' + err.message);
    }
  };
  reader.readAsText(file);
}

/* ==========================================================================
   Kodama Companion Mascot, Minimalist Pomodoro & Teacher Lewis Story Engine
   ========================================================================== */

const teacherLewisChapters = [
  {
    title: "Ch. 1: First Step",
    text: "📖 Chapter 1: Many years ago, Teacher Lewis fell in love with languages because he loved listening to Ghibli stories!"
  },
  {
    title: "Ch. 2: The Dream",
    text: "📖 Chapter 2: Teacher Lewis realized that speaking English opens doors to making friends all across the world!"
  },
  {
    title: "Ch. 3: The Secret",
    text: "📖 Chapter 3: Teacher Lewis discovered that practicing just 10 minutes out loud every day is 10x better than cramming!"
  },
  {
    title: "Ch. 4: Ghibli Music",
    text: "📖 Chapter 4: While teaching, Teacher Lewis always plays calm Ghibli piano songs so students feel relaxed and happy."
  },
  {
    title: "Ch. 5: Courage",
    text: "📖 Chapter 5: Teacher Lewis taught his students that mistakes aren't failures—they are proof of courage!"
  },
  {
    title: "Ch. 6: Mastery",
    text: "📖 Chapter 6: Today, Teacher Lewis is super proud of YOU for practicing English with focus and passion!"
  }
];

let currentStoryIndex = 0;
let pomoInterval = null;
let pomoTimeRemaining = 25 * 60;
let pomoTotalDuration = 25 * 60;
let pomoIsRunning = false;
let focusAutoFadeTimer = null;
let isMascotHovered = false;

function scheduleFocusAutoFade() {
  if (focusAutoFadeTimer) clearTimeout(focusAutoFadeTimer);
  if (!pomoIsRunning) return;

  focusAutoFadeTimer = setTimeout(() => {
    if (pomoIsRunning && !isMascotHovered) {
      const bubble = document.getElementById('mascotBubble');
      if (bubble) bubble.classList.add('focused-auto-collapsed');
    }
  }, 5000);
}

function revealMascotBubble() {
  const bubble = document.getElementById('mascotBubble');
  if (bubble) bubble.classList.remove('focused-auto-collapsed');
}

function setupMascot() {
  const avatarWrap = document.getElementById('mascotAvatarWrap');
  const pomoToggleBtn = document.getElementById('pomoToggleBtn');
  const pomoOptBtn = document.getElementById('pomoOptBtn');
  const presetsContainer = document.getElementById('pomoQuickPresets');
  const presetBtns = document.querySelectorAll('.pomo-quick-btn');
  const mascotWidget = document.getElementById('ghibliMascotWidget');

  if (mascotWidget) {
    mascotWidget.addEventListener('mouseenter', () => {
      isMascotHovered = true;
      if (focusAutoFadeTimer) clearTimeout(focusAutoFadeTimer);
      revealMascotBubble();
    });

    mascotWidget.addEventListener('mouseleave', () => {
      isMascotHovered = false;
      if (pomoIsRunning) {
        scheduleFocusAutoFade();
      }
    });
  }

  if (avatarWrap) {
    avatarWrap.addEventListener('click', () => {
      advanceTeacherLewisStory();
      triggerSparkle(window.innerWidth - 80, window.innerHeight - 80);
      playChimeSound(650, 0.12);
    });
  }

  if (pomoToggleBtn) {
    pomoToggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      if (pomoIsRunning) pausePomodoro();
      else startPomodoro();
    });
  }

  if (pomoOptBtn && presetsContainer) {
    pomoOptBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      presetsContainer.classList.toggle('hidden');
    });
  }

  presetBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      presetBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const mins = parseInt(btn.dataset.mins, 10);
      pomoTotalDuration = mins * 60;
      pomoTimeRemaining = pomoTotalDuration;
      updatePomoDisplay();
      if (presetsContainer) presetsContainer.classList.add('hidden');

      if (pomoIsRunning) pausePomodoro();
      speakMascot(`Timer set to ${mins}m! Press Play when ready.`);
      setMascotExpression('friendly');
    });
  });

  updateStoryChip();
}

function advanceTeacherLewisStory() {
  const chapter = teacherLewisChapters[currentStoryIndex];
  speakMascot(chapter.text);
  updateStoryChip();
  setMascotExpression('talking');
  currentStoryIndex = (currentStoryIndex + 1) % teacherLewisChapters.length;
}

function updateStoryChip() {
  const chapterLabel = document.getElementById('storyChapterLabel');
  if (chapterLabel) {
    chapterLabel.textContent = teacherLewisChapters[currentStoryIndex].title;
  }
}

/* Expressive Mascot Controller with Live Action Status */
function setMascotExpression(state, customAction = null) {
  const img = document.getElementById('mascotAvatarImg');
  const wrap = document.getElementById('mascotAvatarWrap');
  const badge = document.getElementById('mascotExprBadge');
  const actionChip = document.getElementById('mascotActionChip');

  if (!wrap) return;

  wrap.classList.remove('talking', 'celebrating', 'focus-mode', 'expr-sad', 'expr-celebrate');

  let actionText = customAction;

  if (state === 'talking') {
    if (img) img.src = 'images/ghibli/mascot_talking.jpg';
    wrap.classList.add('talking');
    if (badge) badge.textContent = '💬 Storyteller';
    if (!actionText) actionText = '📖 Narrating Teacher Lewis Story';
  } else if (state === 'focused') {
    if (img) img.src = 'images/ghibli/mascot_focused.jpg';
    wrap.classList.add('focus-mode');
    if (badge) badge.textContent = '🍅 Focused';
    if (!actionText) actionText = '🪑 Sitting Cozy & Studying With You';
  } else if (state === 'sad') {
    if (img) img.src = 'images/ghibli/mascot.jpg';
    wrap.classList.add('expr-sad');
    if (badge) badge.textContent = '💙 Gentle Comfort';
    if (!actionText) actionText = '🤗 Giving Encouragement & Comfort';
  } else if (state === 'celebrate') {
    if (img) img.src = 'images/ghibli/mascot.jpg';
    wrap.classList.add('celebrating', 'expr-celebrate');
    if (badge) badge.textContent = '🌟 Joyful!';
    if (!actionText) actionText = '🎉 Celebrating Great Progress!';
  } else {
    if (img) img.src = 'images/ghibli/mascot.jpg';
    if (badge) badge.textContent = '🐾 Sitting Cozy';
    if (!actionText) actionText = '🪑 Sitting Cozy & Ready to Study';
  }

  if (actionChip && actionText) {
    actionChip.innerHTML = `<i class="fa-solid fa-paw"></i> ${actionText}`;
  }
}

function startPomodoro() {
  if (pomoIsRunning) return;
  pomoIsRunning = true;

  revealMascotBubble();
  scheduleFocusAutoFade();

  const icon = document.getElementById('pomoIcon');
  if (icon) icon.className = 'fa-solid fa-pause';

  setMascotExpression('focused');
  playChimeSound(523.25, 0.2);
  speakMascot("🍅 Focus mode active! Let's study English together with Teacher Lewis.");

  pomoInterval = setInterval(() => {
    pomoTimeRemaining--;
    updatePomoDisplay();

    if (pomoTimeRemaining === Math.floor(pomoTotalDuration / 2) && pomoTimeRemaining > 10) {
      speakMascot("Halfway there! Keep going, Teacher Lewis is proud of your focus!");
      playChimeSound(659.25, 0.15);
    } else if (pomoTimeRemaining <= 0) {
      completePomodoroSession();
    }
  }, 1000);
}

function pausePomodoro() {
  pomoIsRunning = false;
  if (pomoInterval) clearInterval(pomoInterval);
  if (focusAutoFadeTimer) clearTimeout(focusAutoFadeTimer);
  revealMascotBubble();

  const icon = document.getElementById('pomoIcon');
  if (icon) icon.className = 'fa-solid fa-play';

  setMascotExpression('friendly');
  speakMascot("Timer paused. Take a deep breath and resume whenever you are ready!");
}

function completePomodoroSession() {
  pausePomodoro();
  setMascotExpression('celebrate');
  playFanfareChime();
  speakMascot("🎉 FOCUS SESSION COMPLETE! Teacher Lewis says: Outstanding work!");
  advanceTeacherLewisStory();
}

function updatePomoDisplay() {
  const display = document.getElementById('pomoMinTime');
  if (display) {
    const mins = Math.floor(pomoTimeRemaining / 60);
    const secs = pomoTimeRemaining % 60;
    display.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
}

function playChimeSound(freq = 523.25, duration = 0.2) {
  if (window.GhibliAudio) {
    window.GhibliAudio.playChime(freq, duration);
  }
}

function playFanfareChime() {
  if (window.GhibliAudio) {
    window.GhibliAudio.playFanfare();
  }
}

function speakMascot(text) {
  const textEl = document.getElementById('mascotTextContent');
  
  revealMascotBubble();
  if (pomoIsRunning) {
    scheduleFocusAutoFade();
  }

  if (textEl) textEl.textContent = `"${text}"`;
}

function triggerSparkle(x, y) {
  for (let i = 0; i < 6; i++) {
    const sparkle = document.createElement('div');
    sparkle.className = 'sparkle';
    sparkle.style.left = `${x + (Math.random() - 0.5) * 60}px`;
    sparkle.style.top = `${y + (Math.random() - 0.5) * 60}px`;
    document.body.appendChild(sparkle);
    setTimeout(() => sparkle.remove(), 600);
  }
}

// Start Application on Load
document.addEventListener('DOMContentLoaded', initWorkbook);
