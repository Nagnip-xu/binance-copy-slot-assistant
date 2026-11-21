'use strict';

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

// A small mobile navigation keeps all destinations available without covering the work.
const menuToggle = $('.menu-toggle');
const mobileNav = $('#mobile-nav');
function closeMenu() {
  menuToggle.setAttribute('aria-expanded', 'false');
  menuToggle.setAttribute('aria-label', '打开导航');
  mobileNav.hidden = true;
}
menuToggle.addEventListener('click', () => {
  const open = menuToggle.getAttribute('aria-expanded') !== 'true';
  menuToggle.setAttribute('aria-expanded', String(open));
  menuToggle.setAttribute('aria-label', open ? '关闭导航' : '打开导航');
  mobileNav.hidden = !open;
});
$$('a', mobileNav).forEach(link => link.addEventListener('click', closeMenu));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && !mobileNav.hidden) {
    closeMenu();
    menuToggle.focus();
  }
});
window.matchMedia('(min-width: 651px)').addEventListener('change', closeMenu);

const shots = {
  desktop: {
    src: 'assets/app-overview.webp', width: 1065, height: 889,
    alt: '桌面控制窗口：上部设置目标，中部查看状态，下部控制任务和阅读日志',
    caption: '桌面控制窗口：设置目标、查看页面响应、控制任务与阅读日志。',
    shortCaption: '桌面控制窗口 · 用户提供的真实运行截图', index: '1 / 2'
  },
  browser: {
    src: 'assets/browser-workflow.webp', width: 1716, height: 893,
    alt: '软件与浏览器联动的真实截图，页面显示带单员项目已满的响应',
    caption: '浏览器联动：软件与网页同时运行，图中展示的是目标满员时的尝试过程。',
    shortCaption: '浏览器联动 · 用户提供的真实运行截图', index: '2 / 2'
  }
};
let currentShot = 'desktop';
const galleryImage = $('#gallery-image');
function selectShot(key, focus = false) {
  currentShot = key;
  const shot = shots[key];
  $$('.gallery-tabs [role="tab"]').forEach(tab => {
    const selected = tab.dataset.shot === key;
    tab.setAttribute('aria-selected', String(selected));
    tab.tabIndex = selected ? 0 : -1;
    if (selected && focus) tab.focus();
  });
  galleryImage.src = shot.src;
  galleryImage.alt = shot.alt;
  galleryImage.width = shot.width;
  galleryImage.height = shot.height;
  $('#gallery-panel').setAttribute('aria-labelledby', `tab-${key}`);
  $('#gallery-caption').textContent = shot.caption;
  $('#gallery-count').textContent = shot.index;
}
$$('.gallery-tabs [role="tab"]').forEach(tab => {
  tab.addEventListener('click', () => selectShot(tab.dataset.shot));
  tab.addEventListener('keydown', event => {
    if (['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) {
      event.preventDefault();
      const key = event.key === 'Home' ? 'desktop' : event.key === 'End' ? 'browser' : currentShot === 'desktop' ? 'browser' : 'desktop';
      selectShot(key, true);
    }
  });
});

const lightbox = $('#lightbox');
let lightboxReturnFocus = null;
let savedOverflow = '';
function openLightbox(src, caption, alt, trigger) {
  lightboxReturnFocus = trigger;
  $('#lightbox-image').src = src;
  $('#lightbox-image').alt = alt;
  $('#lightbox-caption').textContent = caption;
  savedOverflow = document.body.style.overflow;
  document.body.style.overflow = 'hidden';
  lightbox.showModal();
}
$$('[data-lightbox]').forEach(button => button.addEventListener('click', () => {
  openLightbox(button.dataset.lightbox, button.dataset.caption, $('img', button).alt, button);
}));
function openCurrentShot(event) {
  const shot = shots[currentShot];
  openLightbox(shot.src, shot.shortCaption, shot.alt, event.currentTarget);
}
$('#gallery-expand').addEventListener('click', openCurrentShot);
$('#gallery-image-button').addEventListener('click', openCurrentShot);
$('.close-lightbox').addEventListener('click', () => lightbox.close());
lightbox.addEventListener('click', event => {
  if (event.target === lightbox) {
    const box = lightbox.getBoundingClientRect();
    if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) lightbox.close();
  }
});
lightbox.addEventListener('close', () => {
  document.body.style.overflow = savedOverflow;
  lightboxReturnFocus?.focus({preventScroll: true});
});

