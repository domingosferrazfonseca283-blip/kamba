# Kamba

Kamba é uma plataforma de serviços que aproxima clientes e profissionais em Angola.

## Estrutura atual

- páginas HTML na raiz — website institucional e central de apoio
- `css/` — identidade visual e estilos do website
- `js/` — interações da central de ajuda e suporte
- `backend/` — API Flask e base de dados do projeto
- `.github/workflows/pages.yml` — publicação do website no GitHub Pages

## Função do website

O website é exclusivamente institucional e de apoio. Serve para explicar o Kamba, orientar clientes e profissionais, apresentar segurança, privacidade e termos, disponibilizar a central de ajuda e permitir contacto com a equipa.

O marketplace, pedidos, propostas, contratos e restantes funcionalidades principais pertencem ao aplicativo Kamba.

## Suporte

A API possui uma rota `POST /api/support` para registar atendimentos. No website publicado, o endereço da API deve ser configurado através de `window.KAMBA_API` quando o backend estiver hospedado publicamente. Em desenvolvimento local, o website usa automaticamente `http://127.0.0.1:5000/api`.

## Publicação

O website é publicado pelo GitHub Pages através do workflow em `.github/workflows/pages.yml`.

## Próximos passos do produto

1. Continuar o desenvolvimento do aplicativo Kamba.
2. Hospedar a API e a base de dados num ambiente adequado.
3. Configurar `window.KAMBA_API` no website publicado.
4. Integrar pedidos, propostas, contratos, chat e avaliações no aplicativo.
