/* ==========================================================================
   Studio Ghibli Edition - Page 12 Interactive Workbook Logic (v2.2)
   Fixes: Exact Textbook Answer Order for Ex 1.2 (Rachel=1, Carl=2, Peter=3, Simone=4, Terry=5, Jo=6)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  initGhibliPage12();
});

let activeAudio = null;
let currentPlaylistIndex = 0;
let isPlayingPlaylist = false;

/* Voice Recording Store */
const recordedBlobs = {};
let mediaRecorder = null;
let activeRecordingId = null;

/* Ambient Soundscape State (Ghibli Piano Song Engine) */
let isAmbientPlaying = false;
let ambientAudioCtx = null;
let ambientTimer = null;

function initGhibliPage12() {
  setupTimeOfDay();
  setupAudioPlayers();
  setupVoiceRecorder();
  setupDragAndDropEx1_2();
  setupExercise1_1();
  setupExercise1_3();
  setupMascot();
  setupAmbientSoundscape();
  setupHeaderActions();
}

/* 1. Time-of-Day System */
function setupTimeOfDay() {
  const todBtns = document.querySelectorAll('.tod-btn');
  const firefliesContainer = document.getElementById('firefliesContainer');

  todBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      todBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const theme = btn.dataset.theme;
      document.body.className = `theme-${theme}`;

      if (theme === 'night') {
        spawnFireflies(18);
        speakMascot("Nighttime in the Ghibli forest... Listen to the fireflies!");
      } else {
        if (firefliesContainer) firefliesContainer.innerHTML = '';
        if (theme === 'sunset') {
          speakMascot("A warm Ghibli sunset... Perfect for studying!");
        } else {
          speakMascot("Good day! Let's practice English together.");
        }
      }
    });
  });
}

function spawnFireflies(count) {
  const container = document.getElementById('firefliesContainer');
  if (!container) return;
  container.innerHTML = '';
  for (let i = 0; i < count; i++) {
    const firefly = document.createElement('div');
    firefly.className = 'firefly';
    firefly.style.left = `${Math.random() * 100}vw`;
    firefly.style.top = `${Math.random() * 100}vh`;
    firefly.style.animationDelay = `${Math.random() * 5}s`;
    container.appendChild(firefly);
  }
}

/* 2. Audio Player Engine with Fallback & Speech Synthesis */
function playAudioTrack(src, fallbackText = null, onEndedCallback = null) {
  if (activeAudio) {
    activeAudio.pause();
    activeAudio.currentTime = 0;
    activeAudio = null;
  }

  const paths = [src];
  if (src.startsWith('audio/1/')) {
    const filename = src.split('/').pop();
    paths.push(`assets/audio/track_01_${filename}`);
  }

  let attemptIdx = 0;

  function tryNextPath() {
    if (attemptIdx >= paths.length) {
      if (fallbackText) {
        speakSentence(fallbackText, onEndedCallback);
      } else if (onEndedCallback) {
        onEndedCallback();
      }
      return;
    }

    const currentPath = paths[attemptIdx++];
    const audio = new Audio(currentPath);
    activeAudio = audio;

    audio.play().then(() => {
      if (onEndedCallback) {
        audio.onended = onEndedCallback;
      }
    }).catch(err => {
      console.warn(`Could not play ${currentPath}, trying fallback...`, err);
      tryNextPath();
    });
  }

  tryNextPath();
}

function setupAudioPlayers() {
  document.querySelectorAll('.ghibli-audio-play-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      isPlayingPlaylist = false;
      const audioFile = btn.dataset.audio;
      const card = btn.closest('.ghibli-listen-card') || btn.closest('.ghibli-char-card') || btn.closest('.ghibli-draggable-card');
      const name = card ? (card.querySelector('.ghibli-listen-name')?.textContent || card.querySelector('.ghibli-prompt-text span')?.textContent || card.querySelector('span')?.textContent) : '';
      const fallback = name ? `Hi, I am ${name}.` : null;

      if (audioFile) {
        playAudioTrack(audioFile, fallback);
        triggerSparkle(e.clientX, e.clientY);
      }
    });
  });
}

