import React from "react";

function FlashMessages({ messages, onClose }) {
  if (!messages || messages.length === 0) return null;

  return (
    <div
      className="fixed inset-0 flex items-center justify-center z-50 bg-black/50"
      onClick={onClose}
    >
      <div
        className="bg-white rounded p-4 w-80"
        onClick={(e) => e.stopPropagation()} //previene chiusura cliccando dentro
      >
        {messages.map((msg, idx) => (
          <p key={idx} className="mb-2">
            {msg}
          </p>
        ))}
        <button
          className="mt-2 px-4 py-1 bg-green-600 text-white rounded hover:bg-green-700"
          onClick={onClose}
        >
          Chiudi
        </button>
      </div>
    </div>
  );
}

export default FlashMessages;
