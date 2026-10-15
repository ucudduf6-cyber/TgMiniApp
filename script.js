// --- ТЕМА ---
const themeToggle = document.getElementById('theme-toggle');
const body = document.body;
const icon = themeToggle.querySelector('i');

// Проверка сохраненной темы
if (localStorage.getItem('theme') === 'dark') {
  body.classList.add('dark-theme');
  body.classList.remove('light-theme');
  icon.classList.replace('fa-moon', 'fa-sun');
}

themeToggle.addEventListener('click', () => {
  body.classList.toggle('dark-theme');
  body.classList.toggle('light-theme');
  
  if (body.classList.contains('dark-theme')) {
    icon.classList.replace('fa-moon', 'fa-sun');
    localStorage.setItem('theme', 'dark');
  } else {
    icon.classList.replace('fa-sun', 'fa-moon');
    localStorage.setItem('theme', 'light');
  }
});

// --- НАВИГАЦИЯ ---
function startGenerator() {
  document.getElementById('hero').style.display = 'none';
  document.getElementById('templates').style.display = 'block';
}

function goHome() {
  document.getElementById('templates').style.display = 'none';
  document.getElementById('hero').style.display = 'block';
  closeGenerator();
  closeResult();
}

function openTemplate(type) {
  document.getElementById('templates').style.display = 'none';
  document.getElementById('generator').style.display = 'block';
  
  const form = document.getElementById('doc-form');
  form.innerHTML = '';
  
  const titles = {
    script: translations[currentLang].type_script,
    brief: translations[currentLang].type_brief,
    tz: translations[currentLang].type_tz,
    content: translations[currentLang].type_content
  };
  
  document.getElementById('template-title').textContent = titles[type] || 'Document';
  
  // Пример полей (можно расширить)
  const fields = [
    { name: 'title', label: 'Название / Title', type: 'text' },
    { name: 'description', label: 'Описание / Description', type: 'textarea' }
  ];
  
  fields.forEach(f => {
    const label = document.createElement('label');
    label.textContent = f.label;
    
    let input;
    if (f.type === 'textarea') {
      input = document.createElement('textarea');
    } else {
      input = document.createElement('input');
      input.type = f.type;
    }
    input.name = f.name;
    input.required = true;
    
    label.appendChild(input);
    form.appendChild(label);
  });
}

function closeGenerator() {
  document.getElementById('generator').style.display = 'none';
  document.getElementById('templates').style.display = 'block';
}

function generateDocument() {
  const form = document.getElementById('doc-form');
  const formData = new FormData(form);
  const title = formData.get('title');
  const desc = formData.get('description');
  
  const content = `
=== ${title.toUpperCase()} ===
Дата: ${new Date().toLocaleDateString()}
Автор: Vlad Rozhentsev (via Scenarist.PRO)

ОПИСАНИЕ:
${desc}

---
Сгенерировано в Scenarist.PRO
  `.trim();
  
  document.getElementById('generator').style.display = 'none';
  document.getElementById('result').style.display = 'block';
  document.getElementById('preview').textContent = content;
}

function closeResult() {
  document.getElementById('result').style.display = 'none';
  document.getElementById('templates').style.display = 'block';
}

// --- ЭКСПОРТ И ШЕРИНГ ---
function exportPDF() {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();
  const text = document.getElementById('preview').textContent;
  
  doc.setFont("courier"); // Моноширинный шрифт для сценариев
  const splitText = doc.splitTextToSize(text, 180);
  doc.text(splitText, 10, 10);
  doc.save("document.pdf");
}

function shareLink() {
  const text = document.getElementById('preview').textContent;
  // В реальном проекте тут отправка на сервер и получение ссылки
  // Пока эмулируем копирование текста
  navigator.clipboard.writeText(text).then(() => {
    alert(currentLang === 'ru' ? 'Текст скопирован!' : 'Text copied!');
  });
}

function upgradePro() {
  alert("Payment integration coming soon (Boosty/Tinkoff)");
}

function buyPro() {
  upgradePro();
}

function updateFormLabels() {
  // Можно добавить логику перевода лейблов полей при смене языка
}
