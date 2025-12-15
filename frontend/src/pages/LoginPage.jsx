import React, { useState, useEffect } from "react";
import { decodeJwt } from "jose";
import FlashMessages from "../components/FlashMessages";

function Login() {
  // Stati login
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  // Stati signup
  const [signupData, setSignupData] = useState({
    name: "",
    surname: "",
    birthdate: "",
    gender: "",
    username: "",
    password: "",
  });

  // Flash messages
  const [flashMessages, setFlashMessages] = useState([]);
  const [showSignupModal, setShowSignupModal] = useState(false);

  const resetSignup = () => {
    setSignupData({
      name: "",
      surname: "",
      birthdate: "",
      gender: "",
      username: "",
      password: "",
    });
    setShowSignupModal(false);
  };

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch("http://localhost:5000/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        setFlashMessages([data.msg || "Credenziali errate. Riprova."]);
        return;
      }

      const token = data.access_token;
      localStorage.setItem("access_token", token);

      const claims = decodeJwt(token);
      if (claims.is_coordinator) window.location.href = "/coord-profile";
      else window.location.href = "/trips";
    } catch (err) {
      setFlashMessages(["Errore di connessione"]);
    }
  };

  const handleSignupChange = (e) => {
    const { name, value } = e.target;
    setSignupData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSignupSubmit = async (e) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      Object.entries(signupData).forEach(([key, value]) => {
        formData.append(key, value);
      });

      const res = await fetch("http://localhost:5000/api/signup", {
        method: "POST",
        body: formData,
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        setFlashMessages([data.message || "Errore durante la registrazione."]);
        resetSignup();
        return;
      }

      setFlashMessages(["Iscrizione completata! Ora puoi accedere."]);
      resetSignup();
    } catch (err) {
      setFlashMessages(["Errore di connessione"]);
    }
  };

  return (
    <div className="h-screen font-quicksand bg-[url('/login_bg.jpg')] bg-cover bg-center bg-fixed">
      <main>
        <FlashMessages
          messages={flashMessages}
          onClose={() => setFlashMessages([])}
        />
        <div className="text-center bg-white/65 py-1">
          <p className="text-2xl text-teal-900">
            Vivi assieme a noi nuove avventure in giro per il mondo
          </p>
        </div>

        <section
          className="
    w-96 bg-white p-6 rounded-2xl shadow-lg
    mt-10
    mx-auto
    md:mt-20 md:ml-50 md:mx-0
  "
        >
          {/* Form Login */}
          <form
            onSubmit={handleLoginSubmit}
            className="flex flex-col space-y-3 px-4"
          >
            <p className="text-center text-lg font-semibold my-2">
              Bentornato!
            </p>
            <input
              className="border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="Nome utente"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
            <input
              className="border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <div className="flex justify-center">
              <button className="w-1/3 bg-red-700 text-white font-bold text-s py-2 my-3 rounded hover:bg-red-800">
                Accedi
              </button>
            </div>
          </form>

          <hr className="border border-green-700 opacity-30 my-2" />

          {/* Signup */}
          <div className="text-center">
            <p className="text-lg font-semibold my-3">Parti con noi!</p>
            <button
              onClick={() => setShowSignupModal(true)}
              className="w-1/3 bg-orange-400/50 text-red-700 font-bold text-s py-2 my-3 rounded hover:bg-orange-500/50"
            >
              Iscriviti
            </button>
          </div>
        </section>
        {/* Modale Signup */}
        {showSignupModal && (
          <div className="fixed inset-0 flex items-center justify-center z-50 bg-black/50">
            <div className="bg-white rounded shadow-lg w-96 p-4">
              <div className="flex justify-between items-center mb-2">
                <h2 className="text-lg font-bold">
                  Inizia con noi il tuo viaggio
                </h2>
                <button
                  className="text-gray-500 hover:text-gray-800 font-bold"
                  onClick={resetSignup}
                >
                  ×
                </button>
              </div>
              <form
                onSubmit={handleSignupSubmit}
                className="flex flex-col space-y-2"
              >
                <input
                  name="name"
                  placeholder="Nome"
                  className="border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
                  value={signupData.name}
                  onChange={handleSignupChange}
                  required
                />
                <input
                  name="surname"
                  placeholder="Cognome"
                  className="border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
                  value={signupData.surname}
                  onChange={handleSignupChange}
                  required
                />
                <label className="flex justify-center font-semibold">
                  Data di nascita
                </label>
                <div className="flex justify-center">
                  <input
                    name="birthdate"
                    type="date"
                    className="border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
                    value={signupData.birthdate}
                    onChange={handleSignupChange}
                    required
                  />
                </div>
                <div className="flex flex-col items-center mt-2">
                  <div className="flex items-center space-x-2">
                    <input
                      type="radio"
                      name="gender"
                      value="F"
                      checked={signupData.gender === "F"}
                      onChange={handleSignupChange}
                      className="accent-green-700"
                      required
                    />
                    <label>Donna</label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input
                      type="radio"
                      name="gender"
                      value="M"
                      checked={signupData.gender === "M"}
                      onChange={handleSignupChange}
                      className="accent-green-700"
                    />
                    <label>Uomo</label>
                  </div>
                </div>
                <input
                  name="username"
                  placeholder="Nome utente"
                  className="border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
                  value={signupData.username}
                  onChange={handleSignupChange}
                  required
                />
                <input
                  name="password"
                  type="password"
                  placeholder="Password"
                  className="border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
                  value={signupData.password}
                  onChange={handleSignupChange}
                  required
                />
                <button
                  type="submit"
                  className="bg-green-900 text-white font-bold py-2 rounded mt-2 hover:bg-green-700"
                >
                  Iscriviti
                </button>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default Login;
