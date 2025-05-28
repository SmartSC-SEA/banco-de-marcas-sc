// ---------- MODELO E MARCA ----------
function verificarMarca() {
    const marcaSelect = document.getElementById('marca_select');
    const novaMarcaInput = document.getElementById('nova_marca');
    const modeloDiv = document.getElementById('modelo_div');
    const modeloAtual = document.getElementById('modelo_atual')?.value;



    if (!marcaSelect) return;

    if (marcaSelect.value === 'outra') {
        novaMarcaInput.style.display = 'block';
        modeloDiv.innerHTML = `
            <label>Modelo</label>
            <input type="text" name="modelo" class="form-control" placeholder="Digite o modelo">
        `;
    } else {
        novaMarcaInput.style.display = 'none';

        fetch('/modelos_por_marca', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: 'marca=' + encodeURIComponent(marcaSelect.value)
        })
        .then(response => response.json())
        .then(data => {
            let html = `
                <label>Modelo</label>
                <select name="modelo" id="modelo_select" class="form-control mb-2">
                    <option value="">Selecione um modelo</option>
                    ${data.modelos.map(modelo => 
                        `<option value="${modelo}" ${modelo === modeloAtual ? 'selected' : ''}>${modelo}</option>`
                    ).join('')}
                    
                    <option value="outro">Outro (digitar novo modelo)</option>
                </select>
                <input type="text" name="modelo_novo" id="modelo_novo_input" class="form-control mt-2" placeholder="Digite novo modelo" style="display:none;">
                
            `;
            modeloDiv.innerHTML = html;

            const selectModelo = document.getElementById('modelo_select');
            selectModelo.addEventListener('change', () => {
                const novoModeloInput = document.getElementById('modelo_novo_input');
                novoModeloInput.style.display = selectModelo.value === 'outro' ? 'block' : 'none';
            });
        });
    }
}

// ---------- BUSCA CATÁLOGO ----------
function buscarCatalogo() {
    const termo = document.getElementById('termo_busca').value.trim();
    const tipo_busca = document.getElementById('tipo_busca').value;

    if (!termo) {
        alert("Digite um código ou descrição para buscar no catálogo.");
        return;
    }

    document.getElementById('loading').style.display = 'block';
    document.getElementById('resultado_busca').innerHTML = '';

    fetch('/buscar_catalogo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `termo=${encodeURIComponent(termo)}&tipo_busca=${encodeURIComponent(tipo_busca)}`
    })
    .then(response => response.json())
    .then(data => {
        let html = `
        <div style="max-height: 300px; overflow-y: auto; border: 1px solid #ccc; border-radius: 5px;">
            <table class="table table-hover table-bordered m-0">
                <thead class="table-light">
                    <tr><th>Código</th><th>Descrição</th></tr>
                </thead>
                <tbody>
        `;

        if (data.resultados.length === 0) {
            html += `<tr><td colspan="3" class="text-center text-muted">Nenhum resultado encontrado.</td></tr>`;
        } else {
            data.resultados.forEach(item => {
                html += `<tr style="cursor:pointer;" onclick="selecionarItem('${item.itemCodigo}', '${item.itemDescricao.replace(/'/g, "\\'")}')">
                            <td>${item.itemCodigo}</td><td>${item.itemDescricao}</td>
                         </tr>`;
            });
        }

        html += `</tbody></table></div>`;
        document.getElementById('resultado_busca').innerHTML = html;
        document.getElementById('loading').style.display = 'none';
    })
    .catch(error => {
        console.error('Erro:', error);
        document.getElementById('loading').style.display = 'none';
    });
}

// ---------- OUTRAS FUNÇÕES AUXILIARES ----------

function atualizarRelogio() {
    const agora = new Date();
    const dia = String(agora.getDate()).padStart(2, '0');
    const mes = String(agora.getMonth() + 1).padStart(2, '0');
    const ano = agora.getFullYear();
    const hora = String(agora.getHours()).padStart(2, '0');
    const min = String(agora.getMinutes()).padStart(2, '0');
    const seg = String(agora.getSeconds()).padStart(2, '0');

    const relogio = `${dia}/${mes}/${ano} ${hora}:${min}:${seg}`;
    document.getElementById('relogio').textContent = relogio;
}

setInterval(atualizarRelogio, 1000);
atualizarRelogio(); // inicial

function adicionarImagem() {
    const container = document.getElementById('imagem_container');
    const input = document.createElement('input');
    input.type = 'file';
    input.name = 'imagens_produto';
    input.classList.add('form-control', 'mb-2');
    container.appendChild(input);
}

