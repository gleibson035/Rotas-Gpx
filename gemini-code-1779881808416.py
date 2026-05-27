import base64

# Create the HTML structure for a single-page application that clones the interface
# and adds functionality to fetch and convert Carris Metropolitana routes to GPX.
html_content = """<!DOCTYPE html>
<html lang="pt-PT">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Conversor de Rotas - Carris Metropolitana em GPX</title>
    <style>
        *, *::before, *::after {
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #f4f6f8;
            color: #333;
            margin: 0;
            padding: 20px;
            line-height: 1.5;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            background: #ffffff;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }

        header {
            text-align: center;
            border-bottom: 2px solid #ffcc00; /* Cor característica da Carris Metropolitana */
            padding-bottom: 20px;
            margin-bottom: 30px;
        }

        header h1 {
            margin: 0;
            color: #111;
            font-size: 24px;
        }

        header p {
            margin: 5px 0 0 0;
            color: #666;
            font-size: 14px;
        }

        .step-section {
            margin-bottom: 25px;
            padding: 15px;
            background: #fafafa;
            border-left: 4px solid #ffcc00;
            border-radius: 0 4px 4px 0;
        }

        label {
            display: block;
            font-weight: bold;
            margin-bottom: 8px;
            color: #222;
        }

        select, input {
            width: 100%;
            padding: 10px;
            font-size: 15px;
            border: 1px solid #ccc;
            border-radius: 4px;
            background: #fff;
            outline: none;
            transition: border-color 0.2s;
        }

        select:focus, input:focus {
            border-color: #ffcc00;
        }

        select:disabled {
            background: #eee;
            cursor: not-allowed;
        }

        .btn {
            display: inline-block;
            background-color: #ffcc00;
            color: #000;
            font-weight: bold;
            border: none;
            padding: 12px 24px;
            font-size: 15px;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.2s, opacity 0.2s;
            width: 100%;
            text-align: center;
            text-decoration: none;
        }

        .btn:hover {
            background-color: #e6b800;
        }

        .btn:disabled {
            background-color: #ccc;
            color: #666;
            cursor: not-allowed;
        }

        .status {
            margin-top: 15px;
            padding: 10px;
            border-radius: 4px;
            font-size: 14px;
            display: none;
        }

        .status.loading {
            display: block;
            background-color: #eec;
            color: #663;
        }

        .status.success {
            display: block;
            background-color: #d4edda;
            color: #155724;
        }

        .status.error {
            display: block;
            background-color: #f8d7da;
            color: #721c24;
        }

        #preview-box {
            margin-top: 20px;
            display: none;
        }

        textarea {
            width: 100%;
            height: 150px;
            font-family: monospace;
            font-size: 12px;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            background: #f9f9f9;
            resize: vertical;
        }

        footer {
            text-align: center;
            margin-top: 40px;
            font-size: 12px;
            color: #888;
        }
    </style>
</head>
<body>

<div class="container">
    <header>
        <h1>Conversor de Rotas Carris Metropolitana ➔ GPX</h1>
        <p>Selecione a linha e o sentido para gerar o ficheiro GPX compatível com GPS e Strava.</p>
    </header>

    <div class="step-section">
        <label for="linha-select">1. Selecione a Linha (Autocarro):</label>
        <select id="linha-select">
            <option value="">A carregar linhas...</option>
        </select>
    </div>

    <div class="step-section">
        <label for="rota-select">2. Selecione o Sentido / Variante:</label>
        <select id="rota-select" disabled>
            <option value="">Selecione primeiro uma linha</option>
        </select>
    </div>

    <div style="margin-top: 30px;">
        <button id="btn-gerar" class="btn" disabled>Gerar e Descarregar GPX</button>
    </div>

    <div id="status-message" class="status"></div>

    <div id="preview-box">
        <label>Pré-visualização do Ficheiro GPX:</label>
        <textarea id="gpx-preview" readonly></textarea>
    </div>
</div>

<footer>
    Interface inspirada no visualizador de rotas original. Dados obtidos em tempo real via API pública da Carris Metropolitana.
</footer>

<script>
    // Endpoints Oficiais da API da Carris Metropolitana
    const API_LINES = "https://api.carrismetropolitana.pt/lines";
    const API_ROUTES = "https://api.carrismetropolitana.pt/routes";

    const linhaSelect = document.getElementById('linha-select');
    const rotaSelect = document.getElementById('rota-select');
    const btnGerar = document.getElementById('btn-gerar');
    const statusMessage = document.getElementById('status-message');
    const previewBox = document.getElementById('preview-box');
    const gpxPreview = document.getElementById('gpx-preview');

    let dynamicRoutesMap = {};

    // Inicialização: Procura todas as linhas ativas
    async function carregarLinhas() {
        showStatus('A carregar lista de linhas diretamente da API...', 'loading');
        try {
            const response = await fetch(API_LINES);
            if (!response.ok) throw new Error('Não foi possível obter as linhas.');
            const linhas = await response.json();

            // Ordenar linhas por ID numérico/alfabético
            linhas.sort((a, b) => a.id.localeCompare(b.id, undefined, {numeric: true, sensitivity: 'base'}));

            linhaSelect.innerHTML = '<option value="">-- Escolha uma linha --</option>';
            linhas.forEach(linha => {
                const option = document.createElement('option');
                option.value = linha.id;
                option.textContent = `${linha.id} - ${linha.long_name}`;
                linhaSelect.appendChild(option);
            });

            showStatus('Linhas carregadas com sucesso!', 'success');
            setTimeout(() => hideStatus(), 3000);
        } catch (error) {
            console.error(error);
            showStatus('Erro ao ligar à API da Carris Metropolitana. Tente novamente mais tarde.', 'error');
            linhaSelect.innerHTML = '<option value="">Erro ao carregar</option>';
        }
    }

    // Evento: Ao mudar de linha, procura as rotas (variantes e sentidos) dessa linha
    linhaSelect.addEventListener('change', async (e) => {
        const linhaId = e.target.value;
        rotaSelect.innerHTML = '<option value="">Selecione primeiro uma linha</option>';
        rotaSelect.disabled = true;
        btnGerar.disabled = true;
        previewBox.style.display = 'none';

        if (!linhaId) return;

        showStatus(`A obter sentidos e variantes para a linha ${linhaId}...`, 'loading');

        try {
            // Vamos à API de rotas para encontrar as que pertencem a esta linha
            const response = await fetch(API_ROUTES);
            if (!response.ok) throw new Error('Erro ao obter rotas.');
            const todasRotas = await response.json();

            // Filtrar rotas associadas a esta linha
            const rotasFiltradas = todasRotas.filter(r => r.line_id === linhaId);

            if (rotasFiltradas.length === 0) {
                rotaSelect.innerHTML = '<option value="">Nenhum sentido/variante disponível</option>';
                hideStatus();
                return;
            }

            rotaSelect.innerHTML = '<option value="">-- Escolha o Sentido / Variante --</option>';
            
            rotasFiltradas.forEach(rota => {
                // Cada rota tem múltiplos padrões (patterns), vamos salvar a informação
                // O padrão costuma conter o desenho geométrico (path) completo
                if (rota.patterns && rota.patterns.length > 0) {
                    rota.patterns.forEach(patternId => {
                        const option = document.createElement('option');
                        option.value = patternId;
                        
                        // Determinar uma legenda amigável para o utilizador
                        let direcao = rota.direction === 0 ? "Ida" : "Volta";
                        option.textContent = `${direcao}: ${rota.long_name} (Var: ${patternId})`;
                        rotaSelect.appendChild(option);
                    });
                } else {
                    // Fallback se usar o ID da rota diretamente
                    const option = document.createElement('option');
                    option.value = `route_${rota.id}`;
                    let direcao = rota.direction === 0 ? "Ida" : "Volta";
                    option.textContent = `${direcao}: ${rota.long_name}`;
                    rotaSelect.appendChild(option);
                }
            });

            rotaSelect.disabled = false;
            hideStatus();
        } catch (error) {
            console.error(error);
            showStatus('Erro ao carregar detalhes do percurso.', 'error');
        }
    });

    // Evento: Ao mudar a rota/padrão, habilita o botão de geração
    rotaSelect.addEventListener('change', (e) => {
        if (e.target.value) {
            btnGerar.disabled = false;
        } else {
            btnGerar.disabled = true;
        }
    });

    // Evento: Clicar para gerar o GPX
    btnGerar.addEventListener('click', async () => {
        const patternId = rotaSelect.value;
        const linhaSelecionadaTexto = linhaSelect.options[linhaSelect.selectedIndex].text;
        const rotaSelecionadaTexto = rotaSelect.options[rotaSelect.selectedIndex].text;

        showStatus('A extrair geometria do percurso e a gerar o GPX...', 'loading');

        try {
            let geojsonFeatures = [];
            
            if (patternId.startsWith('route_')) {
                // Caso use o endpoint da rota diretamente
                const realRouteId = patternId.replace('route_', '');
                const response = await fetch(`https://api.carrismetropolitana.pt/routes/${realRouteId}`);
                const data = await response.json();
                // Procurar no formato se contém propriedades geométricas ou links
                showStatus('Esta rota não possui traçado de alta definição em GeoJSON direto na API pública.', 'error');
                return;
            } else {
                // Caso padrão: puxar os dados completos do "pattern" que contém o GeoJSON da rota
                const response = await fetch(`https://api.carrismetropolitana.pt/patterns/${patternId}`);
                if (!response.ok) throw new Error('Erro ao descarregar a geometria do padrão.');
                const patternData = await response.json();

                // Na API da Carris Metropolitana, o desenho detalhado está no objeto GeoJSON do pattern
                if (patternData.path && patternData.path.type === "LineString") {
                    geojsonFeatures = patternData.path.coordinates;
                } else if (patternData.path && patternData.path.features) {
                    // Prevenção de variações de estrutura
                    const lineFeature = patternData.path.features.find(f => f.geometry.type === "LineString");
                    if (lineFeature) geojsonFeatures = lineFeature.geometry.coordinates;
                }
            }

            if (!geojsonFeatures || geojsonFeatures.length === 0) {
                throw new Error('A API não devolveu coordenadas geográficas (LineString) válidas para este percurso.');
            }

            // Gerar a estrutura de XML string do ficheiro GPX
            const gpxConteudo = construirGPX(geojsonFeatures, linhaSelecionadaTexto, rotaSelecionadaTexto);

            // Mostrar na caixa de texto
            gpxPreview.value = gpxConteudo;
            previewBox.style.display = 'block';

            // Criar o download automático para o utilizador
            const blob = new Blob([gpxConteudo], { type: 'application/gpx+xml;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.setAttribute("href", url);
            
            // Nome limpo do ficheiro
            const nomeFicheiro = `CarrisMetropolitana_${patternId}.gpx`;
            link.setAttribute("download", nomeFicheiro);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            showStatus(`Sucesso! O ficheiro "${nomeFicheiro}" foi gerado e descarregado.`, 'success');

        } catch (error) {
            console.error(error);
            showStatus(`Erro ao gerar GPX: ${error.message}`, 'error');
        }
    });

    // Função Auxiliar para converter Array de Coordenadas [Lon, Lat] em XML GPX válido
    function construirGPX(coordenadas, nomeLinha, nomeRota) {
        const dataAtual = new Date().toISOString();
        let xml = `<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Conversor Carris Metropolitana" 
     xmlns="http://www.topografix.com/GPX/1/1" 
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
     xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
  <metadata>
    <name>${escapeXml(nomeLinha)} - ${escapeXml(nomeRota)}</name>
    <desc>Rota gerada automaticamente a partir da API pública da Carris Metropolitana</desc>
    <time>${dataAtual}</time>
  </metadata>
  <trk>
    <name>${escapeXml(nomeLinha)}</name>
    <desc>${escapeXml(nomeRota)}</desc>
    <trkseg>
`;

        // Iterar nas coordenadas GeoJSON (Formato: [Longitude, Latitude])
        coordenadas.forEach(ponto => {
            const lon = ponto[0];
            const lat = ponto[1];
            xml += `      <trkpt lat="${lat}" lon="${lon}"></trkpt>\n`;
        });

        xml += `    </trkseg>
  </trk>
</gpx>`;
        return xml;
    }

    // Escapar caracteres especiais para manter o XML válido
    function escapeXml(unsafe) {
        return unsafe.replace(/[<>&'"]/g, function (c) {
            switch (c) {
                case '<': return '&lt;';
                case '>': return '&gt;';
                case '&': return '&amp;';
                case '\'': return '&apos;';
                case '"': return '&quot;';
            }
        });
    }

    // Funções de UI
    function showStatus(text, type) {
        statusMessage.textContent = text;
        statusMessage.className = `status ${type}`;
    }

    function hideStatus() {
        statusMessage.style.display = 'none';
    }

    // Inicializar aplicação ao abrir a página
    carregarLinhas();
</script>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("HTML file successfully created.")