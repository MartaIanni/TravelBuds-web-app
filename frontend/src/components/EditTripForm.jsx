import React, { useState } from "react";
import useDateFormat from "../hooks/useDateFormat";
import FlashMessages from "./FlashMessages";
import { resStatus, getToken } from "../services/auth";

export default function EditTripForm({ trip, onClose }) {
  const { toInputDate } = useDateFormat();
  const [form, setForm] = useState({
    tid: trip.tid,
    destination: trip.destination,
    description: trip.description,
    subtitle: trip.subtitle,
    tour: trip.tour,
    start: toInputDate(trip.start),
    end: toInputDate(trip.end),
    free_seats: trip.free_seats,
    transport_price: trip.transport_price,
    stay_price: trip.stay_price,
    act_price: trip.act_price,
  });

  const [cardImg, setCardImg] = useState(trip.card_img_path || null);
  const [cardPreview, setCardPreview] = useState(
    trip.card_img_path ? trip.card_img_path : null
  );
  const [bgImg, setBgImg] = useState(trip.bg_img_path || null);
  const [bgPreview, setBgPreview] = useState(
    trip.bg_img_path ? trip.bg_img_path : null
  );

  const token = getToken();
  const [flashMessages, setFlashMessages] = useState([]);

  const handleChange = (e) => {
    let value = e.target.value;

    if (e.target.type === "number" && parseFloat(value) < 0) {
      return; // non aggiornare lo state per numeri negativi
    }

    setForm({
      ...form,
      [e.target.name]: value,
    });
  };

  const submitEdit = async (action) => {
    if (!form.destination) {
      setFlashMessages(["Destinazione obbligatoria"]);
      return;
    }
    if (!form.start || !form.end) {
      setFlashMessages(["Date di partenza e arrivo obbligatorie"]);
      return;
    }

    try {
      const fd = new FormData();

      // aggiungo campi testo
      Object.keys(form).forEach((key) => {
        fd.append(key, form[key]);
      });

      // invio immagini solo se aggiornate
      if (cardImg instanceof File) fd.append("card_img_path", cardImg);
      if (bgImg instanceof File) fd.append("bg_img_path", bgImg);

      fd.append("action", action);

      const res = await fetch("http://localhost:5000/api/draft_validation", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: fd,
      });
      if (resStatus(res)) return;

      const data = await res.json();

      if (data.success) {
        setFlashMessages([data.msg]);
        onClose();
        window.location.reload();
      } else {
        setFlashMessages([data.msg || "Errore di rete, riprova."]);
      }
    } catch (err) {
      console.error(err);
      setFlashMessages(["Errore di rete"]);
    }
  };

  return (
    <>
      <FlashMessages
        messages={flashMessages}
        onClose={() => setFlashMessages([])}
      />
      <div onClick={onClose}>
        <div onClick={(e) => e.stopPropagation()}>
          <h2 className="text-2xl font-bold mb-4">Modifica bozza</h2>
          <div className="flex flex-col items-center gap-2">
            <input
              name="destination"
              type="text"
              className="border border-gray-300 rounded-md px-2 py-1 w-full"
              value={form.destination}
              placeholder="Destinazione"
              onChange={handleChange}
              required
            />

            <div className="flex flex-row gap-20">
              <div className="flex flex-col items-center">
                <label>Partenza:</label>
                <input
                  name="start"
                  type="date"
                  className="border border-gray-300 rounded-md px-2 py-1"
                  value={form.start}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="flex flex-col items-center">
                <label>Ritorno:</label>
                <input
                  name="end"
                  type="date"
                  className="border border-gray-300 rounded-md px-2 py-1"
                  value={form.end}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>
            <div className="flex flex-row gap-4">
              <label className="mt-1">Numero di posti:</label>
              <input
                name="free_seats"
                type="number"
                min={0}
                className="border border-gray-300 rounded-md px-2 py-1 w-20"
                value={form.free_seats}
                onChange={handleChange}
              />
            </div>
            <textarea
              name="description"
              className="border border-gray-300 rounded-md px-2 py-1 w-full resize-y h-20"
              value={form.description}
              placeholder="Presentazione del viaggio"
              onChange={handleChange}
              required
            />

            <div className="flex flex-row gap-6">
              <div className="flex flex-col items-center">
                <label>Prezzo trasporti:</label>
                <input
                  name="transport_price"
                  type="number"
                  min={0}
                  className="border border-gray-300 rounded-md px-2 py-1 w-20"
                  value={form.transport_price}
                  onChange={handleChange}
                />
              </div>

              <div className="flex flex-col items-center">
                <label>Prezzo alloggio:</label>
                <input
                  name="stay_price"
                  type="number"
                  min={0}
                  className="border border-gray-300 rounded-md px-2 py-1 w-20"
                  value={form.stay_price}
                  onChange={handleChange}
                />
              </div>

              <div className="flex flex-col items-center">
                <label>Prezzo attività:</label>
                <input
                  name="act_price"
                  type="number"
                  min={0}
                  className="border border-gray-300 rounded-md px-2 py-1 w-20"
                  value={form.act_price}
                  onChange={handleChange}
                />
              </div>
            </div>

            <input
              name="subtitle"
              type="text"
              className="border border-gray-300 rounded-md px-2 py-1 w-full"
              value={form.subtitle}
              placeholder="Sottotitolo"
              onChange={handleChange}
              required
            />

            <textarea
              name="tour"
              className="border border-gray-300 rounded-md px-2 py-1 w-full resize-y h-20"
              value={form.tour}
              placeholder="Itinerario delle giornate"
              onChange={handleChange}
              required
            />

            {/* FILES */}
            <div className="flex justify-between gap-3 border border-gray-300 rounded-md w-full">
              <input
                id="bgImgInput"
                type="file"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files[0];
                  setBgImg(file);
                  setBgPreview(URL.createObjectURL(file));
                }}
              />

              <label
                htmlFor="bgImgInput"
                className="cursor-pointer bg-gray-200 text-gray-700 px-3 py-1 rounded-md hover:bg-gray-300"
              >
                {cardPreview && !bgPreview.includes("no_image.jpg")
                  ? "Cambia foto sfondo"
                  : "Scegli foto di presentazione"}
              </label>
              <span className="text-black-800 mt-1 mr-2">
                {!bgPreview.includes("no_image.jpg")
                  ? "Immagine presente"
                  : "Nessuna immagine"}
              </span>
              {bgPreview && !bgPreview.includes("no_image.jpg") && (
                <img
                  src={bgPreview}
                  alt="Anteprima"
                  className="w-20 h-8 object-cover rounded"
                />
              )}
            </div>

            <div className="flex justify-between gap-3 border border-gray-300 rounded-md w-full">
              <input
                id="cardImgInput"
                type="file"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files[0];
                  setCardImg(file);
                  setCardPreview(URL.createObjectURL(file));
                }}
              />
              <label
                htmlFor="cardImgInput"
                className="cursor-pointer bg-gray-200 text-gray-700 px-3 py-1 rounded-md hover:bg-gray-300"
              >
                {cardPreview && !cardPreview.includes("no_image.jpg")
                  ? "Cambia foto presentazione"
                  : "Scegli foto di presentazione"}
              </label>
              <span className="text-black mt-1 mr-2">
                {!cardPreview.includes("no_image.jpg")
                  ? "Immagine presente"
                  : "Nessuna immagine"}
              </span>
              {cardPreview && !cardPreview.includes("no_image.jpg") && (
                <img
                  src={cardPreview}
                  alt="Anteprima"
                  className="w-20 h-8 object-cover rounded"
                />
              )}
            </div>

            {/* BOTTONI */}
            <div className="flex justify-between gap-5 mt-4">
              <button
                type="button"
                className="bg-[#d44420] text-white px-4 py-2 rounded"
                onClick={(e) => submitEdit("post")}
              >
                Pubblica
              </button>

              <button
                type="button"
                className="bg-amber-600 text-white px-4 py-2 rounded"
                onClick={(e) => submitEdit("save")}
              >
                Salva
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
