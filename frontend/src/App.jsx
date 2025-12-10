import {
  Route,
  createBrowserRouter,
  createRoutesFromElements,
  RouterProvider,
} from "react-router-dom";

import MainLayout from "./layouts/MainLayout";
import LoginPage from "./pages/LoginPage";
import TripsHomePage from "./pages/TripsHomePage";
import TripPage from "./pages/TripPage";
import UserProfilePage from "./pages/UserProfilePage";
import CoordProfilePage from "./pages/CoordProfilePage";
import CheckProtectedRoute from "./components/CheckProtectedRoute";

const router = createBrowserRouter(
  createRoutesFromElements(
    <Route path="/" element={<MainLayout />}>
      <Route index element={<LoginPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/trips"
        element={
          <CheckProtectedRoute role="traveler">
            <TripsHomePage />
          </CheckProtectedRoute>
        }
      />
      <Route
        path="/trip/:id"
        element={
          <CheckProtectedRoute role="traveler">
            <TripPage />
          </CheckProtectedRoute>
        }
      />
      <Route
        path="/user-profile"
        element={
          <CheckProtectedRoute role="traveler">
            <UserProfilePage />
          </CheckProtectedRoute>
        }
      />
      <Route
        path="/coord-profile"
        element={
          <CheckProtectedRoute role="coordinator">
            <CoordProfilePage />
          </CheckProtectedRoute>
        }
      />
    </Route>
  )
);
function App() {
  return <RouterProvider router={router} />;
}

export default App;
