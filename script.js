const app = {
  data: {
    orders: [],
    specs: [],
    learns: [],
    lang: localStorage.getItem('kadr_lang') || 'ru',
    theme: localStorage.getItem('kadr_theme') || 'light',
    role: 'executor'
  },

  translations: {
    ru: {
      nav_orders: "Заказы", nav_specialists: "Специалисты", nav_learning: "Обучение",
      hero_title: "Находи заказы. Собирай команду.",
      hero_subtitle: "Платформа для специалистов кино и видеопроизводства.",
      btn_find_order: "Найти заказ", btn_find_spec: "Найти специалиста", btn_how_it_works: "Как это работает ↓",
      status_active: "Активен", demo_title: "Монтажёр для короткометражки", tag_edit: "Монтаж", tag_cinema: "Кино",
      feat_title: "Что можно сделать?",
      feat_1_title: "Найти заказ", feat_1_desc: "Просматривай проекты и откликайся.", btn_view_orders: "Смотреть заказы",
      feat_2_title: "Найти специалиста", feat_2_desc: "Каталог профессионалов.", btn_view_specs: "Открыть каталог",
      feat_3_title: "Развиваться", feat_3_desc: "Гайды и материалы.", btn_view_learn: "Перейти к материалам",
      how_title: "Как это работает", role_exec: "Я исполнитель", role_client: "Я заказчик",
      step_e1_h: "Создай профиль", step_e1_p: "Добавь портфолио.",
      step_e2_h: "Отправь отклик", step_e2_p: "Напиши сопроводительное.",
      step_e3_h: "Начни работу", step_e3_p: "Обсуди детали.",
      step_c1_h: "Размести задачу", step_c1_p: "Опиши проект.",
      step_c2_h: "Выбери кандидата", step_c2_p: "Изучи отклики.",
      step_c3_h: "Свяжись", step_c3_p: "Начни сотрудничество.",
      sec_orders: "Биржа заказов", btn_post_order: "+ Разместить",
      sec_specs: "Специалисты", btn_create_prof: "+ Профиль",
      sec_learn: "Обучение",
      cat_all: "Все", cat_dir: "Режиссёр", cat_edit: "Монтажёр", cat_op: "Оператор",
      empty_orders: "Пока нет заказов.", btn_create_first: "Разместить заказ",
      cta_title: "Начни со своей задачи",
      footer_desc: "Платформа для кинопрофессионалов.",
      foot_nav: "Навигация", foot_home: "Главная", foot_orders: "Заказы", foot_specs: "Специалисты",
      foot_docs: "Документы", doc_terms: "Соглашение", doc_privacy: "Конфиденциальность",
      foot_contact: "Контакты", foot_rights: "Все права защищены.",
      modal_order_title: "Разместить заказ", lbl_title: "Название", lbl_desc: "Описание", lbl_spec: "Специальность", lbl_budget: "Бюджет", btn_publish: "Опубликовать",
      modal_prof_title: "Профиль специалиста", lbl_name: "Имя", btn_create: "Создать"
    },
    en: {
      nav_orders: "Jobs", nav_specialists: "Specialists", nav_learning: "Learning",
      hero_title: "Find Jobs. Build Teams.",
      hero_subtitle: "Platform for cinema and video production professionals.",
      btn_find_order: "Find Job", btn_find_spec: "Find Specialist", btn_how_it_works: "How it Works ↓",
      status_active: "Active", demo_title: "Editor for Short Film", tag_edit: "Editing", tag_cinema: "Cinema",
      feat_title: "What can you do?",
      feat_1_title: "Find Job", feat_1_desc: "Browse projects and apply.", btn_view_orders: "View Jobs",
      feat_2_title: "Find Specialist", feat_2_desc: "Catalog of professionals.", btn_view_specs: "Open Catalog",
      feat_3_title: "Learn", feat_3_desc: "Guides and materials.", btn_view_learn: "Go to Materials",
      how_title: "How it Works", role_exec: "I am Freelancer", role_client: "I am Client",
      step_e1_h: "Create Profile", step_e1_p: "Add portfolio.",
      step_e2_h: "Apply", step_e2_p: "Send cover letter.",
      step_e3_h: "Start Work", step_e3_p: "Discuss details.",
      step_c1_h: "Post Task", step_c1_p: "Describe project.",
      step_c2_h: "Choose Candidate", step_c2_p: "Review applications.",
      step_c3_h: "Contact", step_c3_p: "Start cooperation.",
      sec_orders: "Job Board", btn_post_order: "+ Post",
      sec_specs: "Specialists", btn_create_prof: "+ Profile",
      sec_learn: "Learning",
      cat_all: "All", cat_dir: "Director", cat_edit: "Editor", cat_op: "Operator",
      empty_orders: "No jobs yet.", btn_create_first: "Post Job",
      cta_title: "Start with your task",
      footer_desc: "Platform for cinema professionals.",
      foot_nav: "Navigation", foot_home: "Home", foot_orders: "Jobs", foot_specs: "Specialists",
      foot_docs: "Documents", doc_terms: "Terms", doc_privacy: "Privacy",
      foot_contact: "Contacts", foot_rights: "All rights reserved.",
      modal_order_title: "Post Job", lbl_title: "Title", lbl_desc: "Description", lbl_spec: "Specialization", lbl_budget: "Budget", btn_publish: "Publish",
      modal_prof_title: "Specialist Profile", lbl_name: "Name", btn_create: "Create"
    },
    zh: {
      nav_orders: "工作", nav_specialists: "专家", nav_learning: "学习",
      hero_title: "寻找订单。组建团队。",
      hero_subtitle: "电影和视频制作专业人士平台。",
      btn_find_order: "找订单", btn_find_spec: "找专家", btn_how_it_works: "如何运作 ↓",
      status_active: "活跃", demo_title: "短片剪辑师", tag_edit: "剪辑", tag_cinema: "电影",
      feat_title: "你能做什么？",
      feat_1_title: "找订单", feat_1_desc: "浏览项目并申请。", btn_view_orders: "查看工作",
      feat_2_title: "找专家", feat_2_desc: "专业人士目录。", btn_view_specs: "打开目录",
      feat_3_title: "学习", feat_3_desc: "指南和资料。", btn_view_learn: "前往资料",
      how_title: "如何运作", role_exec: "我是自由职业者", role_client: "我是客户",
      step_e1_h: "创建资料", step_e1_p: "添加作品集。",
      step_e2_h: "申请", step_e2_p: "发送求职信。",
      step_e3_h: "开始工作", step_e3_p: "讨论细节。",
      step_c1_h: "发布任务", step_c1_p: "描述项目。",
      step_c2_h: "选择候选人", step_c2_p: "审查申请。",
      step_c3_h: "联系", step_c3_p: "开始合作。",
      sec_orders: "工作看板", btn_post_order: "+ 发布",
      sec_specs: "专家", btn_create_prof: "+ 资料",
      sec_learn: "学习",
      cat_all: "全部", cat_dir: "导演", cat_edit: "剪辑师", cat_op: "摄影师",
      empty_orders: "暂无订单。", btn_create_first: "发布订单",
      cta_title: "从你的任务开始",
      footer_desc: "电影专业人士平台。",
      foot_nav: "导航", foot_home: "首页", foot_orders: "工作", foot_specs: "专家",
      foot_docs: "文档", doc_terms: "条款", doc_privacy: "隐私",
      foot_contact: "联系方式", foot_rights: "版权所有。",
      modal_order_title: "发布订单", lbl_title: "标题", lbl_desc: "描述", lbl_spec: "专业", lbl_budget: "预算", btn_publish: "发布",
      modal_prof_title: "专家资料", lbl_name: "姓名", btn_create: "创建"
    }
  },

  init() {
    this.applyTheme();
    this.setLanguage(this.data.lang);
    this.loadData();
    this.renderAll();
    this.setupListeners();
    document.getElementById('year').textContent = new Date().getFullYear();
  },

  setupListeners() {
    // Theme Toggle
    document.getElementById('theme-btn').addEventListener('click', () => {
      this.data.theme = this.data.theme === 'light' ? 'dark' : 'light';
      localStorage.setItem('kadr_theme', this.data.theme);
      this.applyTheme();
    });

    // Lang Toggle
    document.getElementById('lang-btn').addEventListener('click', (e) => {
      e.stopPropagation();
      document.getElementById('lang-menu').classList.toggle('active');
    });
    document.addEventListener('click', () => document.getElementById('lang-menu').classList.remove('active'));
  },

  applyTheme() {
    const body = document.body;
    const sun = document.querySelector('.sun-icon');
    const moon = document.querySelector('.moon-icon');
    
    if (this.data.theme === 'dark') {
      body.classList.add('dark-theme');
      body.classList.remove('light-theme');
      sun.style.display = 'none';
      moon.style.display = 'block';
      document.querySelector('meta[name="theme-color"]').setAttribute('content', '#101722');
    } else {
      body.classList.add('light-theme');
      body.classList.remove('dark-theme');
      sun.style.display = 'block';
      moon.style.display = 'none';
      document.querySelector('meta[name="theme-color"]').setAttribute('content', '#F3F6FB');
    }
  },

  setLanguage(lang) {
    this.data.lang = lang;
    localStorage.setItem('kadr_lang', lang);
    document.getElementById('lang-btn').textContent = lang.toUpperCase() + ' ▾';
    
    const t = this.translations[lang];
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (t[key]) el.textContent = t[key];
    });
    
    // Update placeholders
    document.querySelector('.filter-input').placeholder = lang === 'ru' ? 'Поиск...' : (lang === 'en' ? 'Search...' : '搜索...');
    this.renderAll(); // Re-render cards with translated categories/statuses
  },

  loadData() {
    // Demo Data
    if (!localStorage.getItem('kadr_orders')) {
      this.data.orders = [
        { id: 1, title: 'Рекламный ролик', desc: 'Нужен режиссёр для съёмки.', spec: 'director', budget: 'med' },
        { id: 2, title: 'Свадебный фильм', desc: 'Монтаж исходников.', spec: 'editor', budget: 'low' }
      ];
      this.data.specs = [
        { id: 1, name: 'Алексей С.', spec: 'director', about: 'Опыт 5 лет.' },
        { id: 2, name: 'Мария К.', spec: 'editor', about: 'Premiere Pro, DaVinci.' }
      ];
      this.data.learns = [
        { id: 1, title: 'Основы света', desc: 'Как ставить свет в помещении.' },
        { id: 2, title: 'Монтаж за час', desc: 'Быстрый монтаж для соцсетей.' }
      ];
      localStorage.setItem('kadr_orders', JSON.stringify(this.data.orders));
      localStorage.setItem('kadr_specs', JSON.stringify(this.data.specs));
      localStorage.setItem('kadr_learns', JSON.stringify(this.data.learns));
    } else {
      this.data.orders = JSON.parse(localStorage.getItem('kadr_orders'));
      this.data.specs = JSON.parse(localStorage.getItem('kadr_specs'));
      this.data.learns = JSON.parse(localStorage.getItem('kadr_learns'));
    }
  },

  renderAll() {
    this.renderOrders(this.data.orders);
    this.renderSpecs(this.data.specs);
    this.renderLearns(this.data.learns);
  },

  renderOrders(list) {
    const container = document.getElementById('ordersList');
    const empty = document.getElementById('emptyOrders');
    if (list.length === 0) { container.innerHTML = ''; empty.style.display = 'block'; return; }
    empty.style.display = 'none';
    
    const t = this.translations[this.data.lang];
    container.innerHTML = list.map(o => `
      <div class="card-item glass-panel">
        <h3>${o.title}</h3>
        <p style="color:var(--text-sec); font-size:14px; margin:8px 0;">${o.desc}</p>
        <div class="tags">
          <span class="tag">${o.spec === 'director' ? t.cat_dir : t.cat_edit}</span>
          <span class="tag">${o.budget === 'med' ? '30-100к' : 'до 30к'}</span>
        </div>
        <button class="btn btn-secondary" style="margin-top:12px; width:100%" onclick="app.notify('${t.btn_view_orders}')">${t.btn_view_orders}</button>
      </div>
    `).join('');
  },

  renderSpecs(list) {
    const container = document.getElementById('specsList');
    const t = this.translations[this.data.lang];
    container.innerHTML = list.map(s => `
      <div class="card-item glass-panel">
        <h3>${s.name}</h3>
        <p style="color:var(--accent); font-weight:600; font-size:14px; margin-bottom:8px;">${s.spec === 'director' ? t.cat_dir : t.cat_edit}</p>
        <p style="color:var(--text-sec); font-size:14px;">${s.about}</p>
        <button class="btn btn-secondary" style="margin-top:12px; width:100%" onclick="app.notify('Профиль ${s.name}')">Профиль</button>
      </div>
    `).join('');
  },

  renderLearns(list) {
    const container = document.getElementById('learnList');
    container.innerHTML = list.map(l => `
      <div class="card-item glass-panel">
        <h3>${l.title}</h3>
        <p style="color:var(--text-sec); font-size:14px;">${l.desc}</p>
        <button class="btn btn-secondary" style="margin-top:12px; width:100%" onclick="app.notify('Открываем материал...')">Читать</button>
      </div>
    `).join('');
  },

  filterOrders() {
    const txt = document.getElementById('orderSearch').value.toLowerCase();
    const spec = document.getElementById('orderSpecFilter').value;
    const filtered = this.data.orders.filter(o => 
      o.title.toLowerCase().includes(txt) && 
      (spec === '' || o.spec === spec)
    );
    this.renderOrders(filtered);
  },

  filterSpecs(cat) {
    document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
    
    if (cat === 'all') this.renderSpecs(this.data.specs);
    else this.renderSpecs(this.data.specs.filter(s => s.spec === cat));
  },

  switchRole(role) {
    this.data.role = role;
    document.querySelectorAll('.switch-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
    
    document.querySelectorAll('.steps-list').forEach(l => l.classList.remove('active'));
    document.querySelector(`.${role}-steps`).classList.add('active');
  },

  toggleMobileMenu() {
    const m = document.getElementById('mobileMenu');
    m.classList.toggle('active');
    document.body.style.overflow = m.classList.contains('active') ? 'hidden' : '';
  },
  
  closeMobileMenu() {
    this.toggleMobileMenu();
  },

  openModal(id) { document.getElementById(id).classList.add('active'); },
  closeModal(id) { document.getElementById(id).classList.remove('active'); },
  
  scrollToId(id) {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
    this.closeMobileMenu();
  },
  
  scrollToTop() { window.scrollTo({ top: 0, behavior: 'smooth' }); },

  createOrder(e) {
    e.preventDefault();
    const fd = new FormData(e.target);
    const newOrder = {
      id: Date.now(),
      title: fd.get('title'),
      desc: fd.get('desc'),
      spec: fd.get('spec'),
      budget: fd.get('budget')
    };
    this.data.orders.unshift(newOrder);
    localStorage.setItem('kadr_orders', JSON.stringify(this.data.orders));
    this.renderOrders(this.data.orders);
    this.closeModal('orderModal');
    e.target.reset();
    this.notify('Заказ опубликован!');
  },

  createProfile(e) {
    e.preventDefault();
    const fd = new FormData(e.target);
    const newSpec = {
      id: Date.now(),
      name: fd.get('name'),
      spec: fd.get('spec'),
      about: 'Новый специалист.'
    };
    this.data.specs.unshift(newSpec);
    localStorage.setItem('kadr_specs', JSON.stringify(this.data.specs));
    this.renderSpecs(this.data.specs);
    this.closeModal('profileModal');
    e.target.reset();
    this.notify('Профиль создан!');
  },

  notify(msg) {
    const area = document.getElementById('notifyArea');
    const n = document.createElement('div');
    n.className = 'notify';
    n.textContent = msg;
    area.appendChild(n);
    setTimeout(() => n.remove(), 3000);
  }
};

// Start App
document.addEventListener('DOMContentLoaded', () => app.init());
