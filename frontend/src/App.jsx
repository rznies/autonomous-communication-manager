import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./views/Dashboard";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/queue" replace />} />
          <Route path="queue" element={<Dashboard />} />
          <Route path="metrics" element={<div>Metrics Placeholder</div>} />
          <Route path="contacts" element={<div>Contacts Placeholder</div>} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
