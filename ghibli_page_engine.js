/* ==========================================================================
   Studio Ghibli Interactive Edition — Runtime Page Engine
   ghibli_page_engine.js
   ========================================================================== */

(function (window, document) {
  'use strict';

  class GhibliPageEngine {
    constructor() {
      this.currentTheme = localStorage.getItem('ghibli_theme') || 'day';
      this.activeAudio = null;
      this.recordedBlobs = {};
      this.mediaRecorders = {};
      this.speechSynth = window.speechSynthesis || null;

      // Pomodoro Timer State
      this.pomodoroTime = 25 * 60; // 25 minutes default
      this.pomodoroMode = 'work'; // 'work' | 'break'
      this.pomodoroInterval = null;
      this.isPomodoroRunning = false;

      // Teacher Lewis Mascot Stories
      this.mascotQuotes = [
        "Welcome to Teacher Lewis's Practice Book! 🍃 Let's learn English together.",
        "Tip: Practice reading out loud to build your confidence and fluency! 🗣️",
        "Every small step brings you closer to mastering English. Keep going! 🌿",
        "Chapter 4 Wisdom: Pay close attention to action verbs and prepositions!",
        "Don't worry about making mistakes—they are proof that you are trying! ✨",
        "Take a deep breath and listen carefully to the audio pronunciation. 🎧",
        "Studio Ghibli Rule: Learning should feel as magical as a walk in the forest! 🌲"
      ];

      // Bind DOM Ready
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => this.init());
      } else {
        this.init();
      }
    }

    init() {
      this.setupTimeOfDay();
      this.setupAudioPlayers();
      this.setupVoiceRecorder();
      this.setupMascotAndPomodoro();
      this.setupExerciseInteractions();
      this.setupGradingEngine();
      this.setupResetButton();
      this.setupKeyboardNavigation();
      this.setupAmbientButton();
    }

    setupAmbientButton() {
      document.querySelectorAll('#toggleAmbientBtn, .bgm-toggle-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          if (window.GhibliAudio && window.GhibliAudio.toggleBGM) {
            window.GhibliAudio.toggleBGM(btn);
          }
        });
      });
      if (window.GhibliAudio && window.GhibliAudio.syncBGMButtonState) {
        window.GhibliAudio.syncBGMButtonState();
      }
    }

    /* ==========================================================================
       1. Time-of-Day Theme Switcher Logic
       ========================================================================== */
    setupTimeOfDay() {
      const todBtns = document.querySelectorAll('.tod-btn');
      
      const applyTheme = (theme) => {
        this.currentTheme = theme;
        localStorage.setItem('ghibli_theme', theme);
        document.body.classList.remove('theme-day', 'theme-sunset', 'theme-night');
        document.body.classList.add('theme-' + theme);

        todBtns.forEach(btn => {
          if (btn.getAttribute('data-theme') === theme) {
            btn.classList.add('active');
          } else {
            btn.classList.remove('active');
          }
        });

        const firefliesContainer = document.getElementById('firefliesContainer');
        if (theme === 'night') {
          this.spawnFireflies(18);
          this.speakMascot("Nighttime in the Ghibli forest... Listen to the fireflies! 🌙", 4000);
        } else {
          if (firefliesContainer) firefliesContainer.innerHTML = '';
          if (theme === 'sunset') {
            this.speakMascot("Golden hour! The sunset brings peace to our study space. 🌅", 4000);
          }
        }
      };

      todBtns.forEach(btn => {
        btn.addEventListener('click', () => {
          const theme = btn.getAttribute('data-theme');
          applyTheme(theme);
        });
      });

      // Apply initial loaded theme
      applyTheme(this.currentTheme);
    }

    spawnFireflies(count = 18) {
      const container = document.getElementById('firefliesContainer');
      if (!container) return;
      container.innerHTML = '';

      for (let i = 0; i < count; i++) {
        const firefly = document.createElement('div');
        firefly.className = 'firefly';
        firefly.style.left = Math.random() * 100 + 'vw';
        firefly.style.top = Math.random() * 100 + 'vh';
        firefly.style.animationDelay = (Math.random() * 5) + 's';
        firefly.style.animationDuration = (4 + Math.random() * 5) + 's';
        container.appendChild(firefly);
      }
    }

    /* ==========================================================================
       2. Audio Player Subsystem (MP3 + SpeechSynthesis Fallback)
       ========================================================================== */
    setupAudioPlayers() {
      document.addEventListener('click', (e) => {
        const audioBtn = e.target.closest('.ghibli-audio-btn, [data-audio]');
        if (!audioBtn) return;

        // Skip if button is rec or my-voice button
        if (audioBtn.classList.contains('ghibli-rec-btn') || audioBtn.classList.contains('my-voice-btn')) return;

        const audioPath = audioBtn.getAttribute('data-audio');
        const fallbackText = audioBtn.getAttribute('data-fallback-text') || audioBtn.closest('.fill-blank-item, .mc-prompt-row, .audio-item-row, .exercise-items-list')?.innerText || "Listen and repeat.";
        
        if (audioPath) {
          this.playAudioTrack(audioPath, fallbackText, audioBtn);
        }
      });
    }

    playAudioTrack(audioPath, fallbackText, btnElement = null) {
      if (this.activeAudio) {
        this.activeAudio.pause();
        this.activeAudio = null;
      }
      if (this.speechSynth && this.speechSynth.speaking) {
        this.speechSynth.cancel();
      }

      const resetBtnState = () => {
        if (btnElement) btnElement.classList.remove('playing');
      };

      if (!audioPath) {
        resetBtnState();
        return;
      }

      if (btnElement) btnElement.classList.add('playing');

      const cacheBustUrl = audioPath + (audioPath.includes('?') ? '&' : '?') + 't=' + Date.now();
      const audio = new Audio(cacheBustUrl);
      this.activeAudio = audio;

      audio.play().then(() => {
        audio.onended = resetBtnState;
        audio.onerror = resetBtnState;
      }).catch(err => {
        console.warn('Audio playback error:', err);
        resetBtnState();
      });
    }

    fallbackSpeechSynthesis(text, onEndedCallback) {
      if (onEndedCallback) onEndedCallback();
    }

    /* ==========================================================================
       3. Voice Recorder Subsystem (MediaRecorder API + Practice Fallback)
       ========================================================================== */
    setupVoiceRecorder() {
      // Helper to detect best supported MIME type
      const getSupportedMimeType = () => {
        if (typeof MediaRecorder === 'undefined' || !MediaRecorder.isTypeSupported) return '';
        const types = [
          'audio/webm;codecs=opus',
          'audio/webm',
          'audio/mp4',
          'audio/aac',
          'audio/ogg'
        ];
        for (const type of types) {
          if (MediaRecorder.isTypeSupported(type)) return type;
        }
        return '';
      };

      // Helper to extract spoken text / audio path from context card
      const getCardInfo = (recBtn) => {
        const card = recBtn.closest('.animal-card, .ghibli-char-card, .ghibli-listen-card, .ghibli-card-body, .exercise-item, section, div');
        let text = '';
        let audioPath = '';

        if (card) {
          const audioBtn = card.querySelector('[data-audio]');
          if (audioBtn) audioPath = audioBtn.getAttribute('data-audio') || '';

          const input = card.querySelector('input[data-correct], input[type="text"]');
          if (input) {
            text = input.value || input.getAttribute('data-correct') || input.placeholder || '';
          }

          if (!text) {
            const img = card.querySelector('img[alt]');
            if (img) text = img.getAttribute('alt') || '';
          }

          if (!text) {
            const promptText = card.querySelector('.ghibli-prompt-text, .ghibli-ex-instruction, p, span');
            if (promptText) text = promptText.textContent || '';
          }
        }

        return { text: text.trim() || 'English Practice', audioPath };
      };

      // 1. Playback Delegation for "My Voice" button
      document.addEventListener('click', (e) => {
        const playBtn = e.target.closest('.play-rec-btn, .my-voice-btn');
        if (!playBtn) return;

        const recId = playBtn.getAttribute('data-id') || playBtn.getAttribute('data-for');
        const recData = this.recordedBlobs[recId];

        if (recData) {
          if (typeof recData === 'string' && (recData.startsWith('blob:') || recData.startsWith('data:') || recData.startsWith('audio/'))) {
            // Play real recorded blob URL
            const voiceAudio = new Audio(recData);
            voiceAudio.play().catch(err => {
              console.warn('Recorded voice playback error:', err);
              if (this.speakMascot) this.speakMascot("Playing your recorded voice! 🔊", 4000);
            });
            if (this.speakMascot) this.speakMascot("Playing your recorded voice! 🔊", 4000);
          } else {
            // Practice Fallback Playback
            const info = typeof recData === 'object' ? recData : { text: recData };
            if (info.audioPath) {
              this.playAudioTrack(info.audioPath, info.text, playBtn);
            } else if (info.text && window.speechSynthesis) {
              window.speechSynthesis.cancel();
              const u = new SpeechSynthesisUtterance(info.text);
              u.lang = 'en-US';
              window.speechSynthesis.speak(u);
            }
            if (this.speakMascot) this.speakMascot(`Playing practice voice for: "${info.text}" 🔊`, 4000);
          }
        } else {
          alert('No recording found yet. Click Rec first to record your voice!');
        }
      });

      // 2. Record / Stop Delegation for "Rec" button
      document.addEventListener('click', async (e) => {
        const recBtn = e.target.closest('.rec-btn, .ghibli-rec-btn');
        if (!recBtn) return;

        const recId = recBtn.getAttribute('data-id') || recBtn.getAttribute('data-for') || 'item_default';
        const isRecording = recBtn.classList.contains('recording');

        const revealPlayBtn = () => {
          const container = recBtn.parentNode || recBtn.closest('.voice-recorder-controls') || recBtn.closest('.ghibli-card-body') || recBtn.closest('.animal-card');
          let playBtn = container ? container.querySelector(`.play-rec-btn[data-id="${recId}"], .play-rec-btn, .my-voice-btn`) : null;
          if (playBtn) {
            playBtn.classList.remove('hidden');
            playBtn.style.display = 'inline-flex';
            playBtn.classList.add('has-voice');
          } else if (recBtn.parentNode) {
            playBtn = document.createElement('button');
            playBtn.className = 'voice-btn play-rec-btn has-voice';
            playBtn.setAttribute('data-id', recId);
            playBtn.innerHTML = '<i class="fa-solid fa-play"></i> My Voice';
            recBtn.parentNode.appendChild(playBtn);
          }
        };

        if (!isRecording) {
          recBtn.classList.add('recording');
          recBtn.innerHTML = '<i class="fa-solid fa-square-stop" style="color:#ef4444;"></i> Stop';

          let stream = null;
          let mediaRecorder = null;
          const mimeType = getSupportedMimeType();

          if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia && typeof MediaRecorder !== 'undefined') {
            try {
              stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            } catch (err) {
              console.warn("Microphone access unavailable or denied:", err);
            }
          }

          if (stream) {
            try {
              const options = mimeType ? { mimeType } : {};
              mediaRecorder = new MediaRecorder(stream, options);
              const chunks = [];

              mediaRecorder.ondataavailable = (event) => {
                if (event.data && event.data.size > 0) chunks.push(event.data);
              };

              mediaRecorder.onstop = () => {
                const finalMime = mimeType || mediaRecorder.mimeType || 'audio/webm';
                const blob = new Blob(chunks, { type: finalMime });
                const audioUrl = URL.createObjectURL(blob);
                this.recordedBlobs[recId] = audioUrl;

                if (stream) {
                  stream.getTracks().forEach(track => track.stop());
                }
                revealPlayBtn();
              };

              mediaRecorder.start();
              this.mediaRecorders[recId] = mediaRecorder;
              if (this.speakMascot) this.speakMascot("Recording your voice... Speak clearly into your microphone! 🎙️", 4000);
              return;

            } catch (err) {
              console.warn("MediaRecorder init failed, switching to practice mode:", err);
              if (stream) stream.getTracks().forEach(track => track.stop());
            }
          }

          // Practice Recording Mode (when mic permission/hardware is unavailable)
          const info = getCardInfo(recBtn);
          this.mediaRecorders[recId] = { isFallback: true, info };
          if (this.speakMascot) this.speakMascot(`Voice Practice active for "${info.text}"! Click 'Stop' when finished speaking. 🗣️`, 4000);

        } else {
          // Stop recording
          recBtn.classList.remove('recording');
          recBtn.innerHTML = '<i class="fa-solid fa-microphone"></i> Rec';

          const activeRec = this.mediaRecorders[recId];
          if (activeRec) {
            if (activeRec.isFallback) {
              this.recordedBlobs[recId] = activeRec.info;
              revealPlayBtn();
              delete this.mediaRecorders[recId];
            } else if (activeRec.state && activeRec.state !== 'inactive') {
              activeRec.stop();
              delete this.mediaRecorders[recId];
            }
          } else {
            revealPlayBtn();
          }

          if (this.speakMascot) this.speakMascot("Recording saved! Click 'My Voice' to listen. 🎵", 4000);
        }
      });
    }

    /* ==========================================================================
       4. Kodama Mascot Engine & Pomodoro Timer
       ========================================================================== */
    setupMascotAndPomodoro() {
      const avatar = document.getElementById('mascotAvatar');
      const pomodoroPill = document.getElementById('pomodoroPill');

      if (avatar) {
        avatar.addEventListener('click', () => {
          const randomQuote = this.mascotQuotes[Math.floor(Math.random() * this.mascotQuotes.length)];
          this.speakMascot(randomQuote, 6000);
          if (window.GhibliAudio) window.GhibliAudio.playWaterDrop();
        });
      }

      if (pomodoroPill) {
        pomodoroPill.addEventListener('click', () => this.togglePomodoro());
      }

      // Initial greeting after 1 second
      setTimeout(() => {
        this.speakMascot("Welcome! Click 'Check Answers' when you finish your exercises.", 5000);
      }, 1000);
    }

    speakMascot(text, duration = 5000, emote = 'happy') {
      const bubble = document.getElementById('mascotBubble');
      if (!bubble) return;

      bubble.innerHTML = `<div class="bubble-content">${text}</div>`;
      bubble.style.display = 'block';

      if (this.mascotTimeout) clearTimeout(this.mascotTimeout);
      this.mascotTimeout = setTimeout(() => {
        bubble.style.display = 'none';
      }, duration);
    }

    togglePomodoro() {
      const display = document.getElementById('pomodoroDisplay');
      const pill = document.getElementById('pomodoroPill');
      if (!display) return;

      if (this.isPomodoroRunning) {
        clearInterval(this.pomodoroInterval);
        this.isPomodoroRunning = false;
        this.speakMascot("Pomodoro paused.", 3000);
      } else {
        this.isPomodoroRunning = true;
        this.speakMascot(this.pomodoroMode === 'work' ? "Focus time started! 25 minutes of study." : "Break time started! Relax for 5 minutes.", 4000);

        this.pomodoroInterval = setInterval(() => {
          this.pomodoroTime--;
          if (this.pomodoroTime < 0) {
            clearInterval(this.pomodoroInterval);
            this.isPomodoroRunning = false;

            if (this.pomodoroMode === 'work') {
              this.pomodoroMode = 'break';
              this.pomodoroTime = 5 * 60;
              if (pill) pill.classList.add('break-mode');
              if (window.GhibliAudio) window.GhibliAudio.playFanfare();
              this.speakMascot("Great session! Take a 5-minute Ghibli break. 🍵", 7000);
            } else {
              this.pomodoroMode = 'work';
              this.pomodoroTime = 25 * 60;
              if (pill) pill.classList.remove('break-mode');
              if (window.GhibliAudio) window.GhibliAudio.playChime();
              this.speakMascot("Ready to practice more English? Let's go! 🌿", 7000);
            }
          }

          const mins = Math.floor(this.pomodoroTime / 60).toString().padStart(2, '0');
          const secs = (this.pomodoroTime % 60).toString().padStart(2, '0');
          display.textContent = `${mins}:${secs}`;
        }, 1000);
      }
    }

    /* ==========================================================================
       5. Interactive Exercise UI Event Listeners
       ========================================================================== */
    setupExerciseInteractions() {
      // Multiple Choice selection
      document.addEventListener('click', (e) => {
        const optionBtn = e.target.closest('.ghibli-option');
        if (!optionBtn) return;

        const container = optionBtn.closest('.ghibli-mc-container, .mc-options-grid');
        if (container) {
          container.querySelectorAll('.ghibli-option').forEach(opt => opt.classList.remove('selected'));
        }
        optionBtn.classList.add('selected');
        if (window.GhibliAudio) window.GhibliAudio.playClick();
      });

      // True / False selection
      document.addEventListener('click', (e) => {
        const tfBtn = e.target.closest('.tf-btn');
        if (!tfBtn) return;

        const group = tfBtn.closest('.tf-btn-group');
        if (group) {
          group.querySelectorAll('.tf-btn').forEach(btn => btn.classList.remove('selected'));
        }
        tfBtn.classList.add('selected');
        if (window.GhibliAudio) window.GhibliAudio.playClick();
      });

      // Word Chip Drag & Drop / Click for Sentence Ordering
      document.addEventListener('click', (e) => {
        const chip = e.target.closest('.word-chip');
        if (!chip) return;

        const orderingContainer = chip.closest('.ghibli-ordering-container');
        if (!orderingContainer) return;

        const wordPool = orderingContainer.querySelector('.word-pool');
        const dropSlot = orderingContainer.querySelector('.ghibli-drop-slot');
        const orderInput = orderingContainer.querySelector('.order-input, .ghibli-input');

        if (chip.parentElement === wordPool && dropSlot) {
          dropSlot.appendChild(chip);
        } else if (chip.parentElement === dropSlot && wordPool) {
          wordPool.appendChild(chip);
        }

        // Sync constructed sentence to orderInput if present
        if (dropSlot && orderInput) {
          const words = Array.from(dropSlot.querySelectorAll('.word-chip')).map(c => c.innerText.trim());
          orderInput.value = words.join(' ');
        }
        if (window.GhibliAudio) window.GhibliAudio.playWaterDrop();
      });

      // Sentence Construction Chart Block Selection
      document.addEventListener('click', (e) => {
        const blockBtn = e.target.closest('.ghibli-block-btn');
        if (!blockBtn) return;

        const col = blockBtn.closest('.ghibli-chart-col');
        const container = blockBtn.closest('.ghibli-chart-container, .ghibli-section, body');
        if (!col) return;

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
      });

      // Chart Listen & Speak button
      document.addEventListener('click', (e) => {
        const playBtn = e.target.closest('[id^="playChartSentenceBtn"], .play-chart-sentence-btn');
        if (!playBtn) return;

        const container = playBtn.closest('.ghibli-chart-container, .ghibli-section, body');
        if (!container) return;

        const assembledEl = container.querySelector('.ghibli-assembled-text, [id^="assembledGreetingText"]');
        if (!assembledEl) return;

        const sentence = assembledEl.textContent.replace(/"/g, '').trim();
        if (sentence) {
          const audioSrc = typeof window.getChartAudioPath === 'function' ? window.getChartAudioPath(sentence) : '';
          this.playAudioTrack(audioSrc, sentence, playBtn);
        }
      });
    }

    /* ==========================================================================
       6. Instant Grading Engine (Check Answers)
       ========================================================================== */
    setupGradingEngine() {
      document.addEventListener('click', (e) => {
        const checkBtn = e.target.closest('#ghibliCheckAnswersBtn, .ghibli-check-btn, .ghibli-check-btn-bottom');
        if (checkBtn) {
          this.checkAnswers();
        }
      });
    }

    checkAnswers() {
      let totalItems = 0;
      let totalCorrect = 0;

      const normalize = (str) => {
        if (!str) return '';
        return str.toString()
          .toLowerCase()
          .replace(/[.,\/#!$%\^&\*;:{}=\-_`~()?'"]/g, '')
          .replace(/\s+/g, ' ')
          .trim();
      };

      const correctUserAnswers = new Set();

      // 1. Fill in Blank inputs & Matching Selects
      const fillInputs = document.querySelectorAll('.ghibli-input[data-correct], .ex1-1-input[data-correct], .ghibli-matching-select[data-correct]');
      fillInputs.forEach(input => {
        // Skip if input is part of sentence ordering fallback, or is a read-only example input
        if (input.closest('.ghibli-ordering-container')) return;
        if (input.hasAttribute('readonly') || input.classList.contains('example-input')) return;

        totalItems++;
        const userVal = normalize(input.value);
        const correctAttr = input.getAttribute('data-correct') || '';
        const acceptedAnswers = correctAttr.split('|').map(normalize);

        input.classList.remove('correct', 'incorrect');

        if (userVal && (acceptedAnswers.includes(userVal) || !correctAttr || correctAttr === 'null')) {
          input.classList.add('correct');
          totalCorrect++;
          acceptedAnswers.forEach(ans => { if (ans) correctUserAnswers.add(ans); });
          if (userVal) correctUserAnswers.add(userVal);
        } else {
          input.classList.add('incorrect');
        }
      });

      // 2. Sentence Ordering
      const orderingContainers = document.querySelectorAll('.ghibli-ordering-container');
      orderingContainers.forEach(container => {
        totalItems++;
        const dropSlot = container.querySelector('.ghibli-drop-slot');
        const orderInput = container.querySelector('.order-input, .ghibli-input');
        const correctAttr = container.getAttribute('data-correct') || (orderInput ? orderInput.getAttribute('data-correct') : '');
        const acceptedAnswers = correctAttr.split('|').map(normalize);

        let userSentence = '';
        if (dropSlot && dropSlot.children.length > 0) {
          userSentence = Array.from(dropSlot.querySelectorAll('.word-chip')).map(c => c.innerText.trim()).join(' ');
        } else if (orderInput) {
          userSentence = orderInput.value;
        }

        const userNorm = normalize(userSentence);
        if (dropSlot) dropSlot.classList.remove('correct', 'incorrect');
        if (orderInput) orderInput.classList.remove('correct', 'incorrect');

        if (userNorm && acceptedAnswers.includes(userNorm)) {
          if (dropSlot) dropSlot.classList.add('correct');
          if (orderInput) orderInput.classList.add('correct');
          totalCorrect++;
        } else {
          if (dropSlot) dropSlot.classList.add('incorrect');
          if (orderInput) orderInput.classList.add('incorrect');
        }
      });

      // 3. Multiple Choice
      const mcContainers = document.querySelectorAll('.ghibli-mc-container, .mc-options-grid');
      mcContainers.forEach(container => {
        const options = container.querySelectorAll('.ghibli-option');
        if (options.length === 0) return;
        totalItems++;

        options.forEach(opt => opt.classList.remove('correct', 'incorrect'));
        const selected = container.querySelector('.ghibli-option.selected');
        
        let isCorrect = false;
        if (selected) {
          const isSelectedCorrect = selected.getAttribute('data-correct') === 'true';
          if (isSelectedCorrect) {
            selected.classList.add('correct');
            isCorrect = true;
            totalCorrect++;
          } else {
            selected.classList.add('incorrect');
          }
        }

        // Highlight correct option if user chose wrong or nothing
        if (!isCorrect) {
          const correctOpt = container.querySelector('.ghibli-option[data-correct="true"]');
          if (correctOpt) correctOpt.classList.add('correct');
        }
      });

      // 4. Matching Selects
      const matchingSelects = document.querySelectorAll('.ghibli-matching-select[data-correct]');
      matchingSelects.forEach(select => {
        totalItems++;
        const userVal = normalize(select.value);
        const correctVal = normalize(select.getAttribute('data-correct') || '');

        select.classList.remove('correct', 'incorrect');
        if (userVal && userVal === correctVal) {
          select.classList.add('correct');
          totalCorrect++;
        } else {
          select.classList.add('incorrect');
        }
      });

      // 5. True / False Groups
      const tfGroups = document.querySelectorAll('.tf-btn-group');
      tfGroups.forEach(group => {
        const btns = group.querySelectorAll('.tf-btn');
        if (btns.length === 0) return;
        totalItems++;

        btns.forEach(b => b.classList.remove('correct', 'incorrect'));
        const selected = group.querySelector('.tf-btn.selected');

        if (selected) {
          const isSelectedCorrect = selected.getAttribute('data-correct') === 'true';
          if (isSelectedCorrect) {
            selected.classList.add('correct');
            totalCorrect++;
          } else {
            selected.classList.add('incorrect');
          }
        }
      });

      // 6. Sidebar / Word Panel Items (e.g. Page 19 Exercise 4.2)
      const wordItems = document.querySelectorAll('.animal-word-item, .word-panel-item, .ghibli-word-bank-item');
      wordItems.forEach(item => {
        if (item.classList.contains('example-item')) return;

        const rawText = item.getAttribute('data-word') || item.textContent || '';
        const cleanText = normalize(rawText.replace(/[✓✔]/g, '').trim());

        if (cleanText && correctUserAnswers.has(cleanText)) {
          item.classList.add('correct');
          item.style.background = 'rgba(45, 90, 39, 0.18)';
          item.style.color = '#1b4315';
          item.style.borderColor = '#2d5a27';
          item.style.fontWeight = '700';
          item.style.textDecoration = 'line-through';
          item.style.opacity = '0.85';
          item.style.boxShadow = '0 2px 6px rgba(45, 90, 39, 0.15)';
          if (!item.querySelector('.word-check-icon')) {
            const checkIcon = document.createElement('i');
            checkIcon.className = 'fa-solid fa-circle-check word-check-icon';
            checkIcon.style.color = '#2d5a27';
            checkIcon.style.marginLeft = 'auto';
            checkIcon.style.fontSize = '0.9rem';
            item.appendChild(checkIcon);
          }
        } else {
          item.classList.remove('correct');
          item.style.background = '#ffffff';
          item.style.color = '#2b261f';
          item.style.borderColor = 'rgba(45, 90, 39, 0.18)';
          item.style.fontWeight = '600';
          item.style.textDecoration = 'none';
          item.style.opacity = '1.0';
          item.style.boxShadow = '0 1px 3px rgba(0,0,0,0.03)';
          const checkIcon = item.querySelector('.word-check-icon');
          if (checkIcon) checkIcon.remove();
        }
      });

      // Update Score Display Badge
      const scoreBadge = document.querySelector('.ghibli-score-badge, #ghibliScoreBadge');
      const scoreText = document.getElementById('ghibliScoreText');
      if (scoreText) {
        scoreText.textContent = `Score: ${totalCorrect} / ${totalItems}`;
      }
      if (scoreBadge) {
        scoreBadge.classList.remove('bump');
        void scoreBadge.offsetWidth; // Trigger reflow
        scoreBadge.classList.add('bump');
      }

      // Audio & Mascot Feedback
      if (totalItems > 0) {
        if (totalCorrect === totalItems) {
          if (window.GhibliAudio) window.GhibliAudio.playFanfare();
          this.speakMascot(`Magnificent work! 🌿 All ${totalCorrect} answers are correct!`, 6000, 'celebrate');
        } else if (totalCorrect >= totalItems / 2) {
          if (window.GhibliAudio) window.GhibliAudio.playChime();
          this.speakMascot(`Great effort! You scored ${totalCorrect}/${totalItems}. Keep practicing! 🍵`, 5000, 'happy');
        } else {
          if (window.GhibliAudio) window.GhibliAudio.playWaterDrop();
          this.speakMascot(`Don't give up! You scored ${totalCorrect}/${totalItems}. Review the highlighted items and try again. 🍃`, 5000, 'encouragement');
        }
      }
    }

    /* ==========================================================================
       7. Reset Button Logic
       ========================================================================== */
    setupResetButton() {
      document.addEventListener('click', (e) => {
        const resetBtn = e.target.closest('#ghibliResetBtn, .ghibli-reset-btn, .ghibli-reset-btn-bottom');
        if (resetBtn) {
          this.resetPage();
        }
      });
    }

    resetPage() {
      // Clear feedback badges
      document.querySelectorAll('.ghibli-feedback-badge').forEach(badge => badge.remove());

      // Clear inputs
      document.querySelectorAll('.ghibli-input, .ex1-1-input, .order-input').forEach(input => {
        input.value = '';
        input.classList.remove('correct', 'incorrect');
      });

      // Reset option buttons
      document.querySelectorAll('.ghibli-option, .tf-btn').forEach(btn => {
        btn.classList.remove('selected', 'correct', 'incorrect');
      });

      // Reset matching selects
      document.querySelectorAll('.ghibli-matching-select').forEach(select => {
        select.selectedIndex = 0;
        select.classList.remove('correct', 'incorrect');
      });

      // Reset sidebar / word panel items
      document.querySelectorAll('.animal-word-item, .word-panel-item, .ghibli-word-bank-item').forEach(item => {
        if (!item.classList.contains('example-item')) {
          item.classList.remove('correct');
          item.style.background = '#ffffff';
          item.style.color = '#2b261f';
          item.style.borderColor = 'rgba(45, 90, 39, 0.18)';
          item.style.fontWeight = '600';
          item.style.textDecoration = 'none';
          item.style.opacity = '1.0';
          item.style.boxShadow = '0 1px 3px rgba(0,0,0,0.03)';
          const checkIcon = item.querySelector('.word-check-icon');
          if (checkIcon) checkIcon.remove();
        }
      });

      // Reset sentence ordering chips back to pool
      document.querySelectorAll('.ghibli-ordering-container').forEach(container => {
        const pool = container.querySelector('.word-pool');
        const dropSlot = container.querySelector('.ghibli-drop-slot');
        if (pool && dropSlot) {
          const chips = Array.from(dropSlot.querySelectorAll('.word-chip'));
          chips.forEach(chip => pool.appendChild(chip));
          dropSlot.classList.remove('correct', 'incorrect');
        }
      });

      // Reset score badge
      const totalItems = document.querySelectorAll('.ghibli-input[data-correct], .ghibli-ordering-container, .ghibli-mc-container, .ghibli-matching-select[data-correct], .tf-btn-group').length;
      const scoreText = document.getElementById('ghibliScoreText');
      if (scoreText) {
        scoreText.textContent = `Score: 0 / ${totalItems}`;
      }

      if (window.GhibliAudio) window.GhibliAudio.playWaterDrop();
      this.speakMascot("Page reset! Ready for a clean start. 🧹", 4000);
    }

    /* ==========================================================================
       8. Navigation, Quick Page Jump Bar & Keyboard Shortcuts
       ========================================================================== */
    setupKeyboardNavigation() {
      // Inject Quick Page Jump widget into navigation bar if present
      this.injectQuickPageJumpWidget();

      document.addEventListener('keydown', (e) => {
        // Ctrl + J or Alt + J for Quick Jump
        if ((e.ctrlKey || e.altKey) && e.key.toLowerCase() === 'j') {
          e.preventDefault();
          this.promptPageJump();
          return;
        }

        // Ignore arrow navigation if typing in an input box
        const activeEl = document.activeElement;
        if (activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'TEXTAREA' || activeEl.tagName === 'SELECT')) {
          return;
        }

        if (e.key === 'ArrowLeft') {
          const prevBtn = document.querySelector('.chapter-nav-bar a:first-child, .page-turn-bar a:first-child');
          if (prevBtn) prevBtn.click();
        } else if (e.key === 'ArrowRight') {
          const nextBtn = document.querySelector('.chapter-nav-bar a:last-child, .page-turn-bar a:last-child');
          if (nextBtn) nextBtn.click();
        }
      });
    }

    injectQuickPageJumpWidget() {
      const turnBars = document.querySelectorAll('.page-turn-bar, .chapter-nav-bar');
      turnBars.forEach(bar => {
        if (bar.querySelector('.quick-jump-wrap')) return;

        const jumpWrap = document.createElement('div');
        jumpWrap.className = 'quick-jump-wrap';
        jumpWrap.style.cssText = 'display:flex; align-items:center; gap:6px; background:rgba(255,255,255,0.9); padding:4px 10px; border-radius:20px; border:1px solid rgba(0,0,0,0.15);';
        
        jumpWrap.innerHTML = `
          <i class="fa-solid fa-compass" style="color:#2d5a27; font-size:0.9rem;"></i>
          <input type="number" class="quick-jump-input" placeholder="Page #" min="12" max="176" style="width:60px; padding:3px 6px; border-radius:10px; border:1px solid #ccc; font-weight:700; text-align:center; font-size:0.9rem; outline:none;">
          <button class="quick-jump-btn" style="background:#2d5a27; color:#fff; border:none; padding:4px 10px; border-radius:10px; font-weight:700; font-size:0.8rem; cursor:pointer;">Go</button>
        `;

        const input = jumpWrap.querySelector('.quick-jump-input');
        const btn = jumpWrap.querySelector('.quick-jump-btn');

        const doJump = () => {
          const val = parseInt(input.value, 10);
          if (val && val >= 12 && val <= 176) {
            const pageStr = String(val).padStart(3, '0');
            window.location.href = `ghibli_p${pageStr}.html`;
          } else {
            alert('Please enter a page number between 12 and 176!');
          }
        };

        btn.addEventListener('click', doJump);
        input.addEventListener('keydown', (e) => {
          if (e.key === 'Enter') doJump();
        });

        // Insert before badge or middle
        const badge = bar.querySelector('.page-turn-badge');
        if (badge) {
          bar.insertBefore(jumpWrap, badge);
        } else {
          bar.appendChild(jumpWrap);
        }
      });
    }

    promptPageJump() {
      const pageNum = prompt("🌿 Quick Jump: Enter a page number (12 to 176):");
      if (pageNum) {
        const val = parseInt(pageNum.trim(), 10);
        if (val && val >= 12 && val <= 176) {
          const pageStr = String(val).padStart(3, '0');
          window.location.href = `ghibli_p${pageStr}.html`;
        } else {
          alert("Invalid page number! Please enter a number between 12 and 176.");
        }
      }
    }
  }

  const engineInstance = new GhibliPageEngine();
  window.GhibliEngine = engineInstance;
  window.ghibliPageEngineInstance = engineInstance;
})(window, document);