/* 3. Voice Recorder Engine */
function setupVoiceRecorder() {
  const getSupportedMimeType = () => {
    if (typeof MediaRecorder === 'undefined' || !MediaRecorder.isTypeSupported) return '';
    const types = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/aac', 'audio/ogg'];
    for (const t of types) { if (MediaRecorder.isTypeSupported(t)) return t; }
    return '';
  };

  const getCardInfo = (btn) => {
    const card = btn.closest('.animal-card, .ghibli-char-card, .ghibli-listen-card, .ghibli-card-body, section, div');
    let text = '';
    let audioPath = '';
    if (card) {
      const audioBtn = card.querySelector('[data-audio]');
      if (audioBtn) audioPath = audioBtn.getAttribute('data-audio') || '';
      const input = card.querySelector('input[data-correct], input[type="text"]');
      if (input) text = input.value || input.getAttribute('data-correct') || input.placeholder || '';
      if (!text) { const img = card.querySelector('img[alt]'); if (img) text = img.getAttribute('alt') || ''; }
      if (!text) { const p = card.querySelector('.ghibli-prompt-text, p, span'); if (p) text = p.textContent || ''; }
    }
    return { text: text.trim() || 'English Practice', audioPath };
  };

  document.querySelectorAll('.rec-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = btn.dataset.id || btn.getAttribute('data-for') || 'default_rec';
      const isRecording = activeRecordingId === id || btn.classList.contains('recording');

      const revealPlayBtn = () => {
        const playBtn = document.querySelector(`.play-rec-btn[data-id="${id}"]`) || btn.parentNode.querySelector('.play-rec-btn');
        if (playBtn) {
          playBtn.classList.remove('hidden');
          playBtn.style.display = 'inline-flex';
          playBtn.classList.add('has-voice');
        }
      };

      if (!isRecording) {
        activeRecordingId = id;
        btn.classList.add('recording');
        btn.innerHTML = `<i class="fa-solid fa-square-stop"></i> Stop`;

        let stream = null;
        const mimeType = getSupportedMimeType();

        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia && typeof MediaRecorder !== 'undefined') {
          try { stream = await navigator.mediaDevices.getUserMedia({ audio: true }); }
          catch (err) { console.warn("Microphone access unavailable or denied:", err); }
        }

        if (stream) {
          try {
            const chunks = [];
            const opts = mimeType ? { mimeType } : {};
            mediaRecorder = new MediaRecorder(stream, opts);
            mediaRecorder.ondataavailable = (e) => { if (e.data && e.data.size > 0) chunks.push(e.data); };
            mediaRecorder.onstop = () => {
              const finalMime = mimeType || mediaRecorder.mimeType || 'audio/webm';
              const blob = new Blob(chunks, { type: finalMime });
              recordedBlobs[id] = URL.createObjectURL(blob);
              stream.getTracks().forEach(t => t.stop());
              revealPlayBtn();
            };
            mediaRecorder.start();
            speakMascot("Recording... Speak your sentence out loud!");
            return;
          } catch (err) {
            if (stream) stream.getTracks().forEach(t => t.stop());
          }
        }

        // Fallback Practice Mode
        const info = getCardInfo(btn);
        recordedBlobs[id] = info;
        speakMascot(`Voice Practice active for "${info.text}"! Click 'Stop' when done.`);
      } else {
        activeRecordingId = null;
        btn.classList.remove('recording');
        btn.innerHTML = `<i class="fa-solid fa-microphone"></i> Rec`;

        if (mediaRecorder && mediaRecorder.state && mediaRecorder.state !== 'inactive') {
          mediaRecorder.stop();
        } else {
          revealPlayBtn();
        }
        speakMascot("Voice recorded! Click 'My Voice' to listen back.");
      }
    });
  });

  document.querySelectorAll('.play-rec-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.id;
      const recData = recordedBlobs[id];
      if (recData) {
        if (typeof recData === 'string' && (recData.startsWith('blob:') || recData.startsWith('data:') || recData.startsWith('audio/'))) {
          const audio = new Audio(recData);
          audio.play();
        } else {
          const info = typeof recData === 'object' ? recData : { text: recData };
          if (info.audioPath) {
            playAudioTrack(info.audioPath);
          } else if (info.text && window.speechSynthesis) {
            window.speechSynthesis.cancel();
            const u = new SpeechSynthesisUtterance(info.text);
            u.lang = 'en-US';
            window.speechSynthesis.speak(u);
          }
        }
        triggerSparkle(window.innerWidth / 2, window.innerHeight / 2);
      }
    });
  });
}

