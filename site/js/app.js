const modal=document.getElementById('modal');
const content=document.getElementById('modalContent');

function openModal(type){
  if(!modal||!content)return;
  if(type!=='support')return;
  content.innerHTML=`
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
  document.getElementById('supportBtn')?.addEventListener('click',()=>{
    const name=document.getElementById('supportName').value.trim();
    const contact=document.getElementById('supportContact').value.trim();
    const message=document.getElementById('supportMessage').value.trim();
    const status=document.getElementById('supportStatus');
    if(!name||!contact||!message){
      status.textContent='Preenche o nome, contacto e mensagem.';
      return;
    }
    status.textContent='Mensagem preparada. A integração de atendimento será ligada ao sistema Kamba.';
  });
}

document.querySelectorAll('[data-modal]').forEach(b=>{
  b.addEventListener('click',()=>openModal(b.dataset.modal));
});

document.querySelectorAll('.close').forEach(b=>{
  b.addEventListener('click',()=>modal?.classList.remove('open'));
});

modal?.addEventListener('click',e=>{
  if(e.target===modal)modal.classList.remove('open');
});

const helpFilter=document.getElementById('helpFilter');
const helpCategory=document.getElementById('helpCategory');
const helpGrid=document.getElementById('helpGrid');

function applyHelpFilters(){
  if(!helpGrid)return;
  const term=(helpFilter?.value||'').toLowerCase().trim();
  const cat=helpCategory?.value||'Todos';
  helpGrid.querySelectorAll('.help-item').forEach(item=>{
    const text=item.innerText.toLowerCase();
    const okText=!term||text.includes(term);
    const okCat=cat==='Todos'||item.dataset.cat===cat||item.dataset.cat==='Todos';
    item.style.display=okText&&okCat?'flex':'none';
  });
}

helpFilter?.addEventListener('input',applyHelpFilters);
helpCategory?.addEventListener('change',applyHelpFilters);
applyHelpFilters();

const helpSearch=document.getElementById('helpSearch');
const helpSearchBtn=document.getElementById('helpSearchBtn');

function searchHelp(){
  const q=helpSearch?.value.trim()||'';
  if(q)location.href='servicos.html?q='+encodeURIComponent(q);
  else location.href='servicos.html';
}

helpSearchBtn?.addEventListener('click',searchHelp);
helpSearch?.addEventListener('keydown',e=>{
  if(e.key==='Enter')searchHelp();
});

const params=new URLSearchParams(location.search);
const q=params.get('q');
if(helpFilter&&q){
  helpFilter.value=q;
  applyHelpFilters();
}
