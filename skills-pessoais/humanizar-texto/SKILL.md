---
name: humanizar-texto
description: Reescreve textos gerados por IA (ChatGPT, Claude, Gemini, Copilot…) para que tenham ritmo, estrutura e vocabulário de pessoa, ajustados ao género do texto, mantendo exatamente o mesmo conteúdo factual (números, nomes, datas, citações, grau de certeza). Regras baseadas em estudos sobre as diferenças entre escrita humana e de LLMs. Usa sempre que o utilizador pedir para humanizar, naturalizar, "tirar o tom de IA/ChatGPT", tornar um texto menos robótico, genérico ou formal, rever um rascunho feito com IA, ou quando colar um texto e disser que "parece escrito por IA", mesmo sem usar a palavra humanizar. Serve para emails, artigos, posts, relatórios, resumos académicos e textos de marketing, em português (PT-PT e PT-BR) e inglês (humanize, make it sound human, less AI-sounding, de-GPT this).
compatibility: Claude Desktop / claude.ai e Claude Code. O script opcional scripts/auditar_texto.py precisa de Python 3 sem dependências; a skill funciona sem ele.
metadata:
  version: "1.0.0"
  idioma: pt-PT
---

# Humanizar texto gerado por IA

Reescreve um texto gerado por IA para que soe escrito por uma pessoa que domina o género (notícia, email, artigo académico, post), **sem alterar nenhum facto**. O objetivo é qualidade e adequação ao leitor. Não é contornar detetores (ver "Limites").

## Porque isto não é trocar palavras

Os cinco estudos em "Fontes" mostram o mesmo: a diferença entre texto de IA e texto humano está na **distribuição** de escolhas gramaticais, estruturais e retóricas ao longo do texto, não só em palavras isoladas.

- **Reinhart et al. (2025)** compararam os 66 traços linguísticos de Biber em textos humanos e de LLMs do mesmo género. Os modelos com *instruction tuning* escrevem num estilo **denso e nominal**, mesmo quando lhes pedem registo informal: orações de particípio presente/gerúndio 2 a 5× mais frequentes (GPT-4o: 5,3×), nominalizações 2,1×, orações "que" como sujeito 2,6×, coordenação de sintagmas 1,9×. Modelos maiores não corrigem isto, e o *instruction tuning* agrava-o.
- **Russell et al. (2025)**: leitores que usam LLMs com frequência acertaram em 299 de 300 artigos (voto maioritário), mesmo depois de paráfrase e de "humanização" por prompt. As pistas que usaram, por frequência: vocabulário (53%), estrutura de frase (36%), gramática e pontuação (25%), originalidade (24%), citações (22%), clareza (20%), formatação (15%), conclusões (13%), formalidade (12%), nomes e títulos (12%), tom (9%), introduções (7%).
- **Liang et al. (2024)**: em 950 965 artigos científicos, palavras como *realm*, *intricate*, *showcasing* e *pivotal* dispararam a partir de 2023. Os autores sugerem que o texto gerado pode estar a uniformizar a escrita.
- **Sadasivan et al. (2023/2025)**: a paráfrase recursiva engana detetores automáticos mas degrada o texto. Só 70% das paráfrases foram avaliadas como mantendo bem o conteúdo (mais 23% "em parte"), e a perplexidade subiu de 5,2 para 8,7–10,5 em cinco rondas. Os detetores também falham no sentido inverso: texto humano pode ser marcado como IA.
- **Chakraborty et al. (2023)**: a deteção fica mais fácil quanto mais longo é o texto, porque cada regularidade se acumula. A diversidade humana é tão grande que não existe um único "estilo humano" a imitar.

Consequência prática: **parafrasear não chega** (Russell, exp. 3), e reescrever em ciclo estraga o conteúdo (Sadasivan). O que funciona é diagnosticar os padrões, reescrever uma vez ajustando ao género e verificar factos e padrões no fim.

## Fluxo de trabalho

### Passo 0: Enquadrar
Identifica: **género** (email interno, notícia, resumo académico, post de blogue, relatório…), **leitor**, **registo** (formal/informal), **língua e variante** (PT-PT ≠ PT-BR, sem misturar; responde na língua do texto) e **intensidade** pedida:
- `leve`: só vocabulário, fórmulas e formatação; a estrutura fica igual.
- `normal` (por defeito): tudo o que está abaixo, mantendo a ordem geral das ideias.
- `profunda`: pode reordenar parágrafos, fundir ou partir secções.