function selecionarItem(codigo, descricao) {
    document.querySelector('input[name="codigo_item"]').value = codigo;
    document.querySelector('textarea[name="descricao_produto"]').value = descricao;
    document.getElementById('resultado_busca').innerHTML = '';
    document.getElementById('acao_catalogo').style.display = 'block';
    buscarMarcasExistentes(codigo);
}

function limparCatalogo() {
    document.querySelector('input[name="codigo_item"]').value = '';
    document.querySelector('textarea[name="descricao_produto"]').value = '';
    document.getElementById('acao_catalogo').style.display = 'none';
    document.getElementById('marcas_existentes').innerHTML = '';
    document.getElementById('resultado_busca').innerHTML = '';
}

function buscarMarcasExistentes(codigo_item) {
    fetch('/marcas_existentes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `codigo_item=${encodeURIComponent(codigo_item)}`
    })
    .then(response => response.json())
    .then(data => {
        const container = document.getElementById('marcas_existentes');
        if (data.marcas.length > 0) {
            let html = `
                <h5 class="mt-4">Marcas já cadastradas para este item:</h5>
                <div style="max-height: 200px; overflow-y: auto; border: 1px solid #ccc;">
                <table class="table table-sm table-bordered table-hover mb-0">
                    <thead class="table-light">
                        <tr><th>Código Item</th><th>SGP-e</th><th>Marca</th><th>Fornecedor</th><th>Observação</th></tr>
                    </thead><tbody>
            `;
            data.marcas.forEach(m => {
                html += `<tr>
                            <td>${m.codigo_item}</td>
                            <td>${m.processo_sgpe}</td>
                            <td>${m.marca}</td>
                            <td>${m.fornecedor_amostra}</td>
                            <td>${m.observacao || ''}</td>
                         </tr>`;
            });
            html += '</tbody></table></div>';
            container.innerHTML = html;
        } else {
            container.innerHTML = `<div class="alert alert-success mt-3">Nenhuma marca cadastrada ainda para este item.</div>`;
        }
    });
}

function verAnexos(idMarca) {
  fetch(`/anexos_marca/${idMarca}`)
    .then(response => response.json())
    .then(data => {
      let html = '<ul class="list-group">';
      if (data.imagens.length === 0 && data.documentos.length === 0) {
        html += '<li class="list-group-item">Nenhum anexo encontrado.</li>';
      }
      data.imagens.forEach(img => {
        html += `
          <li class="list-group-item">
            📷 <a href="/uploads/${img}" target="_blank">${img}</a>
          </li>`;
      });
      data.documentos.forEach(doc => {
        html += `
          <li class="list-group-item">
            📄 <a href="/uploads/${doc}" target="_blank">${doc}</a>
          </li>`;
      });
      html += '</ul>';
      document.getElementById('conteudoAnexos').innerHTML = html;
      new bootstrap.Modal(document.getElementById('modalAnexos')).show();
    });
}


// ---------- EVENTOS AUTOMÁTICOS ----------
document.addEventListener('DOMContentLoaded', () => {
    // Atualizar validade automática ao alterar data
    const dataCadastroInput = document.querySelector('input[name="data_cadastro"]');
    const dataValidadeInput = document.querySelector('input[name="data_validade"]');
    if (dataCadastroInput && dataValidadeInput) {
        dataCadastroInput.addEventListener('change', () => {
            const data = new Date(dataCadastroInput.value);
            if (!isNaN(data)) {
                data.setFullYear(data.getFullYear() + 1);
                dataValidadeInput.value = data.toISOString().split('T')[0];
            }
        });
    }

    // Confirmação de busca pública sem filtros
    const formPublica = document.getElementById('form_publica');
    if (formPublica) {
        formPublica.addEventListener('submit', function (e) {
            const codigo = this.querySelector('input[name="codigo_item"]').value.trim();
            const descricao = this.querySelector('input[name="descricao"]').value.trim();
            const marca = this.querySelector('input[name="marca"]').value.trim();

            if (!codigo && !descricao && !marca) {
                const confirmar = confirm("Você está realizando a consulta sem nenhum filtro. Isso pode deixar a busca lenta. Deseja continuar mesmo assim?");
                if (!confirmar) e.preventDefault();
            }
        });
    }

    // Chamar verificarMarca ao carregar a página e ao mudar o select
    const marcaSelect = document.getElementById('marca_select');
    if (marcaSelect) {
        verificarMarca(); // caso tenha valor carregado
        marcaSelect.addEventListener('change', verificarMarca);
    }
});
