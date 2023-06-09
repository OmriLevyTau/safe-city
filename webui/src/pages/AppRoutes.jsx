import { BrowserRouter, Route, Routes } from "react-router-dom";
import Landing from "./Landing";
import AppHome from "./Home";

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/home" element={<AppHome />}></Route>
        <Route path="/" element={<Landing />}></Route>
      </Routes>
    </BrowserRouter>
  );
}

