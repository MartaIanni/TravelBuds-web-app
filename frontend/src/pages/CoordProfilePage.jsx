import React, { useEffect, useState } from "react";
import TripCard from "../components/TripCard";
import NewTripForm from "../components/NewTripForm";
import FlashMessages from "../components/FlashMessages";
import { resStatus, getToken } from "../services/auth";

const CoordProfilePage = () => {
  const [p_trips, setPublicTrips] = useState([]);
  const [d_trips, setDraftTrips] = useState([]);
  const [quests, setQuests] = useState([]);
  const [activeTab, setActiveTab] = useState("d_trips"); // default "d_trips" | "p_trips" | "quests"
  const [newTrip, setNewTrip] = useState(false);
  const closeModal = () => setNewTrip(false);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [flashMessages, setFlashMessages] = useState([]);

  const token = getToken();
  if (!token) {
    navigate("/login");
    return;
  }

  const fetchProfile = async () => {
    try {
      const res = await fetch("http://localhost:5000/api/coord-profile", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (resStatus(res)) return;

      if (!res.ok) {
        const text = await res.text(); // evita crash se non è JSON
        throw new Error(text || `Errore HTTP ${res.status}`);
      }
      const data = await res.json();

      setDraftTrips(data.d_trips || []);
      setPublicTrips(data.p_trips || []);
      setQuests(data.quests || []);
      setAnswers(
        Object.fromEntries(
          (data.quests || []).map((q) => [q.quest_id, q.answer || ""])
        )
      );
    } catch (err) {
      console.error(err);
      setFlashMessages([err.message || "Errore di rete"]);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const submitNewTrip = async (formData, actionType) => {
    try {
      const res = await fetch("http://localhost:5000/api/newtrip_validation", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });
      if (resStatus(res)) return;

      if (!res.ok) {
        const text = await res.text(); // evita crash se non è JSON
        throw new Error(text || `Errore HTTP ${res.status}`);
      }

      const data = await res.json();

      if (data.success) {
        setFlashMessages([data.msg]);
        setNewTrip(false); // chiude il modale
        // eventualmente ricarica i draft trips
        fetchProfile();
      } else {
        setFlashMessages([data.msg || "Errore nella creazione del viaggio"]);
      }
    } catch (err) {
      //debug
      console.error(err);
      setFlashMessages([err.message || "Errore di rete"]);
    }
  };

  const handleAnswerSubmit = async (e, questId) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const res = await fetch(
        "http://localhost:5000/api/coord_answer_validation",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            quest_id: questId,
            answer: answers[questId] || "",
          }),
        }
      );
      if (resStatus(res)) return;

      if (!res.ok) {
        const text = await res.text(); // evita crash se non è JSON
        throw new Error(text || `Errore HTTP ${res.status}`);
      }

      const data = await res.json();

      if (data.success) {
        setFlashMessages([data.msg]);
        setAnswers((prev) => ({ ...prev, [questId]: "" }));
        fetchProfile();
      } else {
        setFlashMessages([
          data.msg || "Errore nell'invio della risposta. Riprova.",
        ]);
      }
    } catch (err) {
      setError(err.message);
      //debug
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-7">
      <FlashMessages
        messages={flashMessages}
        onClose={() => setFlashMessages([])}
      />
      {/* TABS */}
      <div className="flex flex-row justify-between mb-5 font-quicksand">
        <div className="flex gap-4">
          <button
            type="button"
            className={`px-4 py-2 rounded-lg font-bold ${
              activeTab === "d_trips"
                ? "bg-green-900 text-white"
                : "bg-green-200"
            }`}
            onClick={() => setActiveTab("d_trips")}
          >
            Bozze
          </button>

          <button
            type="button"
            className={`px-4 py-2 rounded-lg font-bold ${
              activeTab === "p_trips"
                ? "bg-green-900 text-white"
                : "bg-green-200"
            }`}
            onClick={() => setActiveTab("p_trips")}
          >
            Pubblicati
          </button>

          <button
            type="button"
            className={`px-4 py-2 rounded-lg font-bold ${
              activeTab === "quests"
                ? "bg-green-900 text-white"
                : "bg-green-200"
            }`}
            onClick={() => setActiveTab("quests")}
          >
            Le mie domande
          </button>
        </div>

        <button
          type="button"
          className={"px-4 py-2 rounded-lg font-bold bg-[#d44420] text-white"}
          onClick={() => setNewTrip(true)}
        >
          Nuovo viaggio
        </button>

        {newTrip && (
          <div className="fixed inset-0 bg-black/60 flex justify-center items-center z-50">
            <div className="bg-white p-6 rounded-xl w-1/2">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">
                  Crea una nuova avventura di gruppo
                </h2>
                <button
                  type="button"
                  className="text-gray-500 hover:text-gray-800 font-bold"
                  onClick={closeModal}
                >
                  X
                </button>
              </div>
              <NewTripForm submitNewTrip={submitNewTrip} onClose={closeModal} />
            </div>
          </div>
        )}
      </div>

      {/* CONTENT SECTION */}

      {activeTab === "d_trips" && (
        <div className="flex flex-wrap gap-6">
          {d_trips.length === 0 && (
            <p className="text-gray-500">
              Non hai ancora creato nessun viaggio.
            </p>
          )}

          {d_trips.map((trip) => (
            <TripCard key={trip.tid} trip={trip} section="draft" />
          ))}
        </div>
      )}

      {activeTab === "p_trips" && (
        <div className="flex flex-wrap gap-6">
          {p_trips.length === 0 && (
            <p className="text-gray-500">
              Non hai ancora pubblicato nessun viaggio.
            </p>
          )}

          {p_trips.map((trip) => (
            <TripCard key={trip.tid} trip={trip} section="published" />
          ))}
        </div>
      )}

      {activeTab === "quests" && (
        <div className="flex flex-col gap-4">
          {quests.length === 0 && (
            <p className="text-gray-500">Non hai domande a cui rispondere.</p>
          )}

          {quests.map((q, i) => (
            <div key={q.quest_id} className="bg-white shadow-md p-4 rounded-xl">
              <button
                type="button"
                className="w-full text-left font-bold text-green-900"
                onClick={() =>
                  setQuests((prev) =>
                    prev.map((el) =>
                      el.quest_id === q.quest_id
                        ? { ...el, open: !el.open }
                        : el
                    )
                  )
                }
              >
                Chat con {q.user_username} —{" "}
                <span className="font-normal">{q.destination}</span>
              </button>

              {q.open && (
                <div className="flex flex-col mt-3 pl-3 border-l-4 border-green-800 gap-2">
                  <div>
                    <p>
                      <strong>La domanda di {q.user_username}:</strong>
                    </p>
                    <p className="ml-3">{q.content}</p>
                  </div>

                  {q.answer ? (
                    // Se la risposta esiste, mostra solo la risposta con tasto Chiudi
                    <div className="flex flex-row justify-between gap-2">
                      <div className="flex flex-col">
                        <p>
                          <strong>La tua risposta:</strong>
                        </p>
                        <p className="ml-3">{q.answer}</p>
                      </div>
                      <div className="flex justify-end">
                        <button
                          type="button"
                          className="bg-gray-300 px-3 py-2 rounded hover:bg-gray-400"
                          onClick={() =>
                            setQuests((prev) =>
                              prev.map((el, index) =>
                                index === i ? { ...el, open: false } : el
                              )
                            )
                          }
                        >
                          Chiudi
                        </button>
                      </div>
                    </div>
                  ) : (
                    // Se non c'è risposta, mostra il form per rispondere
                    <form
                      className="flex flex-col gap-2"
                      onSubmit={(e) => handleAnswerSubmit(e, q.quest_id)}
                    >
                      <textarea
                        className="border border-gray-300 rounded px-2 py-1 w-full resize-y"
                        placeholder="Scrivi la tua risposta..."
                        value={answers[q.quest_id] || ""}
                        onChange={(e) =>
                          setAnswers((prev) => ({
                            ...prev,
                            [q.quest_id]: e.target.value,
                          }))
                        }
                        required
                      />
                      <div className="flex justify-end gap-2">
                        <button
                          type="button"
                          className="bg-gray-300 px-3 rounded hover:bg-gray-400"
                          onClick={() =>
                            setQuests((prev) =>
                              prev.map((el, index) =>
                                index === i ? { ...el, open: false } : el
                              )
                            )
                          }
                        >
                          Annulla
                        </button>
                        <button
                          type="button"
                          disabled={loading}
                          className="bg-green-600 rounded p-3 hover:bg-green-500"
                        >
                          {loading ? "Invio..." : "Invia risposta"}
                        </button>
                        {error && <p className="text-red-500 mt-2">{error}</p>}
                      </div>
                    </form>
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

export default CoordProfilePage;
