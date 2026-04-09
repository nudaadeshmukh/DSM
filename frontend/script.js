// Mobile Menu Toggle
function toggleMobileMenu() {
  const navMenu = document.querySelector('.nav-menu');
  navMenu.classList.toggle('mobile-open');
}

// Profile Dropdown Toggle
function toggleProfileDropdown(event) {
  event.stopPropagation();
  const dropdown = document.querySelector('.profile-dropdown');
  dropdown.classList.toggle('show');
}

document.addEventListener('click', function(event) {
  const profileCircle = document.querySelector('.profile-circle');
  const dropdown = document.querySelector('.profile-dropdown');

  if (dropdown && !profileCircle.contains(event.target)) {
    dropdown.classList.remove('show');
  }
});

// Form Submit Handler
function handleLogin(event) {
  event.preventDefault();

  const email = document.getElementById("email").value;

  // simple name extraction from email (before @)
  const name = email.split("@")[0];

  const user = {
    name: name,
    email: email
    
  };

  localStorage.setItem("user", JSON.stringify(user));

  window.location.href = "dashboard.html";
  
}

function handleSignup(event) {
  event.preventDefault();
  window.location.href = 'dashboard.html';
}

// Supply Chain Data Management
let products = [];
let inventory = [];
let routes = [];

function addProduct(event) {
  event.preventDefault();

  const name = document.getElementById('productName').value;
  const holdingCost = document.getElementById('holdingCost').value;
  const orderingCost = document.getElementById('orderingCost').value;

  if (name && holdingCost && orderingCost) {
    products.push({ name, holdingCost, orderingCost });
    document.getElementById('productForm').reset();
    displayProducts();
  }
}

function displayProducts() {
  const tbody = document.getElementById('productsTableBody');
  const table = document.getElementById('productsTable');

  if (products.length === 0) {
    table.style.display = 'none';
    return;
  }

  table.style.display = 'table';
  tbody.innerHTML = products.map(product => `
    <tr>
      <td>${product.name}</td>
      <td>$${product.holdingCost}</td>
      <td>$${product.orderingCost}</td>
    </tr>
  `).join('');
}

function addInventory(event) {
  event.preventDefault();

  const demand = document.getElementById('demand').value;
  const leadTime = document.getElementById('leadTime').value;
  const costs = document.getElementById('costs').value;

  if (demand && leadTime && costs) {
    inventory.push({ demand, leadTime, costs });
    document.getElementById('inventoryForm').reset();
    displayInventory();
  }
}

function displayInventory() {
  const tbody = document.getElementById('inventoryTableBody');
  const table = document.getElementById('inventoryTable');

  if (inventory.length === 0) {
    table.style.display = 'none';
    return;
  }

  table.style.display = 'table';
  tbody.innerHTML = inventory.map(item => `
    <tr>
      <td>${item.demand}</td>
      <td>${item.leadTime} days</td>
      <td>$${item.costs}</td>
    </tr>
  `).join('');
}

function addRoute(event) {
  event.preventDefault();

  const source = document.getElementById('source').value;
  const destination = document.getElementById('destination').value;
  const cost = document.getElementById('cost').value;

  if (source && destination && cost) {
    routes.push({ source, destination, cost });
    document.getElementById('routeForm').reset();
    displayRoutes();
  }
}

function displayRoutes() {
  const tbody = document.getElementById('routesTableBody');
  const table = document.getElementById('routesTable');

  if (routes.length === 0) {
    table.style.display = 'none';
    return;
  }

  table.style.display = 'table';
  tbody.innerHTML = routes.map(route => `
    <tr>
      <td>${route.source}</td>
      <td>${route.destination}</td>
      <td>$${route.cost}</td>
    </tr>
  `).join('');
}

// Run Optimization
function runOptimization() {
  const button = document.getElementById('optimizeBtn');
  const icon = document.getElementById('optimizeIcon');
  const text = document.getElementById('optimizeText');
  const statusText = document.getElementById('statusText');
  const progressBar = document.getElementById('progressBar');

  button.disabled = true;
  button.style.opacity = '0.5';
  icon.innerHTML = '<svg class="spinner" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="10" stroke-width="4" stroke-dasharray="60" stroke-dashoffset="15"/></svg>';
  text.textContent = 'Running...';
  statusText.textContent = 'Processing supply chain data...';
  progressBar.style.display = 'block';

  setTimeout(() => {
    window.location.href = 'results.html';
  }, 2000);
}

// Set active sidebar link
function setActiveSidebarLink() {
  const currentPage = window.location.pathname.split('/').pop();
  const links = document.querySelectorAll('.sidebar-link');

  links.forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPage) {
      link.classList.add('active');
    }
  });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
  // Set active sidebar link if on dashboard pages
  if (document.querySelector('.sidebar')) {
    setActiveSidebarLink();
  }

  // Initialize tables as hidden
  const tables = document.querySelectorAll('table[id$="Table"]');
  tables.forEach(table => {
    table.style.display = 'none';
  });
});

window.onload = function () {
  const user = JSON.parse(localStorage.getItem("user"));

  if (user) {
    const nameEl = document.getElementById("profileName");
    const emailEl = document.getElementById("profileEmail");

    if (nameEl && emailEl) {
      nameEl.innerText = user.name;
      emailEl.innerText = user.email;
    }
  }
};