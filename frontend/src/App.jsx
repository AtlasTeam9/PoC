import { useState } from 'react'
import axios from 'axios'
import './App.css'
import QuestionCard from './components/QuestionCard';
import ListResult from './components/ListResult'

// Configurazione base API (punta al backend Python)
const API_URL = "http://127.0.0.1:8000";

function App() {
  // --- STATO DELL'APPLICAZIONE ---
  const [session, setSession] = useState(null); // ID Sessione
  const [step, setStep] = useState(null); // Dati del nodo corrente (domanda)
  const [finished, setFinished] = useState(false); // Stato di completamento
  const [results, setResults] = useState(null); // Risultati finali
  const [loading, setLoading] = useState(false); // Stato di caricamento
  const [assetName, setAssetName] = useState(""); // Nome dell'asset corrente

  // --- FUNZIONI PRINCIPALI ---
  // 1. INIZIA SESSIONE (Carica Dispositivo)
  const startSessionWithFile = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    try {
      const res = await axios.post(
        `${API_URL}/start-session-with-device-file`,
        formData
      );

      const payload = res.data;

      setSession(payload.session_id);
      setStep(payload);
      setAssetName(payload.asset_name);
      setFinished(false);
    } catch (err) {
      console.error(err);
      alert("Error! Please check that the file is valid and the backend is running.");
    }
    setLoading(false);
  };

  // 2. INVIA RISPOSTA (Sì/No)
  const sendAnswer = async (answer) => {
    try {
      const res = await axios.post(`${API_URL}/submit-answer`, {
        session_id: session,
        answer: answer
      });

      if (res.data.finished) {
        setFinished(true);
        setResults(res.data.final_results);
      } else {
        setStep(res.data);
        if (res.data.asset_name) {
          setAssetName(res.data.asset_name);
        }
      }
    } catch (err) {
      alert("Error submitting answer. Please try again.");
    }
  };

  // 3. SALVA SU FILE (Download)
  const handleSave = () => {
    // Apre direttamente l'URL del backend che forza il download del file
    window.open(`${API_URL}/export-session/${session}`, '_blank');

    setTimeout(() => {
      setSession(null);
      setStep(null);
      setFinished(false);
      setResults(null);
      setAssetName(""); // Resetta anche il nome asset
    }, 100);
  };

  // 4. CARICA DA FILE (Upload/Ripristino)
  const handleUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/import-session`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      // Ripristina lo stato ricevuto dal backend
      setSession(res.data.session_id);

      if (res.data.finished) {
        setFinished(true);
        setResults(res.data.final_results);
        alert("Session restored successfully! The evaluation was already completed.");
      } else {
        setFinished(false);
        setStep({
          tree_id: res.data.tree_id,
          title: res.data.title,
          question: res.data.question,
          device_name: res.data.device_name
        });
        setAssetName(res.data.asset_name);
        alert("Session restored successfully!");
      }
    } catch (err) {
      console.error(err);
      alert("File not valid or server error. Please check the file and try again.");
    }
    setLoading(false);
  };

  // --- RENDERING INTERFACCIA ---

  if (loading) return <div className="container"><h3>Loading...</h3></div>;

  // CASO A: HOME PAGE (Nessuna sessione attiva)
  if (!session) {
  return (
    <div className="container">
      <h1>EN18031 Evaluation</h1>
      <p>Proof of Concept - Team Atlas</p>

      <div style={{ marginTop: 40 }}>
        <label className="carica-file">
          Upload Device File
        </label>
        <div style={{ display: 'flex', justifyContent: 'center', marginTop: 5 }}>
          <input 
            type="file" 
            id="deviceFile"
            onChange={startSessionWithFile} 
            accept=".json"
            style={{ display: 'none' }}
          />
          <label 
            htmlFor="deviceFile" 
            style={{ 
              padding: '5px 10px', 
              background: '#3182ce', 
              color: 'white', 
              borderRadius: '5px', 
              cursor: 'pointer',
              display: 'inline-block'
            }}
          >
            Scegli File
          </label>
        </div>
        <p style={{ fontSize: '0.8rem', color: '#666', marginTop: 5 }}>
          File must contain the device information in JSON format.
        </p>

        <div style={{ marginTop: 20, borderTop: '1px solid #eee', paddingTop: 20 }}>
          <p style={{ fontSize: '0.9rem', color: '#666' }}>Riprendi Sessione:</p>
          <div style={{ display: 'flex', justifyContent: 'center', marginTop: 10 }}>
            <input 
              type="file" 
              id="sessionFile"
              onChange={handleUpload} 
              accept=".json"
              style={{ display: 'none' }}
            />
            <label 
              htmlFor="sessionFile" 
              style={{ 
                padding: '10px 20px', 
                background: '#4299e1', 
                color: 'white', 
                borderRadius: '5px', 
                cursor: 'pointer',
                display: 'inline-block'
              }}
            >
              Upload Session
            </label>
          </div>
        </div>
      </div>
    </div>
    );
  }

  // CASO B: VALUTAZIONE COMPLETATA
  if (finished) {
    return (
      <div className="container">
        <h1 style={{ color: '#48bb78' }}>Evaluation Completed</h1>
        <div style={{ textAlign: 'left', background: '#f7fafc', padding: 15, borderRadius: 8, margin: '20px 0' }}>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.9rem', color: 'black' }}>
            {results && Object.entries(results).map(([asset_name, value]) => (
              <ListResult asset_name={asset_name} data={[value]} />
            ))}
          </pre>
        </div>
        <button className="btn-save" onClick={handleSave}>Download Final Report</button>
        <br /><br />
        <button onClick={() => window.location.reload()} style={{ color: '#666', background: 'none' }}>
          Back to Home
        </button>
      </div>
    );
  }

  // CASO C: DOMANDA ATTIVA (Il loop principale)
  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20 }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '8px' }}>
          <span className="tree-tag" style={{ background: '#3182ce', color: 'white' }}>
            Device: {step.device_name || "Unknown Device"}
          </span>
          <span className="tree-tag" style={{ background: '#4299e1', color: 'white' }}>
            Asset: {assetName}
          </span>
        </div>

        <button onClick={handleSave} style={{ fontSize: '0.8rem', padding: '8px 12px' }}>
          Save and Exit
        </button>
      </div>

      <div style={{ marginTop: 10, fontSize: '0.9rem', color: '#888', marginBottom: 10 }}>
        Requirement (Tree): {step.tree_id}
      </div>

      <QuestionCard step={step} onAnswer={sendAnswer} />
    </div>
  );
}

export default App