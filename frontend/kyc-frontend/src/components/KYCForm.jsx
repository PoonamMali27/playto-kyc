import { useState } from "react";

export default function KYCForm() {
  const [step, setStep] = useState(1);

const [formData, setFormData] = useState({
  name: "",
  email: "",
  phone: "",
  business_name: "",
  business_type: "",
  monthly_volume: "",
  file: null,
});

const handleChange = (e) => {
  const { name, value, files } = e.target;

  if (files) {
    setFormData({ ...formData, [name]: files[0] });
  } else {
    setFormData({ ...formData, [name]: value });
  }
};
  return
  <pre className="mt-4 text-xs bg-gray-100 p-2">
  {JSON.stringify(formData, null, 2)}
</pre>
   (
    <div className="max-w-xl mx-auto mt-10 p-6 border rounded-xl shadow">
      <h2 className="text-xl font-bold mb-4 text-center">
        KYC Form - Step {step}
      </h2>

      {step === 1 && (
        <div>
          <input name="name" placeholder="Name" value={formData.name} onChange={handleChange} className="block w-full p-2 mb-3 border rounded" />

<input name="email" placeholder="Email" value={formData.email} onChange={handleChange} className="block w-full p-2 mb-3 border rounded" />

<input name="phone" placeholder="Phone" value={formData.phone} onChange={handleChange} className="block w-full p-2 mb-3 border rounded" />
        </div>
      )}

      {step === 2 && (
        <div>
        <input name="business_name" placeholder="Business Name" value={formData.business_name} onChange={handleChange} className="block w-full p-2 mb-3 border rounded" />

<input name="business_type" placeholder="Business Type" value={formData.business_type} onChange={handleChange} className="block w-full p-2 mb-3 border rounded" />

<input name="monthly_volume" placeholder="Monthly Volume" value={formData.monthly_volume} onChange={handleChange} className="block w-full p-2 mb-3 border rounded" />
        </div>
      )}

      {step === 3 && (
        <div>
          <input type="file" name="file" onChange={handleChange} className="block w-full p-2 mb-3 border rounded" />
        </div>
      )}

      <div className="flex justify-between mt-4">
        {step > 1 && (
          <button
            onClick={() => setStep(step - 1)}
            className="px-4 py-2 bg-gray-300 rounded"
          >
            Back
          </button>
        )}

        {step < 3 && (
          <button
            onClick={() => setStep(step + 1)}
            className="px-4 py-2 bg-blue-500 text-white rounded"
          >
            Next
          </button>
        )}
      </div>
    </div>
  );
}