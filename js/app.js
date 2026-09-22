const API_BASE = window.KAMBA_API || 'http://127.0.0.1:5000/api';

const modal = document.getElementById('modal');
const content = document.getElementById('modalContent');

function openModal(type) {
  if (!modal || !content) return;
  if (type !== 'support') return;

  content.innerHTML = `
    <h2>Falar com o suporte</h2>
    <div class="modal-form">
      <input id="supportName" placeholder="Nome completo">
      <input id="supportContact" placeholder="Email ou telefone">
      <select id="supportTopic">
        <option>Ajuda com o aplicativo</option>
        <option>Conta e acesso</option>
        <option>Pedido ou proposta</option>
        <option>Contrato</option>
        <option>Segurança ou reclamação</option>
        <option>Outro assunto</option>
      </select>
      <textarea id="supportMessage" placeholder="Descreve a situação ou a tua dúvida"></textarea>
      <button class="btn primary" id="supportBtn">Enviar mensagem</button>
      <span class="modal-note" id="supportStatus"></span>
    </div>`;

  modal.classList.add('open');

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
        'Não foi possível enviar agora. Tenta novamente ou liga para o apoio Kamba.';
    } finally {
      button.disabled = false;
      button.textContent = 'Enviar mensagem';
    }
  });
}

document.querySelectorAll('[data-modal]').forEach(button => {
  button.addEventListener('click', () => openModal(button.dataset.modal));
});

document.querySelectorAll('.close').forEach(button => {
  button.addEventListener('click', () => modal?.classList.remove('open'));
});

modal?.addEventListener('click', event => {
  if (event.target === modal) {
    modal.classList.remove('open');
  }
});


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
