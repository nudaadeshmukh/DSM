const SC_API_BASE = "http://127.0.0.1:5000/api/supply-chain";
const RESULTS_API_BASE = "http://127.0.0.1:5000/api/results";

let _costChart = null;

// Mobile Menu Toggle
function toggleMobileMenu() {
  const navMenu = document.querySelector(".nav-menu");
  navMenu.classList.toggle("mobile-open");
}

// Profile Dropdown Toggle
function toggleProfileDropdown(event) {
  event.stopPropagation();
  const dropdown = document.querySelector(".profile-dropdown");
  dropdown.classList.toggle("show");
}

document.addEventListener("click", function (event) {
  const profileCircle = document.querySelector(".profile-circle");
  const dropdown = document.querySelector(".profile-dropdown");

  if (dropdown && !profileCircle.contains(event.target)) {
    dropdown.classList.remove("show");
  }
});

// Form Submit Handler
async function handleLogin(event) {
  event.preventDefault();

  const email_or_username = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  try {
    const response = await fetch("http://127.0.0.1:5000/api/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email_or_username,
        password,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      alert(data.error || "Login failed");
      return;
    }

    localStorage.setItem("user", JSON.stringify(data));
    window.location.href = "dashboard.html";
  } catch (error) {
    console.error("Error:", error);
    alert("Error connecting to backend");
  }
}

async function handleSignup(event) {
  event.preventDefault();

  const username = document.getElementById("fullName").value;
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const confirm_password = password; // or get confirm field if you have one

  try {
    const response = await fetch("http://127.0.0.1:5000/api/auth/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username,
        email,
        password,
        confirm_password,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      alert(data.error || "Signup failed");
      return;
    }

    alert("Signup successful!");

    // OPTIONAL: still store locally if you want UI usage
    localStorage.setItem("user", JSON.stringify({ username, email }));

    window.location.href = "login.html";
  } catch (error) {
    console.error("Error:", error);
    alert("Error connecting to backend");
  }
}

// Run Optimization (CONNECTED TO BACKEND)
async function runOptimization() {
  const demand = document.getElementById("demand").value;
  const orderingCost = document.getElementById("orderingCost").value;
  const holdingCost = document.getElementById("holdingCost").value;
  const leadTime = document.getElementById("leadTime").value;

  // validation
  if (!demand || !orderingCost || !holdingCost || !leadTime) {
    alert("Please fill all fields!");
    return;
  }

  const data = {
    demand: parseFloat(demand),
    ordering_cost: parseFloat(orderingCost),
    holding_cost: parseFloat(holdingCost),
    lead_time: parseFloat(leadTime),
  };

  console.log("Sending:", data);

  try {
    const response = await fetch("http://127.0.0.1:5000/api/optimize", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    const result = await response.json();

    console.log("Response:", result);

    if (!response.ok) {
      alert(result.error || "Something went wrong!");
      return;
    }

    localStorage.setItem("optimizationResult", JSON.stringify(result));
    window.location.href = "results.html";
  } catch (error) {
    console.error("Error:", error);
    alert("Error connecting to backend!");
  }
}

function renderCostAnalysisChart(data) {
  const canvas = document.getElementById("costChart");
  const emptyEl = document.getElementById("costChartEmpty");
  const wrap = document.querySelector(".cost-chart-wrap");

  if (!canvas || typeof Chart === "undefined") {
    if (emptyEl) emptyEl.hidden = false;
    return;
  }

  let ord = data.annual_ordering_cost;
  let hold = data.annual_holding_cost;
  const trans = Number(data.transport_cost);
  const transport = Number.isFinite(trans) ? trans : 0;

  if (ord == null || hold == null) {
    const total = Number(data.total_cost);
    if (Number.isFinite(total)) {
      const inv = Math.max(0, total - transport);
      ord = inv / 2;
      hold = inv / 2;
    } else {
      ord = 0;
      hold = 0;
    }
  }

  const sum = ord + hold + transport;
  if (sum <= 0) {
    if (_costChart) {
      _costChart.destroy();
      _costChart = null;
    }
    if (wrap) wrap.hidden = true;
    if (emptyEl) {
      emptyEl.hidden = false;
      emptyEl.textContent =
        "No cost data to chart. Run optimization with valid inputs.";
    }
    return;
  }

  if (wrap) wrap.hidden = false;
  if (emptyEl) emptyEl.hidden = true;

  if (_costChart) {
    _costChart.destroy();
    _costChart = null;
  }

  _costChart = new Chart(canvas.getContext("2d"), {
    type: "doughnut",
    data: {
      labels: ["Annual ordering", "Annual holding", "Transport"],
      datasets: [
        {
          data: [ord, hold, transport],
          backgroundColor: ["#6366f1", "#14b8a6", "#06b6d4"],
          borderWidth: 2,
          borderColor: "rgba(255,255,255,0.85)",
          hoverOffset: 6,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "52%",
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            color: "#374151",
            padding: 14,
            font: { family: "Inter, system-ui, sans-serif", size: 13 },
          },
        },
        tooltip: {
          callbacks: {
            label(ctx) {
              const v = Number(ctx.raw);
              const total = ctx.dataset.data.reduce((a, b) => a + b, 0) || 1;
              const pct = ((v / total) * 100).toFixed(1);
              return ` ${ctx.label}: $${v.toLocaleString(undefined, { maximumFractionDigits: 2 })} (${pct}%)`;
            },
          },
        },
      },
    },
  });
}

