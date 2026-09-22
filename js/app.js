const isLocalHost = ['localhost', '127.0.0.1'].includes(location.hostname);
const API_BASE = window.KAMBA_API || (isLocalHost ? 'http://127.0.0.1:5000/api' : '');

const modal = document.getElementById('modal');
const content = document.getElementById('modalContent');
let lastFocusedElement = null;

function openModal(type) {
  if (!modal || !content) return;
  if (type !== 'support') return;

  content.innerHTML = `
    <h2 id="supportDialogTitle">Falar com o suporte</h2>
    <div class="modal-form">
      <label for="supportName">Nome completo</label>
      <input id="supportName" placeholder="Nome completo" autocomplete="name">
      <label for="supportContact">Email ou telefone</label>
      <input id="supportContact" placeholder="Email ou telefone" autocomplete="email">
      <label for="supportTopic">Assunto</label>
      <select id="supportTopic">
        <option>Ajuda com o aplicativo</option>
        <option>Conta e acesso</option>
        <option>Pedido ou proposta</option>
        <option>Contrato</option>
        <option>Segurança ou reclamação</option>
        <option>Outro assunto</option>
      </select>
      <label for="supportMessage">Mensagem</label>
      <textarea id="supportMessage" placeholder="Descreve a situação ou a tua dúvida"></textarea>
      <button type="button" class="btn primary" id="supportBtn">Enviar mensagem</button>
      <span class="modal-note" id="supportStatus" aria-live="polite"></span>
    </div>`;

  lastFocusedElement = document.activeElement;
  modal.setAttribute('role', 'dialog');
  modal.setAttribute('aria-modal', 'true');
  modal.setAttribute('aria-labelledby', 'supportDialogTitle');
  modal.classList.add('open');
  document.getElementById('supportName')?.focus();

  document.getElementById('supportBtn')?.addEventListener('click', async () => {
    const name = document.getElementById('supportName').value.trim();
    const contact = document.getElementById('supportContact').value.trim();
    const topic = document.getElementById('supportTopic').value;
    const message = document.getElementById('supportMessage').value.trim();
    const status = document.getElementById('supportStatus');
    const button = document.getElementById('supportBtn');

    if (!name || !contact || !message) {
      status.textContent = 'Preenche o nome, contacto e mensagem.';
      return;
    }

    button.disabled = true;
    button.textContent = 'A enviar...';
    status.textContent = '';

    try {
      if (!API_BASE) {
        throw new Error('API de suporte ainda não configurada neste domínio.');
      }

      const response = await fetch(`${API_BASE}/support`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name,
          contact,
          topic,
          message
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Não foi possível enviar a mensagem.');
      }

      status.textContent =
        `Mensagem enviada com sucesso. Número do atendimento: #${data.ticket.id}.`;

      document.getElementById('supportName').value = '';
      document.getElementById('supportContact').value = '';
      document.getElementById('supportMessage').value = '';

    } catch (error) {
      status.textContent =
        'O formulário está temporariamente indisponível. Usa um dos telefones de apoio abaixo ou tenta novamente mais tarde.';
    } finally {
      button.disabled = false;
      button.textContent = 'Enviar mensagem';
    }
  });
}

document.querySelectorAll('[data-modal]').forEach(button => {
  button.addEventListener('click', () => openModal(button.dataset.modal));
});

function closeModal() {
  if (!modal) return;
  modal.classList.remove('open');
  lastFocusedElement?.focus?.();
}

document.querySelectorAll('.close').forEach(button => {
  button.setAttribute('type', 'button');
  button.addEventListener('click', closeModal);
});

modal?.addEventListener('click', event => {
  if (event.target === modal) {
    closeModal();
  }
});


const searchInput = document.getElementById('helpSearch');
const searchButton = document.getElementById('helpSearchBtn');
const filterInput = document.getElementById('helpFilter');
const filterSelect = document.getElementById('helpCategory');

[searchInput, filterInput].forEach(input => {
  if (input) input.setAttribute('aria-label', input.getAttribute('placeholder') || 'Pesquisar');
});
searchButton?.setAttribute('type', 'button');
filterSelect?.setAttribute('aria-label', 'Filtrar temas da central de ajuda');

const helpFilter = document.getElementById('helpFilter');
const helpCategory = document.getElementById('helpCategory');
const helpGrid = document.getElementById('helpGrid');

function applyHelpFilters() {
  if (!helpGrid) return;

  const term = (helpFilter?.value || '').toLowerCase().trim();
  const category = helpCategory?.value || 'Todos';

  helpGrid.querySelectorAll('.help-item').forEach(item => {
    const text = item.innerText.toLowerCase();
    const okText = !term || text.includes(term);
    const okCategory =
      category === 'Todos' ||
      item.dataset.cat === category ||
      item.dataset.cat === 'Todos';

    item.style.display = okText && okCategory ? 'flex' : 'none';
  });
}

helpFilter?.addEventListener('input', applyHelpFilters);
helpCategory?.addEventListener('change', applyHelpFilters);
applyHelpFilters();


const helpSearch = document.getElementById('helpSearch');
const helpSearchBtn = document.getElementById('helpSearchBtn');

function searchHelp() {
  const query = helpSearch?.value.trim() || '';

  if (query) {
    location.href = 'servicos.html?q=' + encodeURIComponent(query);
  } else {
    location.href = 'servicos.html';
  }
}

helpSearchBtn?.addEventListener('click', searchHelp);

helpSearch?.addEventListener('keydown', event => {
  if (event.key === 'Enter') {
    searchHelp();
  }
});


const params = new URLSearchParams(location.search);
const query = params.get('q');

if (helpFilter && query) {
  helpFilter.value = query;
  applyHelpFilters();
}


/* Navegação móvel */
const topbar = document.querySelector('.topbar');
const menuButton = document.querySelector('.menu');
const siteNav = topbar?.querySelector('nav');

if (siteNav) siteNav.id = 'site-nav';
if (menuButton) {
  menuButton.type = 'button';
  menuButton.setAttribute('aria-controls', 'site-nav');
}

menuButton?.addEventListener('click', () => {
  const open = topbar?.classList.toggle('mobile-open');
  menuButton.setAttribute('aria-expanded', String(Boolean(open)));
  menuButton.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu');
});

document.querySelectorAll('.topbar nav a, .topbar .actions a').forEach(link => {
  link.addEventListener('click', () => {
    topbar?.classList.remove('mobile-open');
    menuButton?.setAttribute('aria-expanded', 'false');
    menuButton?.setAttribute('aria-label', 'Abrir menu');
  });
});

document.addEventListener('keydown', event => {
  if (event.key === 'Escape') {
    if (modal?.classList.contains('open')) {
      closeModal();
      return;
    }
    topbar?.classList.remove('mobile-open');
    menuButton?.setAttribute('aria-expanded', 'false');
    menuButton?.setAttribute('aria-label', 'Abrir menu');
  }
});