Se o utilizador der uma amostra da sua escrita, usa-a como referência de comprimento de frase, conectores, pontuação e pessoa gramatical. Reinhart et al. mediram as diferenças contra texto humano **do mesmo género**, e é essa a referência certa, não uma ideia genérica de "natural". Se o género não for claro e mudar muito o resultado, pergunta (uma pergunta só).

### Passo 1: Inventário factual (interno)
Antes de mexer, lista para ti cada unidade de conteúdo: números e unidades, datas, nomes de pessoas, instituições e lugares, relações de causa e efeito, comparações, **negações**, **grau de certeza** ("pode", "deverá", "cerca de", "sugere"), obrigações ("deve enviar") e citações literais. Separa as **avaliações sem facto** ("um marco crucial", "um futuro vibrante"): podem sair, mas ficam registadas nas notas.

Reescreve sempre a partir do texto original e usa o inventário só como lista de verificação. Liang et al. geraram texto "tipo LLM" precisamente a partir de esboços de conteúdo, por isso reescrever só a partir de uma lista de pontos reproduz o estilo que queres evitar.

### Passo 2: Diagnóstico
Percorre as regras R1–R21 e anota que padrões existem e onde. Russell et al. testaram várias formas de humanizar: "listar o que soa a IA e só depois editar" deu o melhor resultado, e encadear muitas chamadas de reescrita acrescentou traços de IA.

### Passo 3: Reescrita
Uma passagem completa, aplicando as regras com critério de género. Mexe primeiro na estrutura (abertura, fecho, densidade, ritmo) e só depois no vocabulário.

### Passo 4: Verificação
1. **Factos:** confirma cada item do inventário no texto novo: mesmo valor, mesma unidade, mesma negação, mesmo grau de certeza, citações palavra a palavra. Confirma também que **não entrou nada novo**: nem adjetivos que acrescentam afirmações ("só para", "o primeiro"), nem causas, nem nomes. Se puderes executar Python, corre `python scripts/auditar_texto.py original.txt reescrito.txt` (na pasta desta skill). O script compara números, citações, nomes próprios, negações e modais e mede o ritmo. Não substitui a leitura.
2. **Autoauditoria:** quem reescreve é também um modelo com *instruction tuning*, sujeito às mesmas tendências (Reinhart). Relê o teu texto à procura de marcadores do glossário, tríades, gerúndios encadeados, "não é X, é Y", travessões em série e fechos-resumo que tenhas introduzido.
3. Corrige localmente. **Não reescrevas o texto todo outra vez** (R22).

### Passo 5: Entrega
Ver "Formato de entrega".

## Regras

Cada regra diz o achado que a sustenta. Os marcadores em português são **adaptações** dos achados (medidos em inglês), não medições diretas.

### A. Densidade e gramática

**R1 · Gerúndios e particípios encadeados.** *Achado:* orações de particípio presente 2–5× mais frequentes nos LLMs; o GPT-4o chega a 5,3× (Reinhart). Em português aparecem como gerúndio depois de vírgula: ", promovendo…", ", garantindo…", ", destacando…", ", permitindo…".
*Faz:* passa a verbo conjugado, frase nova ou "e" + verbo. No máximo um destes por parágrafo, e só quando for a forma mais natural.
> "O festival atraiu 20 mil pessoas, ultrapassando o recorde de 2019." → "O festival atraiu 20 mil pessoas e bateu o recorde de 2019."

Se o gerúndio for ambíguo (intenção ou consequência), escolhe a leitura que o contexto sustenta. Se o contexto não decidir, usa "e" e não "para", que acrescentaria uma intenção.

**R2 · Nominalizações.** *Achado:* 2,1× mais nominalizações (Reinhart). Também já tinham sido observados menos sujeitos humanos (Jiang & Hyland, citado por Reinhart).
*Faz:* "a implementação de", "procedeu-se à realização de", "a otimização do" → verbo com o agente como sujeito. Mantém os termos técnicos que são o nome da coisa ("fotossíntese", "regressão logística").
> "Procedeu-se à realização de inquéritos" → "Foram feitos inquéritos" (académico) / "Fizemos inquéritos" (se o autor já fala na primeira pessoa).

