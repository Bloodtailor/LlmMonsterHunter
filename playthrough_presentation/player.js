// Keyframe player: one narrated section at a time, screenshots advancing
// on fractions of the audio's duration. Each keyframe gets a slow
// Ken Burns drift (alternating directions) so the deck reads as motion,
// not a slideshow. Keyboard: space play/pause, arrows change section.

const stage = document.getElementById('stage');
const caption = document.getElementById('caption');
const chaptersEl = document.getElementById('chapters');
const audio = document.getElementById('narration');
const playBtn = document.getElementById('play');
const timeEl = document.getElementById('time');
const scrub = document.getElementById('scrub');
const scrubFill = document.getElementById('scrub-fill');
const titleEl = document.getElementById('slide-title');
const eyebrowEl = document.getElementById('slide-eyebrow');

let current = -1;
let activeKey = -1;
let started = false;

function fmt(seconds) {
  if (!isFinite(seconds)) return '0:00';
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${String(s).padStart(2, '0')}`;
}

function buildChapters() {
  DECK.forEach((slide, i) => {
    const li = document.createElement('li');
    const button = document.createElement('button');
    button.type = 'button';
    button.innerHTML = `<span class="num">${slide.n}</span>${slide.title}`;
    button.addEventListener('click', () => load(i, true));
    li.appendChild(button);
    chaptersEl.appendChild(li);
  });
}

function markChapter() {
  [...chaptersEl.children].forEach((li, i) =>
    li.classList.toggle('active', i === current)
  );
}

function load(index, autoplay) {
  current = Math.max(0, Math.min(DECK.length - 1, index));
  const slide = DECK[current];
  activeKey = -1;

  eyebrowEl.textContent = slide.eyebrow;
  titleEl.textContent = slide.title;

  // Fresh stack of keyframe layers; first one activates on timeupdate 0
  stage.innerHTML = '';
  slide.keys.forEach((key, i) => {
    const layer = document.createElement('div');
    layer.className = 'layer';
    const img = document.createElement('img');
    img.src = key.img;
    img.alt = key.cap || slide.title;
    layer.appendChild(img);
    stage.appendChild(layer);
    void i;
  });

  audio.src = slide.audio;
  markChapter();
  showKey(0);
  if (autoplay && started) audio.play().catch(() => {});
}

function showKey(index) {
  const slide = DECK[current];
  if (index === activeKey || index >= slide.keys.length) return;
  activeKey = index;
  [...stage.children].forEach((layer, i) => {
    layer.classList.toggle('active', i === index);
    // Alternate the drift direction so consecutive frames feel distinct
    layer.classList.remove('kb-a', 'kb-b');
    if (i === index) layer.classList.add(index % 2 === 0 ? 'kb-a' : 'kb-b');
  });
  caption.textContent = slide.keys[index].cap || '';
  caption.classList.remove('pop');
  void caption.offsetWidth; // restart the caption animation
  caption.classList.add('pop');
}

function tick() {
  const dur = audio.duration || 0;
  const t = audio.currentTime || 0;
  timeEl.textContent = `${fmt(t)} / ${fmt(dur)}`;
  scrubFill.style.width = dur ? `${(t / dur) * 100}%` : '0%';
  if (!dur) return;
  const slide = DECK[current];
  const frac = t / dur;
  let next = 0;
  for (let i = 0; i < slide.keys.length; i += 1) {
    if (frac >= slide.keys[i].at) next = i;
  }
  showKey(next);
}

playBtn.addEventListener('click', () => {
  started = true;
  if (audio.paused) audio.play();
  else audio.pause();
});

audio.addEventListener('play', () => {
  playBtn.textContent = 'Pause';
  document.body.classList.add('playing');
});
audio.addEventListener('pause', () => {
  playBtn.textContent = 'Play';
  document.body.classList.remove('playing');
});
audio.addEventListener('timeupdate', tick);
audio.addEventListener('loadedmetadata', tick);
audio.addEventListener('ended', () => {
  if (current < DECK.length - 1) load(current + 1, true);
  else playBtn.textContent = 'Replay';
});

document.getElementById('prev').addEventListener('click', () => load(current - 1, true));
document.getElementById('next').addEventListener('click', () => load(current + 1, true));

scrub.addEventListener('click', (event) => {
  const rect = scrub.getBoundingClientRect();
  const frac = (event.clientX - rect.left) / rect.width;
  if (audio.duration) audio.currentTime = frac * audio.duration;
});

document.addEventListener('keydown', (event) => {
  if (event.key === ' ') {
    event.preventDefault();
    playBtn.click();
  } else if (event.key === 'ArrowRight') load(current + 1, true);
  else if (event.key === 'ArrowLeft') load(current - 1, true);
});

buildChapters();
load(0, false);
