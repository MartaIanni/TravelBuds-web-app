import React, { useState } from "react";
import { useLocation } from "react-router-dom";
import ShowTripModal from "./ShowTripModal";
import FlashMessages from "./FlashMessages";
import { resStatus, getToken } from "../services/auth";
import { NavLink } from "react-router-dom";

export default function TripCard({ trip, section }) {
  const location = useLocation();
  const userProfileCard = location.pathname === "/user-profile";
  const coordProfileCard = location.pathname === "/coord-profile";
  const homePageCard = location.pathname === "/trips";

  const [showModal, setShowModal] = useState(false);

  const isDraft = section === "draft";
  const isPublished = section === "published";

  const [flashMessages, setFlashMessages] = useState([]);

  return (
    <>
      <FlashMessages
        messages={flashMessages}
        onClose={() => setFlashMessages([])}
      />
      <NavLink
        to={coordProfileCard ? "#" : `/trip/${trip.tid}`}
        className={`relative block rounded overflow-hidden no-underline font-quicksand ${
          userProfileCard || coordProfileCard ? "w-98 h-55" : "w-100 h-70"
        }`}
      >
        <img
          src={trip.card_img_path}
          alt={trip.destination}
          className="absolute top-0 left-0 w-full h-full object-cover"
        />

        <div className="absolute inset-0 flex flex-col justify-center items-center text-center  text-white bg-black/10 hover:bg-black/36 p-2">
          <h4 className="font-bold text-4xl">{trip.destination}</h4>

          {homePageCard && (
            <>
              <h6 className="absolute bottom-2 left-2 bg-black/70 px-2 py-1 rounded text-sm">
                {trip.nights} notti
              </h6>
              <h6 className="absolute bottom-2 right-2 bg-black/70 px-2 py-1 rounded text-sm">
                Offerta a {trip.price}€
              </h6>
            </>
          )}

          {userProfileCard && (
            <div className="p-4 flex flex-col items-center">
              <span className="mt-3 px-4 py-1 bg-green-900 text-white rounded-md">
                Visualizza
              </span>
            </div>
          )}

          {coordProfileCard && (
            <>
              {isDraft && (
                <div className="flex mt-5 gap-5 ">
                  <span
                    className="px-4 py-1 bg-green-800 text-white rounded-md hover:bg-emerald-500"
                    onClick={(e) => {
                      e.preventDefault();
                      setShowModal(true); //modale con form di modifica
                    }}
                  >
                    Modifica
                  </span>
                  <span
                    className="px-4 py-1 bg-red-800 text-white rounded-md  hover:bg-red-500"
                    onClick={async (e) => {
                      e.preventDefault();
                      const token = getToken();
                      if (
                        !window.confirm(
                          "Sei sicuro di voler eliminare questo viaggio?"
                        )
                      )
                        return;

                      try {
                        const formData = new FormData();
                        formData.append("tid", trip.tid);

                        const res = await fetch(
                          "http://localhost:5000/api/delete_validation",
                          {
                            method: "POST",
                            headers: {
                              Authorization: `Bearer ${token}`,
                            },
                            body: formData,
                          }
                        );
                        if (resStatus(res)) return;

                        if (res.ok) {
                          setFlashMessages(["Viaggio eliminato con successo!"]);
                          //eventualmente aggiorna la lista dei draft
                          window.location.reload(); //refresh della pagina
                        } else {
                          setFlashMessages([
                            "Errore nell'eliminazione del viaggio",
                          ]);
                        }
                      } catch (err) {
                        console.error(err);
                        setFlashMessages(["Errore di rete, riprova."]);
                      }
                    }}
                  >
                    Elimina
                  </span>
                </div>
              )}
              {isPublished && (
                <span
                  className="mt-5 px-4 py-1 bg-green-900 text-white rounded-md"
                  onClick={(e) => {
                    e.preventDefault();
                    setShowModal(true);
                  }}
                >
                  Visualizza
                </span>
              )}
            </>
          )}
        </div>
      </NavLink>
      {showModal && (
        <ShowTripModal
          trip={trip}
          onClose={() => setShowModal(false)}
          editable={isDraft} // passa prop per sapere se il form deve essere modificabile
        />
      )}
    </>
  );
}
