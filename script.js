// Инициализация Telegram Web App
if (window.Telegram && window.Telegram.WebApp) {
  const tg = window.Telegram.WebApp;
  tg.ready();
  
  // Применяем тему из Telegram
  if (tg.colorScheme === 'light') {
    document.body.classList.remove('dark-theme');
    document.body.classList.add('light-theme');
  }
}

let currentTemplate = null;
let generatedContent = '';

function startGenerator() {
  document.getElementById('hero').style.display = 'none';
  document.getElementById('templates').style.display = 'block';
}

function openTemplate(type) {
  currentTemplate = type;
  document.getElementById('templates').style.display = 'none';
  document.getElementById('generator').style.display = 'block';
  
  const form = document.getElementById('doc-form');
  form.innerHTML = '';
  
  // Динамически создаём поля в зависимости от типа документа
  const fields = templates[type].fields;
  fields.forEach(field => {
    const label = document.createElement('label');
    label.textContent = field.label;
    
    if (field.type === 'textarea') {
      const textarea = document.createElement('textarea');
      textarea.name = field.name;
      textarea.rows = 4;
      textarea.required = field.required;
      label.appendChild(textarea);
    } else {
      const input = document.createElement('input');
      input.type = field.type;
      input.name = field.name;
      input.required = field.required;
      label.appendChild(input);
    }
    
    form.appendChild(label);
  });
  
  document.getElementById('template-title').textContent = templates[type].title;
}

function closeGenerator() {
  document.getElementById('generator').style.display = 'none';
  document.getElementById('templates').style.display = 'block';
}

function generateDocument() {
  const form = document.getElementById('doc-form');
  const formData = new FormData(form);
  const data = Object.fromEntries(formData);
  
  // Генерируем документ по шаблону
  generatedContent = templates[currentTemplate].generate(data);
  
  document.getElementById('generator').style.display = 'none';
  document.getElementById('result').style.display = 'block';
  document.getElementById('preview').textContent = generatedContent;
  
  // Отправляем событие в аналитику
  trackEvent('document_generated', { type: currentTemplate });
}

function exportPDF() {
  if (!generatedContent) return;
  
  // Используем jsPDF для генерации PDF
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();
  
  const lines = doc.splitTextToSize(generatedContent, 180);
  doc.text(lines, 10, 10);
  
  doc.save(`document-${Date.now()}.pdf`);
  
  trackEvent('export_pdf', { type: currentTemplate });
}

function shareLink() {
  if (!generatedContent) return;
  
  // Создаём уникальный ID для документа
  const id = Math.random().toString(36).substr(2, 9);
  
  // Сохраняем в localStorage (в реальном проекте — в базу)
  localStorage.setItem(`doc_${id}`, JSON.stringify({
    type: currentTemplate,
    content: generatedContent,
    createdAt: new Date().toISOString()
  }));
  
  const url = `${window.location.origin}/share/${id}`;
  
  // Копируем ссылку в буфер обмена
  navigator.clipboard.writeText(url).then(() => {
    alert('Ссылка скопирована! Теперь её можно отправить кому угодно.');
    
    trackEvent('share_link', { type: currentTemplate });
  });
}

function upgradePro() {
  // Здесь будет интеграция с платёжной системой
  alert('Функция Upgrade to Pro будет доступна после подключения платёжной системы.');
  
  trackEvent('upgrade_clicked', { type: currentTemplate });
}

function buyPro() {
  upgradePro();
}

// Аналитика
function trackEvent(event, properties) {
  // В реальном проекте — отправка в Google Analytics/Mixpanel
  console.log('Analytics event:', event, properties);
  
  // Для Telegram Mini App
  if (window.Telegram && window.Telegram.WebApp) {
    window.Telegram.WebApp.sendData(JSON.stringify({ event, properties }));
  }
}

// Загрузка документа по ссылке (для публичных страниц)
function loadSharedDocument(id) {
  const doc = localStorage.getItem(`doc_${id}`);
  if (doc) {
    const parsed = JSON.parse(doc);
    generatedContent = parsed.content;
    currentTemplate = parsed.type;
    
    document.getElementById('result').style.display = 'block';
    document.getElementById('preview').textContent = generatedContent;
    
    trackEvent('view_shared_document', { id, type: currentTemplate });
  } else {
    alert('Документ не найден или был удалён.');
  }
}

// Проверка, загружаем ли мы shared документ
const pathParts = window.location.pathname.split('/');
if (pathParts[1] === 'share' && pathParts[2]) {
  loadSharedDocument(pathParts[2]);
}