function renderResultsProductTable(data) {
  const tbody = document.getElementById("resultsTableBody");
  if (!tbody) return;

  const fmt = (v) => (v === undefined || v === null ? "—" : v);
  let lines = Array.isArray(data.product_lines) ? data.product_lines : null;

  if (!lines || lines.length === 0) {
    const label = "Optimization summary";
    lines = [
      {
        label,
        eoq: data.eoq,
        rop: data.rop,
        transport_cost: data.transport_cost,
        total_cost: data.total_cost,
      },
    ];
  }

  tbody.innerHTML = "";
  lines.forEach((row) => {
    const tr = document.createElement("tr");
    const name = row.label ?? row.product_name ?? "—";
    tr.innerHTML = `
          <td><b>${escapeHtml(name)}</b></td>
          <td>${escapeHtml(fmt(row.eoq))}</td>
          <td>${escapeHtml(fmt(row.rop))}</td>
          <td>${escapeHtml(fmt(row.transport_cost))}</td>
          <td>${escapeHtml(fmt(row.total_cost))}</td>`;
    tbody.appendChild(tr);
  });
}

// Load Results on results.html
function loadResults() {
  const raw = localStorage.getItem("optimizationResult");
  const data = raw ? JSON.parse(raw) : null;

  if (!data) {
    renderCostAnalysisChart({});
    const tbody = document.getElementById("resultsTableBody");
    if (tbody) tbody.innerHTML = "";
    return;
  }

  const fmt = (v) => (v === undefined || v === null ? "—" : v);
  const pathLabel = data.best_path ?? data.path ?? "—";

  document.getElementById("eoq").innerText = fmt(data.eoq);
  document.getElementById("rop").innerText = fmt(data.rop);
  document.getElementById("transportCost").innerText = fmt(data.transport_cost);
  document.getElementById("totalCost").innerText = fmt(data.total_cost);
  document.getElementById("path").innerText = pathLabel;

  renderResultsProductTable(data);

  renderCostAnalysisChart(data);
}

// Sidebar highlight
function setActiveSidebarLink() {
  const currentPage = window.location.pathname.split("/").pop();
  const links = document.querySelectorAll(".sidebar-link");

  links.forEach((link) => {
    const href = link.getAttribute("href");
    if (href === currentPage) {
      link.classList.add("active");
    }
  });
}

async function scFetchJson(url, options) {
  const res = await fetch(url, options);
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = new Error(body.error || res.statusText || "Request failed");
    err.body = body;
    err.status = res.status;
    throw err;
  }
  return body;
}

async function fetchJsonArraySafe(url) {
  try {
    const data = await scFetchJson(url);
    return Array.isArray(data) ? data : [];
  } catch {
    return [];
  }
}

function formatDashNumber(n) {
  if (n === undefined || n === null || Number.isNaN(Number(n))) return "—";
  return Number(n).toLocaleString();
}