**R3 · Sujeitos oracionais e abstratos.** *Achado:* orações "que" como sujeito 2,6× (Reinhart).
*Faz:* "O facto de X demonstra que Y", "É importante notar que Y", "Que X seja Y torna-se evidente" → diz Y diretamente, com quem faz a ação como sujeito.

**R4 · Enumerações e tríades.** *Achado:* coordenação de sintagmas 1,9× (Reinhart). Os especialistas de Russell apontam as listas "sempre de três".
*Faz:* **mantém todos os itens** (são conteúdo), mas varia a forma: dois numa frase e o terceiro noutra, ou desenvolve um. Não acrescentes nem cortes itens para fugir ao número três.

**R5 · Palavras longas.** *Achado:* comprimento médio de palavra maior nos LLMs (Reinhart).
*Faz:* "utilizar" → "usar", "efetuar" → "fazer", "no âmbito de" → "em", "relativamente a" → "sobre", "possuir" → "ter".

**R6 · Ajustar ao género, sem receitas fixas.** *Achado:* o GPT-4o usa a passiva sem agente a cerca de **metade** da taxa humana, e os modelos base do Llama ficam perto da taxa humana. Há traços com sentidos opostos conforme o modelo: o GPT-4o evita coordenar orações e o Llama abusa; o GPT-4o abusa de atenuadores ("quase", "ligeiramente") e o Llama evita-os (Reinhart).
*Faz:* **não** convertas todas as passivas em ativas. Em textos académicos, técnicos e noticiosos, mantém a passiva quando o agente não interessa. Calibra a coordenação e os atenuadores pela amostra do utilizador ou pelo que é normal no género.

### B. Vocabulário

**R7 · Marcadores lexicais: o que conta é a densidade.** *Achado:* o GPT-4o usa *camaraderie*, *tapestry*, *palpable* e *intricate* mais de 100× acima da taxa humana; *tapestry* aparece em 23% dos textos e *amidst* em 27% (Reinhart). Ver também Liang e a lista de Russell. Mas uma palavra sozinha não prova nada: os especialistas erraram com textos humanos que tinham *delve* ou *crucial*, e os leigos confundem palavras raras com IA (Russell).
*Faz:* troca os marcadores do glossário pelo termo simples que o género usa, ou corta-os. Mantém palavras raras quando são as mais precisas.

**R8 · Frases-resumo grandiloquentes.** *Achado:* palavras de "relação complexa" (*tapestry*, *intricate*, *amidst*) somadas a positivas (*vibrant*, *solace*) sinalizam "frases sumativas grandiosas, ainda que ocas" (Reinhart). Os especialistas de Russell gozam com o "testemunho" que serve "como farol de esperança".
*Faz:* corta frases que só avaliam ou resumem sem acrescentar facto ("Este marco é um testemunho do poder da colaboração"). Se tiverem uma afirmação real ou a opinião assumida do autor, mantém a afirmação em palavras simples. Regista nas notas o que cortaste.

**R9 · Repetir a palavra simples.** *Achado:* nos textos humanos repete-se *says*; a IA alterna *notes*, *explains*, *highlights* (Russell).
*Faz:* em atribuições, usa "disse"/"diz" e repete sem medo. Não andes a rodar sinónimos para evitar repetição.

### C. Ritmo e estrutura

**R10 · Misturar comprimentos e tipos de frase.** *Achado:* a IA prefere frases complexas com várias orações; nos textos humanos misturam-se frases simples, compostas e complexas, de comprimentos variados. Os especialistas citam como sinal humano "frases e parágrafos curtos e secos" (Russell).
*Faz:* alterna frases curtas e longas. Põe uma frase curta onde há uma ideia forte, e não por calendário. Evita três ou mais frases seguidas com comprimento e abertura parecidos (ver parâmetros).

**R11 · Fórmulas sintáticas.** *Achado:* "not only… but also" e "it's not just X, it's Y" são das pistas estruturais mais citadas (Russell).
*Faz:* elimina "não só… mas também", "não se trata de X, trata-se de Y", "não é apenas X: é Y", "quando se trata de", "num mundo em que" e diz a coisa diretamente.

