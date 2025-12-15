import { useState, useEffect } from "react";
import FlashMessages from "./FlashMessages";

function NewTripForm({ submitNewTrip, onClose }) {
  const [destination, setDestination] = useState("");
  const [subtitle, setSubtitle] = useState("");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [seats, setSeats] = useState(0);
  const [transportPrice, setTransportPrice] = useState(0);
  const [stayPrice, setStayPrice] = useState(0);
  const [actPrice, setActPrice] = useState(0);
  const [cardFile, setCardFile] = useState(null);
  const [bgFile, setBgFile] = useState(null);
  const [cardPreview, setCardPreview] = useState(null);
  const [bgPreview, setBgPreview] = useState(null);
  const [description, setDescription] = useState("");
  const [tour, setTour] = useState("");
  const [flashMessages, setFlashMessages] = useState([]);

  const handleSubmit = (e, actionType) => {
    e.preventDefault();
    // campi obbligatori
    const errors = [];
    if (!destination) errors.push("Destinazione obbligatoria");
    if (!start) errors.push("Data di partenza obbligatoria");
    if (!end) errors.push("Data di ritorno obbligatoria");

    // validazione date
    const today = new Date();
    today.setHours(0, 0, 0, 0); // normalizza a mezzanotte
    const startDate = new Date(start);
    const endDate = new Date(end);
    if (startDate <= today)
      errors.push("La partenza deve essere successiva ad oggi");
    if (startDate > endDate)
      errors.push("La partenza deve essere precedente alla data di ritorno");

    if (errors.length > 0) {
      setFlashMessages(errors);
      return; // blocca invio
    }

    const formData = new FormData();
    formData.append("destination", destination);
    formData.append("subtitle", subtitle);
    formData.append("start", start);
    formData.append("end", end);
    formData.append("seats", seats);
    formData.append("transport_price", transportPrice);
    formData.append("stay_price", stayPrice);
    formData.append("act_price", actPrice);
    formData.append("description", description);
    formData.append("tour", tour);
    formData.append("action", actionType);

    if (cardFile instanceof File) formData.append("card_img_path", cardFile);
    if (bgFile instanceof File) formData.append("bg_img_path", bgFile);

    submitNewTrip(formData, actionType);
  };

  //Per evitare memory leak se l'utente inserisce più volte l'immagine

  useEffect(() => {
    return () => {
      if (bgPreview) URL.revokeObjectURL(bgPreview);
      if (cardPreview) URL.revokeObjectURL(cardPreview);
    };
  }, [bgPreview, cardPreview]);

  return (
    <>
      <FlashMessages
        messages={flashMessages}
        onClose={() => setFlashMessages([])}
      />
      <form className="flex flex-col items-center gap-2">
        <input
          type="text"
          className="border border-gray-300 rounded-md px-2 py-1 w-full"
          value={destination}
          placeholder="Destinazione"
          onChange={(e) => setDestination(e.target.value)}
          required
        />

        <div className="flex flex-row gap-20">
          <div className="flex flex-col items-center">
            <label>Partenza:</label>
            <input
              type="date"
              className="border border-gray-300 rounded-md px-2 py-1"
              value={start}
              onChange={(e) => setStart(e.target.value)}
              required
            />
          </div>

          <div className="flex flex-col items-center">
            <label>Ritorno:</label>
            <input
              type="date"
              className="border border-gray-300 rounded-md px-2 py-1"
              value={end}
              onChange={(e) => setEnd(e.target.value)}
              required
            />
          </div>
        </div>
        <div className="flex flex-row gap-4">
          <label className="mt-1">Numero di posti:</label>
          <input
            type="number"
            min={0}
            className="border border-gray-300 rounded-md px-2 py-1 w-20"
            value={seats}
            onChange={(e) => setSeats(e.target.value)}
          />
        </div>
        <textarea
          className="border border-gray-300 rounded-md px-2 py-1 w-full resize-y h-20"
          value={description}
          placeholder="Presentazione del viaggio"
          onChange={(e) => setDescription(e.target.value)}
          required
        />

        <div className="flex flex-row gap-6">
          <div className="flex flex-col items-center">
            <label>Prezzo trasporti:</label>
            <input
              type="number"
              min={0}
              className="border border-gray-300 rounded-md px-2 py-1 w-20"
              value={transportPrice}
              onChange={(e) => setTransportPrice(e.target.value)}
            />
          </div>

          <div className="flex flex-col items-center">
            <label>Prezzo alloggio:</label>
            <input
              type="number"
              min={0}
              className="border border-gray-300 rounded-md px-2 py-1 w-20"
              value={stayPrice}
              onChange={(e) => setStayPrice(e.target.value)}
            />
          </div>

          <div className="flex flex-col items-center">
            <label>Prezzo attività:</label>
            <input
              type="number"
              min={0}
              className="border border-gray-300 rounded-md px-2 py-1 w-20"
              value={actPrice}
              onChange={(e) => setActPrice(e.target.value)}
            />
          </div>
        </div>

        <input
          type="text"
          className="border border-gray-300 rounded-md px-2 py-1 w-full"
          value={subtitle}
          placeholder="Sottotitolo"
          onChange={(e) => setSubtitle(e.target.value)}
          required
        />

        <textarea
          className="border border-gray-300 rounded-md px-2 py-1 w-full resize-y h-20"
          value={tour}
          placeholder="Itinerario delle giornate"
          onChange={(e) => setTour(e.target.value)}
          required
        />

        {/* FILES */}
        <div className="flex justify-between gap-3 border border-gray-300 rounded-md w-full">
          <input
            id="bgFileInput"
            type="file"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files[0];
              setBgFile(file);
              setBgPreview(URL.createObjectURL(file));
            }}
          />
          <label
            htmlFor="bgFileInput"
            className="cursor-pointer bg-gray-200 text-gray-700 px-3 py-1 rounded-md hover:bg-gray-300"
          >
            Scegli foto di sfondo
          </label>

          <span className="text-gray-600 mt-1 mr-3">
            {!bgFile
              ? "Nessun file selezionato"
              : bgFile instanceof File
              ? bgFile.name
              : bgFile}
          </span>
          {bgPreview && (
            <img
              src={bgPreview}
              alt="Anteprima"
              className="w-20 h-8 object-cover rounded"
            />
          )}
        </div>

        <div className="flex justify-between gap-3 border border-gray-300 rounded-md w-full">
          <input
            id="cardFileInput"
            type="file"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files[0];
              setCardFile(file);
              setCardPreview(URL.createObjectURL(file));
            }}
          />
          <label
            htmlFor="cardFileInput"
            className="cursor-pointer bg-gray-200 text-gray-700 px-3 py-1 rounded-md hover:bg-gray-300"
          >
            Scegli foto di presentazione
          </label>
          <span className="text-gray-600 mt-1 mr-3">
            {!cardFile
              ? "Nessun file selezionato"
              : cardFile instanceof File
              ? cardFile.name
              : cardFile}
          </span>
          {cardPreview && (
            <img
              src={cardPreview}
              alt="Anteprima"
              className="w-20 h-8 object-cover rounded"
            />
          )}
        </div>

        {/* BOTTONI */}
        <div className="flex justify-between gap-5 mt-4">
          <div className="flex justify-between gap-5 mt-4">
            <button
              type="button"
              className="bg-[#d44420] text-white px-4 py-2 rounded"
              onClick={(e) => handleSubmit(e, "post")}
            >
              Pubblica
            </button>

            <button
              type="button"
              className="bg-amber-600 text-white px-4 py-2 rounded"
              onClick={(e) => handleSubmit(e, "save")}
            >
              Salva
            </button>
          </div>
        </div>
      </form>
    </>
  );
}

export default NewTripForm;
