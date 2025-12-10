import React from "react";
import TripReadModal from "./TripReadModal";
import EditTripForm from "./EditTripForm";

export default function ShowTripModal({ trip, onClose, editable }) {
  if (!trip) return null;

  return (
    <div
      className="fixed inset-0 bg-black/60 flex justify-center items-center z-50 font-quicksand"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl w-1/2 p-6 relative"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          className="absolute top-4 right-4 text-gray-500 hover:text-gray-800 font-bold"
          onClick={onClose}
        >
          X
        </button>

        {/* Scelta rispetto a editable */}
        {editable ? (
          <EditTripForm trip={trip} onClose={onClose} />
        ) : (
          <TripReadModal trip={trip} onClose={onClose} />
        )}
      </div>
    </div>
  );
}
