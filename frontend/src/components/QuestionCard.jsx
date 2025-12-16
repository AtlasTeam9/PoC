import React from 'react';

// Questo componente riceve 4 "props" (proprietà) dal padre:
// 1. step: l'oggetto che contiene titolo, domanda e messaggio
// 2. onAnswer: la funzione da chiamare quando l'utente clicca SI o NO
function QuestionCard({ step, onAnswer }) {
  
  return (
    <div>
      {/* 1. Titolo dell'albero corrente */}
      <h2>{step.title}</h2>

      {/* 2. Messaggio di avviso quando si cambia asset o albero */}
      {step.message && (
        <div className="alert">
          ℹ️ {step.message}
        </div>
      )}

      {/* 3. Il testo della domanda */}
      <div className="question-box">
        {step.question.question}
      </div>

      {/* 4. I Bottoni - Chiamano la funzione onAnswer passata dal padre */}
      <div className="btn-group">
        <button 
          className="btn-yes" 
          onClick={() => onAnswer(true)}
        >
          SI
        </button>
        
        <button 
          className="btn-no" 
          onClick={() => onAnswer(false)}
        >
          NO
        </button>
      </div>
    </div>
  );
}

export default QuestionCard;