import { useEffect, useState } from "react";
import axios from "axios";

export default function ReviewerDashboard() {
  const [metrics, setMetrics] = useState(null);
  const [queue, setQueue] = useState([]);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const res = await axios.get("https://playto-kyc-backend-l6t5.onrender.com/api/v1/reviewer/dashboard/");
      setMetrics(res.data.metrics);
      setQueue(res.data.queue);
      console.log("Reviewer dashboard:", res.data);
    } catch (err) {
      console.log("Dashboard error:", err.response?.data || err.message);
    }
  };

 const handleDecision = async (id, state) => {
  const reason = prompt("Enter reason:");

  if (!reason) {
    alert("Reason required");
    return;
  }

  try {
    await axios.post(`https://playto-kyc-backend-l6t5.onrender.com/api/v1/kyc/${id}/state/`, {
      state: state,
      reason: reason,
    });

    alert(`KYC ${state} ✅`);
    loadDashboard();
  } catch (err) {
    console.log("ACTION ERROR 👉", err.response?.data || err.message);
    alert(
      err.response?.data?.details ||
      err.response?.data?.error ||
      "Action failed ❌"
    );
  }
};

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-2xl font-bold mb-6">Reviewer Dashboard</h1>

      {metrics && (
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-white p-4 rounded shadow">
            <p className="text-sm text-gray-500">Queue</p>
            <p className="text-2xl font-bold">{metrics.total_submissions_in_queue}</p>
          </div>

          <div className="bg-white p-4 rounded shadow">
            <p className="text-sm text-gray-500">Avg Time</p>
            <p className="text-2xl font-bold">
              {metrics.average_time_in_queue_hours} hrs
            </p>
          </div>

          <div className="bg-white p-4 rounded shadow">
            <p className="text-sm text-gray-500">Approval Rate</p>
            <p className="text-2xl font-bold">
              {metrics.approval_rate_last_7_days}%
            </p>
          </div>
        </div>
      )}

      <div className="bg-white rounded shadow p-4">
        <h2 className="text-xl font-semibold mb-4">Queue List</h2>

        {queue.length === 0 ? (
          <p>No submissions in queue</p>
        ) : (
          queue.map((item) => (
            <div
              key={item.id}
              className={`border p-4 rounded mb-3 ${
                item.at_risk ? "bg-red-100" : "bg-gray-50"
              }`}
            >
              <p><b>ID:</b> {item.id}</p>
              <p><b>Name:</b> {item.name}</p>
              <p><b>Email:</b> {item.email}</p>
              <p><b>Business:</b> {item.business_name}</p>
              <p><b>State:</b> {item.state}</p>
              <p><b>Time in Queue:</b> {item.time_in_queue_hours} hrs</p>
              <p>
                <b>SLA:</b>{" "}
                {item.at_risk ? "At Risk ⚠️" : "OK ✅"}
              </p>

              {item.documents && (
                <a
                  href={`https://playto-kyc-backend-l6t5.onrender.com${item.documents}`}
                  target="_blank"
                  className="text-blue-600 underline"
                >
                  View Document
                </a>
              )}

              <div className="mt-3 flex gap-2">
                <button
  onClick={() => handleDecision(item.id, "under_review")}
  className="bg-blue-500 text-white px-3 py-1 rounded"
>
  Start Review
</button>
                <button
                  onClick={() => handleDecision(item.id, "approved")}
                  className="bg-green-500 text-white px-3 py-1 rounded"
                >
                  Approve
                </button>

                <button
                  onClick={() => handleDecision(item.id, "rejected")}
                  className="bg-red-500 text-white px-3 py-1 rounded"
                >
                  Reject
                </button>
                <button
  onClick={() => handleDecision(item.id, "more_info_requested")}
  className="bg-orange-500 text-white p-2 rounded"
>
  Request More Info
</button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}