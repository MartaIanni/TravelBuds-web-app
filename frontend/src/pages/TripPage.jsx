import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import FlashMessages from "../components/FlashMessages";
import { resStatus, getToken } from "../services/auth";

export default function TripPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [trip, setTrip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [newBooking, setNewBooking] = useState(false);
  const [showQuest, setShowQuest] = useState(false);

  const [newQuest, setNewQuest] = useState("");

  const [flashMessages, setFlashMessages] = useState([]);
  const token = getToken();

  useEffect(() => {
    const fetchTrip = async () => {
      fetch(`http://localhost:5000/api/trip/${id}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      }).then(async (res) => {
        if (resStatus(res)) return;
        const body = await res.text();
        try {
          const data = JSON.parse(body);

          if (res.ok) {
            setTrip(data);
          } else {
            setFlashMessages(["Errore nel caricamento dei dati, riprova."]);
            if (data.msg === "Token non valido") {
              setFlashMessages(["Errore di rete, riprova."]);
              localStorage.removeItem("access_token");
              navigate("/login");
            }
          }
        } catch (err) {
          // debug
          console.error("Errore parsing JSON:", err, body);
          setFlashMessages(["Errore di rete, riprova."]);
        } finally {
          setLoading(false);
        }
      });
    };
    fetchTrip();
  }, [id]);

  const bookTrip = async () => {
    try {
      const res = await fetch("http://localhost:5000/api/booking", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          tid: trip.tid,
        }),
      });

      if (resStatus(res)) return;

      const data = await res.json();

      if (res.ok && data.success) {
        setFlashMessages([data.msg]);
        setTrip({ ...trip, free_seats: trip.free_seats - 1 }); // aggiorna sulla pagina i posti
        setNewBooking(false);
      } else {
        setFlashMessages([data.msg || "Errore nella prenotazione"]);
      }
    } catch (err) {
      console.error("Errore nella prenotazione:", err);
      setFlashMessages(["Errore di rete, riprova."]);
    }
  };

  const submitQuestForm = async (e) => {
    e.preventDefault();
    if (!newQuest.trim()) {
      setFlashMessages(["Scrivi qualcosa prima di inviare la domanda"]);
      return;
    }

    try {
      const res = await fetch("http://localhost:5000/api/questbox", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          trip_id: trip.tid,
          content: newQuest,
        }),
      });
      if (resStatus(res)) return;

      const data = await res.json();

      if (res.ok && data.success) {
        setFlashMessages([data.msg]);
        setShowQuest(false);
        setNewQuest("");
      } else {
        setFlashMessages([data.msg || "Errore nell'invio della domanda"]);
      }
    } catch (err) {
      console.error("Errore nella richiesta questbox:", err);
      setFlashMessages(["Errore di rete, riprova."]);
    }
  };

  if (loading) return <p className="p-10 text-lg">Caricamento...</p>;
  if (!trip) return <p className="p-10 text-lg">Viaggio non trovato.</p>;

  return (
    <div className="min-h-screen font-quicksand bg-[#e7e5ecd5]">
      <FlashMessages
        messages={flashMessages}
        onClose={() => setFlashMessages([])}
      />
      {/* img */}
      <div className="relative">
        <img
          src={trip.bg_img_path}
          className="w-full h-[600px] object-cover brightness-110"
        />

        {/* Titolo */}
        <div className="absolute top-7 right-36 flex flex-col">
          <p className="text-[40px] font-bold text-[#112142]">
            {trip.destination}
          </p>
          <p className="text-[40px] font-bold text-[#112651]">
            {trip.subtitle}
          </p>
        </div>

        {/* Card */}
        <div className="absolute top-24 left-50 text-white bg-[#152c5b98] rounded-md w-80 h-65 p-6 text-center">
          <p className="font-bold text-sm">
            {trip.start} ∙ {trip.end}
          </p>
          <p className="font-bold text-xs mb-5">({trip.nights} notti)</p>
          <p className="font-bold text-xl">A soli</p>
          <p className="text-4xl font-bold mb-4">{trip.price}€</p>
          <p className="font-bold text-xs mb-4">
            {trip.free_seats} posti disponibili
          </p>

          <button
            className="bg-green-700 px-4 py-2 rounded font-bold"
            onClick={() => setNewBooking(true)}
          >
            Prenota
          </button>
        </div>

        <div className="absolute top-130 left-1/2 -translate-x-1/2 bg-white/70 px-4 py-2 rounded text-black font-bold">
          Scopri i dettagli👇
        </div>
      </div>

      {/* Dettaglio + Aside */}
      <div className="flex justify-between gap-6 px-10 py-10">
        {/* Descrizione */}
        <div className="w-220">
          <div className="bg-[#f8f9fa] text-[#113f72] rounded-xl p-8">
            <h2 className="text-green-700 text-2xl font-bold text-center mb-4">
              {trip.destination} da scoprire
            </h2>
            <hr className="mb-4" />
            <p className="mb-6">{trip.description}</p>

            <h4 className="text-green-700 text-2xl font-bold text-center mb-2">
              L'itinerario nel dettaglio
            </h4>
            <hr className="mb-4" />
            <p>{trip.tour}</p>
          </div>
        </div>

        {/* Aside */}
        <div className="flex flex-col gap-6 w-88">
          <div className="bg-[#f8f9fa] text-[#113f72] rounded-xl p-6">
            <h4 className="text-center text-2xl text-green-700 font-bold mb-4">
              Cosa è incluso
            </h4>
            <hr className="mb-4" />
            <p>
              ✔ <strong>Alloggio</strong> ({trip.stay_price}€)
            </p>
            <p>
              ✔ <strong>Attività</strong> ({trip.act_price}€)
            </p>
            <p>
              ✔ <strong>Trasporti</strong> ({trip.transport_price}€)
            </p>
          </div>

          {/* QuestBox */}
          <div className="bg-[#f8f9fa] text-[#113f72] rounded-xl p-6">
            {new Date(trip.start.split("/").reverse().join("-")) <
            new Date() ? (
              <p className="text-center text-lg font-bold">
                Siamo partiti! Alla prossima!
              </p>
            ) : (
              <>
                <h4 className="text-center text-2xl text-green-700 font-bold mb-4">
                  Hai dubbi?
                </h4>
                <hr className="mb-4" />
                <button
                  className="bg-green-600 text-white text-lg px-4 py-2 rounded w-full"
                  onClick={() => setShowQuest(true)}
                >
                  Contattaci
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Modale Prenota */}
      {newBooking && (
        <div className="fixed inset-0 bg-black/60 flex justify-center items-center">
          <div className="bg-white p-6 rounded-xl w-md">
            <h2 className="text-xl font-bold mb-4">
              Prenota il viaggio per {trip.destination}!
            </h2>
            <p className="mb-4">
              Conferma la tua prenotazione e potrai vederne i dettagli sul tuo
              profilo!
            </p>

            <button
              className="bg-green-700 text-white px-4 py-2 rounded"
              onClick={bookTrip}
            >
              Conferma
            </button>

            <button
              className="ml-3 px-4 py-2 border rounded"
              onClick={() => setNewBooking(false)}
            >
              Chiudi
            </button>
          </div>
        </div>
      )}

      {/* Modale Q&A */}
      {showQuest && (
        <form
          onSubmit={submitQuestForm}
          className="fixed inset-0 bg-black/60 flex justify-center items-center"
        >
          <div className="bg-white p-6 rounded-xl w-md">
            <h2 className="text-xl font-bold mb-4">
              Fai la tua domanda a {trip.coord_username}
            </h2>

            <textarea
              className="border w-full p-2 rounded mb-4"
              value={newQuest}
              onChange={(e) => setNewQuest(e.target.value)}
              placeholder="Scrivi qui la tua domanda"
            />

            <button className="bg-green-700 text-white px-4 py-2 rounded">
              Invia
            </button>

            <button
              className="ml-3 px-4 py-2 border rounded"
              onClick={() => setShowQuest(false)}
            >
              Chiudi
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
