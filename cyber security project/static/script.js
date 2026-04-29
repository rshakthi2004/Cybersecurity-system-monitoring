function goTo(path) {
  window.location.href = path;
}
 
async function login() {
  let emailInput = document.getElementById("email");
  let passwordInput = document.getElementById("password");
  let messageBox = document.getElementById("loginMessage");
 
  let email = emailInput.value;
  let password = passwordInput.value;
 
  try {
    let response = await fetch("http://127.0.0.1:5000/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ email, password })
    });
 
    let data = await response.json();
 
   
    if (response.ok) {
      messageBox.innerHTML = "✔ Login Successful";
      messageBox.className = "message-box success";
 
      setTimeout(() => {
        window.location.href = "/login-success";
      }, 2000);
    }
 
    else {
 
      if (response.status === 404) {
        messageBox.innerHTML = "User does not exist...";
        messageBox.className = "message-box error";
 
        setTimeout(() => {
          window.location.href = "/user-not-found";
        }, 1500);
      }
 
     
      else if (response.status === 401) {
        messageBox.innerHTML = "Invalid password!";
        messageBox.className = "message-box error";
 
        setTimeout(() => {
          window.location.href = "/access-denied";
        }, 1500);
      }
 
      emailInput.value = "";
      passwordInput.value = "";
    }
 
  } catch (error) {
    messageBox.innerHTML = "Server error. Try again.";
    messageBox.className = "message-box error";
  }
}
// ================= SIGNUP =================
async function register() {
  let email = document.getElementById("email").value;
  let password = document.getElementById("password").value;
  let messageBox = document.getElementById("messageBox");
 
 
  if (!email || !password) {
    messageBox.innerHTML = "[SYSTEM] All fields required...";
    messageBox.className = "message-box error";
    return;
  }
 
 
  let errors = [];
 
  if (password.length < 8) {
    errors.push("→ Minimum 8 characters required");
  }
  if (!/[A-Z]/.test(password)) {
    errors.push("→ Missing uppercase letter (A-Z)");
  }
  if (!/[a-z]/.test(password)) {
    errors.push("→ Missing lowercase letter (a-z)");
  }
  if (!/[\W_]/.test(password)) {
    errors.push("→ Missing special character (!@#$...)");
  }
 
  if (errors.length > 0) {
    messageBox.innerHTML = `
      ⚠ SYSTEM SECURITY ALERT<br><br>
      [CREDENTIAL POLICY VIOLATION]<br><br>
      ${errors.join("<br>")}<br><br>
      [ACTION REQUIRED] Update password to meet security standards.
    `;
    messageBox.className = "message-box error";
    return;
  }
 
 
  try {
    let response = await fetch("http://127.0.0.1:5000/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ email, password })
    });
 
    let data = await response.json();
 
   
    if (response.ok) {
   messageBox.innerHTML = "✔ Account created successfully!";
  messageBox.className = "message-box success";
 
     setTimeout(() => {
    window.location.href = "/signup-success";
  }, 1500);
  }
   
 
   
    else {
      messageBox.innerHTML = data.message;
      messageBox.className = "message-box error";
    }
 
  } catch (error) {
    messageBox.innerHTML = "[SYSTEM ERROR] Server not responding...";
    messageBox.className = "message-box error";
    console.error(error);
  }
}
 
 
// ================= FORGOT PASSWORD =================
async function resetPassword() {
  let email = document.getElementById("email").value;
 
  if (!email) {
    alert("Enter email");
    return;
  }
 
  try {
    let response = await fetch("http://127.0.0.1:5000/check-user", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ email })
    });
 
    let data = await response.json();
 
    if (response.ok) {
      alert("User exists! Implement reset logic.");
    } else {
      alert("User not found! Redirecting to signup...");
      window.location.href = "/signup";
    }
 
  } catch (error) {
    alert("Server error");
    console.error(error);
  }
}
// ---------------- DASHBOARD ---------------- //
 
