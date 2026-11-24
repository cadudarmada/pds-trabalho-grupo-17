import { Link, useLocation, useNavigate } from "react-router-dom";
import "./Cabecalho.css";

function Cabecalho() {
  const navigate = useNavigate();
  useLocation();

  const autenticado = Boolean(sessionStorage.getItem("access_token"));

  function handleSair() {
    sessionStorage.removeItem("access_token");
    navigate("/login");
  }

  return (
    <header className="cabecalho">
      <Link to={autenticado ? "/biblioteca" : "/"} className="logo">
        Páginas
      </Link>

      <nav className="navegacao">
        <Link to="/">Pesquisar livros</Link>

        {autenticado ? (
          <>
            <Link to="/biblioteca">Minha Biblioteca</Link>
            <button
              type="button"
              className="botao-sair"
              onClick={handleSair}
            >
              Sair
            </button>
          </>
        ) : (
          <>
            <Link to="/login">Entrar</Link>
            <Link to="/cadastro" className="botao-cadastro">
              Criar conta
            </Link>
          </>
        )}
      </nav>
    </header>
  );
}

export default Cabecalho;
