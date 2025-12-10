import React from "react";
import { NavLink, useNavigate, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { resStatus, getToken, logout } from "../services/auth";

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [user, setUser] = useState(null);

  const hiddenPages = ["/login"];
  const hideBottomBar = hiddenPages.includes(location.pathname);
  const coordProfile = ["/coord-profile"];
  const coordPages = coordProfile.includes(location.pathname);

  useEffect(() => {
    const fetchUser = async () => {
      const token = getToken();

      if (!token) {
        navigate("/login");
        return;
      }
      try {
        const res = await fetch("http://localhost:5000/api/me", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        });

        if (resStatus(res)) return;

        const data = await res.json();
        if (res.ok) setUser(data);
        else if (data.msg === "Token non valido") {
          localStorage.removeItem("access_token");
          navigate("/login");
        }
      } catch (err) {
        console.error("Errore fetch utente:", err);
      }
    };

    fetchUser();
  }, [navigate]);

  const linkClass = ({ isActive }) =>
    isActive
      ? "text-green-900 font-bold hover:underline"
      : "text-green-900 hover:underline";

  return (
    <>
      <nav className="flex justify-center items-center font-quicksand bg-green-900 text-green-200 h-30">
        <h1 className="font-bold text-[80px] m-0 p-0">TravelBuds</h1>
      </nav>

      {!hideBottomBar && (
        <div className="flex justify-between font-quicksand text-center bg-green-200 py-3 px-7 shadow-md">
          <h4 className="text-xl font-bold">
            {user
              ? coordPages
                ? `Ciao ${user.name}!`
                : `Ciao ${user.name}! Noi siamo pronti a partire e tu?`
              : "Caricamento..."}
          </h4>
          <div className="flex justify-center gap-10">
            {coordPages ? (
              <></>
            ) : (
              <>
                <NavLink to="/trips" className={linkClass}>
                  Viaggi
                </NavLink>

                <NavLink to="/user-profile" className={linkClass}>
                  Il mio profilo
                </NavLink>
              </>
            )}

            {/* Uguale per tutti, quindi resta fuori dal ternario */}
            <NavLink
              className="text-green-900 hover:underline"
              onClick={logout}
            >
              Logout
            </NavLink>
          </div>
        </div>
      )}
    </>
  );
};

export default Navbar;