**R12 · Variação distribuída, não um molde novo.** *Achado:* cada regularidade que se repete ao longo de muitas frases soma sinal, e a deteção sobe com o comprimento (Chakraborty: com duas amostras em vez de uma, a AUROC passou de 73% para 97%).
*Faz:* não apliques as correções em padrão fixo (frase curta no fim de cada parágrafo, pergunta retórica em cada secção, um travessão por parágrafo). Em textos longos, revê no fim as **aberturas** e os **fechos** de todos os parágrafos lado a lado.

### D. Organização

**R13 · Abertura.** *Achado:* introduções de IA abrem com cena ("Numa manhã cinzenta de novembro…"), com frase genérica ou a anunciar o que o texto vai dizer (Russell, guia e prompt do *evader*).
*Faz:* começa pelo facto mais relevante ou mais concreto do texto original. Corta "Neste artigo vamos explorar…" e as frases-chavão de abertura.

**R14 · Fecho.** *Achado:* a IA "acaba sempre com uma conclusão arrumada", longa, otimista, que resume tudo; os humanos acabam de forma mais abrupta (Russell).
*Faz:* acaba no último ponto substantivo. Antes de cortar a conclusão, passa para o corpo qualquer facto que só exista lá. Exceção: géneros que exigem conclusão (académico, sumário executivo). Aí mantém-na, curta e sem repetir.

**R15 · Formatação.** *Achado:* listas com rótulo a negrito seguido de dois-pontos, cabeçalhos repetitivos, parágrafos de tamanho igual, títulos sempre em itálico. O prompt do *evader* de Russell parte do princípio de que só 1 em cada 3 artigos tem cabeçalhos.
*Faz:* se os itens estão ligados, passa a prosa. Se a lista for mesmo necessária, usa marcadores simples, sem rótulo a negrito. Varia o tamanho dos parágrafos (um parágrafo de uma frase é legítimo). Cabeçalhos só quando o texto é longo e o género os usa. Respeita qualquer formato que o utilizador exija.

**R16 · Citações e nomes.** *Achado:* nos textos de IA as citações soam formais, iguais ao resto do texto e aparecem sempre no mesmo sítio, muitas vezes no fim do parágrafo. Há nomes repetidos ("Emily" ou "Sarah" em 63% dos artigos do GPT-4o e 70% dos do Claude) e títulos ("Dr.") para toda a gente (Russell).
*Faz:* **nunca alteres o texto dentro de aspas**: é um registo factual. Podes mudar a posição da citação, a atribuição ("disse") e a narração à volta. Não mudes nomes nem títulos. Se uma citação ou um nome parecer inventado (genérico, demasiado polido), assinala-o nas notas para o utilizador confirmar.

### E. Tom e conteúdo

**R17 · Positividade e eufemismo.** *Achado:* tom sempre neutro ou positivo, a "elevar" o leitor, frases de observador reflexivo. A IA evita temas escuros: num artigo sobre uma doença, falou em "embarcar num novo capítulo" (Russell). Os modelos com *instruction tuning* usam certos palavrões mais de 100× menos do que os humanos (Reinhart).
*Faz:* tira o entusiasmo que os factos não sustentam. Diz as más notícias com clareza, sem suavizar e sem dramatizar. Mantém a posição do autor quando ela existe. Não acrescentes palavrões nem calão que o original e o utilizador não justifiquem.

**R18 · Registo.** *Achado:* sem humanização, a IA quase não usa palavras de enchimento, contrações, coloquialismos ou abreviaturas (Russell), e falha o género mesmo quando lhe pedem registo informal (Reinhart). Mas a informalidade sozinha só enganou o especialista que se fiava nela; os outros acertaram na mesma (Russell, exp. 4–5).
*Faz:* num registo informal, permite marcas orais naturais da variante ("aliás", "pois", "só que", primeira pessoa). Num formal, mantém a formalidade com menos densidade. Nunca polvilhes coloquialismos para disfarçar uma estrutura que continua igual.

**R19 · Explicar a mais.** *Achado:* a IA explica demais, mete pormenores irrelevantes e "diz" em vez de "mostrar" (Russell, clareza).
*Faz:* corta repetições do mesmo facto e metacomentários ("vale a pena referir que", "como vimos"). Repetir um facto não é conteúdo novo, por isso cortá-lo não perde informação.

