# Kamba — Descrição Técnica do Projeto

**Tipo de solução:** marketplace digital de serviços  
**Mercado inicial:** Angola  
**Idioma principal:** Português  
**Moeda de referência:** Kwanza (AOA)  
**Estado:** especificação funcional e técnica proposta para orientar o desenvolvimento

## 1. Visão geral

A Kamba é uma plataforma digital que conecta pessoas e organizações que necessitam de serviços a profissionais independentes e empresas que os prestam. O sistema organiza as principais etapas da relação comercial: publicação de pedidos, receção de propostas, comparação, seleção do prestador, formalização dos termos e acompanhamento do trabalho.

A solução funciona como um marketplace de dois lados: o cliente procura e contrata; o prestador apresenta competências, responde a oportunidades e gere os serviços aceites. Um painel administrativo permite à equipa Kamba supervisionar utilizadores, conteúdos e ocorrências.

## 2. Problema e objetivos

### Problema a resolver

A procura e a contratação de serviços podem estar dispersas por contactos pessoais, chamadas, redes sociais e negociações sem registo central. Isso dificulta encontrar profissionais, comparar condições, organizar compromissos e acompanhar o trabalho. Do lado dos prestadores, a dependência de recomendações e redes informais pode limitar a divulgação e a captação de clientes.

### Objetivos

- Facilitar a descoberta de profissionais por categoria e localização.
- Permitir pedidos com descrição, imagens, localização, orçamento indicativo e prazo.
- Permitir propostas estruturadas de preço, prazo e condições.
- Manter pedidos, propostas, decisões e acordos organizados num histórico.
- Disponibilizar acompanhamento do estado dos serviços e comunicação entre as partes.
- Criar mecanismos de avaliação e gestão administrativa.

## 3. Público-alvo e perfis de acesso

### Cliente
Cria conta, gere o perfil, pesquisa categorias, publica pedidos, recebe e compara propostas, seleciona prestadores, consulta acordos, acompanha serviços e pode avaliar ou reportar ocorrências.

### Prestador
Cria perfil profissional ou empresarial, indica categorias, competências e área de atuação, consulta pedidos, envia propostas, gere serviços aceites e atualiza o progresso.

### Administrador
Gere contas, categorias e conteúdos; analisa denúncias; modera perfis; acompanha pedidos e indicadores; gere permissões e consulta registos de auditoria.

## 4. Módulos funcionais

1. **Registo e autenticação:** registo de clientes e prestadores, início e encerramento de sessão, recuperação de acesso e gestão de perfil, com permissões por tipo de conta.
2. **Catálogo e pesquisa:** categorias e subcategorias, pesquisa por palavra-chave e filtros de localização e especialidade. A estrutura deve permitir adicionar categorias.
3. **Pedidos de serviço:** formulário com descrição, categoria, localização, prazo, orçamento indicativo e anexos. O cliente consulta o estado e o histórico.
4. **Propostas e negociação:** prestadores enviam preço, prazo estimado, descrição, validade e condições. O cliente compara e seleciona propostas.
5. **Acordos e contratos:** registo dos termos aceites, incluindo escopo, preço, prazo e responsabilidades. A validade jurídica e os requisitos de assinatura eletrónica devem ser avaliados segundo a legislação aplicável.
6. **Acompanhamento:** estados padronizados, por exemplo: pedido publicado, propostas recebidas, prestador selecionado, acordado, em execução, concluído ou cancelado. As alterações relevantes ficam no histórico.
7. **Comunicação e notificações:** mensagens relacionadas com pedidos e notificações sobre propostas, alterações de estado e mensagens.
8. **Avaliações e reclamações:** avaliação após conclusão, denúncia de problemas e análise administrativa.
9. **Painel administrativo:** gestão de utilizadores, prestadores, categorias, pedidos, denúncias, avaliações e indicadores operacionais.

## 5. Fluxo operacional principal

1. O cliente cria uma conta e publica um pedido com os detalhes necessários.
2. O sistema disponibiliza o pedido aos prestadores elegíveis por categoria e área de atuação.
3. Os prestadores interessados submetem propostas com preço, prazo e condições.
4. O cliente consulta e compara as propostas e seleciona um prestador.
5. As partes confirmam os termos do serviço, que ficam registados na plataforma.
6. O prestador atualiza o progresso e o cliente acompanha o estado do trabalho.
7. O serviço é marcado como concluído; as partes consultam o histórico e o cliente pode avaliar.

O fluxo deve prever pedidos sem propostas, propostas recusadas, alterações acordadas, cancelamentos e reclamações. As regras de cancelamento, reembolso e resolução de conflitos devem ser definidas antes do lançamento.

## 6. Arquitetura técnica proposta

Recomenda-se uma arquitetura modular, separando interface, lógica de negócio e persistência de dados. A escolha final das tecnologias deve considerar orçamento, equipa, custos de operação, manutenção e escala.

| Camada | Responsabilidade | Opção técnica indicativa |
|---|---|---|
| Frontend | Interface web responsiva para telemóvel, tablet e computador | React / Next.js ou equivalente |
| Backend / API | Autenticação, regras de negócio, pedidos, propostas, contratos, notificações e administração | Node.js / NestJS, Django ou Laravel |
| Base de dados | Contas, serviços, propostas, acordos e histórico | PostgreSQL ou equivalente |
| Ficheiros | Armazenamento de imagens e documentos com controlo de acesso | Armazenamento compatível com S3 |
| Infraestrutura | Alojamento, backups, monitorização e distribuição | Cloud ou infraestrutura gerida |

