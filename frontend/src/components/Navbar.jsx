import React from "react";
import { NavLink, useNavigate, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { resStatus, getToken, logout } from "../services/auth";

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [user, setUser] = useState(null);
  const [isOpen, setIsOpen] = useState(false); // stato hamburger

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
      {/* TITLE */}
      <nav className="flex justify-center items-center font-quicksand bg-green-900 text-green-200 h-30">
        <h1 className="font-bold text-[80px] m-0 p-0">TravelBuds</h1>
      </nav>

      {!hideBottomBar && (
        <div className="font-quicksand bg-green-200 py-3 px-7 shadow-md">
          {/* TOP BAR */}
          <div className="flex justify-between items-center h-7 relative">
            {/* MOBILE */}
            <h4 className="text-xl font-bold md:hidden">
              {user ? `Ciao ${user.name}!` : "Caricamento..."}
            </h4>

            {/* DESKTOP: frase estesa rispetto al ruolo user */}
            <h4 className="text-xl font-bold hidden md:block">
              {user
                ? coordPages
                  ? `Ciao ${user.name}!`
                  : `Ciao ${user.name}! Noi siamo pronti a partire e tu?`
                : "Caricamento..."}
            </h4>

            {/* HAMBURGER MOBILE */}
            <button
              className="md:hidden text-green-900 text-3xl"
              onClick={() => setIsOpen(!isOpen)}
            >
              ☰
            </button>

            {/* MENU DESKTOP */}
            <div className="hidden md:flex gap-10">
              {!coordPages && (
                <>
                  <NavLink to="/trips" className={linkClass}>
                    Viaggi
                  </NavLink>
                  <NavLink to="/user-profile" className={linkClass}>
                    Il mio profilo
                  </NavLink>
                </>
              )}

              <NavLink
                className="text-green-900 hover:underline"
                onClick={logout}
              >
                Logout
              </NavLink>
            </div>

            {/* MENU MOBILE DROPDOWN */}
            {isOpen && (
              <div className="md:hidden absolute right-0 top-6 mt-2 w-48 bg-green-50 p-4 rounded-lg shadow-lg flex flex-col gap-3 z-50">
                {!coordPages && (
                  <>
                    <NavLink
                      to="/trips"
                      className="text-green-900 font-semibold"
                      onClick={() => setIsOpen(false)}
                    >
                      Viaggi
                    </NavLink>

                    <NavLink
                      to="/user-profile"
                      className="text-green-900 font-semibold"
                      onClick={() => setIsOpen(false)}
                    >
                      Il mio profilo
                    </NavLink>
                  </>
                )}
                <button
                  className="text-green-900 font-semibold text-left"
                  onClick={() => {
                    setIsOpen(false);
                    logout();
                  }}
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default Navbar;
