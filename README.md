# Come eseguire il codice

## Opzione 1 - Da terminale
1. Aprire un terminale e recarsi nella cartella backend
1. Creare l'ambiente virtuale python, attivarlo, installare i requirements e avviare il server:
    1. Da Windows: 
        1. `python -m venv .venv`

        1. `.venv\Scripts\Activate.ps1`

        1. `pip install -r requirements.txt`

        1. `uvicorn main:app --reload`

    1. Da Mac/Linux: 
        1. `python3 -m venv .venv`

        1. `source .venv/bin/activate` 

        1. `pip install -r requirements.txt`   

        1. `uvicorn main:app --reload`

1. Lasciare il terminale aperto, aprirne uno nuovo e recarsi nella cartella frontend
1. Avviare il server:
    1. Da Windows/Mac/Linux: 
        1. `npm install`

        1. `npm run dev`

1. Lasciare anche questo terminale aperto
1. Recarsi alla pagina web `http://localhost:5173`


## Opzione 2 - Con Docker
1. Aprire Docker Desktop e assicurarsi che il Docker Engine sia "running"

1. Aprire un terminale e recarsi nella cartella PoC

1. Eseguire il comando `docker-compose up --build`

1. Ci metterà un po' di tempo per costruire tutto, una volta terminato lasciare il terminale aperto

1. Recarsi alla pagina web `http://localhost:3000`

<br>
<br>


# SCENARI IMPLEMENTATI

### Scenario 1: Caricamento schermata iniziale
Creata una pagina React iniziale dove l'utente vede due bottoni.

### Scenario 2: Caricamento file dispositivo
Schiacciando il primo bottone nella pagine principale l'utente può caricare un file JSON che rappresenta un dispositivo.

### Scenario 3: Ripresa sessione
Schiacciando il secondo bottone nella pagine principale l'utente può caricare un file JSON che rappresenta una sessione salvata ma non completata oppure una sessione terminata.

### Scenario 4: Navigazione degli alberi
Implementati di due soli alberi (ACM-1 e ACM-2).
L'utente può rispondere alle domande dei requisiti e vedersi venir posta la domanda successiva secondo senso logico, rispettando le dipendente tra requisiti. 

### Scenario 5: Salvataggio e Ripristino 
L'utente può premere "Salva ed Esci" in qualsiasi punto della valutazione. Il sistema scarica un JSON contenente i dati inseriti fino a quel momento. Se l'utente ricarica la pagina, può caricare il JSON precedentemente salvato e riprendere da dove aveva lasciato.

Allo stesso modo, si può salvare una valutazione terminata e caricando il JSON scaricato si vedrà nuovamente la valutazione finale.