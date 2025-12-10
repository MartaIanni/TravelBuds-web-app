import React from "react";

export default function TripReadModal({ trip }) {
  return (
    <>
      <div>
        <h2 className="text-2xl font-bold mb-4">{trip.destination}</h2>
        <p className="mb-1">
          <strong>Partenza:</strong> {trip.start}
        </p>
        <p className="mb-1">
          <strong>Ritorno:</strong> {trip.end}
        </p>
        <p className="mb-1">
          <strong>Descrizione:</strong>{" "}
          {trip.description || "Nessuna descrizione"}
        </p>
        <p className="mb-1">
          <strong>Prezzo:</strong> {trip.price} €
        </p>

        <h3 className="mt-4 font-bold">
          {trip.participants?.length || 0} Partecipanti:
        </h3>
        <ul className="list-disc list-inside">
          {trip.participants?.length > 0 ? (
            trip.participants.map((p, idx) => <li key={idx}>{p}</li>)
          ) : (
            <li>Nessun partecipante</li>
          )}
        </ul>
      </div>
    </>
  );
}
