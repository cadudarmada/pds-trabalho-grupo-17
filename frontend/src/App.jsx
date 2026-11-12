import { BrowserRouter, Routes, Route } from "react-router-dom";

import Cadastro from "./pages/Cadastro";
import Login from "./pages/Login";
import PesquisaLivros from "./pages/PesquisaLivros";
import Cabecalho from "./components/Cabecalho";

function App() {
  return (
    <BrowserRouter>
      <Cabecalho />

      <Routes>
        <Route path="/" element={<PesquisaLivros />} />
        <Route path="/cadastro" element={<Cadastro />} />
        <Route path="/login" element={<Login />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