// Illustrative state only: this site has no account connection or trading requests.
const flowSteps = [
  {
    label: '从这里开始', title: '先把任务交代清楚。',
    description: '在桌面窗口填写交易员 ID、金额与速率，选择浏览器。ID 决定实际目标，名称用于展示。',
    console: '任务参数', rows: [['目标', '由你填写的交易员 ID'], ['浏览器', 'Edge / Chrome'], ['真实提交', 'OFF · 首次运行默认']],
    footer: '等待你在软件中点击「启动」'
  },
  {
    label: '本机连接', title: '打开属于这次任务的浏览器。',
    description: '软件通过本机 CDP 连接独立浏览器。先核实实际页面来源，再在这个窗口登录；日常浏览器的登录态不一定共用。',
    console: '浏览器协作', rows: [['连接', '本机 CDP'], ['账户状态', '需要你在页面中登录'], ['API Key', '无需填写']],
    footer: '网页登录状态由浏览器承载'
  },
  {
    label: '持续观察', title: '让变化有迹可循。',
    description: '本演示将人数读取频率设为每秒10次，展示页面状态、人数变化与日志反馈。人数变化时提醒；监控与提交循环各自独立。',
    console: '页面监控', rows: [['页面状态', '显示在桌面窗口'], ['人数读取', '每秒10次'], ['变化反馈', '日志记录 + 声音提醒']],
    footer: '这里展示机制，不是实时运行数据'
  },
  {
    label: '由你决定', title: '默认监控，保留主动权。',
    description: '真实提交关闭时，可以观察页面与人数状态。需要真实申请时，由你在软件中开启并确认；停止按钮用于停止后续尝试。',
    console: '控制与反馈', rows: [['当前分支', '仅监控'], ['真实提交', 'OFF'], ['任务控制', '可主动停止']],
    footer: '开启下方演示开关，查看另一条分支'
  }
];
let activeStep = 0;
let playTimer = null;
const playButton = $('#demo-play');
const stepButtons = $$('.flow-stop');
function stopPlayback() {
  clearTimeout(playTimer);
  playTimer = null;
  playButton.setAttribute('aria-pressed', 'false');
  $('span', playButton).textContent = '播放流程';
  $('use', playButton).setAttribute('href', '#i-play');
  $('#mechanism').classList.remove('is-playing');
}
function renderStep(index, focus = false) {
  activeStep = index;
  const submitBranch = $('#submit-demo').checked && index === 3;
  const step = submitBranch ? {
    label: '可选的真实提交', title: '确认之后，再尝试申请。',
    description: '真实软件开启此模式后，会按设定速率持续尝试，不以人数先减少为条件。收到成功返回后停止并提醒，最终结果仍需到平台核实。',
    console: '真实提交分支', rows: [['开启方式', '用户确认后开启'], ['循环控制', '共享整体速率限制'], ['成功返回后', '停止尝试并提醒']],
    footer: '此处仅为演示，不会提交任何真实申请'
  } : flowSteps[index];
  stepButtons.forEach((button, buttonIndex) => {
    const selected = buttonIndex === index;
    button.setAttribute('aria-selected', String(selected));
    button.tabIndex = selected ? 0 : -1;
    if (selected && focus) button.focus();
  });
  $('#flow-panel').setAttribute('aria-labelledby', `flow-${index}`);
  $('#flow-progress').style.width = `${index / 3 * 100}%`;
  $('#step-title').textContent = step.title;
  $('#step-description').textContent = step.description;
  $('#console-title').textContent = step.console;
  const rows = $('#console-rows');
  rows.replaceChildren(...step.rows.map(([label, value], rowIndex) => {
    const row = document.createElement('div');
    const term = document.createElement('dt');
    const detail = document.createElement('dd');
    term.textContent = label;
    detail.textContent = value;
    if (rowIndex === 2) detail.classList.add('console-status');
    row.append(term, detail);
    return row;
  }));
  $('#console-footer').textContent = step.footer;
  $('#step-position').textContent = `${index + 1} / 4`;
  $('#next-step').firstChild.textContent = index === 3 ? '回到起点' : '下一步';
}
stepButtons.forEach((button, index) => {
  button.addEventListener('click', () => { stopPlayback(); renderStep(index); });
  button.addEventListener('keydown', event => {
    if (['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) {
      event.preventDefault();
      stopPlayback();
      const next = event.key === 'Home' ? 0 : event.key === 'End' ? 3 : (index + (event.key === 'ArrowRight' ? 1 : 3)) % 4;
      renderStep(next, true);
    }
  });
});
$('#next-step').addEventListener('click', () => { stopPlayback(); renderStep((activeStep + 1) % 4); });
$('#submit-demo').addEventListener('change', () => { stopPlayback(); renderStep(3); });
playButton.addEventListener('click', () => {
  if (playTimer) { stopPlayback(); return; }
  renderStep(0);
  playButton.setAttribute('aria-pressed', 'true');
  $('span', playButton).textContent = '暂停播放';
  $('use', playButton).setAttribute('href', '#i-pause');
  $('#mechanism').classList.add('is-playing');
  const advance = () => {
    if (activeStep === 3) { stopPlayback(); return; }
    renderStep(activeStep + 1);
    playTimer = setTimeout(advance, 3200);
  };
  playTimer = setTimeout(advance, 3200);
});
document.addEventListener('visibilitychange', () => { if (document.hidden) stopPlayback(); });
new IntersectionObserver(entries => {
  if (!entries[0].isIntersecting) stopPlayback();
}, {threshold: 0}).observe($('#mechanism'));

let toastTimer;
function notify(message) {
  const toast = $('#toast');
  toast.textContent = message;
  toast.classList.add('is-visible');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('is-visible'), 3500);
}
$('#copy-start').addEventListener('click', async () => {
  try {
    if (!navigator.clipboard?.writeText) throw new Error('clipboard-unavailable');
    await navigator.clipboard.writeText('START.cmd');
    notify('已复制 START.cmd，在解压后的项目中双击此文件。');
  } catch {
    notify('未能访问剪贴板。请手动复制文件名：START.cmd');
  }
});

// One bounded scroll gesture carries the cover's connecting route; content stays visible.
let scrollQueued = false;
function updateRoute() {
  if (!reducedMotion.matches) {
    const distance = Math.min(window.scrollY, 850);
    document.documentElement.style.setProperty('--route-shift', `${-distance * 0.035}px`);
  }
  scrollQueued = false;
}
window.addEventListener('scroll', () => {
  if (!scrollQueued && window.scrollY < 1100 && !reducedMotion.matches) {
    scrollQueued = true;
    requestAnimationFrame(updateRoute);
  }
}, {passive: true});
reducedMotion.addEventListener('change', () => {
  document.documentElement.style.setProperty('--route-shift', '0px');
});
