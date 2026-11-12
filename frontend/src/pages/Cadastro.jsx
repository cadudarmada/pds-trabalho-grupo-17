
import { useState } from "react";
import "./Cadastro.css";

function Cadastro() {
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [mensagem, setMensagem] = useState("");
  const [tipoMensagem, setTipoMensagem] = useState("");

  function handleSubmit(event) {
    event.preventDefault();

    if (nome.trim().length < 3) {
      setTipoMensagem("erro");
      setMensagem("O nome precisa ter pelo menos 3 caracteres.");
      return;
    }

    if (senha.length < 8) {
      setTipoMensagem("erro");
      setMensagem("A senha precisa ter pelo menos 8 caracteres.");
      return;
    }

    if (!email.includes("@") || !email.includes(".")) {
      setTipoMensagem("erro");
      setMensagem("Digite um e-mail válido.");
      return;
    }

    setTipoMensagem("sucesso");
    setMensagem("Formulário validado com sucesso!");
  }

  return (
    <div className="cadastro-container">
      <div className="cadastro-card">
        <h1>Criar conta</h1>

        <p>
          Cadastre-se para começar a organizar suas leituras.
        </p>

        {mensagem && (
          <p className={`mensagem ${tipoMensagem}`}>
            {mensagem}
          </p>
        )}

        <form onSubmit={handleSubmit} noValidate>
          <div className="cadastro-campo">
            <label htmlFor="nome">Nome</label>
            <input
              type="text"
              id="nome"
              name="nome"
              placeholder="Digite seu nome"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              required
              minLength={3}
              maxLength={100}
            />
          </div>

          <div className="cadastro-campo">
            <label htmlFor="email">E-mail</label>
            <input
              type="email"
              id="email"
              name="email"
              placeholder="Digite seu e-mail"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              maxLength={255}
            />
          </div>

          <div className="cadastro-campo">
            <label htmlFor="senha">Senha</label>
            <input
              type="password"
              id="senha"
              name="senha"
              placeholder="Digite sua senha"
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
              required
              minLength={8}
              maxLength={128}
            />
          </div>

          <button type="submit">
            Criar conta
          </button>
        </form>
      </div>
    </div>
  );
}

export default Cadastro;
