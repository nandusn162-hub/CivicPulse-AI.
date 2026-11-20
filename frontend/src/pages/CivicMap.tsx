import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { Filter, Layers, AlertCircle, Eye, ChevronRight } from 'lucide-react';
import { fetchComplaints, ComplaintData } from '../lib/api';

// Create custom colored markers for Leaflet without missing asset 404s
const createCustomIcon = (priority: string) => {
  let color = '#3b82f6'; // blue
  if (priority === 'critical') color = '#e11d48'; // red
  else if (priority === 'high') color = '#f59e0b'; // amber
  else if (priority === 'medium') color = '#0284c7'; // sky

  const svgHtml = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="30" height="30" fill="${color}">
      <path d="M12 0c-4.418 0-8 3.582-8 8 0 5.25 7.05 15.25 7.35 15.67a1 1 0 0 0 1.3 0c.3-.42 7.35-10.42 7.35-15.67 0-4.418-3.582-8-8-8zm0 11a3 3 0 1 1 0-6 3 3 0 0 1 0 6z"/>
    </svg>
  `;

  return L.divIcon({
    html: svgHtml,
    className: 'custom-leaflet-pin',
    iconSize: [30, 30],
    iconAnchor: [15, 30],
    popupAnchor: [0, -28],
  });
};

export default function CivicMapPage() {
  const [complaints, setComplaints] = useState<ComplaintData[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedPriority, setSelectedPriority] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMapComplaints();
  }, []);

  const loadMapComplaints = async () => {
    setLoading(true);
    try {
      const data = await fetchComplaints({ limit: 100 });
      setComplaints(data);
    } catch (err) {
      console.error('Failed to load map data', err);
    } finally {
      setLoading(false);
    }
  };

  const filtered = complaints.filter((c) => {
    if (selectedCategory !== 'all' && c.category !== selectedCategory) return false;
    if (selectedPriority !== 'all' && c.priority !== selectedPriority) return false;
    if (selectedStatus !== 'all' && c.status !== selectedStatus) return false;
    return true;
  });

  return (
    <div className="space-y-4">
      {/* Header & Filter Controls */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Interactive Civic Map</h1>
          <p className="text-xs text-slate-500">
            Real-time geospatial distribution of citizen reports across municipal wards.
          </p>
        </div>

        {/* Filter controls */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-1.5 bg-slate-50 border border-slate-200 px-2.5 py-1.5 rounded-xl text-xs">
            <span className="text-slate-400 font-medium">Category:</span>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="bg-transparent font-semibold text-slate-800 focus:outline-none"
            >
              <option value="all">All</option>
              <option value="pothole">Potholes</option>
              <option value="garbage">Garbage</option>
              <option value="water_leak">Water Leaks</option>
              <option value="streetlight">Lighting</option>
              <option value="drainage">Drainage</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5 bg-slate-50 border border-slate-200 px-2.5 py-1.5 rounded-xl text-xs">
            <span className="text-slate-400 font-medium">Priority:</span>
            <select
              value={selectedPriority}
              onChange={(e) => setSelectedPriority(e.target.value)}
              className="bg-transparent font-semibold text-slate-800 focus:outline-none"
            >
              <option value="all">All</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5 bg-slate-50 border border-slate-200 px-2.5 py-1.5 rounded-xl text-xs">
            <span className="text-slate-400 font-medium">Status:</span>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="bg-transparent font-semibold text-slate-800 focus:outline-none"
            >
              <option value="all">All</option>
              <option value="submitted">Submitted</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>
        </div>
      </div>

      {/* Map Container */}
      <div className="bg-white p-2 rounded-2xl border border-slate-200/80 shadow-xs h-[650px] relative overflow-hidden">
        {loading ? (
          <div className="h-full flex items-center justify-center text-slate-400 text-sm">
            <div className="w-8 h-8 border-3 border-teal-500 border-t-transparent rounded-full animate-spin mr-3"></div>
            Loading map coordinates...
          </div>
        ) : (
          <MapContainer
            center={[12.9698, 77.7499]} // Bengaluru / Whitefield center
            zoom={13}
            scrollWheelZoom={true}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {filtered.map((c) => {
              // Default coordinates with slight offset if missing
              const lat = c.latitude || 12.9698 + (Math.random() - 0.5) * 0.05;
              const lng = c.longitude || 77.7499 + (Math.random() - 0.5) * 0.05;

              return (
                <Marker key={c.id} position={[lat, lng]} icon={createCustomIcon(c.priority)}>
                  <Popup>
                    <div className="p-1 space-y-1.5 min-w-[200px]">
                      <div className="flex items-center justify-between text-[11px]">
                        <span className="font-bold uppercase text-slate-500">{c.category.replace('_', ' ')}</span>
                        <span className="px-1.5 py-0.2 rounded text-[10px] font-bold capitalize bg-slate-100">
                          {c.priority}
                        </span>
                      </div>
                      <h4 className="font-bold text-slate-900 text-xs">{c.title}</h4>
                      <p className="text-[11px] text-slate-500 line-clamp-2">{c.description}</p>
                      <div className="pt-1.5 border-t border-slate-100 flex items-center justify-between">
                        <span className="text-[10px] text-slate-400 capitalize">{c.status.replace('_', ' ')}</span>
                        <Link
                          to={`/complaints/${c.id}`}
                          className="text-[11px] font-bold text-teal-600 hover:text-teal-700 flex items-center gap-0.5"
                        >
                          <span>Diagnostics</span>
                          <ChevronRight size={12} />
                        </Link>
                      </div>
                    </div>
                  </Popup>
                </Marker>
              );
            })}
          </MapContainer>
        )}

        {/* Floating Map Legend */}
        <div className="absolute bottom-5 right-5 z-[400] bg-white/95 backdrop-blur-md px-3.5 py-2.5 rounded-xl border border-slate-200 shadow-md text-xs space-y-1.5">
          <div className="font-bold text-slate-700 text-[11px] uppercase tracking-wider mb-1">
            Priority Indicators
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-600"></span>
            <span className="text-slate-600">Critical Priority</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
            <span className="text-slate-600">High Priority</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-sky-500"></span>
            <span className="text-slate-600">Medium / Normal</span>
          </div>
        </div>
      </div>
    </div>
  );
}