function formatDashDate(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return String(iso);
  return d.toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

async function initDashboardPage() {
  const setCount = (id, n) => {
    const el = document.getElementById(id);
    if (el) el.textContent = typeof n === "number" ? n.toLocaleString() : "—";
  };

  const [
    suppliers,
    warehouses,
    retailers,
    products,
    routes,
    inventory,
    results,
  ] = await Promise.all([
    fetchJsonArraySafe(`${SC_API_BASE}/suppliers`),
    fetchJsonArraySafe(`${SC_API_BASE}/warehouses`),
    fetchJsonArraySafe(`${SC_API_BASE}/retailers`),
    fetchJsonArraySafe(`${SC_API_BASE}/products`),
    fetchJsonArraySafe(`${SC_API_BASE}/routes`),
    fetchJsonArraySafe(`${SC_API_BASE}/inventory`),
    fetchJsonArraySafe(`${RESULTS_API_BASE}/`),
  ]);

  setCount("dashCountSuppliers", suppliers.length);
  setCount("dashCountWarehouses", warehouses.length);
  setCount("dashCountRetailers", retailers.length);
  setCount("dashCountProducts", products.length);
  setCount("dashCountRoutes", routes.length);
  setCount("dashCountInventory", inventory.length);
  setCount("dashCountResults", results.length);

  const latestEoq = document.getElementById("dashLatestEoq");
  const latestRop = document.getElementById("dashLatestRop");
  const latestTransport = document.getElementById("dashLatestTransport");
  const latestTotal = document.getElementById("dashLatestTotal");
  const latestPath = document.getElementById("dashLatestPath");
  const latestWhen = document.getElementById("dashLatestWhen");
  const latestBox = document.getElementById("dashLatestResult");

  try {
    const res = await fetch(`${RESULTS_API_BASE}/latest`);
    if (!res.ok) {
      if (latestEoq) latestEoq.textContent = "—";
      if (latestRop) latestRop.textContent = "—";
      if (latestTransport) latestTransport.textContent = "—";
      if (latestTotal) latestTotal.textContent = "—";
      if (latestPath) latestPath.textContent = "No saved runs yet";
      if (latestWhen) latestWhen.textContent = "—";
      return;
    }
    const row = await res.json();
    if (latestEoq) latestEoq.textContent = formatDashNumber(row.eoq);
    if (latestRop) latestRop.textContent = formatDashNumber(row.rop);
    if (latestTransport)
      latestTransport.textContent = formatDashNumber(row.transport_cost);
    if (latestTotal) latestTotal.textContent = formatDashNumber(row.total_cost);
    if (latestPath)
      latestPath.textContent = row.best_path != null ? row.best_path : "—";
    const when = row.created_at ?? row.createdAt;
    if (latestWhen) latestWhen.textContent = formatDashDate(when);
  } catch {
    if (latestBox) {
      if (latestPath)
        latestPath.textContent = "Could not load (is the API running?)";
    }
  }
}

function scFormatRouteRow(r) {
  if (r.source != null && r.destination != null) {
    return {
      id: r.route_id,
      src: String(r.source),
      dest: String(r.destination),
      cost: r.cost,
    };
  }
  const st = r.source_type != null ? `${r.source_type}${r.source_id}` : "—";
  const dt =
    r.destination_type != null
      ? `${r.destination_type}${r.destination_id}`
      : "—";
  return {
    id: r.route_id,
    src: st,
    dest: dt,
    cost: r.cost,
  };
}

async function refreshSupplyChainTables() {
  const whSel = document.getElementById("scInvWarehouse");
  const prSel = document.getElementById("scInvProduct");
  if (!whSel || !prSel) return;

  const [products, warehouses, inventory, routes, suppliers, retailers] =
    await Promise.all([
      scFetchJson(`${SC_API_BASE}/products`),
      scFetchJson(`${SC_API_BASE}/warehouses`),
      scFetchJson(`${SC_API_BASE}/inventory`),
      scFetchJson(`${SC_API_BASE}/routes`),
      scFetchJson(`${SC_API_BASE}/suppliers`),
      scFetchJson(`${SC_API_BASE}/retailers`),
    ]);

  const productById = Object.fromEntries(
    products.map((p) => [p.product_id, p]),
  );
  const whById = Object.fromEntries(warehouses.map((w) => [w.warehouse_id, w]));

  const whPrev = whSel.value;
  whSel.innerHTML = '<option value="">Select warehouse</option>';
  warehouses.forEach((w) => {
    const opt = document.createElement("option");
    opt.value = String(w.warehouse_id);
    opt.textContent = `${w.name} (#${w.warehouse_id})`;
    whSel.appendChild(opt);
  });
  if (whPrev && [...whSel.options].some((o) => o.value === whPrev))
    whSel.value = whPrev;

  const prPrev = prSel.value;
  prSel.innerHTML = '<option value="">Select product</option>';
  products.forEach((p) => {
    const opt = document.createElement("option");
    opt.value = String(p.product_id);
    opt.textContent = `${p.name} (#${p.product_id})`;
    prSel.appendChild(opt);
  });
  if (prPrev && [...prSel.options].some((o) => o.value === prPrev))
    prSel.value = prPrev;

  const prodBody = document.getElementById("productsTableBody");
  prodBody.innerHTML = "";
  products.forEach((p) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
          <td>${p.product_id}</td>
          <td>${escapeHtml(p.name)}</td>
          <td>${p.holding_cost}</td>
          <td>${p.ordering_cost}</td>
          <td class="table-actions"><button type="button" class="btn btn-danger btn-sm" data-sc-del-product="${p.product_id}">Delete</button></td>`;
    prodBody.appendChild(tr);
  });
  prodBody.querySelectorAll("[data-sc-del-product]").forEach((btn) => {
    btn.addEventListener("click", () =>
      deleteScProduct(Number(btn.getAttribute("data-sc-del-product"))),
    );
  });

  const invBody = document.getElementById("inventoryTableBody");
  invBody.innerHTML = "";
  inventory.forEach((row) => {
    const locId = row.location_id ?? row.warehouse_id;
    const wh = whById[locId];
    const pr = productById[row.product_id];
    const locLabel = wh
      ? `${escapeHtml(wh.name)} (#${locId})`
      : `Location ${locId}`;
    const prLabel = pr
      ? `${escapeHtml(pr.name)} (#${row.product_id})`
      : `Product ${row.product_id}`;
    const tr = document.createElement("tr");
    tr.innerHTML = `
          <td>${row.inventory_id}</td>
          <td>${locLabel}</td>
          <td>${prLabel}</td>
          <td>${row.demand}</td>
          <td>${row.lead_time}</td>
          <td>${row.ordering_cost}</td>
          <td>${row.holding_cost}</td>
          <td class="table-actions"><button type="button" class="btn btn-danger btn-sm" data-sc-del-inv="${row.inventory_id}">Delete</button></td>`;
    invBody.appendChild(tr);
  });
  invBody.querySelectorAll("[data-sc-del-inv]").forEach((btn) => {
    btn.addEventListener("click", () =>
      deleteScInventory(Number(btn.getAttribute("data-sc-del-inv"))),
    );
  });

  const routeBody = document.getElementById("routesTableBody");
  routeBody.innerHTML = "";
  routes.forEach((r) => {
    const f = scFormatRouteRow(r);
    const tr = document.createElement("tr");
    tr.innerHTML = `
          <td>${f.id != null ? f.id : "—"}</td>
          <td>${escapeHtml(f.src)}</td>
          <td>${escapeHtml(f.dest)}</td>
          <td>${f.cost}</td>
          <td class="table-actions">${f.id != null ? `<button type="button" class="btn btn-danger btn-sm" data-sc-del-route="${f.id}">Delete</button>` : "—"}</td>`;
    routeBody.appendChild(tr);
  });
  routeBody.querySelectorAll("[data-sc-del-route]").forEach((btn) => {
    btn.addEventListener("click", () =>
      deleteScRoute(Number(btn.getAttribute("data-sc-del-route"))),
    );
  });

  const nodesSummary = document.getElementById("scNodesSummary");
  if (nodesSummary) {
    nodesSummary.innerHTML = `
          <strong>${warehouses.length}</strong> warehouse(s),
          <strong>${suppliers.length}</strong> supplier(s),
          <strong>${retailers.length}</strong> retailer(s)`;
  }
}

function escapeHtml(s) {
  const d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

async function initSupplyChainPage() {
  try {
    await refreshSupplyChainTables();
  } catch (e) {
    console.error(e);
    alert(
      e.body?.error ||
        e.message ||
        "Could not load LogiBrain data. Is the API running?",
    );
  }
}

async function submitScWarehouse(event) {
  event.preventDefault();
  const name = document.getElementById("scWhName").value.trim();
  const location = document.getElementById("scWhLoc").value.trim();
  try {
    await scFetchJson(`${SC_API_BASE}/warehouses`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, location }),
    });
    document.getElementById("scWarehouseForm").reset();
    await refreshSupplyChainTables();
  } catch (e) {
    alert(e.body?.error || e.message);
  }
}

