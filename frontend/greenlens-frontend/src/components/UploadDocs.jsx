import { useState } from "react";
import api from "../utils/api";

export default function UploadDocs() {
  const [file, setFile] = useState(null);
  const [msg, setMsg] = useState("");

  const handleUpload = async () => {
    if (!file) return setMsg("Please select a PDF file.");
    try {
      const res = await api.uploadDoc(file);
      // api.uploadDoc returns res.data from backend, which contains 'message'
      setMsg(res.message || "File uploaded successfully.");
    } catch (err) {
      console.error("UploadDocs error:", err);
      setMsg("Upload failed. Please check the backend logs.");
    }
  };

  return (
    <div className="uploader">
      <h2>Upload ESG / CSRD / EU Taxonomy PDFs 📄</h2>
      <input type="file" accept="application/pdf" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload}>Upload</button>
      <p>{msg}</p>
    </div>
  );
}