**R20 · Especificidade, sem inventar.** *Achado:* a escrita humana não ficcional tem afirmações específicas e verificáveis e reviravoltas inesperadas; a IA é "segura" e genérica (Russell, originalidade e factualidade). O *evader* de Russell mandava acrescentar dados específicos, mas aqui isso violaria a regra de ouro, e dados acrescentados por um modelo são um risco de alucinação.
*Faz:* põe à frente os pormenores concretos que **já estão** no texto e substitui generalidades pela versão específica que o próprio texto dá. Se faltar especificidade, **não a inventes**: indica nas notas onde um dado concreto ajudaria.

**R21 · Erros não; liberdades legítimas, sim.** *Achado:* os humanos cometem mais pequenos erros e usam pontuação mais variada (travessões, parênteses, aspas no meio das frases); a IA é gramaticalmente impecável (Russell).
*Faz:* não metas erros de propósito. Isso piora a qualidade e é uma pista superficial, que os especialistas não usam sozinha. Usa as liberdades que o género admite: frases sem verbo, frases começadas por "E" ou "Mas", parênteses, dois-pontos, uma pergunta. Nenhum recurso deve virar tique (R12). Em particular, não metas um travessão em cada parágrafo.

### F. Processo

**R22 · Uma passagem e verificação, sem ciclos.** *Achado:* na paráfrase recursiva, só 70% dos textos mantiveram bem o conteúdo e a qualidade baixou a cada ronda (Sadasivan). Humanizar em vários passos acrescentou traços de IA (Russell).
*Faz:* uma reescrita completa e depois só correções pontuais. Se o utilizador pedir "mais humano ainda", parte da versão anterior e aplica só as regras que ainda falham. Não reescrevas o texto do zero.

## Glossário de marcadores

O que conta é a densidade, não a presença (R7). A coluna PT é uma adaptação.

| Marcador medido (EN) | Fonte | Equivalentes PT frequentes | O que fazer |
|---|---|---|---|
| tapestry | Reinhart (>100×; 23% dos textos GPT-4o), Russell | tapeçaria, mosaico, teia | cortar a metáfora; dizer o que se junta |
| testament | Russell | é um testemunho de, prova viva de | "mostra" ou cortar |
| intricate | Reinhart (>100×), Liang (top 4) | intrincado, complexo | dizer em que consiste, se o texto o diz; senão cortar |
| realm, landscape | Liang (*realm*, top 4), Russell | domínio, âmbito, panorama, cenário | "em", "hoje" ou cortar |
| pivotal, crucial, paramount, key, essential | Liang (*pivotal*), Russell | crucial, fundamental, essencial, primordial, chave | "importante" (uma vez) ou mostrar a consequência |
| showcasing, underscore, highlights | Liang (*showcasing*), Reinhart (*underscore* 107× no GPT-4o Mini), Russell | evidenciar, sublinhar, realçar, destacar | "mostra"; nas atribuições, "disse" |
| vibrant | Reinhart, Russell | vibrante, dinâmico | cortar ou usar um adjetivo concreto do texto |
| palpable, camaraderie, solace, fleeting, unease | Reinhart | palpável, camaradagem, consolo, fugaz, inquietação | descrever o comportamento que o texto refere ou cortar |
| amidst | Reinhart (27% dos textos GPT-4o) | em meio a, no seio de | "durante", "com", "entre" |
| grapple, unravel, ignite | Reinhart | debater-se com, desvendar, despoletar | "lidar com", "explicar", "provocar" |
| delve, dive into | Russell | aprofundar, mergulhar em | "analisar", "ver", "tratar" |
| foster, harness, elevate, empower, enhance | Russell | fomentar, potenciar, alavancar, capacitar, impulsionar | "aumentar", "ajudar", "usar", "permitir" |
| navigate, journey | Russell | navegar (desafios), jornada, percurso | "lidar com", "processo" ou cortar |
| seamless, robust, comprehensive, transformative, groundbreaking | Russell | sem falhas, robusto, abrangente, transformador, inovador | dizer o que faz ou o que muda |
| additionally, moreover | Russell | além disso, adicionalmente, ademais | "também", "e" ou nada |
| in conclusion, in summary | Russell | em suma, em conclusão, em última análise | cortar (R14) |
| it's important to note | Russell | é importante notar/salientar que, vale a pena referir | cortar e dizer a coisa |
| in a world where, when it comes to | Russell | num mundo em que, quando se trata de, em constante evolução | cortar |
| paving the way | Russell | abrir caminho | cortar ou dizer o passo concreto, se existir |
| not only… but also / it's not about X, it's about Y | Russell | não só… mas também / não se trata de X, trata-se de Y | afirmar diretamente (R11) |
| notes, explains (vs *says*) | Russell | salientou, explicou, referiu, sublinhou | "disse" (R9) |

