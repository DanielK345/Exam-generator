import React from "react";

function Question({ question, index, answer, onAnswer }) {
  const { type, question: questionText, options } = question;

  return (
    <div className="question-card">
      <div className="question-number">Question {index + 1}</div>
      <span className={`question-type ${type}`}>
        {type === "mcq" ? "Multiple Choice" : type === "true_false" ? "True / False" : "Short Answer"}
      </span>
      <div className="question-text">{questionText}</div>

      {(type === "mcq" || type === "true_false") && options && (
        <ul className="options-list">
          {options.map((option, i) => (
            <li key={i}>
              <label className={answer === option ? "selected" : ""}>
                <input
                  type="radio"
                  name={`question-${index}`}
                  value={option}
                  checked={answer === option}
                  onChange={() => onAnswer(option)}
                />
                {option}
              </label>
            </li>
          ))}
        </ul>
      )}

      {type === "short_answer" && (
        <input
          className="short-answer-input"
          type="text"
          placeholder="Type your answer..."
          value={answer || ""}
          onChange={(e) => onAnswer(e.target.value)}
        />
      )}
    </div>
  );
}

export default Question;
