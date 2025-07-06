"use client";
import React, { useState } from "react";
import FitSelector from "../components/FitSelector";
import InputField from "../components/InputField";
import { getRecommendation } from "../utils/api";
import styles from "./page.module.css";

export default function Home() {
  const [height, setHeight] = useState(180);
  const [weight, setWeight] = useState(75);
  const [unit, setUnit] = useState("metric");
  const [fit, setFit] = useState("Regular");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleCalculate = async () => {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const rec = await getRecommendation({ height, weight, fit, unit });
      setResult(rec);
    } catch (e) {
      setError("Sorry, we couldn't get your size. Please try again later.");
    }
    setLoading(false);
  };

  return (
    <main className={styles.main}>
      <div className={styles.card}>
        <h1 className={styles.title}>Find Your Perfect Suit Size</h1>
        <p className={styles.subtitle}>AI-powered. Free. Instant. No signup.</p>
        <div className={styles.inputs}>
          <InputField
            label="Height"
            value={height}
            onChange={setHeight}
            unit={unit === "metric" ? "cm" : "in"}
            min={unit === "metric" ? 140 : 55}
            max={unit === "metric" ? 210 : 82}
          />
          <InputField
            label="Weight"
            value={weight}
            onChange={setWeight}
            unit={unit === "metric" ? "kg" : "lb"}
            min={unit === "metric" ? 45 : 100}
            max={unit === "metric" ? 160 : 350}
          />
          <div className={styles.unitToggle}>
            <button
              className={unit === "metric" ? styles.unitActive : styles.unit}
              onClick={() => setUnit("metric")}
            >
              Metric
            </button>
            <button
              className={unit === "imperial" ? styles.unitActive : styles.unit}
              onClick={() => setUnit("imperial")}
            >
              Imperial
            </button>
          </div>
          <FitSelector fit={fit} setFit={setFit} />
        </div>
        <button
          className={styles.calculateBtn}
          onClick={handleCalculate}
          disabled={loading}
        >
          {loading ? "Calculating..." : "Find My Size"}
        </button>
        {error && <div className={styles.error}>{error}</div>}
        {result && (
          <div className={styles.resultCard}>
            <h2>Your Recommended Size</h2>
            <div className={styles.size}>{result.recommendation?.size || result.size}</div>
            <div className={styles.confidence}>
              Confidence: {Math.round((result.recommendation?.confidence || result.confidence) * 100)}% ({result.recommendation?.confidenceLevel || result.confidenceLevel})
            </div>
            <div className={styles.message}>{result.message}</div>
            {result.recommendation && (
              <div className={styles.details}>
                <p><strong>Body Type:</strong> {result.recommendation.bodyType}</p>
                {result.recommendation.rationale && (
                  <p><strong>Rationale:</strong> {result.recommendation.rationale}</p>
                )}
                {result.recommendation.alterations && result.recommendation.alterations.length > 0 && (
                  <div>
                    <strong>Recommended Alterations:</strong>
                    <ul>
                      {result.recommendation.alterations.map((alteration, index) => (
                        <li key={index}>{alteration.replace('_', ' ')}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
      <footer className={styles.footer}>
        Powered by <b>suitsize.ai</b>
      </footer>
    </main>
  );
} 