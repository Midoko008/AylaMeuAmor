import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../App.css';

export default function PaginaInicial() {
  const [figurasFiltradas, setFigurasFiltradas] = useState([]);
  const [filtro, setFiltro] = useState('');
  const [obras, setObras] = useState([]);
  const [obraSelecionada, setObraSelecionada] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetch('http://localhost:5000/obras')
      .then(res => res.json())
      .then(data => setObras(data))
      .catch(err => console.error('Erro ao buscar obras:', err));
  }, []);

  useEffect(() => {
    let url = 'http://localhost:5000/figuras';

    const termo = filtro.trim();
    if (termo) {
      url = `http://localhost:5000/figuras/buscar?q=${encodeURIComponent(termo)}`;
    } else if (obraSelecionada) {
      url = `http://localhost:5000/figuras/obras/${obraSelecionada}`;
    }

    fetch(url)
      .then(res => res.json())
      .then(data => setFigurasFiltradas(data))
      .catch(err => {
        console.error('Erro ao buscar figures:', err);
        setFigurasFiltradas([]);
      });
  }, [filtro, obraSelecionada]);

  function irParaPerfil() {
    navigate('/perfil');
  }

  function abrirDetalhes(id) {
    navigate(`/figura/${id}`);
  }

  function irParaAdicionarFigura() {
    navigate('/adicionar-figura');
  }

  function irParaCarrinho() {
    navigate('/carrinho');
  }

  function adicionarAoCarrinho(e, figuraId) {
    e.stopPropagation();
    fetch('http://localhost:5000/carrinho', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ produto_id: figuraId }),
    })
      .then(res => res.json())
      .then(data => alert(data.mensagem || data.erro))
      .catch(() => alert('Erro ao adicionar ao carrinho'));
  }

  return (
    <div className="pagina-inicial">
      <header className="header">
        <h1>Feed de Figures</h1>
        <div className="botoes-topo">
          <button className="botao-perfil" onClick={irParaPerfil}>Ver Perfil</button>
          <button className="botao-adicionar" onClick={irParaAdicionarFigura}>Adicionar Figura</button>
          <button
            className="botao-carrinho topo"
            onClick={irParaCarrinho}
            aria-label="Ver carrinho"
            title="Ver carrinho"
          >
            <svg className="icone-carrinho" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="24" height="24">
              <circle cx="9" cy="21" r="1"></circle>
              <circle cx="20" cy="21" r="1"></circle>
              <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
            </svg>
          </button>
        </div>
      </header>

      <div className="filtros-container">
        <input
          type="text"
          placeholder="Buscar figures pelo nome..."
          value={filtro}
          onChange={e => {
            setFiltro(e.target.value);
            setObraSelecionada('');
          }}
          className="barra-pesquisa"
        />

        <select
          value={obraSelecionada}
          onChange={e => {
            setObraSelecionada(e.target.value);
            setFiltro('');
          }}
          className="select-categoria"
        >
          <option value="">Filtrar por obra...</option>
          {obras.map(o => (
            <option key={o.id} value={o.id}>{o.nome}</option>
          ))}
        </select>
      </div>

      <div className="lista-produtos">
        {figurasFiltradas.length === 0 ? (
          <p>Nenhuma figure encontrada.</p>
        ) : (
          figurasFiltradas.map(figura => (
            <div
              key={figura.id}
              className="card-produto"
              onClick={() => abrirDetalhes(figura.id)}
            >
              <img
                src={figura.imagem_url}
                alt={figura.nome}
                className="imagem-produto"
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = '/img/imagem-nao-disponivel.png';
                }}
              />
              <h3>{figura.nome}</h3>
              <p>Preço: R$ {figura.preco.toFixed(2)}</p>
              <button
                className="botao-carrinho card"
                onClick={(e) => adicionarAoCarrinho(e, figura.id)}
                aria-label={`Adicionar ${figura.nome} ao carrinho`}
                title="Adicionar ao carrinho"
              >
                <svg
                  className="icone-carrinho"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  width="20"
                  height="20"
                >
                  <circle cx="9" cy="21" r="1"></circle>
                  <circle cx="20" cy="21" r="1"></circle>
                  <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
                </svg>
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
