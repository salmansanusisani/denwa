import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listCalls } from "../api/client.js";

// TODO(frontend): table/list of past calls — caller number, question asked, answer given,
// resolved status, timestamp. Must render real backend data, not mock, for the DoD.
export default function CallHistory() {
  const [calls, setCalls] = useState([]);

  useEffect(() => {
    // TODO(frontend): listCalls(companyId).then(setCalls)
  }, []);

  return (
    <div>
      <h1>Call history</h1>
      {/* TODO(frontend): render a table row per call, link each row to /calls/:callJobId */}
    </div>
  );
}
