
import { Link } from "react-router-dom";
import "./Cabecalho.css";

function Cabecalho() {
  return (
    <header className="cabecalho">
      <Link to="/" className="logo">
        Páginas
      </Link>

      <nav className="navegacao">
        <Link to="/">Pesquisar livros</Link>
        <Link to="/login">Entrar</Link>
        <Link to="/cadastro" className="botao-cadastro">
          Criar conta
        </Link>
      </nav>
    </header>
  );
}

export default Cabecalho;
