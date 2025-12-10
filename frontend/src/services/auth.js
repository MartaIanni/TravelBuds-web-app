export function logout() {
  localStorage.removeItem("access_token");
  window.location.href = "/login";
}

export function getToken() {
  return localStorage.getItem("access_token");
}

export function resStatus(res) {
  if (res.status === 401 || res.status === 422) {
    logout();
    return true; // segnala che c’è stato logout
  }
  return false;
}
