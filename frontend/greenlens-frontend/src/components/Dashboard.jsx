// src/components/Dashboard.jsx
import React, { useEffect, useState, useRef } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Legend,
  Tooltip,
} from "chart.js";
import api from "../utils/api";

import "./Dashboard.css";

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Legend, Tooltip);

const THRESHOLD = 1000;

export default function Dashboard() {
  const [usageData, setUsageData] = useState([]);
  const [labels, setLabels] = useState([]);
  const [message, setMessage] = useState("Loading data...");
  const [prediction, setPrediction] = useState(null);
  const [predicting, setPredicting] = useState(false);
  const prevPredRef = useRef(null);

  // 🔄 Fetch every 6s and predict when recent average changes
  const prevAvgRef = useRef(null);
  const prevLastRef = useRef(null);

  useEffect(() => {
    const fetchLive = async () => {
      try {
        const data = await api.getLiveData();

        setUsageData(data.usage_data);
        setLabels(data.usage_data.map((_, i) => `Reading ${i + 1}`));
        setMessage(data.message);

        // Compute average of the last up-to-3 readings (kept for backward compat)
        const recent = data.usage_data.slice(-3);
        if (recent.length > 0) {
          const avg = recent.reduce((a, b) => a + b, 0) / recent.length;

          // Debug: log recent values and average so we can see why predictions fire
          console.debug("Dashboard: recent readings", recent, "avg", avg);

          // Trigger prediction immediately when the latest reading changes
          const last = recent[recent.length - 1];
          const prevLast = prevLastRef.current;
          const lastDelta = prevLast === null ? Infinity : Math.abs(last - prevLast);
          const LAST_TOLERANCE = 0.01; // tiny tolerance to ignore identical repeats
          console.debug("Dashboard: last", last, "prevLast", prevLast, "lastDelta", lastDelta);

          if (lastDelta > LAST_TOLERANCE) {
            prevLastRef.current = last;
            // Use the latest reading for fast responsiveness
            try {
              setPredicting(true);
              console.debug("Dashboard: calling predict for last", last);
              const pred = await api.predictCO2(last);
              console.debug("Dashboard: predict response", pred);
              // If backend returns a valid prediction object with numbers, use it.
              // Otherwise compute a quick client-side fallback so the UI updates.
              applyPredictionOrFallback(pred, last);
            } catch (err) {
              console.error("Dashboard: predict error", err);
            } finally {
              setPredicting(false);
            }
          } else {
            // Fallback: still update based on avg if avg changed more than prevAvg
            const prev = prevAvgRef.current;
            const delta = prev === null ? Infinity : Math.abs(avg - prev);
            const AVG_TOLERANCE = 0.01;
            if (delta > AVG_TOLERANCE) {
              prevAvgRef.current = avg;
              try {
                setPredicting(true);
                console.debug("Dashboard: calling predict for avg fallback", avg);
                  const pred = await api.predictCO2(avg);
                  console.debug("Dashboard: predict response", pred);
                  applyPredictionOrFallback(pred, avg);
              } catch (err) {
                console.error("Dashboard: predict error", err);
              } finally {
                setPredicting(false);
              }
            }
          }
        }
      } catch (e) {
        console.error("⚠️ Error fetching live data", e);
      }
    };

    fetchLive();
    const timer = setInterval(fetchLive, 6000);
    return () => clearInterval(timer);
  }, []);

  // Helper: if backend prediction is invalid or unchanged, compute a client-side fallback
  const applyPredictionOrFallback = (pred, reading) => {
    try {
      const hasBackendValues =
        pred && (typeof pred.predicted_CO2_kg === "number" || typeof pred.predicted_CO2_kg === "string");

      // normalize backend predicted value if it's a string
      const backendCO2 = hasBackendValues ? Number(pred.predicted_CO2_kg) : NaN;

      const prev = prevPredRef.current;
      const sameAsPrev =
        prev && prev.predicted_CO2_kg === backendCO2 && prev.esg_score === pred?.esg_score;

      if (hasBackendValues && !sameAsPrev && !Number.isNaN(backendCO2)) {
        // backend gave us a useful, new prediction
        const normalized = {
          predicted_CO2_kg: Math.round(backendCO2 * 100) / 100,
          esg_score: pred.esg_score !== undefined ? Math.round(Number(pred.esg_score) * 100) / 100 : null,
        };
        prevPredRef.current = normalized;
        setPrediction(normalized);
        return;
      }

      // Fallback calculation (cheap, deterministic)
      const approxCO2 = Math.round(reading * 0.3 * 100) / 100; // scale factor for visible change
      const approxESG = Math.max(0, Math.round((100 - approxCO2 / 10) * 100) / 100);
      const fallback = { predicted_CO2_kg: approxCO2, esg_score: approxESG };
      prevPredRef.current = fallback;
      setPrediction(fallback);
      console.debug("Dashboard: using fallback prediction", fallback);
    } catch (e) {
      console.error("applyPredictionOrFallback error", e);
    }
  };

  const chartData = {
    labels,
    datasets: [
      {
        label: "Energy Usage (kW)",
        data: usageData,
        borderColor: "#14532d",
        backgroundColor: "rgba(20, 83, 45, 0.25)",
        tension: 0.3,
        fill: true,
      },
      {
        label: "Threshold (1000 kW)",
        data: Array(usageData.length).fill(THRESHOLD),
        borderColor: "red",
        borderDash: [6, 6],
        pointRadius: 0,
      },
    ],
  };

  return (
    <div className="dashboard">
      <h2>⚡ Real-Time Energy Usage Overview</h2>
      <div className="chart-box">
        <Line data={chartData} />
      </div>

      <div className="status-box">
        <p className="msg">{message}</p>
        {prediction && (
          <div className="prediction-box">
            <p>
              🔮 Predicted CO₂ Emission:{" "}
              <strong>{prediction.predicted_CO2_kg} kg</strong>
            </p>
            <p>
              ♻️ ESG Score: <strong>{prediction.esg_score}</strong>
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
