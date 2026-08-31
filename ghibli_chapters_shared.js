/* ==========================================================================
   Ghibli Chapters Shared JS — Works for Ch2-Ch9
   Provides: Time-of-day, audio, mascot, voice recorder, pomodoro
   Usage: <script src="ghibli_chapters_shared.js" data-chapter="2"></script>
   ========================================================================== */

(function() {
  'use strict';

  // Get chapter number from script data attribute or default to 2
  const currentScript = document.currentScript;
  const CHAPTER = currentScript ? (parseInt(currentScript.getAttribute('data-chapter')) || 2) : 2;
  const MASCOT_BASE = `images/ghibli/ch${CHAPTER}/`;

  /* ----------------------------------------------------------------
     State Variables
  ---------------------------------------------------------------- */
  let activeAudio = null;
  let isAmbientPlaying = false;
  let bgSongAudio = null;
  let mediaRecorder = null;
  let activeRecordingId = null;
  const recordedBlobs = {};
  let pomoInterval = null;
  let pomoTimeRemaining = 25 * 60;
  let pomoTotalDuration = 25 * 60;
  let pomoIsRunning = false;
  let focusAutoFadeTimer = null;
  let isMascotHovered = false;
  let currentStoryIndex = 0;

  const teacherLewisChapters = [
    { title: "Ch. 1: Origins", text: "📖 Chapter 1: Teacher Lewis grew up in a small village surrounded by forests, where he first fell in love with languages and storytelling." },
    { title: "Ch. 2: The Journey", text: "📖 Chapter 2: As a young man, Teacher Lewis traveled to many countries, learning English by talking to locals and making many wonderful friends." },
    { title: "Ch. 3: The Discovery", text: "📖 Chapter 3: Teacher Lewis discovered that speaking out loud every day for just 10 minutes is 10x more effective than silent reading." },
    { title: "Ch. 4: Ghibli Music", text: "📖 Chapter 4: Teacher Lewis always plays calm Studio Ghibli piano music while teaching — the melody helps students focus and feel at peace." },
    { title: "Ch. 5: Courage", text: "📖 Chapter 5: Teacher Lewis taught his students: 'Mistakes are not failures — they are proof of courage and the seeds of mastery!'" },
    { title: "Ch. 6: The Village", text: "📖 Chapter 6: Teacher Lewis once taught English to an entire fishing village in one summer — just using songs, stories and laughter." },
    { title: "Ch. 7: Mastery", text: "📖 Chapter 7: Today, Teacher Lewis is incredibly proud of YOU for practicing English with focus, heart and passion. Keep going!" }
  ];

  /* ----------------------------------------------------------------
     Audio Engine
  ---------------------------------------------------------------- */
  function getAudioCandidates(src) {
    if (!src) return [];
    const list = [];
    const cleanSrc = src.trim().split('?')[0].split('#')[0];
    if (!cleanSrc) return [];

    list.push(cleanSrc);

    const m1 = cleanSrc.match(/^audio\/(\d+)\/(.+)$/i);
    if (m1) {
      const unitNum = parseInt(m1[1], 10);
      const filename = m1[2];
      const unitPadded = String(unitNum).padStart(2, '0');
      list.push(`assets/audio/track_${unitPadded}_${filename}`);
      list.push(`assets/audio/track_${unitNum}_${filename}`);
      list.push(`assets/audio/${filename}`);

      const mUnitPrefix = filename.match(/^(\d+)_(.+)$/);
      if (mUnitPrefix) {
        const rest = mUnitPrefix[2];
        list.push(`assets/audio/track_${unitPadded}_${rest}`);
        list.push(`assets/audio/track_${unitNum}_${rest}`);
      }

      const baseName = filename.replace(/\.mp3$/i, '');
      list.push(`audio/${unitNum}/${baseName}_a_usuk.mp3`);
      list.push(`audio/${unitNum}/${baseName}_usuk.mp3`);
      list.push(`audio/${unitNum}/${baseName}_uk.mp3`);
      list.push(`audio/${unitNum}/${baseName}_us.mp3`);
      list.push(`audio/${unitNum}/${baseName}_a.mp3`);
    }

    const m2 = cleanSrc.match(/^assets\/audio\/track_(\d+)_(.+)\.mp3$/i);
    if (m2) {
      const unitNum = parseInt(m2[1], 10);
      const rest = m2[2];
      list.push(`audio/${unitNum}/${unitNum}_${rest}.mp3`);
      list.push(`audio/${unitNum}/${rest}.mp3`);
    }

    return Array.from(new Set(list));
  }

  function fallbackSpeechSynthesis(text, onEndedCallback) {
    if (!window.speechSynthesis || typeof SpeechSynthesisUtterance === 'undefined') {
      if (onEndedCallback) onEndedCallback();
      return;
    }
    const cleanText = String(text || '').replace(/<[^>]*>/g, ' ').replace(/[{}\[\]\(\)]/g, ' ').replace(/\s+/g, ' ').trim();
    if (!cleanText) {
      if (onEndedCallback) onEndedCallback();
      return;
    }
    try {
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(cleanText);
      u.lang = 'en-US';
      u.rate = 0.92;
      u.onend = () => { if (onEndedCallback) onEndedCallback(); };
      u.onerror = () => { if (onEndedCallback) onEndedCallback(); };
      window.speechSynthesis.speak(u);
    } catch (e) {
      if (onEndedCallback) onEndedCallback();
    }
  }

  function playAudioTrack(src, fallbackText = null, onEndedCallback = null) {
    if (activeAudio) { activeAudio.pause(); activeAudio.currentTime = 0; activeAudio = null; }
    if (window.speechSynthesis && window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
    }

    const done = () => {
      activeAudio = null;
      if (window.GhibliAudio && typeof window.GhibliAudio.unduckBGM === 'function') {
        window.GhibliAudio.unduckBGM();
      }
      if (onEndedCallback) onEndedCallback();
    };

    if (window.GhibliAudio && typeof window.GhibliAudio.duckBGM === 'function') {
      window.GhibliAudio.duckBGM();
    }

    const candidates = getAudioCandidates(src);
    let candidateIndex = 0;

    const tryNext = () => {
      if (candidateIndex >= candidates.length) {
        if (fallbackText) {
          fallbackSpeechSynthesis(fallbackText, done);
        } else {
          done();
        }
        return;
      }

      const currentSrc = candidates[candidateIndex++];
      const audio = new Audio();
      audio.preload = 'auto';
      activeAudio = audio;

      let hasHandledError = false;
      const onError = () => {
        if (hasHandledError) return;
        hasHandledError = true;
        tryNext();
      };

      audio.onended = done;
      audio.onerror = onError;
      audio.src = currentSrc;

      const playPromise = audio.play();
      if (playPromise !== undefined) {
        playPromise.catch(() => {
          onError();
        });
      }
    };

    if (candidates.length > 0) {
      tryNext();
    } else if (fallbackText) {
      fallbackSpeechSynthesis(fallbackText, done);
    } else {
      done();
    }
  }

  function setupAudioPlayers() {
    document.querySelectorAll('.ghibli-audio-play-btn, .ghibli-audio-btn, [data-audio]').forEach(btn => {
      btn.addEventListener('click', e => {
        e.stopPropagation();
        if (btn.classList.contains('rec-btn') || btn.classList.contains('play-rec-btn')) return;
        const src = btn.dataset.audio || btn.getAttribute('data-audio');
        const fallbackText = btn.getAttribute('data-fallback-text') || btn.getAttribute('data-text') || btn.closest('.ghibli-char-card, .exercise-card, section')?.textContent;
        const icon = btn.querySelector('i');
        const originalClass = icon ? icon.className : '';
        if (icon) icon.className = 'fa-solid fa-volume-high fa-beat';
        playAudioTrack(src, fallbackText, () => {
          if (icon && originalClass) icon.className = originalClass;
        });
        if (typeof speakMascot === 'function') {
          speakMascot("Listen carefully and repeat out loud! 🎧");
        }
      });
    });
  }

  /* ----------------------------------------------------------------
     Voice Recorder
  ---------------------------------------------------------------- */
  /* ----------------------------------------------------------------
     Voice Recorder
  ---------------------------------------------------------------- */
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
          btn.innerHTML = '<i class="fa-solid fa-circle" style="color:#ef4444;"></i> Stop';
          btn.style.background = 'rgba(239,68,68,0.2)';

          let stream = null;
          const mimeType = getSupportedMimeType();

          if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia && typeof MediaRecorder !== 'undefined') {
            try { stream = await navigator.mediaDevices.getUserMedia({ audio: true }); }
            catch(e) { console.warn('Microphone access restricted:', e); }
          }

          if (stream) {
            try {
              const chunks = [];
              const opts = mimeType ? { mimeType } : {};
              mediaRecorder = new MediaRecorder(stream, opts);
              mediaRecorder.ondataavailable = e => { if (e.data && e.data.size > 0) chunks.push(e.data); };
              mediaRecorder.onstop = () => {
                const finalMime = mimeType || mediaRecorder.mimeType || 'audio/webm';
                const blob = new Blob(chunks, { type: finalMime });
                recordedBlobs[id] = URL.createObjectURL(blob);
                stream.getTracks().forEach(t => t.stop());
                revealPlayBtn();
              };
              mediaRecorder.start();
              speakMascot("Recording your voice! Speak clearly 🎙️");
              return;
            } catch(e) {
              if (stream) stream.getTracks().forEach(t => t.stop());
            }
          }

          // Fallback Practice Mode
          const info = getCardInfo(btn);
          recordedBlobs[id] = info;
          speakMascot(`Voice Practice active for "${info.text}"! Click 'Stop' when done. 🗣️`);
        } else {
          activeRecordingId = null;
          btn.classList.remove('recording');
          btn.innerHTML = '<i class="fa-solid fa-microphone"></i> Rec';
          btn.style.background = '';

          if (mediaRecorder && mediaRecorder.state && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
          } else {
            revealPlayBtn();
          }
          speakMascot("Great recording! Click 'My Voice' to hear yourself 🎵");
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
          speakMascot("Playing your recording! Does it sound good? 🔊");
        }
      });
    });
  }

  /* ----------------------------------------------------------------
     Time of Day
  ---------------------------------------------------------------- */
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
          speakMascot("Nighttime in the Ghibli world... The fireflies light your path! 🌙");
        } else {
          if (firefliesContainer) firefliesContainer.innerHTML = '';
          speakMascot(theme === 'sunset' ? "A warm Ghibli sunset... Perfect for focused studying! 🌅" : "Good day! Let's learn English together! ☀️");
        }
      });
    });
  }

  function spawnFireflies(count) {
    const container = document.getElementById('firefliesContainer');
    if (!container) return;
    container.innerHTML = '';
    for (let i = 0; i < count; i++) {
      const f = document.createElement('div');
      f.className = 'firefly';
      f.style.left = `${Math.random() * 100}vw`;
      f.style.top = `${Math.random() * 100}vh`;
      f.style.animationDelay = `${Math.random() * 5}s`;
      container.appendChild(f);
    }
  }

  /* ----------------------------------------------------------------
     Mascot System
  ---------------------------------------------------------------- */
  function speakMascot(text) {
    const el = document.getElementById('mascotTextContent');
    revealMascotBubble();
    if (pomoIsRunning) scheduleFocusAutoFade();
    if (el) el.textContent = `"${text}"`;
  }

  function revealMascotBubble() {
    const bubble = document.getElementById('mascotBubble');
    if (bubble) bubble.classList.remove('focused-auto-collapsed');
  }

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

  function setMascotExpression(state) {
    const img = document.getElementById('mascotAvatarImg');
    const wrap = document.getElementById('mascotAvatarWrap');
    const badge = document.getElementById('mascotExprBadge');
    const actionChip = document.getElementById('mascotActionChip');
    if (!wrap) return;
    wrap.classList.remove('talking', 'celebrating', 'focus-mode', 'expr-sad', 'expr-celebrate');
    let actionText = '';
    if (state === 'talking') {
      if (img) img.src = MASCOT_BASE + 'mascot_talking.jpg';
      wrap.classList.add('talking');
      if (badge) badge.textContent = '💬 Storyteller';
      actionText = '📖 Narrating Teacher Lewis Story';
    } else if (state === 'focused') {
      if (img) img.src = MASCOT_BASE + 'mascot_focused.jpg';
      wrap.classList.add('focus-mode');
      if (badge) badge.textContent = '🍅 Focused';
      actionText = '🪑 Studying Together';
    } else if (state === 'sad') {
      if (img) img.src = MASCOT_BASE + 'mascot.jpg';
      wrap.classList.add('expr-sad');
      if (badge) badge.textContent = '💙 Encouraging';
      actionText = '🤗 Giving Encouragement';
    } else if (state === 'celebrate') {
      if (img) img.src = MASCOT_BASE + 'mascot.jpg';
      wrap.classList.add('celebrating', 'expr-celebrate');
      if (badge) badge.textContent = '🌟 Joyful!';
      actionText = '🎉 Celebrating Great Progress!';
    } else {
      if (img) img.src = MASCOT_BASE + 'mascot.jpg';
      if (badge) badge.textContent = '🐾 Ready to Study';
      actionText = '🪑 Sitting Cozy & Ready';
    }
    if (actionChip) actionChip.innerHTML = `<i class="fa-solid fa-paw"></i> ${actionText}`;
  }

  function advanceTeacherLewisStory() {
    const chapter = teacherLewisChapters[currentStoryIndex];
    speakMascot(chapter.text);
    const lbl = document.getElementById('storyChapterLabel');
    if (lbl) lbl.textContent = chapter.title;
    setMascotExpression('talking');
    currentStoryIndex = (currentStoryIndex + 1) % teacherLewisChapters.length;
  }

  function setupMascot() {
    const avatarWrap = document.getElementById('mascotAvatarWrap');
    const mascotWidget = document.getElementById('ghibliMascotWidget');
    const pomoToggleBtn = document.getElementById('pomoToggleBtn');
    const pomoOptBtn = document.getElementById('pomoOptBtn');
    const presetsContainer = document.getElementById('pomoQuickPresets');
    const presetBtns = document.querySelectorAll('.pomo-quick-btn');

    if (mascotWidget) {
      mascotWidget.addEventListener('mouseenter', () => { isMascotHovered = true; if (focusAutoFadeTimer) clearTimeout(focusAutoFadeTimer); revealMascotBubble(); });
      mascotWidget.addEventListener('mouseleave', () => { isMascotHovered = false; if (pomoIsRunning) scheduleFocusAutoFade(); });
    }

    if (avatarWrap) {
      avatarWrap.addEventListener('click', () => { advanceTeacherLewisStory(); triggerSparkle(window.innerWidth - 80, window.innerHeight - 80); playChime(650, 0.12); });
    }

    if (pomoToggleBtn) {
      pomoToggleBtn.addEventListener('click', e => { e.stopPropagation(); pomoIsRunning ? pausePomodoro() : startPomodoro(); });
    }

    if (pomoOptBtn && presetsContainer) {
      pomoOptBtn.addEventListener('click', e => { e.stopPropagation(); presetsContainer.classList.toggle('hidden'); });
    }

    presetBtns.forEach(btn => {
      btn.addEventListener('click', e => {
        e.stopPropagation();
        presetBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const mins = parseInt(btn.dataset.mins, 10);
        pomoTotalDuration = mins * 60;
        pomoTimeRemaining = pomoTotalDuration;
        updatePomoDisplay();
        if (presetsContainer) presetsContainer.classList.add('hidden');
        if (pomoIsRunning) pausePomodoro();
        speakMascot(`Timer set to ${mins} minutes! Press Play when ready. 🍅`);
      });
    });
  }

  /* ----------------------------------------------------------------
     Pomodoro
  ---------------------------------------------------------------- */
  function startPomodoro() {
    if (pomoIsRunning) return;
    pomoIsRunning = true;
    revealMascotBubble();
    scheduleFocusAutoFade();
    const icon = document.getElementById('pomoIcon');
    if (icon) icon.className = 'fa-solid fa-pause';
    setMascotExpression('focused');
    playChime(523.25, 0.2);
    speakMascot("🍅 Focus mode! Let's study English together with Teacher Lewis!");
    pomoInterval = setInterval(() => {
      pomoTimeRemaining--;
      updatePomoDisplay();
      if (pomoTimeRemaining === Math.floor(pomoTotalDuration / 2) && pomoTimeRemaining > 10) {
        speakMascot("Halfway there! Keep going, Teacher Lewis is proud of your focus! 💪");
        playChime(659.25, 0.15);
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
    playFanfare();
    speakMascot("🎉 FOCUS SESSION COMPLETE! Teacher Lewis says: Outstanding work today!");
  }

  function updatePomoDisplay() {
    const display = document.getElementById('pomoMinTime');
    if (display) {
      const mins = Math.floor(pomoTimeRemaining / 60);
      const secs = pomoTimeRemaining % 60;
      display.textContent = `${mins.toString().padStart(2,'0')}:${secs.toString().padStart(2,'0')}`;
    }
  }

  /* ----------------------------------------------------------------
     Ambient Soundscape
  ---------------------------------------------------------------- */
  function setupAmbientSoundscape() {
    const toggleBtn = document.getElementById('toggleAmbientBtn');
    if (!toggleBtn) return;
    toggleBtn.addEventListener('click', () => {
      if (window.GhibliAudio && window.GhibliAudio.toggleBGM) {
        window.GhibliAudio.toggleBGM(toggleBtn);
        if (window.GhibliAudio.isBGMPlaying()) {
          speakMascot("Playing chill Ghibli piano music... Relax and study! 🎹");
        }
      }
    });
    if (window.GhibliAudio && window.GhibliAudio.syncBGMButtonState) {
      window.GhibliAudio.syncBGMButtonState();
    }
  }

  /* ----------------------------------------------------------------
     Chime & Sparkle Effects
  ---------------------------------------------------------------- */
  function playChime(freq = 523.25, duration = 0.2) {
    if (window.GhibliAudio && window.GhibliAudio.playChime) { window.GhibliAudio.playChime(freq, duration); return; }
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain); gain.connect(ctx.destination);
      osc.frequency.value = freq; osc.type = 'sine';
      gain.gain.setValueAtTime(0.3, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
      osc.start(); osc.stop(ctx.currentTime + duration);
    } catch(e) {}
  }

  function playFanfare() {
    if (window.GhibliAudio && window.GhibliAudio.playFanfare) { window.GhibliAudio.playFanfare(); return; }
    [523.25, 659.25, 783.99, 1046.50].forEach((freq, i) => setTimeout(() => playChime(freq, 0.3), i * 120));
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

  /* ----------------------------------------------------------------
     Live Sentence Mirroring System (Exercise 5.1)
  ---------------------------------------------------------------- */
  function isEx51Card(card, input) {
    if (!card) return false;
    const sec = card.closest('.ghibli-section, .ghibli-exercise-card, section');
    if (sec) {
      const exNum = sec.querySelector('.ghibli-ex-num, .exercise-num');
      if (exNum && exNum.textContent.trim() === '5.1') return true;
    }
    if (input) {
      if (input.id && input.id.startsWith('ex51')) return true;
      if (input.className && input.className.includes('ex51')) return true;
    }
    return false;
  }

  function setupSentenceMirroring() {
    const cards = document.querySelectorAll('.ghibli-char-card, .fill-blank-item, .exercise-item');
    cards.forEach(card => {
      if (card.dataset.mirroringSetup) return;

      const input = card.querySelector('input.ghibli-input');
      if (!input || input.classList.contains('ghibli-inline-input')) return;

      // Only apply mirroring to Exercise 5.1 cards
      if (!isEx51Card(card, input)) return;

      const promptWrap = card.querySelector('.ghibli-prompt-text, .ghibli-sentence-text, .item-text');
      if (!promptWrap) return;

      const targetSpan = promptWrap.querySelector('span:not(.ghibli-eg-badge):not(.ghibli-example-badge):not(.item-index)') || promptWrap;
      const rawText = targetSpan.textContent.trim();

      const hasBlank = /\[blank\]/i.test(rawText);
      const hasUnderscores = /_{2,}/.test(rawText);

      if (hasBlank || hasUnderscores) {
        card.dataset.mirroringSetup = 'true';
        card.dataset.origSentence = rawText;

        const isExample = input.hasAttribute('readonly') || input.classList.contains('correct') || input.classList.contains('example-input') || card.classList.contains('example-card');
        const initialVal = input.value.trim();

        let formattedHtml = rawText;
        formattedHtml = formattedHtml.replace(/\(([a-zA-Z\s]+)\)/g, '<span class="ghibli-clue-hint">($1)</span>');

        if (hasBlank) {
          formattedHtml = formattedHtml.replace(/\[blank\]/gi, '<span class="ghibli-mirrored-blank placeholder" data-placeholder="______">______</span>');
        } else if (hasUnderscores) {
          formattedHtml = formattedHtml.replace(/_{2,}/g, '<span class="ghibli-mirrored-blank placeholder" data-placeholder="______">______</span>');
        }

        targetSpan.innerHTML = formattedHtml;

        const blankSpan = targetSpan.querySelector('.ghibli-mirrored-blank');
        if (blankSpan && isExample) {
          blankSpan.classList.add('example-blank');
          if (initialVal) {
            blankSpan.textContent = 'goes';
            blankSpan.classList.remove('placeholder');
            blankSpan.classList.add('has-value', 'correct');
          }
        }
      }
    });

    document.addEventListener('input', e => {
      const input = e.target.closest('input.ghibli-input');
      if (!input || input.classList.contains('ghibli-inline-input')) return;

      const card = input.closest('.ghibli-char-card, .fill-blank-item, .exercise-item');
      if (!card || !isEx51Card(card, input)) return;

      const promptWrap = card.querySelector('.ghibli-prompt-text, .ghibli-sentence-text, .item-text');
      if (!promptWrap) return;

      const targetSpan = promptWrap.querySelector('span:not(.ghibli-eg-badge):not(.ghibli-example-badge):not(.item-index)') || promptWrap;
      const blankSpan = targetSpan.querySelector('.ghibli-mirrored-blank');
      if (blankSpan && blankSpan.classList.contains('example-blank')) return;

      const val = input.value;
      const origSentence = card.dataset.origSentence || '';

      if (!val || !val.trim()) {
        if (origSentence) {
          let resetHtml = origSentence.replace(/\(([a-zA-Z\s]+)\)/g, '<span class="ghibli-clue-hint">($1)</span>');
          if (/\[blank\]/i.test(resetHtml)) {
            resetHtml = resetHtml.replace(/\[blank\]/gi, '<span class="ghibli-mirrored-blank placeholder" data-placeholder="______">______</span>');
          } else {
            resetHtml = resetHtml.replace(/_{2,}/g, '<span class="ghibli-mirrored-blank placeholder" data-placeholder="______">______</span>');
          }
          targetSpan.innerHTML = resetHtml;
        }
      } else {
        const trimmedVal = val.trim();
        const promptPrefix = origSentence.split(/_{2,}|\[blank\]/i)[0].trim();

        if (promptPrefix && trimmedVal.toLowerCase().startsWith(promptPrefix.toLowerCase() + ' ') && trimmedVal.length > promptPrefix.length + 3) {
          targetSpan.innerHTML = `<span class="ghibli-mirrored-blank has-value">${val}</span>`;
        } else {
          if (!targetSpan.querySelector('.ghibli-mirrored-blank')) {
            let baseHtml = origSentence.replace(/\(([a-zA-Z\s]+)\)/g, '<span class="ghibli-clue-hint">($1)</span>');
            if (/\[blank\]/i.test(baseHtml)) {
              baseHtml = baseHtml.replace(/\[blank\]/gi, '<span class="ghibli-mirrored-blank placeholder" data-placeholder="______">______</span>');
            } else {
              baseHtml = baseHtml.replace(/_{2,}/g, '<span class="ghibli-mirrored-blank placeholder" data-placeholder="______">______</span>');
            }
            targetSpan.innerHTML = baseHtml;
          }
          const currentBlank = targetSpan.querySelector('.ghibli-mirrored-blank');
          if (currentBlank) {
            currentBlank.textContent = val;
            currentBlank.className = 'ghibli-mirrored-blank has-value';
          }
          const currentClue = targetSpan.querySelector('.ghibli-clue-hint');
          if (currentClue) currentClue.style.opacity = '0.35';
        }
      }
    });
  }

  /* ----------------------------------------------------------------
     Check Answers Helper (call from each chapter's script)
  ---------------------------------------------------------------- */
  window.GhibliChapterShared = {
    checkAnswers: function(answersMap, inputClassMap, totalQs) {
      // answersMap: { inputId: expectedAnswer, ... }
      // inputClassMap: object to track prefix groups
      let correct = 0;
      Object.entries(answersMap).forEach(([id, expected]) => {
        const input = document.getElementById(id);
        if (!input) return;
        const user = input.value.trim().toLowerCase().replace(/['']/g,"'").replace(/\s+/g,' ');
        const exp = expected.toLowerCase().replace(/['']/g,"'").replace(/\s+/g,' ');
        const userClean = user.replace(/\.$/, '');
        const expClean = exp.replace(/\.$/, '');
        
        let isMatch = (user === exp) || (userClean === expClean);
        if (!isMatch) {
          const wordsExp = expClean.split(' ');
          const wordsUser = userClean.split(' ');
          if (wordsUser.length === 1 && wordsExp.includes(wordsUser[0])) {
            isMatch = true;
          }
        }

        const card = input.closest('.ghibli-char-card, .fill-blank-item, .exercise-item');
        const blank = card ? card.querySelector('.ghibli-mirrored-blank') : null;

        if (isMatch) {
          input.classList.add('correct');
          input.classList.remove('incorrect');
          if (blank && !blank.classList.contains('example-blank')) {
            blank.classList.add('correct');
            blank.classList.remove('incorrect');
          }
          correct++;
        } else if (user !== '') {
          input.classList.add('incorrect');
          input.classList.remove('correct');
          if (blank && !blank.classList.contains('example-blank')) {
            blank.classList.add('incorrect');
            blank.classList.remove('correct');
          }
        }
      });
      const scoreText = document.getElementById('ghibliScoreText');
      if (scoreText) scoreText.textContent = `${correct} / ${totalQs}`;
      if (correct === totalQs) {
        setMascotExpression('celebrate');
        playFanfare();
        speakMascot(`🌟 PERFECT SCORE! ${totalQs}/${totalQs}! Teacher Lewis is SO proud of you!`);
        triggerSparkle(window.innerWidth / 2, window.innerHeight / 3);
      } else if (correct > 0) {
        setMascotExpression('talking');
        speakMascot(`Good effort! ${correct}/${totalQs} correct! Keep trying to get a perfect score! 💪`);
      } else {
        setMascotExpression('sad');
        speakMascot("Don't worry! Teacher Lewis says: Mistakes are just proof you are trying! Give it another go! 🌱");
      }
      return correct;
    },
    resetPage: function(inputSelectors, total) {
      inputSelectors.forEach(sel => {
        document.querySelectorAll(sel).forEach(i => {
          i.value = '';
          i.classList.remove('correct','incorrect');
          const card = i.closest('.ghibli-char-card, .fill-blank-item, .exercise-item');
          if (card) {
            const promptWrap = card.querySelector('.ghibli-prompt-text, .ghibli-sentence-text, .item-text');
            const targetSpan = promptWrap ? (promptWrap.querySelector('span:not(.ghibli-eg-badge):not(.ghibli-example-badge):not(.item-index)') || promptWrap) : null;
            const origSentence = card.dataset.origSentence;
            if (targetSpan && origSentence) {
              let resetHtml = origSentence.replace(/\(([a-zA-Z\s]+)\)/g, '<span class="ghibli-clue-hint">($1)</span>');
              if (/\[blank\]/i.test(resetHtml)) {
                resetHtml = resetHtml.replace(/\[blank\]/gi, '<span class="ghibli-mirrored-blank placeholder" data-placeholder="______">______</span>');
              } else {
                resetHtml = resetHtml.replace(/_{2,}/g, '<span class="ghibli-mirrored-blank placeholder" data-placeholder="______">______</span>');
              }
              targetSpan.innerHTML = resetHtml;
            }
          }
        });
      });
      const scoreText = document.getElementById('ghibliScoreText');
      if (scoreText) scoreText.textContent = `0 / ${total}`;
      setMascotExpression('friendly');
      speakMascot("Page reset! Ready for a fresh start! Let's go! 🌿");
    }
  };

  /* ----------------------------------------------------------------
     Chart Selection Subsystem
  ---------------------------------------------------------------- */
  function setupChartInteractions() {
    document.addEventListener('click', e => {
      const blockBtn = e.target.closest('.ghibli-block-btn');
      if (blockBtn) {
        const col = blockBtn.closest('.ghibli-chart-col');
        const container = blockBtn.closest('.ghibli-chart-container, .ghibli-section, body');
        if (col) {
          col.querySelectorAll('.ghibli-block-btn').forEach(btn => {
            btn.classList.remove('selected');
            btn.style.background = '#ffffff';
            btn.style.color = '#1e293b';
            btn.style.borderColor = '#cbd5e1';
            btn.style.fontWeight = '600';
          });
          blockBtn.classList.add('selected');
          blockBtn.style.background = '#2d5a27';
          blockBtn.style.color = '#ffffff';
          blockBtn.style.borderColor = '#2d5a27';
          blockBtn.style.fontWeight = '700';

          if (container) {
            const selectedBtns = container.querySelectorAll('.ghibli-chart-col .ghibli-block-btn.selected');
            const words = Array.from(selectedBtns).map(b => (b.getAttribute('data-value') || b.textContent).trim());
            const sentence = words.join(' ');
            const assembledEl = container.querySelector('.ghibli-assembled-text, [id^="assembledGreetingText"]');
            if (assembledEl) {
              assembledEl.textContent = `"${sentence}"`;
            }
          }
          if (window.GhibliAudio && window.GhibliAudio.playClick) {
            window.GhibliAudio.playClick();
          }
        }
      }

      const playBtn = e.target.closest('[id^="playChartSentenceBtn"], .play-chart-sentence-btn');
      if (playBtn) {
        const container = playBtn.closest('.ghibli-chart-container, .ghibli-section, body');
        if (container) {
          const assembledEl = container.querySelector('.ghibli-assembled-text, [id^="assembledGreetingText"]');
          if (assembledEl) {
            const sentence = assembledEl.textContent.replace(/"/g, '').trim();
            if (sentence) {
              const audioSrc = typeof window.getChartAudioPath === 'function' ? window.getChartAudioPath(sentence) : '';
              playAudioTrack(audioSrc, sentence);
            }
          }
        }
      }
    });
  }

  /* ----------------------------------------------------------------
     Init
  ---------------------------------------------------------------- */
  document.addEventListener('DOMContentLoaded', () => {
    setupTimeOfDay();
    setupAudioPlayers();
    setupVoiceRecorder();
    setupMascot();
    setupAmbientSoundscape();
    setupChartInteractions();
    setupSentenceMirroring();
  });

})();

