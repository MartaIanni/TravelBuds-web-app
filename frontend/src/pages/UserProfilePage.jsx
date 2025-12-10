import React, { useEffect, useState } from "react";
import TripCard from "../components/TripCard";
import { resStatus, getToken } from "../services/auth";

const UserProfilePage = () => {
  const [trips, setTrips] = useState([]);
  const [quests, setQuests] = useState([]);
  const [activeTab, setActiveTab] = useState("trips"); // default "trips" | "quests"

  const token = getToken();

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await fetch("http://localhost:5000/api/user-profile", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (resStatus(res)) return;

        const data = await res.json();

        setTrips(data.trips || []);
        setQuests(data.quests || []);
      } catch (err) {
        console.error(err);
      }
    };

    fetchProfile();
  }, []);

  return (
    <div className="p-6">
      {/* TABS */}
      <div className="flex gap-4 mb-5 font-quicksand">
        <button
          type="button"
          className={`px-4 py-2 rounded-lg font-bold ${
            activeTab === "trips" ? "bg-green-900 text-white" : "bg-green-200"
          }`}
          onClick={() => setActiveTab("trips")}
        >
          I miei viaggi
        </button>

        <button
          type="button"
          className={`px-4 py-2 rounded-lg font-bold ${
            activeTab === "quests" ? "bg-green-900 text-white" : "bg-green-200"
          }`}
          onClick={() => setActiveTab("quests")}
        >
          Le mie domande
        </button>
      </div>

      {/* CONTENT SECTION */}
      {activeTab === "trips" && (
        <div className="flex flex-wrap gap-6">
          {trips.length === 0 && (
            <p className="text-gray-500">
              Non hai ancora prenotato nessun viaggio.
            </p>
          )}

          {trips.map((trip) => (
            <TripCard key={trip.tid} trip={trip} />
          ))}
        </div>
      )}

      {activeTab === "quests" && (
        <div className="flex flex-col gap-4">
          {quests.length === 0 && (
            <p className="text-gray-500">Non hai ancora fatto domande.</p>
          )}

          {quests.map((q, i) => (
            <div key={i} className="bg-white shadow-md p-4 rounded-xl">
              <button
                type="button"
                className="w-full text-left font-bold text-green-900"
                onClick={() =>
                  setQuests((prev) =>
                    prev.map((el, index) =>
                      index === i ? { ...el, open: !el.open } : el
                    )
                  )
                }
              >
                Chat con {q.coord_username} -{" "}
                <span className="font-normal">{q.destination}</span>
              </button>

              {q.open && (
                <div className="mt-3 pl-3 border-l-4 border-green-800">
                  <p>
                    <strong>La tua domanda:</strong>
                  </p>
                  <p className="ml-3">{q.content}</p>

                  {q.answer ? (
                    <>
                      <p className="mt-3">
                        <strong>Risposta:</strong>
                      </p>
                      <p className="ml-3">{q.answer}</p>
                    </>
                  ) : (
                    <p className="mt-3 italic text-gray-500">
                      In attesa di risposta...
                    </p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default UserProfilePage;