/* 4. Drag and Drop Engine for Exercise 1.2 (Exact Textbook Key Alignment)
   Correct Order:
   Slot 1: Rachel (A)
   Slot 2: Carl (D)
   Slot 3: Peter (B)
   Slot 4: Simone (F)
   Slot 5: Terry (E)
   Slot 6: Jo (C)
*/
const answers1_2 = {
  rachel: 1,
  carl: 2,
  peter: 3,
  simone: 4,
  terry: 5,
  jo: 6
};

const ex1_2_playlist = [
  { person: 'rachel', file: 'audio/1/1_2_1.mp3', text: "Number 1. Hi, I'm Rachel." },
  { person: 'carl', file: 'audio/1/1_2_4.mp3', text: "Number 2. My name's Carl." },
  { person: 'peter', file: 'audio/1/1_2_2.mp3', text: "Number 3. Hello, my name's Peter." },
  { person: 'simone', file: 'audio/1/1_2_6.mp3', text: "Number 4. Hi, my name's Simone." },
  { person: 'terry', file: 'audio/1/1_2_5.mp3', text: "Number 5. Hello, I'm Terry." },
  { person: 'jo', file: 'audio/1/1_2_3.mp3', text: "Number 6. Hi, I'm Jo." }
];

function setupDragAndDropEx1_2() {
  const cards = document.querySelectorAll('.ghibli-draggable-card');
  const slots = document.querySelectorAll('.ghibli-drop-slot');
  const pool = document.getElementById('speakerPool');

  let draggedCard = null;

  cards.forEach(card => {
    card.addEventListener('dragstart', (e) => {
      draggedCard = card;
      card.classList.add('is-dragging');
      e.dataTransfer.setData('text/plain', card.dataset.person);
    });

    card.addEventListener('dragend', () => {
      draggedCard = null;
      cards.forEach(c => c.classList.remove('is-dragging'));
    });
  });

  slots.forEach(slot => {
    slot.addEventListener('dragover', (e) => {
      e.preventDefault();
      slot.classList.add('drag-over');
    });

    slot.addEventListener('dragleave', () => {
      slot.classList.remove('drag-over');
    });

    slot.addEventListener('drop', (e) => {
      e.preventDefault();
      slot.classList.remove('drag-over');

      if (draggedCard) {
        const existing = slot.querySelector('.ghibli-draggable-card');
        if (existing) {
          pool.appendChild(existing);
        }

        slot.appendChild(draggedCard);
        speakMascot(`Placed ${draggedCard.dataset.person.toUpperCase()} into Slot ${slot.dataset.slot}!`);
      }
    });
  });

  const fullAudioBtn = document.getElementById('playFullEx1_2Btn');
  if (fullAudioBtn) {
    fullAudioBtn.addEventListener('click', () => {
      if (isPlayingPlaylist) {
        isPlayingPlaylist = false;
        if (activeAudio) activeAudio.pause();
        fullAudioBtn.innerHTML = `<i class="fa-solid fa-headphones"></i> Play Full Exercise 1.2 Audio`;
        return;
      }

      isPlayingPlaylist = true;
      currentPlaylistIndex = 0;
      fullAudioBtn.innerHTML = `<i class="fa-solid fa-square-stop"></i> Stop Audio`;
      playNextPlaylistItem();
    });
  }
}

function playNextPlaylistItem() {
  const fullAudioBtn = document.getElementById('playFullEx1_2Btn');
  if (!isPlayingPlaylist || currentPlaylistIndex >= ex1_2_playlist.length) {
    isPlayingPlaylist = false;
    if (fullAudioBtn) {
      fullAudioBtn.innerHTML = `<i class="fa-solid fa-headphones"></i> Play Full Exercise 1.2 Audio`;
    }
    document.querySelectorAll('.ghibli-draggable-card').forEach(c => c.style.borderColor = '');
    return;
  }

  const item = ex1_2_playlist[currentPlaylistIndex];
  
  document.querySelectorAll('.ghibli-draggable-card').forEach(card => {
    if (card.dataset.person === item.person) {
      card.style.borderColor = 'var(--ghibli-accent-amber)';
      card.style.boxShadow = '0 0 15px rgba(217, 119, 36, 0.4)';
    } else {
      card.style.borderColor = '';
      card.style.boxShadow = '';
    }
  });

  currentPlaylistIndex++;
  playAudioTrack(item.file, item.text, () => {
    setTimeout(playNextPlaylistItem, 600);
  });
}

