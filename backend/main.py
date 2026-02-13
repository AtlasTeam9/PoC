import json
import os
import uuid
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from utils.session import Session
from utils.device import Device
from utils.position import Position
from typing import Dict, Any

app = FastAPI()

# -- Configurazione CORS, permette la comunicazione tra frontend e backend --
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -- Caricamento dati (cartella corrente e cartella assets, in particolare "trees.json") --
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.join(BASE_DIR, "..", "assets", "trees.json")

# -- Caricamento alberi decisionali e risultati da file JSON --
try:
    with open(ASSETS_PATH, "r") as f:
        DATA = json.load(f)
        TREES_LIST = DATA["trees"]
        RESULTS = DATA["results"]
except FileNotFoundError:
    print(f"Errore: Il file {ASSETS_PATH} non è stato trovato.")
    TREES_LIST = []
    RESULTS = {}

# -- Variabile per salvare lo stato in memoria durante l'esecuzione --
sessions : Dict[str, Session] = {}

# -- Modelli dei dati, per validare input e output --
class AnswerInput(BaseModel):
    session_id: str
    answer: bool

# -- FUNZIONI --
def get_next_tree_index(current_index: int, current_asset_results: Dict[str,Any]) -> int | None:
    """
    Calcola il prossimo albero eseguibile per l'asset corrente, saltando gli alberi le cui dipendenze non sono soddisfatte.
    Prende in input l'indice dell'albero corrente e i risultati dell'asset attuale.
    """
    next_index = current_index + 1

    while next_index < len(TREES_LIST): # Scorre tutti gli alberi successivi
        tree = TREES_LIST[next_index]
        dependencies = tree.get("dependencies", []) # Prende le dipendenze dell'albero
        skip_tree = False

        # Per ogni dipendenza trovata, controllo se l'albero da cui dipende ha dato esito FAIL o NOT_APPLICABLE, in quel caso l'albero è da saltare, impostando il risultato a NOT_APPLICABLE
        for dep in dependencies: 
            dep_result = current_asset_results.get(dep)
            if dep_result and dep_result.get("status") in ["FAIL", "NOT_APPLICABLE"]:
                skip_tree = True
                current_asset_results[tree["id"]] = RESULTS.get("result_na", {"status": "NOT_APPLICABLE"})
                break

        # Se non ho bisogno di saltare l'albero, ritorno l'indice del prossimo albero eseguibile
        if not skip_tree: 
            return next_index
        next_index += 1 # Controllo albero successivo
    return None # Nessun albero rimasto


# -- ENDPOINTS API --
# Inizializza una nuova sessione con file dispositivo caricato
@app.post("/start-session-with-device-file")
async def start_session_file(file: UploadFile = File(...)) -> Dict[str , Any]:
    try:
        # Legge il contenuto del file caricato
        content = await file.read()
        device_data = json.loads(content)
        assets = device_data.get("assets", []) # Lista di asset dal file dispositivo

        if not assets:
            raise HTTPException(400, "Nessun asset trovato nel file caricato.")
        
        session_id = str(uuid.uuid4())

        device = Device(device_name=device_data.get("device_name", "Unknown Device"), device_assets=assets)

        position = Position(0, 0, TREES_LIST[0]["root"])
        
        # Inizializza la sessione in memoria
        session = Session(session_id, device, position)
        sessions[session.session_id] = session

        # Prepara lo spazio per i risultati del primo asset
        first_asset_id = assets[0]["id"]
        session.results[first_asset_id] = {}

        # Prende la prima domanda del primo albero
        first_question = TREES_LIST[0]["nodes"][TREES_LIST[0]["root"]]

        # Ritorna i dati iniziali della sessione
        return {
            "session_id": session.session_id,
            "device_name": device.device_name,
            "asset_name": assets[0]["name"],
            "asset_index": 0,
            "total_assets": len(assets),
            "tree_id": TREES_LIST[0]["id"],
            "title": TREES_LIST[0]["title"],
            "question": first_question
        }
    except json.JSONDecodeError:
        raise HTTPException(400, "File JSON non valido.")

