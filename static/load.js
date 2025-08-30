document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("search-form");
  const resultsDiv = document.getElementById("results");
  const paginationDiv = document.getElementById("pagination");

  let currentPage = 0;
  let lastQuery = ""; 

 
  function buildBaseQuery() {
    const city  = (form.city?.value || "").trim();
    const state = (form.state?.value || "").trim();
    const type  = (form.type?.value || "");

    const params = new URLSearchParams();
    if (city)  params.append("city", city);
    if (state) params.append("state", state);
    if (type)  params.append("type", type);

    return "/api/events" + (params.toString() ? "?" + params.toString() : "");
  }

  // Rend une liste d'événements en "cartes"
  function renderEvents(list) {
    if (!list || list.length === 0) {
      resultsDiv.innerHTML = "<p>No events found.</p>";
      return;
    }

    let html = "";
    list.forEach(ev => {
      const name  = ev.name  || "Untitled event";
      const date  = ev.date  || "N/A";
      const venue = ev.venue || "Unknown venue";
      const city  = ev.city  ? `, ${ev.city}` : "";
      const url   = ev.url   || "#";

      html += `
        <div class="event-card">
          <h3>${name}</h3>
          <p><strong>Date:</strong> ${date}</p>
          <p><strong>Location:</strong> ${venue}${city}</p>
          <a href="${url}" target="_blank" rel="noopener" class="details-btn">View Details</a>
        </div>
      `;
    });
    resultsDiv.innerHTML = html;
  }

 
  function renderPagination(curr, total) {
    let buttons = "";
    if (curr > 0) {
      buttons += `<button id="prev-btn" class="btn">Previous</button>`;
    }
    if (total > 0 && curr < total - 1) {
      buttons += `<button id="next-btn" class="btn">Next</button>`;
    }
    paginationDiv.innerHTML = buttons;

    const prev = document.getElementById("prev-btn");
    const next = document.getElementById("next-btn");
    if (prev) prev.addEventListener("click", () => loadEvents(curr - 1));
    if (next) next.addEventListener("click", () => loadEvents(curr + 1));
  }


  function loadEvents(page = 0) {
  
    const sep = lastQuery.includes("?") ? "&" : "?";
    const url = `${lastQuery}${sep}page=${page}`;

    resultsDiv.innerHTML = "<p>Loading events...</p>";
    paginationDiv.innerHTML = "";

    fetch(url)
      .then(resp => {
        if (!resp.ok) throw new Error("Network error");
        return resp.json();
      })
      .then(data => {
        renderEvents(data.events || []);
        currentPage = Number(data.current_page || 0);
        const totalPages = Number(data.total_pages || 0);
        renderPagination(currentPage, totalPages);
      })
      .catch(err => {
        console.error("Error fetching events:", err);
        resultsDiv.innerHTML = "<p style='color:red;'>Error loading events.</p>";
      });
  }


  form.addEventListener("submit", function (e) {
    e.preventDefault();
    lastQuery = buildBaseQuery() || "/api/events"; 
    currentPage = 0;
    loadEvents(currentPage);
  });
});
