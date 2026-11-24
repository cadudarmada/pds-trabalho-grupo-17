import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./PesquisaLivros.css";

function PesquisaLivros() {
  const navigate = useNavigate();
  const [termo, setTermo] = useState("");
  const [livros, setLivros] = useState([]);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState("");
  const [pesquisou, setPesquisou] = useState(false);

  const [livrosNaBiblioteca, setLivrosNaBiblioteca] = useState(new Set());
  const [adicionandoId, setAdicionandoId] = useState(null);
  const [feedbackPorLivro, setFeedbackPorLivro] = useState({});

  const autenticado = Boolean(sessionStorage.getItem("access_token"));

  useEffect(() => {
    let ativo = true;

    async function carregarIdsBiblioteca() {
      const token = sessionStorage.getItem("access_token");
      if (!token) {
        return;
      }

      try {
        const resposta = await fetch("http://127.0.0.1:8000/biblioteca", {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!ativo) {
          return;
        }

        if (resposta.status === 401) {
          sessionStorage.removeItem("access_token");
          return;
        }

        if (!resposta.ok) {
          return;
        }

        const itens = await resposta.json();
        const ids = new Set(itens.map((item) => item.livro.google_books_id));
        setLivrosNaBiblioteca(ids);
      } catch {
        // Ignora erro silencioso ao pré-carregar IDs da biblioteca
      }
    }

    carregarIdsBiblioteca();

    return () => {
      ativo = false;
    };
  }, []);

  async function handleSubmit(evento) {
    evento.preventDefault();

    if (termo.trim().length < 2) {
      setErro("Digite pelo menos 2 caracteres.");
      return;
    }

    setCarregando(true);
    setErro("");
    setPesquisou(true);
    setLivros([]);
    setFeedbackPorLivro({});

    try {
      const resposta = await fetch(
        `http://127.0.0.1:8000/livros/pesquisa?termo=${encodeURIComponent(termo)}`
      );

      const dados = await resposta.json();

      if (!resposta.ok) {
        throw new Error("Não foi possível realizar a pesquisa.");
      }

      setLivros(dados.livros);
    } catch (erroRequisicao) {
      setErro(erroRequisicao.message || "Erro ao pesquisar livros.");
    } finally {
      setCarregando(false);
    }
  }

  async function handleAdicionarBiblioteca(livro) {
    const token = sessionStorage.getItem("access_token");

    if (!token) {
      navigate("/login");
      return;
    }

    if (!livro.id || !livro.titulo) {
      setFeedbackPorLivro((anterior) => ({
        ...anterior,
        [livro.id]: {
          tipo: "erro",
          texto: "Este livro não possui dados suficientes para ser salvo.",
        },
      }));
      return;
    }

    setAdicionandoId(livro.id);
    setFeedbackPorLivro((anterior) => ({
      ...anterior,
      [livro.id]: null,
    }));

    try {
      const resposta = await fetch("http://127.0.0.1:8000/biblioteca", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          google_books_id: livro.id,
          titulo: livro.titulo,
          autores: livro.autores || [],
          editora: livro.editora || null,
          data_publicacao: livro.data_publicacao || null,
          isbn: livro.isbn || null,
          descricao: livro.descricao || null,
          capa: livro.capa || null,
        }),
      });

      if (resposta.status === 401) {
        sessionStorage.removeItem("access_token");
        navigate("/login");
        return;
      }

      const dados = await resposta.json();

      if (resposta.status === 409) {
        setLivrosNaBiblioteca((anterior) => new Set(anterior).add(livro.id));
        setFeedbackPorLivro((anterior) => ({
          ...anterior,
          [livro.id]: {
            tipo: "sucesso",
            texto: dados.detail || "Este livro já está na sua biblioteca.",
          },
        }));
        return;
      }

      if (!resposta.ok) {
        throw new Error(
          typeof dados.detail === "string"
            ? dados.detail
            : "Não foi possível adicionar o livro à biblioteca."
        );
      }

      setLivrosNaBiblioteca((anterior) => new Set(anterior).add(livro.id));
      setFeedbackPorLivro((anterior) => ({
        ...anterior,
        [livro.id]: {
          tipo: "sucesso",
          texto: "Livro adicionado à sua biblioteca!",
        },
      }));
    } catch (erroAdicao) {
      setFeedbackPorLivro((anterior) => ({
        ...anterior,
        [livro.id]: {
          tipo: "erro",
          texto: erroAdicao.message || "Erro ao conectar com o servidor.",
        },
      }));
    } finally {
      setAdicionandoId(null);
    }
  }

  return (
    <main className="pagina-pesquisa">
      <section className="introducao-pesquisa">
        <h1>Descubra seu próximo livro.</h1>

        <p>
          Explore livros, encontre novos autores e descubra histórias que
          merecem ser lidas.
        </p>

        <form className="formulario-pesquisa" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Pesquise por título ou autor..."
            value={termo}
            onChange={(evento) => setTermo(evento.target.value)}
          />

          <button type="submit" disabled={carregando}>
            {carregando ? "Pesquisando..." : "Pesquisar"}
          </button>
        </form>
      </section>

      <section className="secao-resultados">
        {carregando && (
          <p className="mensagem-pesquisa">Pesquisando livros...</p>
        )}

        {erro && <p className="mensagem-erro">{erro}</p>}

        {pesquisou && !carregando && !erro && livros.length === 0 && (
          <p className="mensagem-pesquisa">Nenhum livro encontrado.</p>
        )}

        {livros.length > 0 && (
          <>
            <h2>Resultados da pesquisa</h2>

            <div className="lista-livros">
              {livros.map((livro) => {
                const jaAdicionado = livrosNaBiblioteca.has(livro.id);
                const adicionandoEste = adicionandoId === livro.id;
                const feedback = feedbackPorLivro[livro.id];

                return (
                  <article className="livro-card" key={livro.id}>
                    <div className="livro-capa">
                      {livro.capa ? (
                        <img
                          src={livro.capa}
                          alt={`Capa de ${livro.titulo}`}
                        />
                      ) : (
                        <div className="capa-indisponivel">
                          Capa indisponível
                        </div>
                      )}
                    </div>

                    <div className="livro-informacoes">
                      <h3>{livro.titulo}</h3>

                      <p className="livro-autores">
                        {livro.autores.join(", ") || "Autor não informado"}
                      </p>

                      <p>
                        {livro.editora || "Editora não informada"}
                        {" · "}
                        {livro.data_publicacao || "Data não informada"}
                      </p>

                      {livro.descricao && (
                        <p className="livro-descricao">{livro.descricao}</p>
                      )}

                      <div className="livro-acoes">
                        {autenticado ? (
                          <button
                            type="button"
                            className={
                              jaAdicionado
                                ? "botao-adicionado"
                                : "botao-adicionar"
                            }
                            disabled={jaAdicionado || adicionandoEste}
                            onClick={() => handleAdicionarBiblioteca(livro)}
                          >
                            {adicionandoEste
                              ? "Adicionando..."
                              : jaAdicionado
                                ? "Na sua biblioteca"
                                : "Adicionar à biblioteca"}
                          </button>
                        ) : (
                          <Link to="/login" className="link-entrar-salvar">
                            Entre para adicionar à biblioteca
                          </Link>
                        )}

                        {feedback && (
                          <span className={`feedback-livro ${feedback.tipo}`}>
                            {feedback.texto}
                          </span>
                        )}
                      </div>
                    </div>
                  </article>
                );
              })}
            </div>
          </>
        )}
      </section>
    </main>
  );
}

export default PesquisaLivros;
