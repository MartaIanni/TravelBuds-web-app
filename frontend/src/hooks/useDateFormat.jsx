export default function useDateFormat() {
  // Converte formato DB -> formato input 'modifica viaggio'
  const toInputDate = (dateStr) => {
    if (!dateStr) return "";
    // Se arriva già in formato YYYY-MM-DD lo ritorna cosi' come'e'
    if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) return dateStr;

    const [day, month, year] = dateStr.split("/");
    return `${year}-${month}-${day}`;
  };

  return { toInputDate };
}
