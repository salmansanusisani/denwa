import { useState } from "react";
import { triggerIntake } from "../api/client.js";

// TODO(frontend): "Simulate missed call" button — DoD requires a pending/loading state until
// a result comes back.
export default function IntakeSimulate() {
  const [status, setStatus] = useState("idle"); // idle | pending | done | failed

  async function handleSimulate() {
    // TODO(frontend): read company_id + caller_number, call triggerIntake, set status.
  }

  return (
    <div>
      <h1>Simulate a missed call</h1>
      <button onClick={handleSimulate}>Simulate missed call</button>
      {status === "pending" && <p>Calling customer back…</p>}
      {status === "failed" && <p>Call failed.</p>}
    </div>
  );
}