Estas tecnologias são referências de implementação, não uma declaração de que a plataforma já foi construída com elas. A solução deverá expor APIs documentadas e permitir evolução para aplicação móvel.

## 7. Modelo de dados — entidades principais

- **Utilizador:** identificação, contactos, credenciais protegidas, tipo de conta, estado e datas.
- **Perfil profissional:** nome comercial, descrição, competências, categorias, zona de atuação, documentos de validação e disponibilidade.
- **Categoria:** nome, descrição, categoria superior e estado.
- **Pedido:** cliente, categoria, descrição, localização, orçamento, prazo, anexos e estado.
- **Proposta:** pedido, prestador, preço, prazo, condições, validade e estado.
- **Acordo/contrato:** partes, escopo, valor, prazo, condições, versão e registos de aceitação.
- **Serviço:** pedido aceite, responsáveis, estado, datas e histórico de progresso.
- **Mensagem/notificação:** remetente, destinatário, contexto, conteúdo, data e estado de leitura/entrega.
- **Avaliação/reclamação:** serviço, autor, classificação, comentário, estado de análise e resolução.
- **Registo de auditoria:** utilizador, ação, recurso afetado, data e metadados relevantes.

## 8. Segurança, privacidade e confiança

- Aplicar controlo de acesso por função e verificar permissões no servidor.
- Guardar palavras-passe com hashing seguro; nunca armazenar credenciais em texto simples.
- Utilizar HTTPS/TLS, validação de dados e limitação de tentativas de autenticação.
- Restringir o acesso a documentos e imagens e validar formatos e tamanhos de ficheiros.
- Manter cópias de segurança, registos de auditoria e procedimentos de recuperação.
- Recolher apenas dados pessoais necessários e definir prazos de retenção.
- Estabelecer processos de denúncia, moderação e resposta a incidentes.

A implementação deverá ser revista à luz da legislação angolana aplicável à proteção de dados, comércio eletrónico, defesa do consumidor, contratação e pagamentos. Este documento não constitui parecer jurídico.

## 9. Pagamentos e integrações

A plataforma poderá começar por registar os valores acordados sem processar pagamentos diretamente. Numa fase posterior, poderá integrar prestadores de pagamento autorizados e adequados ao mercado angolano, com suporte a AOA, confirmação de transações, reconciliação e tratamento de falhas.

Qualquer integração financeira deverá ser implementada após seleção do fornecedor, análise contratual e regulatória, testes de segurança e definição de comissões, reembolsos e responsabilidades. A Kamba não deverá guardar dados sensíveis de cartões.

Outras integrações possíveis incluem mapas e geolocalização, correio eletrónico, SMS, armazenamento de ficheiros e ferramentas de análise operacional.

## 10. Requisitos não funcionais

- **Usabilidade:** linguagem simples, navegação consistente e formulários curtos.
- **Responsividade:** funcionamento adequado em smartphones, tablets e computadores.
- **Desempenho:** operações eficientes, paginação e otimização de imagens.
- **Disponibilidade:** alojamento monitorizado, backups e plano de recuperação.
- **Escalabilidade:** capacidade de aumentar utilizadores, pedidos e ficheiros.
- **Manutenibilidade:** código modular, documentação, testes e ambientes separados.
- **Acessibilidade:** contraste adequado, rótulos claros, navegação por teclado e erros compreensíveis.

## 11. Âmbito recomendado para a primeira versão (MVP)

Para validar a procura e reduzir o custo inicial, recomenda-se lançar uma versão mínima funcional com:

- Registo, autenticação e perfis de clientes e prestadores.
- Categorias e pesquisa básica.
- Publicação e gestão de pedidos.
- Submissão, consulta e comparação de propostas.
- Seleção do prestador e registo dos termos acordados.
- Estados básicos de acompanhamento.
- Notificações essenciais e painel administrativo.
- Avaliação após conclusão e mecanismo básico de denúncia.

Aplicação móvel nativa, pagamentos integrados, verificação documental avançada, chat em tempo real e análise avançada podem ser planeados para fases seguintes.

## 12. Indicadores de desempenho

- Número de clientes e prestadores registados e ativos.
- Pedidos publicados por categoria e localização.
- Percentagem de pedidos que recebem pelo menos uma proposta.
- Tempo médio até à primeira proposta e até à seleção.
- Taxa de conversão de pedidos em serviços contratados.
- Taxas de conclusão, cancelamento e reclamação.
- Avaliação média e utilização recorrente.

## 13. Critérios de aceitação iniciais

- Um cliente consegue criar conta, publicar um pedido e consultar o estado.
- Um prestador consegue criar perfil, consultar pedidos relevantes e enviar proposta.
- O cliente consegue visualizar, comparar e selecionar propostas.
- A seleção gera um registo de serviço e dos termos aceites.
- As alterações de estado ficam registadas e visíveis às partes autorizadas.
- O administrador consegue gerir categorias, utilizadores e denúncias.
- As operações protegidas respeitam permissões e os dados privados não ficam acessíveis a utilizadores não autorizados.

## 14. Resultado esperado

Espera-se que a Kamba disponibilize um ambiente digital centralizado para organizar a relação entre quem procura serviços e quem os presta. O valor diferenciador proposto está na integração do ciclo de contratação — desde o pedido até ao acompanhamento — e na criação de oportunidades de visibilidade e captação de clientes para profissionais e empresas.

O sucesso dependerá da qualidade e confiança dos prestadores, da facilidade de utilização, da capacidade de atrair clientes, da clareza das regras comerciais e da execução consistente dos serviços.

---

**KAMBA — Conectamos clientes. Valorizamos profissionais. Simplificamos serviços.**
