/**
 * WeatherGPT - Main Application Controller
 */

window.currentCity = "Indore";
window.currentLanguage = "hinglish";
window.currentPersona = "citizen";

document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

async function initApp() {
  setupEventListeners();
  window.chatController.init(updateWeatherDashboard);

  // Initialize Radar Map
  window.radarViewer.init(22.7196, 75.8577);

  // Initial Weather Load for default city (Indore)
  await loadCityWeather(window.currentCity);

  // Check Backend Health
  checkBackendHealth();
}

function setupEventListeners() {
  // City Selector Dropdown
  const citySelect = document.getElementById('citySelector');
  if (citySelect) {
    citySelect.addEventListener('change', (e) => {
      window.currentCity = e.target.value;
      loadCityWeather(window.currentCity);
    });
  }

  // Persona Chips
  const personaChips = document.querySelectorAll('.persona-chip');
  personaChips.forEach(chip => {
    chip.addEventListener('click', () => {
      personaChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      window.currentPersona = chip.dataset.persona;
    });
  });

  // Language Buttons
  const langBtns = document.querySelectorAll('.lang-btn');
  langBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      langBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      window.currentLanguage = btn.dataset.lang;
      window.voiceEngine.setLanguage(window.currentLanguage);
    });
  });

  // Suggestion Chips Click
  const sugBtns = document.querySelectorAll('.sug-chip');
  sugBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const q = btn.dataset.query;
      if (q) window.chatController.sendMessage(q);
    });
  });

  // Voice Mic Button
  const micBtn = document.getElementById('voiceMicBtn');
  if (micBtn) {
    micBtn.addEventListener('click', () => {
      window.voiceEngine.toggleRecording(micBtn, (transcript) => {
        const inputField = document.getElementById('chatInput');
        if (inputField) {
          inputField.value = transcript;
          window.chatController.sendMessage(transcript);
          inputField.value = '';
        }
      });
    });
  }

  // Dashboard Tabs Switcher
  const dashTabs = document.querySelectorAll('.dash-tab');
  const dashPanes = document.querySelectorAll('.dash-content-pane');
  dashTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      dashTabs.forEach(t => t.classList.remove('active'));
      dashPanes.forEach(p => p.classList.remove('active'));

      tab.classList.add('active');
      const targetId = tab.dataset.tab;
      
      if (targetId === 'weather-view') {
        document.getElementById('weatherView').classList.add('active');
      } else if (targetId === 'radar-view') {
        document.getElementById('radarView').classList.add('active');
        window.radarViewer.resize();
      } else if (targetId === 'nwp-view') {
        document.getElementById('nwpView').classList.add('active');
        loadNWPComparison(window.currentCity);
      } else if (targetId === 'climate-view') {
        document.getElementById('climateView').classList.add('active');
        loadClimateTrends(window.currentCity);
      }
    });
  });
}

async function loadCityWeather(city) {
  try {
    const resp = await fetch(`http://localhost:8000/api/weather/forecast?location=${encodeURIComponent(city)}`);
    if (resp.ok) {
      const weather = await resp.json();
      updateWeatherDashboard(weather);
      window.radarViewer.updateLocation(weather.latitude, weather.longitude, weather.location);
    }
  } catch (e) {
    console.warn("Could not fetch city weather from API, backend might be starting:", e);
  }
}

