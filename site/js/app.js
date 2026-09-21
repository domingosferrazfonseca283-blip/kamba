const modal=document.getElementById('modal');const content=document.getElementById('modalContent');
const API_BASE=window.KAMBA_API||'http://127.0.0.1:5000/api';

function openModal(type){
 if(!modal||!content)return;
 const forms={
  login:{title:'Entrar no Kamba',body:'<div class="modal-form"><input placeholder="Email ou telefone"><input type="password" placeholder="Palavra-passe"><button class="btn primary">Entrar</button></div>'},
  signup:{title:'Criar conta',body:'<div class="modal-form"><input id="signupName" placeholder="Nome completo"><input id="signupPhone" placeholder="Telefone"><input id="signupEmail" placeholder="Email"><select id="signupRole"><option value="client">Quero contratar serviços</option><option value="professional">Quero prestar serviços</option><option value="both">Ambos</option></select><button class="btn primary" id="signupBtn">Criar conta</button><span class="modal-note" id="signupStatus"></span></div>'},
  details:{title:'Publicar pedido',body:'<div class="modal-form"><select id="requestService"><option>Eletricidade</option><option>Canalização</option><option>Reparações</option><option>Limpeza</option><option>Tecnologia</option><option>Design</option></select><textarea id="requestDescription" placeholder="Descreve o serviço que precisas"></textarea><input id="requestLocation" placeholder="Localização"><input id="requestBudget" type="number" placeholder="Orçamento (Kz)"><input id="requestDate" type="date"><button class="btn primary" id="requestBtn">Publicar pedido</button><span class="modal-note" id="requestStatus"></span></div>'},
  pro:{title:'Criar perfil profissional',body:'<div class="modal-form"><input placeholder="Nome profissional"><input placeholder="Especialidade"><input placeholder="Localização"><input placeholder="Preço inicial (Kz)"><textarea placeholder="Fala sobre os teus serviços"></textarea><button class="btn primary">Criar perfil</button></div>'},
  support:{title:'Falar com o suporte',body:'<div class="modal-form"><input placeholder="Nome"><input placeholder="Email ou telefone"><textarea placeholder="Descreve o que aconteceu"></textarea><button class="btn primary">Enviar mensagem</button></div>'}
 };
 const f=forms[type]||forms.login;
 content.innerHTML='<h2>'+f.title+'</h2>'+f.body;modal.classList.add('open');
 if(type==='signup')document.getElementById('signupBtn')?.addEventListener('click',createUser);
 if(type==='details')document.getElementById('requestBtn')?.addEventListener('click',publishRequest);
}

async function createUser(){
 const status=document.getElementById('signupStatus');
 const body={name:document.getElementById('signupName').value.trim(),phone:document.getElementById('signupPhone').value.trim(),email:document.getElementById('signupEmail').value.trim()||null,role:document.getElementById('signupRole').value};
 if(!body.name||!body.phone){status.textContent='Nome e telefone são obrigatórios.';return}
 try{
  const res=await fetch(API_BASE+'/users',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const data=await res.json(); if(!res.ok)throw new Error(data.error||'Não foi possível criar a conta.');
  localStorage.setItem('kambaUser',JSON.stringify(data)); status.textContent='Conta criada com sucesso.';
 }catch(e){status.textContent='API indisponível. Inicia o backend no Termux.';}
}

async function publishRequest(){
 const status=document.getElementById('requestStatus');
 let user=JSON.parse(localStorage.getItem('kambaUser')||'null');
 if(!user){
  status.textContent='Primeiro cria uma conta no Kamba.';
  return;
 }
 const body={client_id:user.id,service:document.getElementById('requestService').value,description:document.getElementById('requestDescription').value.trim(),location:document.getElementById('requestLocation').value.trim(),budget:document.getElementById('requestBudget').value||null,date:document.getElementById('requestDate').value||null};
 if(!body.description||!body.location){status.textContent='Preenche a descrição e a localização.';return}
 try{
  const res=await fetch(API_BASE+'/requests',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const data=await res.json();if(!res.ok)throw new Error(data.error||'Erro ao publicar.');
  status.textContent='Pedido publicado! ID #'+data.id;
 }catch(e){status.textContent='Não foi possível publicar. Confirma se a API está ligada.';}
}

document.querySelectorAll('[data-modal]').forEach(b=>b.addEventListener('click',()=>openModal(b.dataset.modal)));
document.querySelectorAll('.close').forEach(b=>b.addEventListener('click',()=>modal?.classList.remove('open')));
modal?.addEventListener('click',e=>{if(e.target===modal)modal.classList.remove('open')});
document.getElementById('publishBtn')?.addEventListener('click',()=>openModal('details'));
document.getElementById('searchBtn')?.addEventListener('click',()=>{const q=document.getElementById('serviceSearch')?.value.trim();if(q)location.href='servicos.html?q='+encodeURIComponent(q);else location.href='servicos.html'});

const params=new URLSearchParams(location.search);const cat=params.get('cat');const q=params.get('q');const filter=document.getElementById('catFilter');const search=document.getElementById('serviceSearch');if(filter&&cat)filter.value=cat;if(search&&q)search.value=q;
function applyFilters(){document.querySelectorAll('.service-item').forEach(el=>{const okCat=!filter||filter.value==='Todos'||el.dataset.cat===filter.value;const term=(search?.value||'').toLowerCase();const okQ=!term||el.innerText.toLowerCase().includes(term);el.style.display=okCat&&okQ?'flex':'none'})}
filter?.addEventListener('change',applyFilters);search?.addEventListener('input',applyFilters);if(filter||search)applyFilters();
