import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Login from "./pages/Login.jsx";
import Onboarding from "./pages/Onboarding.jsx";
import IntakeSimulate from "./pages/IntakeSimulate.jsx";
import CallHistory from "./pages/CallHistory.jsx";
import CallDetail from "./pages/CallDetail.jsx";

// TODO(frontend): gate routes behind Login once basic auth exists.
export default function App() {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/">Login</Link> | <Link to="/onboarding">Onboarding</Link> |{" "}
        <Link to="/intake">Simulate Call</Link> | <Link to="/calls">Call History</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/onboarding" element={<Onboarding />} />
        <Route path="/intake" element={<IntakeSimulate />} />
        <Route path="/calls" element={<CallHistory />} />
        <Route path="/calls/:callJobId" element={<CallDetail />} />
      </Routes>
    </BrowserRouter>
  );
}
