// The player: builds the deck from data.js, keeps audio and slides in
// step, and owns the transport. Audio is the clock - a section ends when
// its narration ends - so a 2x listen stays perfectly in sync without a
// second set of timings.

(function () {
  const stage = document.getElementById('stage');
  const chapterList = document.getElementById('chapters');
  const playButton = document.getElementById('play');
  const prevButton = document.getElementById('prev');
  const nextButton = document.getElementById('next');
  const speedButton = document.getElementById('speed');
  const scrub = document.getElementById('scrub');
  const scrubFill = document.getElementById('scrub-fill');
  const timeLabel = document.getElementById('time');
  const audio = document.getElementById('narration');

  let current = 0;
  let fastMode = false;

  // ===== build =====

  function el(tag, className, html) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (html !== undefined) node.innerHTML = html;
    return node;
  }

  function buildMetrics(metrics) {
    const wrap = el('div', 'metrics');
    metrics.forEach((metric) => {
      const box = el('div', 'metric' + (metric.tone ? ' ' + metric.tone : ''));
      box.appendChild(el('div', 'value', metric.value));
      box.appendChild(el('div', 'label', metric.label));
      wrap.appendChild(box);
    });
    return wrap;
  }

  function buildBars(bars) {
    const wrap = el('div', 'bars');
    bars.forEach((bar) => {
      const row = el('div', 'bar-row' + (bar.tone ? ' ' + bar.tone : ''));
      row.appendChild(el('div', 'name', bar.name));
      const track = el('div', 'bar-track');
      const fill = el('div', 'bar-fill');
      fill.style.setProperty('--pct', Math.max(0, Math.min(100, bar.pct)) + '%');
      track.appendChild(fill);
      row.appendChild(track);
      row.appendChild(el('div', 'num', bar.readout));
      wrap.appendChild(row);
    });
    return wrap;
  }

  function buildLadder(rungs) {
    const wrap = el('div', 'ladder');
    rungs.forEach((rung) => {
      wrap.appendChild(el('span', 'rung' + (rung.state ? ' ' + rung.state : ''), rung.text));
    });
    return wrap;
  }

  function buildWall(wall) {
    const wrap = el('div', 'wall');
    const attempts = el('div', 'attempts');
    wall.attacks.forEach((text) => attempts.appendChild(el('div', 'chip attack', text)));
    wrap.appendChild(attempts);
    wrap.appendChild(el('div', 'barrier', wall.barrier));
    const outcomes = el('div', 'outcomes');
    wall.held.forEach((text) => outcomes.appendChild(el('div', 'chip held', text)));
    wrap.appendChild(outcomes);
    return wrap;
  }

  function buildTable(table) {
    const wrap = el('div', 'table-wrap');
    const node = el('table');
    const head = el('thead');
    const headRow = el('tr');
    table.columns.forEach((column, index) => {
      headRow.appendChild(el('th', index > 0 ? 'num' : '', column));
    });
    head.appendChild(headRow);
    node.appendChild(head);
    const body = el('tbody');
    table.rows.forEach((row) => {
      const tr = el('tr');
      row.forEach((cell, index) => {
        tr.appendChild(el('td', index > 0 ? 'num' : '', cell));
      });
      body.appendChild(tr);
    });
    node.appendChild(body);
    wrap.appendChild(node);
    return wrap;
  }

  function buildFiles(files) {
    const wrap = el('div', 'files');
    files.forEach((file) => {
      const link = el('a', 'file-link', file.label);
      link.href = file.href;
      link.target = '_blank';
      link.rel = 'noopener';
      wrap.appendChild(link);
    });
    return wrap;
  }

  function buildShot(shot) {
    const figure = el('figure');
    const image = el('img', 'shot');
    image.src = shot.src;
    image.alt = shot.alt;
    image.loading = 'lazy';
    figure.appendChild(image);
    if (shot.caption) figure.appendChild(el('figcaption', '', shot.caption));
    return figure;
  }

  DECK.forEach((section, index) => {
    const slide = el('section', 'slide');
    slide.id = 'slide-' + index;
    slide.setAttribute('aria-label', section.title);

    slide.appendChild(el('div', 'eyebrow', section.eyebrow));
    slide.appendChild(el('h2', '', section.title));
    if (section.lede) slide.appendChild(el('p', 'lede', section.lede));
    (section.body || []).forEach((paragraph) => slide.appendChild(el('p', '', paragraph)));
    if (section.metrics) slide.appendChild(buildMetrics(section.metrics));
    if (section.bars) slide.appendChild(buildBars(section.bars));
    if (section.ladder) slide.appendChild(buildLadder(section.ladder));
    if (section.wall) slide.appendChild(buildWall(section.wall));
    if (section.table) slide.appendChild(buildTable(section.table));
    if (section.shot) slide.appendChild(buildShot(section.shot));
    if (section.files) slide.appendChild(buildFiles(section.files));

    stage.appendChild(slide);

    const item = el('li');
    const button = el('button', 'chapter');
    button.type = 'button';
    button.appendChild(el('span', 'chapter-num', String(index + 1).padStart(2, '0')));
    button.appendChild(el('span', '', section.title));
    button.addEventListener('click', () => go(index, true));
    item.appendChild(button);
    chapterList.appendChild(item);
  });

  const slides = Array.from(stage.querySelectorAll('.slide'));
  const chapterButtons = Array.from(chapterList.querySelectorAll('.chapter'));

  // ===== transport =====

  function formatTime(seconds) {
    if (!isFinite(seconds)) return '0:00';
    const whole = Math.max(0, Math.floor(seconds));
    return Math.floor(whole / 60) + ':' + String(whole % 60).padStart(2, '0');
  }

  function go(index, autoplay) {
    if (index < 0 || index >= slides.length) return;
    current = index;
    slides.forEach((slide, i) => slide.classList.toggle('active', i === index));
    chapterButtons.forEach((button, i) => {
      button.setAttribute('aria-current', i === index ? 'true' : 'false');
      button.classList.toggle('done', i < index);
    });
    // Re-trigger the entrance choreography
    const active = slides[index];
    active.style.animation = 'none';
    void active.offsetWidth;
    active.style.animation = '';

    const track = DECK[index].audio;
    if (track) {
      audio.src = track;
      audio.playbackRate = fastMode ? 2 : 1;
      if (autoplay !== false) {
        audio.play().catch(() => {
          /* autoplay blocked until a user gesture - controls still work */
        });
      }
    } else {
      audio.removeAttribute('src');
    }
    updateProgress();
  }

  function updateProgress() {
    const ratio = audio.duration ? audio.currentTime / audio.duration : 0;
    scrubFill.style.width = (ratio * 100).toFixed(2) + '%';
    timeLabel.textContent =
      formatTime(audio.currentTime) +
      ' / ' +
      formatTime(audio.duration) +
      '  ·  ' +
      (current + 1) +
      '/' +
      slides.length;
  }

  playButton.addEventListener('click', () => {
    if (audio.paused) {
      audio.play().catch(() => {});
    } else {
      audio.pause();
    }
  });

  audio.addEventListener('play', () => {
    playButton.textContent = 'Pause';
  });
  audio.addEventListener('pause', () => {
    playButton.textContent = 'Play';
  });
  audio.addEventListener('timeupdate', updateProgress);
  audio.addEventListener('loadedmetadata', updateProgress);
  audio.addEventListener('ended', () => {
    if (current < slides.length - 1) go(current + 1, true);
  });

  prevButton.addEventListener('click', () => go(current - 1, !audio.paused));
  nextButton.addEventListener('click', () => go(current + 1, !audio.paused));

  speedButton.addEventListener('click', () => {
    fastMode = !fastMode;
    audio.playbackRate = fastMode ? 2 : 1;
    speedButton.setAttribute('aria-pressed', String(fastMode));
    speedButton.textContent = fastMode ? '2× speed' : '1× speed';
  });

  scrub.addEventListener('click', (event) => {
    if (!audio.duration) return;
    const bounds = scrub.getBoundingClientRect();
    audio.currentTime = ((event.clientX - bounds.left) / bounds.width) * audio.duration;
  });

  document.addEventListener('keydown', (event) => {
    if (event.target.tagName === 'INPUT') return;
    if (event.code === 'Space') {
      event.preventDefault();
      playButton.click();
    } else if (event.code === 'ArrowRight') {
      nextButton.click();
    } else if (event.code === 'ArrowLeft') {
      prevButton.click();
    }
  });

  go(0, false);
})();
