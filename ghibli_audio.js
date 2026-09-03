/* ==========================================================================
   Studio Ghibli Relaxing Audio Engine & Continuous BGM System (ghibli_audio.js)
   Acoustic kalimba, wooden marimba, forest dewdrop clicks & peaceful chimes
   + Continuous Background Music Engine (audio/ghibli_bg_music.wav)
   + Seamless SPA Page Router (uninterrupted music playback across pages)
   ========================================================================== */

(function (window, document) {
  'use strict';

  class StudioGhibliAudio {
    constructor() {
      this.ctx = null;
      this.isMuted = false;
      this.noteIndex = 0;
      this.lastPlayTime = 0;
      
      // Soothing F Major / D Minor Pentatonic Scale for UI clicks (Joe Hisaishi / Ghibli feel)
      this.pentatonicScale = [
        349.23, // F4
        392.00, // G4
        440.00, // A4
        523.25, // C5
        587.33, // D5
        698.46, // F5
        783.99, // G5
        880.00  // A5
      ];

      // Lazy-loaded audio elements as backup fallback
      this._wavClick = null;
      this._wavWaterdrop = null;
      this._wavChime = null;

      // Continuous Background Music System (Compressed MP3 with WAV fallback)
      this.bgmTrack = 'audio/ghibli_bg_music.mp3';
      this.bgmAudio = null;
      this.bgmSaveInterval = null;
      this.isNavigating = false;

      // Initialize audio context & BGM on user interaction
      this._bindUserGesture();

      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => this._onDomReady());
      } else {
        this._onDomReady();
      }
    }

    get wavClick() {
      if (!this._wavClick) this._wavClick = new Audio('audio/ghibli_click.wav');
      return this._wavClick;
    }

    get wavWaterdrop() {
      if (!this._wavWaterdrop) this._wavWaterdrop = new Audio('audio/ghibli_waterdrop.wav');
      return this._wavWaterdrop;
    }

    get wavChime() {
      if (!this._wavChime) this._wavChime = new Audio('audio/ghibli_chime.wav');
      return this._wavChime;
    }

    _onDomReady() {
      this.initBGM();
      this.attachGlobalClickSound();
      this.initSPARouter();
    }

    _initContext() {
      if (!this.ctx) {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (AudioCtx) {
          this.ctx = new AudioCtx();
        }
      }
      if (this.ctx && this.ctx.state === 'suspended') {
        this.ctx.resume();
      }
    }

    _bindUserGesture() {
      const unlock = () => {
        this._initContext();
        if (localStorage.getItem('ghibli_bgm_playing') !== 'false' && this.bgmAudio && this.bgmAudio.paused) {
          this.playBGM();
        }
      };
      
      const events = ['click', 'keydown', 'touchstart', 'pointerdown', 'mousemove', 'scroll', 'mouseenter'];
      events.forEach(evt => {
        document.addEventListener(evt, unlock, { passive: true });
        window.addEventListener(evt, unlock, { passive: true });
      });
    }

    /* ----------------------------------------------------------------
       BACKGROUND MUSIC (BGM) MANAGER
    ---------------------------------------------------------------- */
    initBGM() {
      if (!this.bgmAudio) {
        this.bgmAudio = new Audio(this.bgmTrack);
        this.bgmAudio.loop = true;
        this.bgmAudio.volume = 0.35;
      }

      // Restore position if available
      const savedTime = parseFloat(localStorage.getItem('ghibli_bgm_time') || '0');
      if (!isNaN(savedTime) && savedTime > 0 && this.bgmAudio.currentTime === 0) {
        try { this.bgmAudio.currentTime = savedTime; } catch(e) {}
      }

      // Default BGM to playing on ALL pages unless user explicitly paused it ('false')
      const bgmState = localStorage.getItem('ghibli_bgm_playing');
      if (bgmState !== 'false') {
        localStorage.setItem('ghibli_bgm_playing', 'true');
        this.playBGM();
      } else {
        this.syncBGMButtonState();
      }

      // Periodically update saved playback position
      if (!this.bgmSaveInterval) {
        this.bgmSaveInterval = setInterval(() => {
          if (this.bgmAudio && !this.bgmAudio.paused) {
            localStorage.setItem('ghibli_bgm_time', this.bgmAudio.currentTime);
          }
        }, 1000);
      }
    }

    isBGMPlaying() {
      return localStorage.getItem('ghibli_bgm_playing') === 'true' && this.bgmAudio && !this.bgmAudio.paused;
    }

    playBGM() {
      if (!this.bgmAudio) {
        this.bgmAudio = new Audio(this.bgmTrack);
        this.bgmAudio.loop = true;
        this.bgmAudio.volume = 0.35;
      }

      localStorage.setItem('ghibli_bgm_playing', 'true');
      this._initContext();

      this.bgmAudio.play().then(() => {
        this.syncBGMButtonState();
      }).catch(() => {
        // Will resume on first user interaction gesture
        this.syncBGMButtonState();
      });
    }

    pauseBGM() {
      localStorage.setItem('ghibli_bgm_playing', 'false');
      if (this.bgmAudio) {
        this.bgmAudio.pause();
      }
      this.syncBGMButtonState();
    }

    duckBGM() {
      if (this.bgmAudio && !this.bgmAudio.paused) {
        this._prevBgmVol = this.bgmAudio.volume;
        this.bgmAudio.volume = 0.05;
      }
    }

    unduckBGM() {
      if (this.bgmAudio && !this.bgmAudio.paused) {
        this.bgmAudio.volume = this._prevBgmVol || 0.35;
      }
    }

    toggleBGM(btnElement = null) {
      const isPlaying = localStorage.getItem('ghibli_bgm_playing') === 'true' && this.bgmAudio && !this.bgmAudio.paused;
      if (isPlaying) {
        this.pauseBGM();
      } else {
        this.playBGM();
      }
      this.syncBGMButtonState(btnElement);
    }

    syncBGMButtonState(targetBtn = null) {
      const isPlaying = localStorage.getItem('ghibli_bgm_playing') === 'true';
      const buttons = document.querySelectorAll('#toggleAmbientBtn, .bgm-toggle-btn');
      
      buttons.forEach(btn => {
        if (isPlaying) {
          btn.classList.add('active');
          btn.innerHTML = '<i class="fa-solid fa-music"></i> <span class="bgm-btn-text">Music: Playing 🎵</span>';
          btn.style.background = 'var(--ghibli-accent-gold, #e5a93c)';
          btn.style.color = '#fff';
        } else {
          btn.classList.remove('active');
          btn.innerHTML = '<i class="fa-solid fa-music"></i> <span class="bgm-btn-text">Music: Off</span>';
          btn.style.background = '';
          btn.style.color = '';
        }
      });
    }

    /* ----------------------------------------------------------------
       CONTINUOUS SPA PAGE ROUTER
       Note: Flawed innerHTML swapper is safely disabled to prevent
       script execution failures, CSS mismatches, and memory leaks.
       Pages perform reliable native document transitions, while
       ghibli_reader.html serves as the seamless continuous music host.
    ---------------------------------------------------------------- */
    initSPARouter() {
      // Intentionally bypassed: native document navigation guarantees full
      // stylesheet loading and complete script execution without weird loading bugs.
    }

    /**
     * Play relaxing wooden kalimba / marimba click note
     * Cycles through pentatonic scale for a soothing musical interaction
     */
    playClick() {
      if (this.isMuted) return;

      // Debounce rapid multi-clicks (under 50ms)
      const nowMs = Date.now();
      if (nowMs - this.lastPlayTime < 50) return;
      this.lastPlayTime = nowMs;

      this._initContext();

      if (!this.ctx) {
        // Fallback to WAV audio
        this.wavClick.currentTime = 0;
        this.wavClick.play().catch(() => {});
        return;
      }

      try {
        const now = this.ctx.currentTime;
        const freq = this.pentatonicScale[this.noteIndex % this.pentatonicScale.length];
        this.noteIndex++;

        // Lowpass Acoustic Wooden Filter (warm, soft, no digital sharpness)
        const filter = this.ctx.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(2100, now);
        filter.Q.setValueAtTime(1.2, now);

        // Master Envelope Gain
        const masterGain = this.ctx.createGain();
        masterGain.gain.setValueAtTime(0.001, now);
        masterGain.gain.linearRampToValueAtTime(0.075, now + 0.004); // 4ms soft attack
        masterGain.gain.exponentialRampToValueAtTime(0.0001, now + 0.18); // 180ms kalimba decay

        // Harmonics: Fundamental + 2nd Harmonic + 3rd Harmonic (Acoustic Wood body)
        const harmonics = [
          { mult: 1.0, amp: 1.0 },
          { mult: 2.0, amp: 0.32 },
          { mult: 3.0, amp: 0.10 }
        ];

        harmonics.forEach(h => {
          const osc = this.ctx.createOscillator();
          const oscGain = this.ctx.createGain();

          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq * h.mult, now);
          oscGain.gain.setValueAtTime(h.amp, now);

          osc.connect(oscGain);
          oscGain.connect(filter);
          osc.start(now);
          osc.stop(now + 0.2);
        });

        filter.connect(masterGain);
        masterGain.connect(this.ctx.destination);
      } catch (e) {
        this.wavClick.currentTime = 0;
        this.wavClick.play().catch(() => {});
      }
    }

    /**
     * Play soft forest dewdrop water click sound (for toggles, inputs, pins)
     */
    playWaterDrop() {
      if (this.isMuted) return;
      this._initContext();

      if (!this.ctx) {
        this.wavWaterdrop.currentTime = 0;
        this.wavWaterdrop.play().catch(() => {});
        return;
      }

      try {
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        const filter = this.ctx.createBiquadFilter();

        // Dewdrop pitch envelope glide upward
        osc.type = 'sine';
        osc.frequency.setValueAtTime(360, now);
        osc.frequency.exponentialRampToValueAtTime(560, now + 0.035);

        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(1400, now);
        filter.Q.setValueAtTime(3.0, now); // Resonant water body

        gain.gain.setValueAtTime(0.001, now);
        gain.gain.linearRampToValueAtTime(0.09, now + 0.003);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.08);

        osc.connect(filter);
        filter.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(now);
        osc.stop(now + 0.09);
      } catch (e) {
        this.wavWaterdrop.currentTime = 0;
        this.wavWaterdrop.play().catch(() => {});
      }
    }

    /**
     * Play relaxing acoustic glass/piano chime
     */
    playChime(freqs = [523.25, 659.25, 783.99], duration = 0.35) {
      if (this.isMuted) return;
      this._initContext();

      if (!this.ctx) {
        this.wavChime.currentTime = 0;
        this.wavChime.play().catch(() => {});
        return;
      }

      try {
        const freqsArray = Array.isArray(freqs) ? freqs : [freqs];
        freqsArray.forEach((freq, idx) => {
          const startTime = this.ctx.currentTime + idx * 0.07;
          const osc = this.ctx.createOscillator();
          const osc2 = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          const filter = this.ctx.createBiquadFilter();

          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, startTime);

          osc2.type = 'sine';
          osc2.frequency.setValueAtTime(freq * 2.001, startTime); // Subtle chorus overtone

          filter.type = 'lowpass';
          filter.frequency.setValueAtTime(2800, startTime);

          gain.gain.setValueAtTime(0.001, startTime);
          gain.gain.linearRampToValueAtTime(0.08, startTime + 0.01);
          gain.gain.exponentialRampToValueAtTime(0.0001, startTime + duration);

          osc.connect(filter);
          osc2.connect(filter);
          filter.connect(gain);
          gain.connect(this.ctx.destination);

          osc.start(startTime);
          osc2.start(startTime);
          osc.stop(startTime + duration + 0.05);
          osc2.stop(startTime + duration + 0.05);
        });
      } catch (e) {
        this.wavChime.currentTime = 0;
        this.wavChime.play().catch(() => {});
      }
    }

    /**
     * Play lush celebration fanfare
     */
    playFanfare() {
      // Fmaj7 / Cmaj7 arpeggio: C5, E5, G5, B5, C6
      this.playChime([523.25, 659.25, 783.99, 987.77, 1046.50], 0.45);
    }

    /**
     * Attach global click sound handler to all interactive UI elements
     */
    attachGlobalClickSound() {
      document.addEventListener('click', (e) => {
        const target = e.target;
        if (!target) return;

        const interactiveEl = target.closest(
          'button, a, input[type="button"], input[type="submit"], input[type="checkbox"], input[type="radio"], select, .btn, .card, .sticker-card, .audio-pin, .nav-item, .tab, [role="button"], .interactive, .clickable, .exercise-option, .matching-item'
        );

        if (interactiveEl) {
          // Do not play click sound over exercise audio or voice recorder buttons
          if (interactiveEl.closest('.ghibli-audio-play-btn, .ghibli-audio-btn, .rec-btn, .play-rec-btn, .voice-btn, [data-audio]')) {
            return;
          }

          // If checkbox or toggle, use waterdrop sound for variety
          if (interactiveEl.tagName === 'INPUT' && (interactiveEl.type === 'checkbox' || interactiveEl.type === 'radio')) {
            this.playWaterDrop();
          } else {
            this.playClick();
          }
        }
      }, true); // Use capture phase so all clicks get lush sound feedback!
    }
  }

  // Create global singleton instance
  const instance = new StudioGhibliAudio();
  window.GhibliAudio = instance;

  // Expose global shorthand helper functions for existing script compatibility
  window.playGhibliClick = function () { instance.playClick(); };
  window.playGhibliWaterdrop = function () { instance.playWaterDrop(); };
  window.playChimeSound = function (freq = 523.25, duration = 0.2) { instance.playChime(freq, duration); };
  window.playFanfareChime = function () { instance.playFanfare(); };

  window.getChartAudioPath = function (sentence) {
    return 'audio/3/3_3_a.mp3';
  };

})(window, document);


