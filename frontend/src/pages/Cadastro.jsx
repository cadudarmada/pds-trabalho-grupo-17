
import { useState } from "react";
import "./Cadastro.css";

function Cadastro() {
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [mensagem, setMensagem] = useState("");
  const [tipoMensagem, setTipoMensagem] = useState("");

  
async function handleSubmit(event) {
  event.preventDefault();

  setMensagem("");
  setTipoMensagem("");

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

  try {
    const resposta = await fetch(
      "http://127.0.0.1:8000/usuarios/cadastro",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          nome: nome.trim(),
          email: email.trim(),
          senha: senha,
        }),
      }
    );

    const dados = await resposta.json();

    
    if (!resposta.ok) {

        let mensagemErro = "Não foi possível realizar o cadastro.";

            if (typeof dados.detail === "string") {
                mensagemErro = dados.detail;
            } else if (Array.isArray(dados.detail)) {
                mensagemErro = dados.detail
                    .map((erro) => {
                    const campo = erro.loc?.at(-1);

                    if (campo === "email") {
                        return "Digite um endereço de e-mail válido.";
                    }

                    if (campo === "senha" && erro.type === "string_too_short") {
                        return "A senha precisa ter pelo menos 8 caracteres.";
                    }

                    if (campo === "nome" && erro.type === "string_too_short") {
                        return "O nome precisa ter pelo menos 3 caracteres.";
                    }

                    return "Verifique os dados informados.";
                    })
                    .join(" ");
            }

        throw new Error(mensagemErro);
    }


    setTipoMensagem("sucesso");
    setMensagem(`Conta criada com sucesso! Bem-vindo(a), ${dados.nome}.`);

    setNome("");
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