let cpuData = [];
let memoryData = [];
let chart;
let allProcesses = [];
 
 
let timeIndex = 0;
 
function loadDashboard() {
  const chartElement = document.getElementById("chart");
 
  if (!chartElement) return;
 
  const ctx = chartElement.getContext("2d");
 
  chart = new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "CPU %",
          borderColor: "red",
          data: [],
          fill: false,
          tension: 0.4
        },
        {
          label: "Memory %",
          borderColor: "blue",
          data: [],
          fill: false,
          tension: 0.4
        }
      ]
    },
    options: {
      responsive: true,
      animation: {
        duration: 800,
        easing: "easeInOutQuad"
      },
      interaction: {
        mode: "index",
        intersect: false
      },
      plugins: {
        legend: {
          display: true
        },
        zoom: {
          pan: {
            enabled: true,
            mode: "x"
          },
          zoom: {
            wheel: {
              enabled: true
            },
            pinch: {
              enabled: true
            },
            mode: "x"
          }
        }
      },
      scales: {
        y: {
          min: 0,
          max: 100
        }
      }
    }
  });
 
  loadHistory();
 
  fetchData();
  setInterval(fetchData, 2000);
}
 
// ---------------- FETCH LIVE DATA ---------------- //
 
function fetchData() {
  fetch("/api/data")
    .then(res => {
      if (!res.ok) throw new Error("Server error");
      return res.json();
    })
    .then(data => {
 
      if (data.error) {
        showError(data.error);
        return;
      }
 
      let cpu = data.system_data.cpu;
      let mem = data.system_data.memory;
 
      document.getElementById("cpu").innerText = cpu + "%";
      document.getElementById("memory").innerText = mem + "%";
 
      cpuData.push(cpu);
      memoryData.push(mem);
 
   
      let now = new Date();
      let timeLabel = now.toLocaleTimeString([], { hour12: false });
 
      chart.data.labels.push(timeLabel);
 
     
      if (cpuData.length > 20) {
        cpuData.shift();
        memoryData.shift();
        chart.data.labels.shift();
      }
 
      chart.data.datasets[0].data = [...cpuData];
      chart.data.datasets[1].data = [...memoryData];
 
      chart.update();
 
      // Alerts
      let alertList = document.getElementById("alerts");
      if (alertList) {
        alertList.innerHTML = "";
        data.alerts.forEach(a => {
          let li = document.createElement("li");
          li.textContent = a;
          li.style.color = "red";
          alertList.appendChild(li);
        });
      }
 
      // Processes
      let procList = document.getElementById("processes");
 
      if (procList) {
        allProcesses = data.system_data.processes;
 
        let searchBox = document.getElementById("searchProcess");
        let search = searchBox ? searchBox.value.toLowerCase() : "";
 
        let filtered = search === ""
          ? allProcesses
          : allProcesses.filter(p => {
              let name = (typeof p === "object" ? p.name : p) || "";
              return name.toLowerCase().includes(search);
            });
 
        procList.innerHTML = "";
 
        filtered.forEach(p => {
          let li = document.createElement("li");
 
          if (typeof p === "object") {
            li.textContent = `${p.name || "Unknown"} - ${p.cpu || 0}%`;
          } else {
            li.textContent = p;
          }
 
          procList.appendChild(li);
        });
      }
 
    })
    .catch(err => {
      console.error(err);
      showError("Backend not reachable");
 
      document.getElementById("cpu").innerText = "Error";
      document.getElementById("memory").innerText = "Error";
    });
}
// ---------------- SEARCH FUNCTION ---------------- //
 
function filterProcesses() {
  let search = document
    .getElementById("searchProcess")
    .value
    .toLowerCase()
    .trim();
 
  let procList = document.getElementById("processes");
  if (!procList) return;
 
  let filtered;
 
  if (search === "") {
    filtered = allProcesses; // show all
  } else {
    filtered = allProcesses.filter(p => {
      let name = (typeof p === "object" ? p.name : p) || "";
      return name.toLowerCase() === search;  
    });
  }
 
  procList.innerHTML = "";
 
  filtered.forEach(p => {
    let li = document.createElement("li");
 
    if (typeof p === "object") {
      li.textContent = `${p.name || "Unknown"} - ${p.cpu || 0}%`;
    } else {
      li.textContent = p;
    }
 
    procList.appendChild(li);
  });
}
 
