// src/utils/api.js
import axios from "axios";

const BASE_URL = "http://127.0.0.1:8000";

const api = {
  // 🌿 Get real-time live data
  getLiveData: async () => {
    const res = await axios.get(`${BASE_URL}/live-data`);
    return res.data;
  },

  // 🔮 Predict CO2 and ESG score
  predictCO2: async (avgUsage) => {
    // Derive auxiliary features from the current time and the avg usage so
    // predictions change meaningfully when `avgUsage` changes.
    const now = new Date();
    const monthNum = now.getMonth() + 1; // 1-12
    const monthNames = [
      "January",
      "February",
      "March",
      "April",
      "May",
      "June",
      "July",
      "August",
      "September",
      "October",
      "November",
      "December",
    ];

    // simple heuristic: winter months are Nov-Mar
    const isWinter = [11, 12, 1, 2, 3].includes(monthNum) ? 1 : 0;

    // Estimate a 'previous CO2' as proportional to recent usage so it varies
    // with the chart. This keeps values deterministic for same avgUsage.
    const prevCO2 = Math.round(avgUsage * 0.8 * 100) / 100; // 2dp

    // Estimate renewable share inversely related to usage (higher usage -> lower share)
    let renewableShare = 0.9 - avgUsage / 2000; // when avgUsage=0 -> 0.9, at 1000 -> 0.4
    renewableShare = Math.max(0.01, Math.min(0.99, renewableShare));

    const payload = {
      Company: "GreenLens",
      Month: monthNames[monthNum - 1],
      Total_Usage_kWh: avgUsage,
      month: monthNum,
      is_winter: isWinter,
      prev_CO2: prevCO2,
      renewable_share: renewableShare,
    };

    const res = await axios.post(`${BASE_URL}/predict`, payload);
    return res.data;
  },

  // 📄 Upload & Ingest PDF for RAG
  uploadDoc: async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await axios.post(`${BASE_URL}/ingest_docs`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data;
  },

  // 🤖 Ask ESG / sustainability questions
  askQuestion: async (question) => {
    const res = await axios.post(`${BASE_URL}/ask`, { question });
    return res.data;
  },
};

export default api;
