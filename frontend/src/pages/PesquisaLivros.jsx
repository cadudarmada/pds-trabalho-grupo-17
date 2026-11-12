
import { useState } from "react";
import "./PesquisaLivros.css";

function PesquisaLivros() {
    const [termo, setTermo] = useState("");
    const [livros, setLivros] = useState([]);
    const [carregando, setCarregando] = useState(false);
    const [erro, setErro] = useState("");
    const [pesquisou, setPesquisou] = useState(false);

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

        try {
            const resposta = await fetch(
                `http://127.0.0.1:8000/livros/pesquisa?termo=${encodeURIComponent(termo)}`
            );

            const dados = await resposta.json();

            if (!resposta.ok) {
                throw new Error("Não foi possível realizar a pesquisa.");
            }

            setLivros(dados.livros);
        } catch (erro) {
            setErro(erro.message || "Erro ao pesquisar livros.");
        } finally {
            setCarregando(false);
        }
    }

    return (
        <main className="pagina-pesquisa">
            <section className="introducao-pesquisa">
                <h1>Descubra seu próximo livro.</h1>

                <p>
                    Explore livros, encontre novos autores e descubra
                    histórias que merecem ser lidas.
                </p>

                <form
                    className="formulario-pesquisa"
                    onSubmit={handleSubmit}
                >
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
                    <p className="mensagem-pesquisa">
                        Pesquisando livros...
                    </p>
                )}

                {erro && (
                    <p className="mensagem-erro">{erro}</p>
                )}

                {pesquisou && !carregando && !erro && livros.length === 0 && (
                    <p className="mensagem-pesquisa">
                        Nenhum livro encontrado.
                    </p>
                )}

                {livros.length > 0 && (
                    <>
                        <h2>Resultados da pesquisa</h2>

                        <div className="lista-livros">
                            {livros.map((livro) => (
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
                                            <p className="livro-descricao">
                                                {livro.descricao}
                                            </p>
                                        )}
                                    </div>
                                </article>
                            ))}
                        </div>
                    </>
                )}
            </section>
        </main>
    );
}

export default PesquisaLivros;