## Exemplos

Os exemplos mostram mudanças de **ritmo e estrutura** (abertura, fecho, densidade, posição das citações, tamanho de frases e parágrafos) com o conteúdo factual intacto. Repara no que **não** muda.

### Exemplo 1: notícia local (intensidade normal)

**Antes (IA):**
> Num momento decisivo para o centro histórico, a Câmara Municipal de Évora anunciou em março um investimento de 2,3 milhões de euros na requalificação do Mercado Municipal, reforçando o seu compromisso com o comércio local. A iniciativa, que prevê a substituição da cobertura, a modernização das bancas e a criação de um espaço para produtores biológicos, representa um marco crucial na revitalização da cidade. "Este projeto é fundamental para o futuro de Évora", salientou o vereador João Mendes. As obras deverão arrancar em setembro e ficar concluídas no final de 2026, garantindo um futuro vibrante para este espaço emblemático. Em suma, trata-se de um testemunho claro de que tradição e inovação podem caminhar lado a lado.

**Depois:**
> A Câmara Municipal de Évora anunciou em março que vai investir 2,3 milhões de euros na requalificação do Mercado Municipal. A cobertura será substituída e as bancas modernizadas.
>
> Haverá também um espaço novo, para produtores biológicos.
>
> "Este projeto é fundamental para o futuro de Évora", disse o vereador João Mendes. As obras deverão arrancar em setembro e ficar concluídas no final de 2026.

**O que mudou na estrutura:** um bloco de 5 frases longas (média de 23 palavras, de 14 a 36) passa a três parágrafos de tamanho desigual, com frases de 8 a 21 palavras (R10, R15). A abertura-chavão sai e o texto começa pelo facto (R13). Os dois gerúndios avaliativos saem (R1, R8). A tríade fica partida em 2 + 1, com os três itens (R4). A citação passa do fim para o meio do último parágrafo, com "disse" (R9, R16). A conclusão-resumo é cortada e o texto acaba num facto (R14).
**Factos verificados (11/11):** Câmara Municipal de Évora · março · 2,3 milhões de euros · requalificação · Mercado Municipal · cobertura · bancas · espaço para produtores biológicos · citação literal · vereador João Mendes · "deverão" arrancar em setembro e concluir no final de 2026 (a modalidade mantém-se).
**Cortado por não ter facto:** "momento decisivo", "reforçando o seu compromisso com o comércio local", "marco crucial na revitalização", "futuro vibrante… espaço emblemático", "Em suma… lado a lado".
**Armadilha evitada:** "um espaço *só* para produtores biológicos" acrescentaria exclusividade, que o original não afirma.

### Exemplo 2: email interno (formatação e registo)

**Antes (IA):**
> Assunto: Atualização importante sobre o projeto Atlas
>
> Olá equipa,
>
> Espero que este email vos encontre bem! Gostaria de partilhar convosco uma atualização importante sobre o estado do projeto Atlas.
>
> - **Prazo:** A entrega da versão beta foi adiada de 14 para 28 de novembro, devido a atrasos na integração com o sistema de pagamentos.
> - **Orçamento:** O orçamento mantém-se inalterado, nos 48 mil euros.
> - **Próximos passos:** A Marta irá coordenar os testes com o cliente na semana de 17 de novembro.
>
> Não se trata apenas de um ajuste de calendário: trata-se de um passo essencial para o sucesso do Atlas. Agradeço desde já a vossa compreensão e o vosso empenho contínuo. Juntos, continuaremos a construir algo verdadeiramente extraordinário!
>
> Com os melhores cumprimentos,
> Rui