# Gestisce la risposta dell'utente
@app.post("/submit-answer")
def submit_answer(data: AnswerInput) -> Dict[str , Any]:
    # Recupera la sessione dalla memoria
    session = sessions.get(data.session_id)
    if not session:
        raise HTTPException(404, "Sessione non trovata.")
    
    # Recupera i dati correnti della sessione
    device_name = session.device.device_name
    asset_index = session.position.current_asset_index
    current_asset = session.device.device_assets[asset_index]
    asset_id = current_asset["id"]

    tree_index = session.position.current_tree_index
    current_tree = TREES_LIST[tree_index]

    current_node = current_tree["nodes"][session.position.current_node_id]

    # Calcola il prossimo step
    next_step_key = "true" if data.answer else "false"
    next_step_id = current_node[next_step_key]

    # Controlla se il prossimo step è un risultato
    if next_step_id in RESULTS:
        # Se lo è, salva il risultato per l'albero corrente
        result = RESULTS[next_step_id]

        if asset_id not in session.results:
            session.results[asset_id] = {}
        session.results[asset_id][current_tree["id"]] = result

        # Trova il prossimo albero eseguibile chiamando la funzione
        next_tree_index = get_next_tree_index(tree_index, session.results[asset_id])

        # Se non ci sono più alberi per l'asset corrente
        if next_tree_index is not None:
            # Stesso asset, prossimo albero
            session.position.current_tree_index = next_tree_index
            next_tree = TREES_LIST[next_tree_index]
            session.position.current_node_id = next_tree["root"]

            # Ritorna la prossima domanda
            return {
                "finished": session.finished,
                "device_name": device_name,
                "asset_name": current_asset["name"],
                "tree_id": next_tree["id"],
                "title": next_tree["title"],
                "question": next_tree["nodes"][next_tree["root"]],
                "message": f"Asset {current_asset['name']}: Concluso {current_tree['id']}, iniziato {next_tree['id']}"
            }
        else:
            # Alberi per asset correnti terminati, controllo se ci sono altri asset da valutare
            next_asset_index = asset_index + 1

            if next_asset_index < len(session.device.device_assets):
                session.position.current_asset_index = next_asset_index
                session.position.current_tree_index = 0 # Reset alberi
                new_asset = session.device.device_assets[next_asset_index]
                
                # Setup per nuovo asset
                session.results[new_asset["id"]] = {}
                first_tree = TREES_LIST[0]
                session.position.current_node_id = first_tree["root"]
                
                return {
                    "finished": session.finished,
                    "device_name": device_name,
                    "asset_name": new_asset["name"],
                    "asset_index": next_asset_index,
                    "tree_id": first_tree["id"],
                    "title": first_tree["title"],
                    "question": first_tree["nodes"][first_tree["root"]],
                    "message": f"Asset {current_asset['name']} completato! Passaggio a: {new_asset['name']}"
                }
            else:
                # --- TUTTO FINITO, sia asset che alberi ---
                session.finished = True
                return {
                    "finished": session.finished,
                    "final_results": session.results
                }
    else:
        # Se il prossimo passo non è un risultato, continua nell'albero corrente
        # Passo al prossimo nodo nello stesso albero per lo stesso asset
        session.position.current_node_id = next_step_id

        return {
            "finished": session.finished,
            "device_name": device_name,
            "asset_name": current_asset["name"],
            "tree_id": current_tree["id"],
            "title": current_tree["title"],
            "question": current_tree["nodes"][next_step_id]
        }
    
# Esporta la sessione come file JSON
@app.get("/export-session/{session_id}")
def export_session(session_id: str) -> JSONResponse: 
    """
    Restituisce l'intero oggetto sessione come JSON.
    """
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    # Restituisce il JSON e ne forza il download
    return JSONResponse(
        content=session.to_dict(),
        headers={"Content-Disposition": f"attachment; filename=session_{session_id}.json"}
    )

# Importa una sessione esistente da file JSON
@app.post("/import-session")
async def import_session(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Riceve un file JSON, lo legge e lo rimette in memoria (sessions).
    """
    try:
        content = await file.read()
        data = json.loads(content)
        
        # Validazione minima
        session_id = data.get("session_id")
        if not session_id:
            raise HTTPException(400, "JSON non valido: manca session_id")
        
        device_data = data["device"]
        device = Device(
            device_name=device_data["device_name"],
            device_assets=device_data["device_assets"]
        )

        pos_data = data["position"]
        position = Position(
            current_asset_index=pos_data["current_asset_index"],
            current_tree_index=pos_data["current_tree_index"],
            current_node_id=pos_data["current_node_id"]
        )

        session = Session(
            session_id=session_id,
            device=device,
            position=position
        )
        session.results = data.get("results", {})
        session.finished = data.get("finished", False)

        # Ripristina la sessione in memoria
        sessions[session_id] = session

        # Controlla se la sessione è già finita
        if session.finished:
            return {
                "session_id": session_id,
                "finished": session.finished,
                "final_results": session.results
            }
        
        # Se la sessione non è finita, ritorna lo stato attuale per far riprendere le domande
        current_asset = device.device_assets[position.current_asset_index]
        tree = TREES_LIST[position.current_tree_index]
        node = tree["nodes"][position.current_node_id]
        
        return {
            "session_id": session_id,
            "finished": session.finished,
            "device_name": device.device_name,
            "asset_name": current_asset["name"],
            "tree_id": tree["id"],
            "title": tree["title"],
            "question": node
        }
        
    except Exception as e:
        raise HTTPException(400, f"Errore nel caricamento file: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)