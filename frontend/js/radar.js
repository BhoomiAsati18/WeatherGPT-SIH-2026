/**
 * WeatherGPT - Interactive Doppler Radar Module (Leaflet + RainViewer API)
 */

class RadarViewer {
  constructor(containerId) {
    this.containerId = containerId;
    this.map = null;
    this.radarLayer = null;
    this.currentLat = 22.7196; // Indore default
    this.currentLon = 75.8577;
  }

  init(lat, lon) {
    if (this.map) return;

    this.currentLat = lat || this.currentLat;
    this.currentLon = lon || this.currentLon;

    const el = document.getElementById(this.containerId);
    if (!el) return;

    // Create Leaflet Map
    this.map = L.map(this.containerId, {
      center: [this.currentLat, this.currentLon],
      zoom: 7,
      zoomControl: true
    });

    // Dark Basemap tile layer
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; CartoDB & OpenStreetMap',
      maxZoom: 19
    }).addTo(this.map);

    // Marker for current city
    this.marker = L.marker([this.currentLat, this.currentLon]).addTo(this.map);
    this.marker.bindPopup("<b>Selected Location</b>").openPopup();

    // Fetch live RainViewer radar timestamps
    this.loadRainViewerTiles();
  }

  updateLocation(lat, lon, cityName) {
    this.currentLat = lat;
    this.currentLon = lon;
    if (this.map) {
      this.map.setView([lat, lon], 7);
      if (this.marker) {
        this.marker.setLatLng([lat, lon]);
        this.marker.bindPopup(`<b>${cityName}</b>`).openPopup();
      }
      this.map.invalidateSize();
    }
  }

  async loadRainViewerTiles() {
    try {
      const resp = await fetch('https://api.rainviewer.com/public/weather-maps.json');
      if (resp.ok) {
        const data = await resp.json();
        const radarFrames = data.radar?.past;
        if (radarFrames && radarFrames.length > 0) {
          const latest = radarFrames[radarFrames.length - 1];
          const tilePath = latest.path;

          if (this.radarLayer) {
            this.map.removeLayer(this.radarLayer);
          }

          // Add radar overlay
          this.radarLayer = L.tileLayer(`https://tilecache.rainviewer.com${tilePath}/256/{z}/{x}/{y}/2/1_1.png`, {
            opacity: 0.65,
            zIndex: 100
          }).addTo(this.map);

          const timeEl = document.getElementById('radarTimestamp');
          if (timeEl) {
            const dt = new Date(latest.time * 1000);
            timeEl.textContent = `Live Radar Scan: ${dt.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`;
          }
        }
      }
    } catch (e) {
      console.warn("RainViewer radar live tile fetch note:", e);
    }
  }

  resize() {
    if (this.map) {
      setTimeout(() => {
        this.map.invalidateSize();
      }, 100);
    }
  }
}

window.radarViewer = new RadarViewer('radarMap');
