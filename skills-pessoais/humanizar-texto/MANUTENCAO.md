# humanizar-texto: instalação, testes e otimização

Este ficheiro é para quem mantém a skill. O Claude não precisa dele para a usar.

## Conteúdo da pasta

| Ficheiro | Para quê |
|---|---|
| `SKILL.md` | Instruções que o Claude segue: fluxo (com a limpeza de artefactos e o mapa do texto), regras de construção R23–R29, regras de superfície R1–R22, Modo académico A1–A7, glossário, exemplos, parâmetros P1–P11, fontes |
| `scripts/limpar_artefactos.py` | Limpeza opcional (Passo 0B): remove caracteres invisíveis, espaços anómalos, marcadores de ferramenta e parâmetros de rastreio, e lista frases de assistente, espaços reservados e formatação a rever |
| `scripts/auditar_texto.py` | Verificação opcional (Python 3, sem dependências): ritmo, marcadores, sinais de molde (abertura de definição, fecho de receita, frases com enumeração), comparação de factos e distância ao original (P10) |
| `evals/` | 7 casos de teste para medir a skill antes e depois de cada alteração (não entram no pacote `.skill`) |
| `MANUTENCAO.md` | Este guia |

## Instalar

**Claude Desktop / claude.ai.** Abre o ficheiro `humanizar-texto.skill` e usa o botão de guardar a skill. Em alternativa, comprime a pasta `humanizar-texto/` em `.zip` e carrega-a na secção de Skills das definições (em Capacidades). O script só corre se a execução de código estiver ativa. Sem ela, a skill funciona na mesma e a verificação de factos é feita à mão (Passo 4).

**Claude Code.** Copia a pasta para um destes sítios:

```bash
cp -r humanizar-texto ~/.claude/skills/
```

(para todas as sessões), ou para `.claude/skills/` dentro de um projeto (só nesse projeto). A skill aciona-se pela descrição ("humaniza este texto…") ou à mão com `/humanizar-texto`. No Claude Code a skill lê ficheiros, grava a versão nova como `<nome>-humanizado.<ext>` e pode correr o script:

```bash
python ~/.claude/skills/humanizar-texto/scripts/auditar_texto.py original.txt reescrito.txt
```

## Otimizar

1. **Muda uma coisa de cada vez.** As regras (R1–R22) e os parâmetros (P1–P7) têm códigos fixos para poderes comparar versões. Os parâmetros são escolhas operacionais, não números dos estudos, e são o primeiro sítio a afinar.
2. **Mede antes e depois** com os casos em `evals/`:
   - No Claude Code, dentro da pasta da skill: `claude plugin eval . --allow-tools Write,Edit,Bash` (corre cada caso com e sem a skill; são execuções reais, com custo).
   - Ou pede ao Claude: "usa o skill-creator para testar e melhorar a skill humanizar-texto". Ele corre os casos, mostra os resultados lado a lado e recolhe o teu feedback.
3. **Acrescenta casos** sempre que a skill falhar num texto real: cria uma pasta nova em `evals/` com `prompt.md`, `case.yaml` e `graders/` (copia um caso existente). Os casos mais úteis são os de factos que mudaram, registo errado e textos que já eram humanos.
4. **Afina o acionamento** (quando a skill entra em ação) com a otimização de descrição do skill-creator. Só funciona no Claude Code, porque usa `claude -p`.
5. **Novos marcadores:** junta-os ao glossário do `SKILL.md` com a fonte, mantendo a distinção entre medido (EN) e adaptado (PT), e à lista `MARCADORES` no script.
6. **Versões:** sobe `metadata.version` no `SKILL.md` e regista a mudança abaixo.

## Histórico

- **1.2.0 (2026-11-18):** construção do texto. Mapa do texto no Passo 2; regras R23–R29 (molde de exposição, explicar o tema, tensão resolvida por receita, partes com o mesmo peso, frases coladas por adição, reordenar/fundir/partir/cortar, textos curtos e genéricos); intensidade `normal` passa a incluir a construção; verificação de distância ao original (P10) e frases com enumeração (P11); a ausência de marcadores deixa de contar como sinal de texto humano; exemplo 7; caso de teste `expositivo-curto-estrutura`. Motivo: num texto expositivo de ~100 palavras, a 1.1.0 devolvia quase o mesmo texto. Os achados do StoryScope entraram a partir de um resumo: **falta ler o PDF e confirmar os números e a referência**.
- **1.1.0 (2026-11-18):** Modo académico (A1–A7), Passo 0B de limpeza de artefactos com o script `limpar_artefactos.py`, exemplos 4–6, parâmetros P8–P9, nota sobre marcas d'água nos Limites, descrição encurtada para menos de 200 caracteres e caso de teste `limpeza-tom-academico`.
- **1.0.0 (2026-11-18):** versão inicial, baseada em Reinhart et al. (2025), Russell et al. (2025), Liang et al. (2024), Sadasivan et al. (2023/2025) e Chakraborty et al. (2023).
