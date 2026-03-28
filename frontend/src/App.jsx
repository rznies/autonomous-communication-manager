import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./views/Dashboard";
import Analytics from "./views/Analytics";
import Contacts from "./views/Contacts";
import LandingPage from "./views/LandingPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/app" element={<Layout />}>
          <Route index element={<Navigate to="/app/queue" replace />} />
          <Route path="queue" element={<Dashboard />} />
          <Route path="metrics" element={<Analytics />} />
          <Route path="contacts" element={<Contacts />} />
        </Route>
        {/* Support old /queue links just in case */}
        <Route path="/queue" element={<Navigate to="/app/queue" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
