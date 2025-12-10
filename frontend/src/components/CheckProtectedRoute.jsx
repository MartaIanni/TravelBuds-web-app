import React from "react";
import { Navigate } from "react-router-dom";
import { decodeJwt } from "jose";
import { getToken } from "../services/auth";

const CheckProtectedRoute = ({ role, children }) => {
  const token = getToken();

  if (!token) return <Navigate to="/login" replace />;

  try {
    const claims = decodeJwt(token);

    // Controllo ruolo
    const roleMap = {
      coordinator: claims.is_coordinator,
      traveler: !claims.is_coordinator,
    };

    if (!roleMap[role]) {
      // Token presente ma ruolo non corretto
      return <Navigate to="/login" replace />;
    }

    return children;
  } catch {
    // Token non decodificabile
    console.error("Errore decoding token:", err);
    return <Navigate to="/login" replace />;
  }
};

export default CheckProtectedRoute;