async function submitScSupplier(event) {
  event.preventDefault();
  const name = document.getElementById("scSupName").value.trim();
  const lead_time = parseFloat(document.getElementById("scSupLead").value);
  try {
    await scFetchJson(`${SC_API_BASE}/suppliers`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, lead_time }),
    });
    document.getElementById("scSupplierForm").reset();
    await refreshSupplyChainTables();
  } catch (e) {
    alert(e.body?.error || e.message);
  }
}

async function submitScRetailer(event) {
  event.preventDefault();
  const name = document.getElementById("scRetName").value.trim();
  const location = document.getElementById("scRetLoc").value.trim();
  try {
    await scFetchJson(`${SC_API_BASE}/retailers`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, location }),
    });
    document.getElementById("scRetailerForm").reset();
    await refreshSupplyChainTables();
  } catch (e) {
    alert(e.body?.error || e.message);
  }
}

async function submitScProduct(event) {
  event.preventDefault();
  const name = document.getElementById("scProdName").value.trim();
  const holding_cost = parseFloat(
    document.getElementById("scProdHolding").value,
  );
  const ordering_cost = parseFloat(
    document.getElementById("scProdOrdering").value,
  );
  try {
    await scFetchJson(`${SC_API_BASE}/products`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, holding_cost, ordering_cost }),
    });
    document.getElementById("scProductForm").reset();
    await refreshSupplyChainTables();
  } catch (e) {
    alert(e.body?.error || e.message);
  }
}

