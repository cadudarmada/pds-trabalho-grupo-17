
import { useState } from "react";
import { Link } from "react-router-dom";
import "./Cadastro.css";

function Login() {
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [mensagem, setMensagem] = useState("");
  const [tipoMensagem, setTipoMensagem] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();

    setMensagem("");
    setTipoMensagem("");

    if (!email.trim() || !senha) {
      setTipoMensagem("erro");
      setMensagem("Preencha o e-mail e a senha.");
      return;
    }

    if (!email.includes("@") || !email.includes(".")) {
      setTipoMensagem("erro");
      setMensagem("Digite um e-mail válido.");
      return;
    }

    try {
      const resposta = await fetch(
        "http://127.0.0.1:8000/usuarios/login",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: email.trim(),
            senha: senha,
          }),
        }
      );

      const dados = await resposta.json();

      if (!resposta.ok) {
        throw new Error(
          typeof dados.detail === "string"
            ? dados.detail
            : "Não foi possível realizar o login."
        );
      }

      setTipoMensagem("sucesso");
      setMensagem("Login realizado com sucesso!");

      setEmail("");
      setSenha("");

    } catch (erro) {
      setTipoMensagem("erro");
      setMensagem(
        erro.message || "Não foi possível conectar ao servidor."
      );
    }
  }

  return (
    <div className="cadastro-container">
      <div className="cadastro-card">
        <h1>Entrar</h1>

        <p>
          Acesse sua conta para continuar organizando suas leituras.
        </p>

        {mensagem && (
          <p className={`mensagem ${tipoMensagem}`}>
            {mensagem}
          </p>
        )}

        <form onSubmit={handleSubmit} noValidate>
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
            />
          </div>

          <button type="submit">
            Entrar
          </button>
        </form>

        <p className="link-cadastro">
          Ainda não tem conta? <Link to="/cadastro">Criar conta</Link>
        </p>
      </div>
    </div>
  );
}

export default Login;
