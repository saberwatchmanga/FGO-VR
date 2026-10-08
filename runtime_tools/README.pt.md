# FGO VR — PCVR 0.2.1 / Quest 3 0.2.0

[English](README.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Español](README.es.md) | [Português](README.pt.md) | [Italiano](README.it.md)

Jogue **Fate/Grand Order VR feat. Mash Kyrielight** com uma build de compatibilidade baseada no AstroQuest/shadPS4. O projeto tem como alvo o jogo japonês de PS4 **CUSA09078**, nas versões **01.00 / 01.01**.

- **PCVR:** OpenXR pelo Virtual Desktop e VDXR.
- **Quest 3 standalone:** núcleo ARM64 local com FEX e Turnip; o PC não transmite os quadros do jogo.

Esta é, no momento, uma prévia privada. O repositório e os releases continuam privados/em rascunho. O vídeo de demonstração do lançamento é uma prévia privada, acessível somente por contas autorizadas do YouTube: [Assistir ao vídeo de prévia privada](https://youtu.be/zBSpUSqpUaw). Os pacotes não incluem dados de jogos de PS4, PKGs, firmware, chaves nem saves. Você precisa fornecer seu próprio jogo extraído.

## Downloads

Os pacotes de prévia estão preparados nos [releases em rascunho](https://github.com/saberwatchmanga/FGO-VR/releases):

| Arquivo | Componente |
| --- | --- |
| `FGO-VR-0.2.1-PCVR-Windows.zip` | Build PCVR para Windows e configurações externas de resolução |
| `FGO-VR-0.2.0-Quest3.apk` | Build standalone para Quest 3, sem alterações nesta atualização para PC |
| `FGO-VR-0.2.1-Source.zip` | Patches fixados, snapshots dos fontes modificados, referências de build e licenças |
| `SHA256SUMS` / `artifact-manifest.json` | Verificação dos arquivos e versões dos componentes |

## Início rápido no Windows / PCVR

Requisitos: Windows de 64 bits, GPU e driver compatíveis com Vulkan, runtime do Microsoft Visual C++, Virtual Desktop Streamer no PC e Virtual Desktop no headset.

1. Extraia `FGO-VR-0.2.1-PCVR-Windows.zip`.
2. Coloque seu jogo base extraído, incluindo `eboot.bin`, em `FGO-PC/games/CUSA09078`. Coloque a atualização opcional ao lado, em `FGO-PC/games/CUSA09078-UPDATE`. A atualização não funciona sem o jogo base.
3. Conecte o headset pelo Virtual Desktop e mantenha o Streamer em execução.
4. Dê um duplo clique em **`Launch-PCVR.cmd`**. O launcher seleciona o VDXR para esse processo sem alterar a configuração OpenXR do sistema. Para sair, feche a janela do jogo.
5. Para mudar a resolução, abra **`Resolution-Settings.cmd`**. É necessário ter Python 3 com Tk. Salve a configuração e reinicie o jogo. Sem Python, edite `FGO-Resolution/settings.json` ou use um launcher direto em `profiles`.
6. **`Launch-PCVR-Original.cmd`** sempre usa a build na resolução original e os mesmos saves.

Os launchers originais com nomes em chinês também foram mantidos. Fontes de sistema opcionais seguem as instruções upstream do AstroQuest; arquivos de sistema do console não estão incluídos.

Local dos saves: `FGO-PC/runtime-vr/user/home/1000/savedata/CUSA09078`. Feche o jogo antes de fazer backup do diretório inteiro do título.

## Início rápido no Quest 3 standalone

Instale `FGO-VR-0.2.0-Quest3.apk` (pacote `com.fgovr.quest`, código da versão 2). Uma atualização com a mesma assinatura pode preservar os dados do app. Ative a depuração USB e copie as pastas do jogo extraído para:

```text
/data/local/tmp/fgovr/games/CUSA09078
/data/local/tmp/fgovr/games/CUSA09078-UPDATE
```

O segundo caminho é apenas para a atualização opcional 1.01.

Deixe os arquivos legíveis. Veja os comandos e detalhes de atualização em [Instalação no Quest](docs/INSTALL_QUEST.md).

Com apenas um Quest conectado via USB, use a ferramenta de configurações do Windows para enviar a configuração de resolução ao Quest e, depois, feche e reinicie o app. A ferramenta faz backup da configuração existente e altera somente `fgo_render_scale`.

Os logs e as configurações ficam em `/sdcard/Android/data/com.fgovr.quest/files/`. O arquivo `vrhost.txt` aceita `fgo_render_scale=100/110/125`. Depois de iniciado, o jogo roda localmente no headset.

## Perfis de resolução

Os dois componentes usam **100 / OFF** por padrão: isso equivale a 100% / 1.00x e mantém a resolução original. Valores mais altos aumentam o uso de GPU e memória. Estes são perfis internos de renderização do jogo; a porcentagem de resolução exibida pelo VDXR é uma medição separada.

| Perfil | PCVR | Quest 3 | Resultado observado |
| --- | --- | --- | --- |
| 100 | Resolução original | Resolução original | Usuário do Quest relatou aliasing forte |
| 110 | Disponível | Disponível | Usuário do Quest considerou aceitável, com aliasing visível |
| 125 | Somente a inicialização foi verificada | Disponível | Usuário do Quest relatou engasgos perceptíveis |
| 150 | Disponível | Somente PC | Usuário de PCVR/VDXR relatou boa qualidade de imagem e confirmou ter concluído o jogo inteiro |

**110** é o perfil inicial recomendado para o Quest. As imagens do Quest no vídeo de prévia foram capturadas no modo standalone em 100 (1.00x); o aliasing fica mais evidente que no PC. Se você tiver um PC gamer, prefira o streaming PCVR pelo Virtual Desktop. Se o desempenho ficar ruim, volte para 100. O PC testado tinha i5-13400F / RTX 4070 / 64 GB de RAM; não há alegação de FPS quantitativo nem de desempenho confirmado durante toda a história.

Os alvos verificados por olho são 1408×1512 em 100, 1536×1663 em 110, 1792×1890 em 125 e 2048×2268 em PC150. O patch substitui a solicitação canônica verificada do jogo de 1.4f, preserva as demais solicitações e verificações de alocação e evita multiplicar a escala repetidamente.

### Correção de transição no PCVR 0.2.1

Em resoluções mais altas, uma transição da história antes esgotava o pool fixo de memória gráfica do jogo. Uma mensagem malformada de falta de memória causava então uma segunda falha. O PCVR 0.2.1 aumenta em conjunto o pool gráfico e o orçamento correspondente de memória Backing/Direct local ao processo, além de corrigir o formato da mensagem. O orçamento extra não é gravado nas configurações salvas.

Em **7 de outubro de 2026**, o usuário confirmou **a conclusão do jogo inteiro em PCVR / VDXR a 1.50x**. A transição que antes causava a falha também passou no novo teste, e a sessão registrada terminou normalmente. As verificações de inicialização PC125/150 e o retorno a 100 também passaram. O APK e o código-fonte do Quest continuam na versão 0.2.0; essa correção de PC não foi aplicada ao Quest.

O SHA-256 do core aceito é `563be6008f73855c3b4425c93bca104692999e97f0fb16cf956c5d3aa40123c1`.

Veja os [detalhes dos testes](TESTING.md) e o [registro de aceitação do usuário](docs/USER_ACCEPTANCE_20261007.md).

- Uma sessão posterior em PC150 terminou com uma violação de acesso durante o pré-carregamento do Unity. A causa ainda não foi identificada; veja os [detalhes dos testes](TESTING.md).

## Controles

| Entrada | Mapeamento |
| --- | --- |
| Left Touch stick | Direções do menu |
| Left / right grip | L1 / R1 |
| Left / right trigger | L2 / R2 |
| Right A | Cross / confirmar |
| Cliques simultâneos dos dois sticks | Recentrar |
| Keyboard Q / E | Confirmar |
| Keyboard arrows | Seleção do menu |

A pose de mira da mão direita é conectada ao rastreamento DualShock normal do jogo. Os controles básicos funcionam. O comportamento completo do Move, a mira precisa e todas as interações de treinamento ainda não foram validados.

## Limitações atuais

- Quest125 apresenta engasgos no headset do usuário; Quest110 ainda tem aliasing.
- **PCVR / VDXR 1.50x: o usuário confirmou que concluiu o jogo inteiro.** Nesta rodada de correção, PC125 só teve a inicialização verificada.
- A estabilidade em execuções repetidas, o FPS medido no headset e o conforto em outros equipamentos não foram avaliados separadamente.
- Ainda há lacunas nas camadas adicionais de reprojeção, no suporte completo ao Move e em algumas interfaces de rastreamento.
- Esta build tem como alvo o FGO VR. Outros jogos de PSVR precisam de verificações próprias de compatibilidade.

## Fontes, builds e créditos

Baseado no [AstroQuest](https://github.com/bigmak94/AstroQuest), fixado no commit `9f42c44d4e838e3a0df67913e350c4f098110862`, e no [shadPS4](https://github.com/shadps4-emu/shadPS4).

Os patches completos por plataforma estão em `patches`; os arquivos modificados estão em `source_snapshot`. **Aplique um único patch completo para a plataforma escolhida. Não empilhe patches de fases anteriores.**

`tools/prepare_source.py` obtém o código-fonte upstream fixado e aplica o patch da plataforma escolhida. Consulte as [instruções de build](docs/BUILD.md) para ver as entradas fixadas e os scripts de referência. Alguns caminhos de desenvolvedor precisam ser ajustados; não há promessa de build com um clique em uma máquina limpa. As chaves de assinatura do release não estão incluídas.

Os avisos de código-fonte seguem GPL-2.0-or-later e as licenças de terceiros aplicáveis. Consulte [LICENSE](LICENSE), [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) e os avisos upstream. Este é um projeto de compatibilidade não oficial; o jogo original e os personagens pertencem aos respectivos titulares dos direitos.

## Apoio

Se este projeto for útil para você, apoie seu desenvolvimento contínuo em [Ko-fi / terry2418](https://ko-fi.com/terry2418). Obrigado pelo apoio.