**Depois:**
> Assunto: Beta do Atlas adiada para 28 de novembro
>
> Olá a todos,
>
> A entrega da beta do Atlas já não é a 14 de novembro. Passou para dia 28, porque a integração com o sistema de pagamentos atrasou.
>
> O orçamento fica igual: 48 mil euros.
>
> Na semana de 17 de novembro, a Marta coordena os testes com o cliente.
>
> Obrigado pela compreensão,
> Rui

**O que mudou na estrutura:** a notícia vai para o assunto e para a primeira frase (R13). A lista com rótulos a negrito passa a três parágrafos curtos de tamanho diferente (R15, R10). Saem a cortesia de abertura, a fórmula "não se trata de… trata-se de" e a exortação final (R11, R14, R17). O registo fica de equipa ("já não é", "fica igual") sem ficar desleixado (R18).
**Factos verificados (6/6):** adiamento de 14 para 28 de novembro · causa: integração com o sistema de pagamentos · orçamento inalterado · 48 mil euros · a Marta coordena os testes com o cliente na semana de 17 de novembro · assinado por Rui.

### Exemplo 3: resumo académico (o registo mantém-se formal)

**Antes (IA):**
> Este estudo explora a intrincada relação entre o uso de redes sociais e a qualidade do sono em adolescentes, oferecendo contributos cruciais para a compreensão deste fenómeno multifacetado. Através da realização de inquéritos a 412 estudantes do ensino secundário, procedeu-se à análise da associação entre o tempo de ecrã noturno e a duração do sono. Os resultados revelam que os participantes que utilizavam o telemóvel mais de duas horas após as 22h dormiam, em média, menos 47 minutos, sublinhando a importância de intervenções direcionadas. Estes achados abrem caminho para futuras investigações neste domínio em constante evolução.

**Depois:**
> Este estudo analisa a relação entre o uso de redes sociais e a qualidade do sono em adolescentes. Foram inquiridos 412 estudantes do ensino secundário e analisou-se a associação entre o tempo de ecrã à noite e a duração do sono. Os participantes que usavam o telemóvel mais de duas horas depois das 22h dormiam, em média, menos 47 minutos. Os resultados reforçam a importância de intervenções direcionadas.

**O que mudou na estrutura:** saem os dois gerúndios (R1) e as nominalizações "realização de inquéritos" e "procedeu-se à análise" (R2). **As passivas ficam** ("foram inquiridos", "analisou-se"), porque o género as usa (R6). Nada passa a coloquial (R18). A última frase muda de função: deixa de ser promessa vaga e passa a ser a conclusão do estudo (R14, R8). O original tinha três frases seguidas de 27 a 29 palavras; agora as frases têm 18 a 23 palavras e a última, curta (8), fecha o texto (R10).
**Factos verificados (8/8):** relação entre redes sociais e qualidade do sono · adolescentes · inquéritos · 412 estudantes do ensino secundário · associação entre tempo de ecrã noturno e duração do sono · mais de duas horas depois das 22h · menos 47 minutos em média · importância de intervenções direcionadas, com a mesma força ("reforçam" = "sublinhando").
**Cortado:** "contributos cruciais… fenómeno multifacetado", "abrem caminho… em constante evolução".

### Microexemplos em inglês (frases citadas por Reinhart et al.)

> GPT-4o: "Bryan, leaning on his agility, dances around the ring, evading Show's heavy blows."
> → "Bryan relies on his agility. He dances around the ring and dodges Show's heavy blows." (R1: dois particípios passam a verbos conjugados)

> Llama 3 70B Instruct: "These schemes can help to reduce deforestation, habitat destruction, and pollution, while also promoting sustainable consumption patterns."
> → "These schemes can help reduce deforestation, habitat destruction and pollution. They can also encourage more sustainable consumption." (R2, R4: os três itens mantêm-se; o "can" fica, porque o grau de certeza também é conteúdo)

## Formato de entrega

1. **O texto reescrito**, pronto a usar, no mesmo formato de base (email continua email, Markdown continua Markdown).
2. **Notas da revisão** (curtas, na língua do utilizador):
   - `Factos: N/N mantidos` (e qualquer dúvida concreta).
   - As 3 a 6 mudanças principais, com o código da regra (ex.: "R14: conclusão-resumo cortada").
   - `Cortado por não ter facto:` as avaliações que saíram, para o utilizador poder repor alguma.
   - `A confirmar:` nomes, citações ou números que parecem genéricos ou inventados (R16, R20) e pontos vagos onde um dado concreto ajudaria.

