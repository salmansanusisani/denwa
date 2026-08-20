import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getCallDetail } from "../api/client.js";

// TODO(frontend): full structured result + transcript link if available.
export default function CallDetail() {
  const { callJobId } = useParams();
  const [detail, setDetail] = useState(null);

  useEffect(() => {
    // TODO(frontend): getCallDetail(callJobId).then(setDetail)
  }, [callJobId]);

  return (
    <div>
      <h1>Call detail</h1>
      {/* TODO(frontend): question_asked, answer_given, resolved, needs_human_followup, transcript_url */}
    </div>
  );
}
