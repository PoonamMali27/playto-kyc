import { useState, useEffect } from "react";
import axios from "axios";
import ReviewerDashboard from "./components/ReviewerDashboard";
function App() {
  const [step, setStep] = useState(1);
const [view, setView] = useState("merchant");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [businessName, setBusinessName] = useState("");
  const [businessType, setBusinessType] = useState("");
  const [monthlyVolume, setMonthlyVolume] = useState("");
  const [file, setFile] = useState(null);
  const [kycId, setKycId] = useState(null);
  const [documentType, setDocumentType] = useState("PAN");

  useEffect(() => {
    const loadDraft = async () => {
      try {
        const res = await axios.get("https://playto-kyc-backend-l6t5.onrender.com/api/v1/kyc/draft/latest/");

        setKycId(res.data.id);
        setName(res.data.name || "");
        setEmail(res.data.email || "");
        setPhone(res.data.phone || "");
        setBusinessName(res.data.business_name || "");
        setBusinessType(res.data.business_type || "");
        setMonthlyVolume(res.data.monthly_volume || "");

        console.log("Draft loaded ✅", res.data);
      } catch (err) {
        console.log("No draft found or error:", err.response?.data);
      }
    };

    loadDraft();
  }, []);

  const nextStep = () => setStep(step + 1);
  const prevStep = () => setStep(step - 1);

  const handleSubmit = async () => {
    if (!name || !email || !phone || !businessName || !businessType || !monthlyVolume) {
  alert("Please complete all fields before final submit");
  return;
}
    try {
      console.log("SUBMIT CLICKED");

      const res = await axios.post("https://playto-kyc-backend-l6t5.onrender.com/api/v1/kyc/", {
        name,
        email,
        phone,
        business_name: businessName,
        business_type: businessType,
        monthly_volume: monthlyVolume,
      });

      console.log("SUBMIT SUCCESS 👉", res.data);
      setKycId(res.data.id);
      alert("KYC submitted successfully ✅");
    } catch (err) {
      console.log("SUBMIT ERROR 👉", err.response?.data || err.message);
      alert("Submit failed ❌");
    }
  };

  const handleSaveDraft = async () => {
    try {
      const res = await axios.post("https://playto-kyc-backend-l6t5.onrender.com/api/v1/kyc/draft/", {
        id: kycId,
        name,
        email,
        phone,
        business_name: businessName,
        business_type: businessType,
        monthly_volume: monthlyVolume || null,
      });

      console.log("DRAFT SAVED 👉", res.data);
      setKycId(res.data.id);
      alert("Draft saved ✅");
    } catch (err) {
      console.log("DRAFT ERROR 👉", err.response?.data || err.message);
      alert("Draft save failed ❌");
    }
  };

  const handleUpload = async () => {
    console.log("KYC ID 👉", kycId);
    console.log("FILE 👉", file);

    if (!kycId) {
      alert("Please submit or save draft first before uploading document");
      return;
    }

    if (!file) {
      alert("Please select a file first");
      return;
    }

    const formData = new FormData();
    formData.append("document_type", documentType);
formData.append("document", file);

    try {
      const res = await axios.post(
        `https://playto-kyc-backend-l6t5.onrender.com/api/v1/upload/${kycId}/`,
        formData
      );

      console.log("UPLOAD SUCCESS 👉", res.data);
      alert("Document Uploaded ✅");
    } catch (err) {
  console.log("UPLOAD ERROR 👉", err.response?.data || err.message);

  alert(
    err.response?.data?.details ||
    err.response?.data?.error ||
    "Upload failed ❌"
  );
}
  };
 //return <ReviewerDashboard />;

 const handleResubmit = async () => {
  if (!kycId) {
    alert("No KYC found to resubmit");
    return;
  }

  try {
    const res = await axios.post(
      `https://playto-kyc-backend-l6t5.onrender.com/api/v1/kyc/${kycId}/resubmit/`
    );

    console.log("RESUBMIT SUCCESS 👉", res.data);
    alert("KYC resubmitted successfully ✅");
  } catch (err) {
    console.log("RESUBMIT ERROR 👉", err.response?.data || err.message);
    alert("Resubmit failed ❌");
  }
};
 return (
  <div className="min-h-screen bg-gray-100 p-6">
    <div className="flex justify-center gap-4 mb-6">
      <button
        type="button"
        onClick={() => setView("merchant")}
        className="bg-blue-500 text-white px-4 py-2 rounded"
      >
        Merchant Form
      </button>

      <button
        type="button"
        onClick={() => setView("reviewer")}
        className="bg-green-500 text-white px-4 py-2 rounded"
      >
        Reviewer Dashboard
      </button>
    </div>

    {view === "merchant" && (
      <div className="flex items-center justify-center">
        <div className="bg-white p-8 rounded-xl shadow-md w-full max-w-md">
          {step === 1 && (
            <>
              <h1 className="text-xl font-bold mb-4">KYC Form - Step 1</h1>

              <input type="text" placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} className="w-full p-2 border rounded mb-3" />
              <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full p-2 border rounded mb-3" />
              <input type="text" placeholder="Phone" value={phone} onChange={(e) => setPhone(e.target.value)} className="w-full p-2 border rounded mb-3" />

              <button type="button" onClick={nextStep} className="bg-blue-500 text-white p-2 w-full rounded">
                Next
              </button>
            </>
          )}

          {step === 2 && (
            <>
              <h1 className="text-xl font-bold mb-4">KYC Form - Step 2</h1>

              <input type="text" placeholder="Business Name" value={businessName} onChange={(e) => setBusinessName(e.target.value)} className="w-full p-2 border rounded mb-3" />
              <input type="text" placeholder="Business Type" value={businessType} onChange={(e) => setBusinessType(e.target.value)} className="w-full p-2 border rounded mb-3" />

              <input
                type="number"
                placeholder="Monthly Volume (USD)"
                value={monthlyVolume}
                onChange={(e) => setMonthlyVolume(e.target.value)}
                className="w-full p-2 border rounded mb-3"
              />

              <select
                value={documentType}
                onChange={(e) => setDocumentType(e.target.value)}
                className="w-full p-2 border rounded mb-3"
              >
                <option value="PAN">PAN</option>
                <option value="AADHAAR">Aadhaar</option>
                <option value="BANK_STATEMENT">Bank Statement</option>
              </select>

              <div
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => {
                  e.preventDefault();
                  setFile(e.dataTransfer.files[0]);
                }}
                className="w-full p-6 border-2 border-dashed rounded mb-3 text-center bg-gray-50"
              >
                <p className="text-gray-600">
                  Drag & drop document here
                </p>
                <p className="text-sm text-gray-400 mb-2">
                  or choose file
                </p>

                <input
                  type="file"
                  onChange={(e) => setFile(e.target.files[0])}
                  className="w-full"
                />

                {file && (
                  <p className="text-sm text-green-600 mt-2">
                    Selected: {file.name}
                  </p>
                )}
              </div>

              <div className="flex gap-2 flex-wrap">
                <button type="button" onClick={prevStep} className="bg-gray-400 text-white p-2 rounded">Back</button>
                <button type="button" onClick={handleSubmit} className="bg-green-500 text-white p-2 rounded">Submit</button>
                <button type="button" onClick={handleUpload} className="bg-purple-500 text-white p-2 rounded">Upload Document</button>
                <button type="button" onClick={handleSaveDraft} className="bg-yellow-500 text-white p-2 rounded">Save Draft</button>
                <button
                  type="button"
                  onClick={handleResubmit}
                  className="bg-indigo-500 text-white p-2 rounded"
                >
                  Resubmit
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    )}

    {view === "reviewer" && <ReviewerDashboard />}
  </div>
);
}

export default App;