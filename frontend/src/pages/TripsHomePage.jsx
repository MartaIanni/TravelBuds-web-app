import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import TripCard from "../components/TripCard";
import { resStatus, getToken } from "../services/auth";

export default function TripsHomePage() {
  const [trips, setTrips] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTrips = async () => {
      const token = getToken();
      if (!token) {
        navigate("/login");
        return;
      }

      try {
        const res = await fetch("http://localhost:5000/api/trips", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        });

        if (resStatus(res)) return;

        let data = {};
        try {
          data = await res.json();
        } catch {
          console.error("Errore parsing JSON");
          data = [];
        }

        if (res.ok) {
          setTrips(Array.isArray(data) ? data : []);
        } else if (data.msg === "Token non valido") {
          navigate("/login");
        }
      } catch (err) {
        console.error("Errore di connessione:", err);
      }
    };

    fetchTrips();
  }, [navigate]);

  return (
    <div className="min-h-screen font-quicksand relative">
      {trips.length > 0 ? (
        <div className="flex flex-wrap justify-center gap-4 mt-4 mb-2">
          {trips.map((trip) => (
            <TripCard key={trip.tid} trip={trip} />
          ))}
        </div>
      ) : (
        <p className="text-center mt-6">Nessun viaggio disponibile.</p>
      )}
    </div>
  );
}
