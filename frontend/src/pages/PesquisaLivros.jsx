import { useState } from "react";

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
        <div>
            <h1>Pesquisar livros</h1>

            <p>
                Encontre livros pelo título ou pelo nome do autor.
            </p>

            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    placeholder="Digite o título ou autor..."
                    value={termo}
                    onChange={(evento) => setTermo(evento.target.value)}
                />

                <button type="submit" disabled={carregando}>
                    {carregando ? "Pesquisando..." : "Pesquisar"}
                </button>
            </form>

            {carregando && <p>Pesquisando livros...</p>}

            {erro && <p>{erro}</p>}

            {pesquisou && !carregando && !erro && livros.length === 0 && (
                <p>Nenhum livro encontrado.</p>
            )}

            <div>
                {livros.map((livro) => (
                    <div key={livro.id}>
                        {livro.capa && (
                            <img
                                src={livro.capa}
                                alt={`Capa de ${livro.titulo}`}
                                width="120"
                            />
                        )}

                        <h2>{livro.titulo}</h2>

                        <p>
                            Autor(es): {livro.autores.join(", ") || "Não informado"}
                        </p>

                        <p>
                            Editora: {livro.editora || "Não informada"}
                        </p>

                        <p>
                            Publicação: {livro.data_publicacao || "Não informada"}
                        </p>

                        {livro.descricao && (
                            <p>{livro.descricao}</p>
                        )}
                    </div>
                ))}
            </div>

        </div>
    );
}

export default PesquisaLivros;
