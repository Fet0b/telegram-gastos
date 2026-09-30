# Deploy

_Pendente — ainda não implementado._

Decisão já tomada com o dono do projeto, a detalhar quando o deploy for
implementado: GitHub Actions builda a imagem, publica no GitHub Container
Registry (GHCR) e conecta via SSH no servidor local para dar pull e
reiniciar o container. CI de testes/lint roda a cada push.
