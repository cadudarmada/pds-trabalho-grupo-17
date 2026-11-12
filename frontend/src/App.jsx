import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Cadastro from "./pages/Cadastro";
import Login from "./pages/Login";
import PesquisaLivros from "./pages/PesquisaLivros";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<PesquisaLivros />} />
        <Route path="/cadastro" element={<Cadastro />} />
        <Route path="/login" element={<Login />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