function updateWeatherDashboard(weather) {
  if (!weather) return;

  // City & condition
  document.getElementById('cardLocation').textContent = weather.location;
  document.getElementById('cardCondition').textContent = weather.condition;
  document.getElementById('cardTemp').textContent = Math.round(weather.temperature) + '°';
  document.getElementById('cardApparent').textContent = Math.round(weather.apparent_temperature) + '°C';
  document.getElementById('cardPrecipChance').textContent = weather.precipitation_probability + '%';

  // Metrics
  document.getElementById('metricWind').textContent = `${weather.wind_speed} km/h`;
  document.getElementById('metricHumidity').textContent = `${weather.humidity}%`;
  document.getElementById('metricUV').textContent = `${weather.uv_index}`;
  document.getElementById('metricAQI').textContent = `${weather.air_quality_index || 45} (Good)`;

  // Alert Box in hero card
  const alertBox = document.getElementById('cardAlertBox');
  if (weather.severe_warning && weather.severe_warning.severity !== 'normal') {
    alertBox.style.display = 'block';
    document.getElementById('cardAlertTitle').textContent = weather.severe_warning.headline;
    document.getElementById('cardAlertDesc').textContent = weather.severe_warning.description;

    // Also update top ticker
    const tickerText = document.getElementById('tickerText');
    if (tickerText) {
      tickerText.textContent = `${weather.location}: ${weather.severe_warning.headline} - ${weather.severe_warning.description}`;
    }
  } else {
    alertBox.style.display = 'none';
  }

  // Hourly Strip
  const hourlyContainer = document.getElementById('hourlyStrip');
  if (hourlyContainer && weather.hourly) {
    hourlyContainer.innerHTML = '';
    weather.hourly.slice(0, 12).forEach(item => {
      const el = document.createElement('div');
      el.className = 'hourly-item';
      el.innerHTML = `
        <span class="hourly-time">${item.time}</span>
        <span class="hourly-icon">${item.condition.split(' ')[0] || '🌤️'}</span>
        <span class="hourly-temp">${Math.round(item.temperature)}°C</span>
        <span class="hourly-rain">${item.precipitation_probability}% 💧</span>
      `;
      hourlyContainer.appendChild(el);
    });
  }

  // 7-Day Outlook
  const dailyContainer = document.getElementById('dailyList');
  if (dailyContainer && weather.daily) {
    dailyContainer.innerHTML = '';
    weather.daily.forEach(d => {
      const row = document.createElement('div');
      row.className = 'daily-row';
      row.innerHTML = `
        <span class="daily-day">${d.date}</span>
        <span class="daily-cond">${d.condition}</span>
        <span class="daily-temps">${Math.round(d.max_temp)}°<span class="temp-min">${Math.round(d.min_temp)}°</span></span>
      `;
      dailyContainer.appendChild(row);
    });
  }
}

async function loadNWPComparison(city) {
  try {
    const resp = await fetch(`http://localhost:8000/api/weather/models?location=${encodeURIComponent(city)}`);
    if (resp.ok) {
      const data = await resp.json();
      document.getElementById('nwpConsensusText').textContent = data.consensus_summary;
    }
  } catch (e) {
    console.warn("NWP fetch error:", e);
  }
}

async function loadClimateTrends(city) {
  try {
    const resp = await fetch(`http://localhost:8000/api/climate/history?location=${encodeURIComponent(city)}`);
    if (resp.ok) {
      const data = await resp.json();
      const barsContainer = document.getElementById('climateBars');
      barsContainer.innerHTML = '';

      const maxRain = Math.max(...data.annual_rainfall_mm, 1200);

      data.historical_years.forEach((yr, idx) => {
        const val = data.annual_rainfall_mm[idx];
        const pct = Math.round((val / maxRain) * 100);
        const col = document.createElement('div');
        col.className = 'climate-bar-col';
        col.innerHTML = `
          <span class="climate-bar-val">${val}mm</span>
          <div class="climate-bar-fill" style="height:${pct}%"></div>
          <span class="climate-bar-year">${yr}</span>
        `;
        barsContainer.appendChild(col);
      });

      document.getElementById('climateAnalysisText').textContent = data.summary_analysis;
    }
  } catch (e) {
    console.warn("Climate history error:", e);
  }
}

async function checkBackendHealth() {
  const statusEl = document.getElementById('apiStatus');
  try {
    const resp = await fetch('http://localhost:8000/health');
    if (resp.ok) {
      statusEl.classList.add('online');
      statusEl.querySelector('.status-label').textContent = 'Online';
    } else {
      throw new Error();
    }
  } catch (e) {
    if (statusEl) {
      statusEl.classList.remove('online');
      statusEl.querySelector('.status-dot').style.background = '#f59e0b';
      statusEl.querySelector('.status-label').textContent = 'Connecting...';
    }
  }
}