async function submitScInventory(event) {
  event.preventDefault();
  const warehouse_id = parseInt(
    document.getElementById("scInvWarehouse").value,
    10,
  );
  const product_id = parseInt(
    document.getElementById("scInvProduct").value,
    10,
  );
  const demand = parseFloat(document.getElementById("scInvDemand").value);
  const ordering_cost = parseFloat(
    document.getElementById("scInvOrdering").value,
  );
  const holding_cost = parseFloat(
    document.getElementById("scInvHolding").value,
  );
  const lead_time = parseFloat(document.getElementById("scInvLead").value);
  try {
    await scFetchJson(`${SC_API_BASE}/inventory`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        warehouse_id,
        product_id,
        demand,
        ordering_cost,
        holding_cost,
        lead_time,
      }),
    });
    document.getElementById("scInventoryForm").reset();
    await refreshSupplyChainTables();
  } catch (e) {
    alert(e.body?.error || e.message);
  }
}

async function submitScRoute(event) {
  event.preventDefault();
  const source_type = document.getElementById("scRouteSrcType").value;
  const source_id = parseInt(document.getElementById("scRouteSrcId").value, 10);
  const destination_type = document.getElementById("scRouteDstType").value;
  const destination_id = parseInt(
    document.getElementById("scRouteDstId").value,
    10,
  );
  const cost = parseFloat(document.getElementById("scRouteCost").value);
  try {
    await scFetchJson(`${SC_API_BASE}/routes`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        source_type,
        source_id,
        destination_type,
        destination_id,
        cost,
      }),
    });
    document.getElementById("routeForm").reset();
    await refreshSupplyChainTables();
  } catch (e) {
    alert(e.body?.error || e.message);
  }
}

async function deleteScProduct(productId) {
  if (!confirm("Delete this product?")) return;
  try {
    await scFetchJson(`${SC_API_BASE}/products/${productId}`, {
      method: "DELETE",
    });
    await refreshSupplyChainTables();
  } catch (e) {
    alert(e.body?.error || e.message);
  }
}

async function deleteScInventory(inventoryId) {
  if (!confirm("Delete this inventory row?")) return;
  try {
    await scFetchJson(`${SC_API_BASE}/inventory/${inventoryId}`, {
      method: "DELETE",
    });
    await refreshSupplyChainTables();
  } catch (e) {
    alert(e.body?.error || e.message);
  }
}

async function deleteScRoute(routeId) {
  if (!confirm("Delete this route?")) return;
  try {
    await scFetchJson(`${SC_API_BASE}/routes/${routeId}`, { method: "DELETE" });
    await refreshSupplyChainTables();
  } catch (e) {
    alert(e.body?.error || e.message);
  }
}

document.addEventListener("DOMContentLoaded", function () {
  if (document.querySelector(".sidebar")) {
    setActiveSidebarLink();
  }
  if (
    document.getElementById("productsTableBody") &&
    document.getElementById("scProductForm")
  ) {
    initSupplyChainPage();
  }
  if (document.getElementById("dashCountSuppliers")) {
    initDashboardPage().catch(() => {
      const ids = [
        "dashCountSuppliers",
        "dashCountWarehouses",
        "dashCountRetailers",
        "dashCountProducts",
        "dashCountRoutes",
        "dashCountInventory",
        "dashCountResults",
      ];
      ids.forEach((id) => {
        const el = document.getElementById(id);
        if (el) el.textContent = "—";
      });
      const pathEl = document.getElementById("dashLatestPath");
      if (pathEl) pathEl.textContent = "Could not load (is the API running?)";
    });
  }
});

// Profile data load
window.onload = function () {
  const user = JSON.parse(localStorage.getItem("user"));

  if (user) {
    const nameEl = document.getElementById("profileName");
    const emailEl = document.getElementById("profileEmail");

    if (nameEl && emailEl) {
      nameEl.innerText = user.username || user.name || "";
      emailEl.innerText = user.email || "";
    }
  }
};