/* 5. Exercise 1.1 & 1.3 Setup */
const answers1_1 = {
  1: "I'm Natalie.",
  2: "My name's Sue.",
  3: "I'm Ryan.",
  4: "My name's Mia.",
  5: "My name's Amelia."
};

function setupExercise1_1() {
  document.querySelectorAll('.ex1-1-input').forEach(input => {
    input.addEventListener('input', () => {
      input.classList.remove('correct', 'incorrect');
    });
  });
}

let selectedBlocks = {
  greeting: 'Hi!',
  subject: 'I',
  verb: 'am',
  name: 'Charlotte.'
};

function setupExercise1_3() {
  const columns = ['greeting', 'subject', 'verb', 'name'];

  columns.forEach(colKey => {
    const colBtns = document.querySelectorAll(`.ghibli-block-btn[data-col="${colKey}"]`);
    colBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        colBtns.forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        selectedBlocks[colKey] = btn.dataset.value;
        updateAssembledGreeting();
      });
    });
  });

  const playGreetingBtn = document.getElementById('playGreetingBtn');
  if (playGreetingBtn) {
    playGreetingBtn.addEventListener('click', () => {
      const sentence = `${selectedBlocks.greeting} ${selectedBlocks.subject} ${selectedBlocks.verb} ${selectedBlocks.name}`;
      playAudioTrack('audio/1/1_3_a.mp3', sentence);
      speakMascot(`Formed: "${sentence}"`);
    });
  }
}

function updateAssembledGreeting() {
  const displayEl = document.getElementById('assembledGreetingText');
  if (displayEl) {
    displayEl.textContent = `"${selectedBlocks.greeting} ${selectedBlocks.subject} ${selectedBlocks.verb} ${selectedBlocks.name}"`;
  }
}

function speakSentence(text, onEnded = null) {
  if ('speechSynthesis' in window) {
    const synth = window.speechSynthesis;
    synth.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    if (onEnded) utterance.onend = onEnded;
    synth.speak(utterance);
  } else if (onEnded) {
    onEnded();
  }
}

/* ==========================================================================
   6. Kodama Companion Mascot, Minimalist Pomodoro & Teacher Lewis Story Engine
   ========================================================================== */

/* 6A. Teacher Lewis Progressive Story Chapters */
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

/* 6B. Pomodoro Minimalist State */
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

  // Avatar Click Action -> Tell next chapter of Teacher Lewis story!
  if (avatarWrap) {
    avatarWrap.addEventListener('click', () => {
      advanceTeacherLewisStory();
      triggerSparkle(window.innerWidth - 80, window.innerHeight - 80);
      playChimeSound(650, 0.12);
    });
  }

  // Minimalist Pomodoro Play/Pause Toggle
  if (pomoToggleBtn) {
    pomoToggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      if (pomoIsRunning) {
        pausePomodoro();
      } else {
        startPomodoro();
      }
    });
  }

  // Timer Presets Toggle Dropdown
  if (pomoOptBtn && presetsContainer) {
    pomoOptBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      presetsContainer.classList.toggle('hidden');
    });
  }

  // Preset Buttons Selection
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

  // Display initial story chapter
  updateStoryChip();
}

function advanceTeacherLewisStory() {
  const chapter = teacherLewisChapters[currentStoryIndex];
  speakMascot(chapter.text);
  updateStoryChip();
  setMascotExpression('talking');

  // Loop or advance chapter index
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

/* Minimalist Pomodoro Controls */
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

/* 7. Ghibli Looping Chill Soundtrack Player */
let bgSongAudio = null;

function setupAmbientSoundscape() {
  const toggleBtn = document.getElementById('toggleAmbientBtn');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      if (window.GhibliAudio && window.GhibliAudio.toggleBGM) {
        window.GhibliAudio.toggleBGM(toggleBtn);
        if (window.GhibliAudio.isBGMPlaying()) {
          speakMascot("Playing chill Studio Ghibli piano song...");
        }
      }
    });
    if (window.GhibliAudio && window.GhibliAudio.syncBGMButtonState) {
      window.GhibliAudio.syncBGMButtonState();
    }
  }
}

function startGhibliSongLoop() {
  if (window.GhibliAudio && window.GhibliAudio.playBGM) {
    window.GhibliAudio.playBGM();
  }
}

