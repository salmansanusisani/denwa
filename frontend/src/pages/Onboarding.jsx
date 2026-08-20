import { useState } from "react";
import { createCompany, uploadDocument } from "../api/client.js";

// TODO(frontend): form to create a demo company + upload its knowledge-base file(s)/text.
// DoD: must show a success/failure state after the upload call.
export default function Onboarding() {
  const [status, setStatus] = useState("idle"); // idle | loading | success | error

  async function handleSubmit(e) {
    e.preventDefault();
    // TODO(frontend): read form fields, call createCompany then uploadDocument, set status accordingly.
  }

  return (
    <div>
      <h1>Onboard a company</h1>
      <form onSubmit={handleSubmit}>{/* TODO(frontend): name, phone_number, file input */}</form>
      {status === "loading" && <p>Uploading…</p>}
      {status === "success" && <p>Company created.</p>}
      {status === "error" && <p>Something went wrong.</p>}
    </div>
  );
}
