import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./MinhaBiblioteca.css";

const OPCOES_STATUS = [
  { valor: "QUERO_LER", rotulo: "Quero ler" },
  { valor: "LENDO", rotulo: "Lendo" },
  { valor: "LIDO", rotulo: "Lido" },
  { valor: "ABANDONADO", rotulo: "Abandonado" },
];

const ROTULO_POR_STATUS = {
  QUERO_LER: "Quero ler",
  LENDO: "Lendo",
  LIDO: "Lido",
  ABANDONADO: "Abandonado",
};

function formatarData(dataIso) {
  if (!dataIso) {
    return "";
  }

  return new Date(dataIso).toLocaleDateString("pt-BR");
}

function MinhaBiblioteca() {
  const navigate = useNavigate();
  const [itens, setItens] = useState([]);
  const [filtroStatus, setFiltroStatus] = useState("TODOS");
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [atualizandoId, setAtualizandoId] = useState(null);
  const [feedbackPorItem, setFeedbackPorItem] = useState({});

  useEffect(() => {
    let ativo = true;

    async function carregarBiblioteca() {
      const token = sessionStorage.getItem("access_token");

      if (!token) {
        navigate("/login", { replace: true });
        return;
      }

      setCarregando(true);
      setErro("");

      const url =
        filtroStatus === "TODOS"
          ? "http://127.0.0.1:8000/biblioteca"
          : `http://127.0.0.1:8000/biblioteca?status=${encodeURIComponent(filtroStatus)}`;

      try {
        const resposta = await fetch(url, {
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
          navigate("/login", { replace: true });
          return;
        }

        if (!resposta.ok) {
          throw new Error("Não foi possível carregar sua biblioteca.");
        }

        const dados = await resposta.json();
        setItens(dados);
      } catch (erroRequisicao) {
        if (!ativo) {
          return;
        }

        setErro(
          erroRequisicao.message ||
            "Não foi possível conectar ao servidor. Tente novamente."
        );
      } finally {
        if (ativo) {
          setCarregando(false);
        }
      }
    }

    carregarBiblioteca();

    return () => {
      ativo = false;
    };
  }, [navigate, filtroStatus]);

  async function handleAtualizarStatus(itemId, novoStatus) {
    const token = sessionStorage.getItem("access_token");

    if (!token) {
      navigate("/login", { replace: true });
      return;
    }

    setAtualizandoId(itemId);
    setFeedbackPorItem((anterior) => ({
      ...anterior,
      [itemId]: null,
    }));

    try {
      const resposta = await fetch(
        `http://127.0.0.1:8000/biblioteca/${itemId}/status`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ status: novoStatus }),
        }
      );

      if (resposta.status === 401) {
        sessionStorage.removeItem("access_token");
        navigate("/login", { replace: true });
        return;
      }

      const dados = await resposta.json();

      if (!resposta.ok) {
        throw new Error(
          typeof dados.detail === "string"
            ? dados.detail
            : "Não foi possível atualizar o status."
        );
      }

      setItens((anterior) => {
        if (filtroStatus !== "TODOS" && dados.status !== filtroStatus) {
          return anterior.filter((item) => item.id !== itemId);
        }

        return anterior.map((item) => (item.id === itemId ? dados : item));
      });

      setFeedbackPorItem((anterior) => ({
        ...anterior,
        [itemId]: {
          tipo: "sucesso",
          texto: "Status atualizado!",
        },
      }));
    } catch (erroAtualizacao) {
      setFeedbackPorItem((anterior) => ({
        ...anterior,
        [itemId]: {
          tipo: "erro",
          texto:
            erroAtualizacao.message || "Erro ao atualizar status de leitura.",
        },
      }));
    } finally {
      setAtualizandoId(null);
    }
  }

  const totalLivros = itens.length;
  const rotuloTotal =
    totalLivros === 1 ? "1 livro" : `${totalLivros} livros`;

  return (
    <main className="pagina-biblioteca">
      <section className="introducao-biblioteca">
        <div className="introducao-texto">
          <h1>Minha Biblioteca</h1>
          <p>
            Acompanhe sua coleção pessoal de livros e organize suas próximas
            leituras em um só lugar.
          </p>
        </div>

        <Link to="/" className="botao-explorar">
          Pesquisar livros
        </Link>
      </section>

      <section className="secao-colecao">
        <div className="colecao-cabecalho">
          <h2>
            Sua coleção {!carregando && totalLivros > 0 ? `(${rotuloTotal})` : ""}
          </h2>

          <div className="filtros-status" role="group" aria-label="Filtrar por status">
            <button
              type="button"
              className={
                filtroStatus === "TODOS"
                  ? "filtro-botao ativo"
                  : "filtro-botao"
              }
              onClick={() => setFiltroStatus("TODOS")}
            >
              Todos
            </button>

            {OPCOES_STATUS.map((opcao) => (
              <button
                type="button"
                key={opcao.valor}
                className={
                  filtroStatus === opcao.valor
                    ? "filtro-botao ativo"
                    : "filtro-botao"
                }
                onClick={() => setFiltroStatus(opcao.valor)}
              >
                {opcao.rotulo}
              </button>
            ))}
          </div>
        </div>

        {carregando ? (
          <p className="mensagem-biblioteca">Carregando sua biblioteca...</p>
        ) : erro ? (
          <p className="mensagem-erro">{erro}</p>
        ) : totalLivros === 0 ? (
          <div className="biblioteca-vazia">
            {filtroStatus === "TODOS" ? (
              <>
                <p className="biblioteca-vazia-titulo">
                  Sua biblioteca ainda está vazia.
                </p>
                <p className="biblioteca-vazia-descricao">
                  Pesquise por títulos ou autores para começar a montar sua
                  estante pessoal.
                </p>
                <Link to="/" className="botao-explorar">
                  Explorar catálogo
                </Link>
              </>
            ) : (
              <>
                <p className="biblioteca-vazia-titulo">
                  Nenhum livro com o status &ldquo;{ROTULO_POR_STATUS[filtroStatus]}&rdquo;.
                </p>
                <p className="biblioteca-vazia-descricao">
                  Altere o filtro acima ou atualize o status de algum livro da
                  sua coleção.
                </p>
              </>
            )}
          </div>
        ) : (
          <div className="lista-biblioteca">
            {itens.map((item) => {
              const { livro } = item;
              const salvandoEste = atualizandoId === item.id;
              const feedback = feedbackPorItem[item.id];
              const classeBadge = `status-badge status-${item.status.toLowerCase()}`;

              return (
                <article className="biblioteca-card" key={item.id}>
                  <div className="biblioteca-capa">
                    {livro.capa ? (
                      <img
                        src={livro.capa}
                        alt={`Capa de ${livro.titulo}`}
                      />
                    ) : (
                      <div className="biblioteca-capa-indisponivel">
                        Capa indisponível
                      </div>
                    )}
                  </div>

                  <div className="biblioteca-informacoes">
                    <div className="biblioteca-titulo-linha">
                      <h3>{livro.titulo}</h3>
                      <span className={classeBadge}>
                        {ROTULO_POR_STATUS[item.status] || item.status}
                      </span>
                    </div>

                    <p className="biblioteca-autores">
                      {livro.autores.join(", ") || "Autor não informado"}
                    </p>

                    <p className="biblioteca-meta">
                      {livro.editora || "Editora não informada"}
                      {" · "}
                      {livro.data_publicacao || "Data não informada"}
                    </p>

                    <p className="biblioteca-data-adicao">
                      Adicionado em {formatarData(item.data_adicao)}
                    </p>

                    {livro.descricao && (
                      <p className="biblioteca-descricao">{livro.descricao}</p>
                    )}

                    <div className="biblioteca-status-controle">
                      <label htmlFor={`status-${item.id}`}>
                        Status de leitura:
                      </label>

                      <select
                        id={`status-${item.id}`}
                        value={item.status}
                        disabled={salvandoEste}
                        onChange={(evento) =>
                          handleAtualizarStatus(item.id, evento.target.value)
                        }
                      >
                        {OPCOES_STATUS.map((opcao) => (
                          <option key={opcao.valor} value={opcao.valor}>
                            {opcao.rotulo}
                          </option>
                        ))}
                      </select>

                      {salvandoEste && (
                        <span className="status-feedback salvando">
                          Salvando...
                        </span>
                      )}

                      {!salvandoEste && feedback && (
                        <span className={`status-feedback ${feedback.tipo}`}>
                          {feedback.texto}
                        </span>
                      )}
                    </div>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </section>
    </main>
  );
}

export default MinhaBiblioteca;