function stopGhibliSongLoop() {
  if (window.GhibliAudio && window.GhibliAudio.pauseBGM) {
    window.GhibliAudio.pauseBGM();
  }
}

/* 8. Header & Global Grade Actions with Progressive Story & Sad/Encouraging Mascot Response */
function setupHeaderActions() {
  const checkBtn = document.getElementById('ghibliCheckAnswersBtn');
  const resetBtn = document.getElementById('ghibliResetBtn');
  const scoreText = document.getElementById('ghibliScoreText');

  if (checkBtn) {
    checkBtn.addEventListener('click', () => {
      let correctCount = 0;
      let totalQuestions = 5 + 6;

      // Check Ex 1.1
      Object.keys(answers1_1).forEach(id => {
        const input = document.getElementById(`ex1_1_input_${id}`);
        if (input) {
          const userVal = input.value.trim();
          const expectedVal = answers1_1[id];

          const cleanUser = userVal.replace(/’/g, "'").toLowerCase();
          const cleanExpected = expectedVal.replace(/’/g, "'").toLowerCase();

          if (cleanUser === cleanExpected) {
            input.classList.add('correct');
            input.classList.remove('incorrect');
            correctCount++;
          } else if (cleanUser !== '') {
            input.classList.add('incorrect');
            input.classList.remove('correct');
          }
        }
      });

      // Check Ex 1.2 Drag & Drop Slots
      document.querySelectorAll('.ghibli-drop-slot').forEach(slot => {
        const slotNum = parseInt(slot.dataset.slot);
        const card = slot.querySelector('.ghibli-draggable-card');

        if (card) {
          const person = card.dataset.person;
          const expectedOrder = answers1_2[person];

          if (slotNum === expectedOrder) {
            card.classList.add('correct');
            card.classList.remove('incorrect');
            correctCount++;
          } else {
            card.classList.add('incorrect');
            card.classList.remove('correct');
          }
        }
      });

      if (scoreText) {
        scoreText.textContent = `${correctCount} / ${totalQuestions}`;
      }

      if (correctCount === totalQuestions) {
        setMascotExpression('celebrate');
        playFanfareChime();
        speakMascot("100% PERFECT SCORE! 🌟 Teacher Lewis awards you the Traveler's Backpack Sticker & Spirit Name Tag!");
        unlockUnit1Stickers(true);
      } else if (correctCount > 0) {
        setMascotExpression('talking');
        speakMascot(`Great effort! You scored ${correctCount} / ${totalQuestions}! Score 100% (11/11) to unlock Teacher Lewis's Traveler's Backpack sticker!`);
        unlockUnit1Stickers(false);
      } else {
        // Incorrect / 0 score -> Mascot shows sad/encouraging state!
        setMascotExpression('sad');
        speakMascot("Don't worry! Teacher Lewis says: Mistakes are just proof you are trying! Give it another shot!");
      }

      triggerSparkle(window.innerWidth / 2, window.innerHeight / 3);
    });
  }

  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      document.querySelectorAll('.ghibli-input').forEach(i => {
        i.value = '';
        i.classList.remove('correct', 'incorrect');
      });
      
      const pool = document.getElementById('speakerPool');
      document.querySelectorAll('.ghibli-draggable-card').forEach(c => {
        c.classList.remove('correct', 'incorrect');
        if (pool) pool.appendChild(c);
      });

      if (scoreText) scoreText.textContent = `0 / 11`;
      setMascotExpression('friendly');
      speakMascot("Page reset! Ready for a fresh start on your story journey!");
    });
  }
}

/* Sparkle Particle Generator */
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

function unlockUnit1Stickers(isPerfectScore) {
  if (window.TeacherLewisAPI && window.TeacherLewisAPI.unlockSticker) {
    window.TeacherLewisAPI.unlockSticker('sticker-2'); // Spirit Name Tag
    if (isPerfectScore) {
      window.TeacherLewisAPI.unlockSticker('sticker-1'); // Traveler's Backpack (100% ONLY!)
    }
  } else {
    try {
      const inv = JSON.parse(localStorage.getItem('teacher_lewis_inventory') || '{}');
      inv['sticker-2'] = true;
      if (isPerfectScore) {
        inv['sticker-1'] = true;
      }
      localStorage.setItem('teacher_lewis_inventory', JSON.stringify(inv));
    } catch(e) {}
  }
}

