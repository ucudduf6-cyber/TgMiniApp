const translations = {
  ru: {
    hero_title: "Профессиональные документы для кино — за 2 минуты",
    hero_subtitle: "Сценарии, брифы, ТЗ. Бесплатно. Без регистрации.",
    btn_start: "Начать сейчас",
    select_template: "Выберите тип документа",
    type_script: "Сценарий", desc_script: "Стандарты индустрии",
    type_brief: "Бриф", desc_brief: "Для заказчика",
    type_tz: "Тех. задание", desc_tz: "Для съемочной группы",
    type_content: "Контент-план", desc_content: "Для соцсетей",
    btn_back: "Назад",
    btn_generate: "Сгенерировать",
    btn_cancel: "Отмена",
    res_title: "Ваш документ готов!",
    btn_pdf: "Скачать PDF",
    btn_share: "Поделиться ссылкой",
    btn_pro: "Upgrade PRO",
    btn_new: "Создать новый",
    pricing_title: "Тарифы",
    feat_basic: "Базовые шаблоны",
    feat_export: "Экспорт PDF",
    feat_all: "Все шаблоны",
    feat_logo: "Свой логотип",
    feat_support: "Приоритет",
    btn_buy: "Купить"
  },
  en: {
    hero_title: "Professional Film Docs in 2 Minutes",
    hero_subtitle: "Scripts, briefs, specs. Free. No registration.",
    btn_start: "Start Now",
    select_template: "Select Document Type",
    type_script: "Script", desc_script: "Industry standards",
    type_brief: "Brief", desc_brief: "For clients",
    type_tz: "Tech Spec", desc_tz: "For crew",
    type_content: "Content Plan", desc_content: "For social media",
    btn_back: "Back",
    btn_generate: "Generate",
    btn_cancel: "Cancel",
    res_title: "Your document is ready!",
    btn_pdf: "Download PDF",
    btn_share: "Share Link",
    btn_pro: "Upgrade PRO",
    btn_new: "Create New",
    pricing_title: "Pricing",
    feat_basic: "Basic templates",
    feat_export: "PDF Export",
    feat_all: "All templates",
    feat_logo: "Custom logo",
    feat_support: "Priority support",
    btn_buy: "Buy"
  },
  zh: {
    hero_title: "2分钟内生成专业电影文档",
    hero_subtitle: "剧本、简报、技术规格。免费。无需注册。",
    btn_start: "立即开始",
    select_template: "选择文档类型",
    type_script: "剧本", desc_script: "行业标准",
    type_brief: "简报", desc_brief: "给客户",
    type_tz: "技术规格", desc_tz: "给剧组",
    type_content: "内容计划", desc_content: "社交媒体",
    btn_back: "返回",
    btn_generate: "生成",
    btn_cancel: "取消",
    res_title: "文档已准备就绪！",
    btn_pdf: "下载 PDF",
    btn_share: "分享链接",
    btn_pro: "升级专业版",
    btn_new: "创建新文档",
    pricing_title: "价格方案",
    feat_basic: "基础模板",
    feat_export: "导出 PDF",
    feat_all: "所有模板",
    feat_logo: "自定义 Logo",
    feat_support: "优先支持",
    btn_buy: "购买"
  }
};

let currentLang = 'ru';

function setLanguage(lang) {
  currentLang = lang;
  document.getElementById('current-lang').textContent = lang.toUpperCase();
  document.getElementById('lang-menu').classList.remove('active');
  
  const elements = document.querySelectorAll('[data-key]');
  elements.forEach(el => {
    const key = el.getAttribute('data-key');
    if (translations[lang][key]) {
      el.textContent = translations[lang][key];
    }
  });
  
  // Обновляем плейсхолдеры форм, если нужно
  updateFormLabels();
}

function toggleLangMenu() {
  document.getElementById('lang-menu').classList.toggle('active');
}

document.getElementById('lang-btn').addEventListener('click', (e) => {
  e.stopPropagation();
  toggleLangMenu();
});

document.addEventListener('click', () => {
  document.getElementById('lang-menu').classList.remove('active');
});
