import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./MinhaBiblioteca.css";

function MinhaBiblioteca() {
  const navigate = useNavigate();
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  useEffect(() => {
    let ativo = true;

    async function validarSessao() {
      const token = sessionStorage.getItem("access_token");

      if (!token) {
        navigate("/login", { replace: true });
        return;
      }

      try {
        const resposta = await fetch("http://127.0.0.1:8000/usuarios/me", {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!ativo) {
          return;
        }

        if (!resposta.ok) {
          sessionStorage.removeItem("access_token");
          navigate("/login", { replace: true });
          return;
        }

        setCarregando(false);
      } catch {
        if (!ativo) {
          return;
        }

        setErro("Não foi possível verificar sua sessão. Tente novamente.");
        setCarregando(false);
      }
    }

    validarSessao();

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
          <h2>Sua coleção</h2>

          <div className="biblioteca-vazia">
            <p className="biblioteca-vazia-titulo">
              Sua biblioteca ainda está vazia.
            </p>
            <p className="biblioteca-vazia-descricao">
              Pesquise por títulos ou autores para começar a montar sua estante
              pessoal.
            </p>
            <Link to="/" className="botao-explorar">
              Explorar catálogo
            </Link>
          </div>
        </section>
      )}
    </main>
  );
}

export default MinhaBiblioteca;