// ---------------- LOAD DB HISTORY ---------------- //
 
function loadHistory() {
  fetch("/api/history")
    .then(res => res.json())
    .then(data => {
      chart.data.labels = data.map(d => d.time);
      chart.data.datasets[0].data = data.map(d => d.cpu);
      chart.data.datasets[1].data = data.map(d => d.memory);
      chart.update();
    });
}
 
// ---------------- PORT SCAN ---------------- //
 
function scanPorts() {
  fetch("/api/scan")
    .then(res => res.json())
    .then(data => {
      let portList = document.getElementById("ports");
 
      if (!portList) return;
 
      portList.innerHTML = "";
 
      data.open_ports.forEach(p => {
        let li = document.createElement("li");
        li.textContent = "Port " + p + " OPEN";
        portList.appendChild(li);
      });
    })
    .catch(() => {
      showError("Port scan failed");
    });
}
 
// ---------------- ERROR HANDLER ---------------- //
 
function showError(message) {
  let alertBox = document.getElementById("alerts");
 
  if (alertBox) {
    alertBox.innerHTML =
      `<li style="color:red;">${message}</li>`;
  }
}
 
 const API_KEY = "4189d6c66a0e45f7aa8e64712da79d3e";
 
const NEWS_URL =
  `https://newsapi.org/v2/everything?q=cybersecurity OR hacking OR malware OR ransomware&sortBy=publishedAt&apiKey=${API_KEY}`;
 
async function loadNews() {
  try {
    const res = await fetch(NEWS_URL);
    const data = await res.json();
 
    const container = document.getElementById("news-container");
    container.innerHTML = "";
 
    data.articles.slice(0, 12).forEach(article => {
      const div = document.createElement("div");
      div.className = "news-item";
 
      div.innerHTML = `
        <strong>🛡️ ${article.title}</strong>
        <small>${new Date(article.publishedAt).toLocaleTimeString()}</small>
      `;
 
      div.onclick = () => window.open(article.url, "_blank");
 
      container.appendChild(div);
    });
 
  } catch (err) {
    console.log("News error:", err);
  }
}
 
loadNews();
setInterval(loadNews, 60000);
 
function goToGeo() {
    window.location.href = "/geo-map";
}
 
 
// protocol
  let protocolChart;
 
// Initial dummy data
let protocolData = {
    TCP: 10,
    UDP: 5,
    ICMP: 2,
    HTTP: 8,
    HTTPS: 12
};
 
function createChart() {
    const ctx = document.getElementById('protocolChart').getContext('2d');
 
    protocolChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['TCP', 'UDP', 'ICMP', 'HTTP', 'HTTPS'],
            datasets: [{
                data: Object.values(protocolData),
                backgroundColor: [
                    '#00ffcc',
                    '#ffcc00',
                    '#ff4444',
                    '#3399ff',
                    '#9933ff'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: {
                        color: '#ffffff'
                    }
                }
            }
        }
    });
}
function updateChart(newData) {
    protocolData = newData;
 
    protocolChart.data.datasets[0].data = Object.values(protocolData);
    protocolChart.update();
}
async function fetchProtocolData() {
    const res = await fetch('/protocol-stats');
    const data = await res.json();
 
    updateChart(data);
}
createChart();
fetchProtocolData();
 
// Refresh every 2 seconds
setInterval(fetchProtocolData, 2000);
 
 
function goToProtocol() {
    window.location.href = "/protocol";
}
function goToIP() {
    window.location.href = "/ip";
}
 
// ---------------- AUTO LOAD ---------------- //
window.onload = loadDashboard;
 