import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./MinhaBiblioteca.css";

function formatarData(dataIso) {
  if (!dataIso) {
    return "";
  }

  return new Date(dataIso).toLocaleDateString("pt-BR");
}

function MinhaBiblioteca() {
  const navigate = useNavigate();
  const [itens, setItens] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  useEffect(() => {
    let ativo = true;

    async function carregarBiblioteca() {
      const token = sessionStorage.getItem("access_token");

      if (!token) {
        navigate("/login", { replace: true });
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
  }, [navigate]);

  if (carregando) {
    return (
      <main className="pagina-biblioteca">
        <p className="mensagem-biblioteca">Carregando sua biblioteca...</p>
      </main>
    );
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

      {erro ? (
        <p className="mensagem-erro">{erro}</p>
      ) : (
        <section className="secao-colecao">
          <h2>
            Sua coleção {totalLivros > 0 ? `(${rotuloTotal})` : ""}
          </h2>

          {totalLivros === 0 ? (
            <div className="biblioteca-vazia">
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
            </div>
          ) : (
            <div className="lista-biblioteca">
              {itens.map((item) => {
                const { livro } = item;

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
                      <h3>{livro.titulo}</h3>

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
                        <p className="biblioteca-descricao">
                          {livro.descricao}
                        </p>
                      )}
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </section>
      )}
    </main>
  );
}

export default MinhaBiblioteca;