Se o utilizador pedir "só o texto", entrega só o texto. Se o texto já soar humano, diz isso e faz só ajustes mínimos: forçar mudanças pioraria o texto, e humanos também escrevem "crucial" (R7). No Claude Code, quando o texto vem de um ficheiro, grava a versão nova como `<nome>-humanizado.<ext>`, a menos que peçam para substituir. O original faz falta para a verificação.

Nunca mexas em: código, fórmulas, dados de tabelas, citações literais, termos jurídicos ou técnicos com sentido fixo, nomes próprios.

## Parâmetros ajustáveis

São escolhas operacionais desta skill para pôr em prática os achados, **não** valores medidos nos estudos. Ajusta-os quando otimizares a skill.

| ID | Parâmetro | Valor atual |
|---|---|---|
| P1 | Gerúndios explicativos depois de vírgula (R1) | ≤ 1 por parágrafo |
| P2 | Frases curtas (≤ 8 palavras) (R10) | pelo menos 1 por cada ~120 palavras, em posições variadas |
| P3 | Frases seguidas com comprimento parecido (±3 palavras) (R10) | no máximo 3 |
| P4 | Marcadores do glossário (R7) | 0 por defeito; ≤ 1 por 300 palavras se forem o termo certo |
| P5 | Tríades "A, B e C" (R4) | ≤ 1 por ~200 palavras (com todos os itens mantidos) |
| P6 | Parágrafos (R15) | tamanhos variados; com 4+ parágrafos, pelo menos um claramente mais curto |
| P7 | Reescritas completas (R22) | 1, depois só correções locais |

## Limites

- **Detetores:** esta skill não garante passar em detetores e não deve ser apresentada assim. Os detetores falham nos dois sentidos (Sadasivan). Em textos longos a deteção continua possível (Chakraborty), e especialistas humanos apanharam artigos "humanizados" por prompt (Russell).
- **Autoria:** quando o contexto exige declarar o uso de IA (regras académicas, editoriais, profissionais), a reescrita não substitui essa declaração.
- **Evidência:** os estudos analisam sobretudo inglês americano e modelos de 2023–2025 (GPT-3.5/4o, o1-pro, Claude 3.5 Sonnet, Llama 2/3). Os equivalentes portugueses e os parâmetros P1–P7 são adaptações a validar com os evals da skill.

## Fontes

1. Reinhart, A., Markey, B., Laudenbach, M., Pantusen, K., Yurko, R., Weinberg, G., & Brown, D. W. (2025). *Do LLMs write like humans? Variation in grammatical and rhetorical styles.* PNAS, 122(8), e2422455122. https://doi.org/10.1073/pnas.2422455122 · Corpus HAP-E: https://doi.org/10.57967/hf/3770 · Código: https://doi.org/10.17605/OSF.IO/7MRQN
2. Russell, J., Karpinska, M., & Iyyer, M. (2025). *People who frequently use ChatGPT for writing tasks are accurate and robust detectors of AI-generated text.* arXiv:2501.15654. https://arxiv.org/abs/2501.15654 · Dados e guia: https://github.com/jenna-russell/human_detectors
3. Liang, W., Zhang, Y., Wu, Z., Lepp, H., Ji, W., Zhao, X., Cao, H., Liu, S., He, S., Huang, Z., Yang, D., Potts, C., Manning, C. D., & Zou, J. Y. (2024). *Mapping the Increasing Use of LLMs in Scientific Papers.* arXiv:2404.01268. https://arxiv.org/abs/2404.01268
4. Sadasivan, V. S., Kumar, A., Balasubramanian, S., Wang, W., & Feizi, S. (2023, v4 2025). *Can AI-Generated Text be Reliably Detected?* arXiv:2303.11156. https://arxiv.org/abs/2303.11156 · Código: https://github.com/vinusankars/Reliability-of-AI-text-detectors
5. Chakraborty, S., Bedi, A. S., Zhu, S., An, B., Manocha, D., & Huang, F. (2023). *On the Possibilities of AI-Generated Text Detection.* arXiv:2304.04736. https://arxiv.org/abs/2304.04736

Para instalar, testar e otimizar esta skill (Claude Desktop e Claude Code), vê `MANUTENCAO.md`.
