import { useState, useEffect, useCallback } from "react";

function Timer({ totalMinutes, onTimeUp }) {
  const [secondsLeft, setSecondsLeft] = useState(totalMinutes * 60);

  const handleTimeUp = useCallback(() => {
    onTimeUp();
  }, [onTimeUp]);

  useEffect(() => {
    if (secondsLeft <= 0) {
      handleTimeUp();
      return;
    }

    const interval = setInterval(() => {
      setSecondsLeft((prev) => prev - 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [secondsLeft, handleTimeUp]);

  const minutes = Math.floor(secondsLeft / 60);
  const seconds = secondsLeft % 60;
  const timeStr = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;

  let className = "timer";
  if (secondsLeft < 60) {
    className += " danger";
  } else if (secondsLeft < 300) {
    className += " warning";
  }

  return <div className={className}>{timeStr}</div>;
}

export default Timer;
