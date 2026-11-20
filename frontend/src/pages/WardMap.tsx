import React, { useState, useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { authorizedFetch, fetchComplaints, type ComplaintData } from '../lib/api';

interface WardStats {
  ward: string;
  total: number;
  resolved: number;
  pending: number;
  high_priority: number;
  lat: number | null;
  lng: number | null;
}

// Ward marker icon (blue circle)
function wardIcon(isSelected: boolean) {
  const color = isSelected ? '#2563eb' : '#6366f1';
  const size = isSelected ? 32 : 24;
  return L.divIcon({
    className: '',
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    html: `<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
      <circle cx="${size / 2}" cy="${size / 2}" r="${size / 2 - 2}" fill="${color}" stroke="#fff" stroke-width="2" opacity="0.85"/>
      <text x="${size / 2}" y="${size / 2 + 1}" text-anchor="middle" dominant-baseline="middle" fill="white" font-size="${size * 0.4}" font-weight="bold">W</text>
    </svg>`,
  });
}

// Complaint marker (small colored dot)
const priorityColors: Record<string, string> = {
  critical: '#ef4444',
  high: '#f97316',
  medium: '#eab308',
  low: '#22c55e',
};

function complaintIcon(priority: string) {
  const color = priorityColors[priority] ?? '#6b7280';
  return L.divIcon({
    className: '',
    iconSize: [14, 14],
    iconAnchor: [7, 7],
    html: `<svg width="14" height="14"><circle cx="7" cy="7" r="5" fill="${color}" stroke="#fff" stroke-width="1.5"/></svg>`,
  });
}

function FlyTo({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.flyTo(center, zoom, { duration: 0.8 });
  }, [center, zoom, map]);
  return null;
}

export default function WardMapPage() {
  const [wards, setWards] = useState<WardStats[]>([]);
  const [selectedWard, setSelectedWard] = useState<string | null>(null);
  const [complaints, setComplaints] = useState<ComplaintData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Default center: Whitefield, Bangalore
  const defaultCenter: [number, number] = [12.9716, 77.7500];
  const defaultZoom = 13;

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const [wardData, complaintData] = await Promise.all([
          authorizedFetch<WardStats[]>('/api/v1/complaints/wards'),
          fetchComplaints({ limit: 200 }),
        ]);
        setWards(wardData);
        setComplaints(complaintData);
      } catch (e: any) {
        setError(e.message ?? 'Failed to load ward data');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const selectedWardData = useMemo(() => wards.find((w) => w.ward === selectedWard), [wards, selectedWard]);

  const filteredComplaints = useMemo(() => {
    if (!selectedWard) return [];
    return complaints.filter((c) => c.ward === selectedWard && c.latitude && c.longitude);
  }, [complaints, selectedWard]);

  const mapCenter: [number, number] = useMemo(() => {
    if (selectedWardData?.lat && selectedWardData?.lng) {
      return [selectedWardData.lat, selectedWardData.lng];
    }
    return defaultCenter;
  }, [selectedWardData]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
        <span className="ml-3 text-gray-600">Loading ward data…</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <p className="text-red-700 font-medium">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Explore Ward Map</h1>
        <span className="text-sm text-gray-500">{wards.length} ward{wards.length !== 1 ? 's' : ''} with complaints</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Ward selector sidebar */}
        <div className="lg:col-span-1 space-y-3">
          <h2 className="font-semibold text-gray-700">Select a Ward</h2>
          {wards.length === 0 ? (
            <div className="bg-gray-50 rounded-lg p-4 text-center text-gray-500 text-sm">
              No ward data available yet. Submit complaints with a ward to see data here.
            </div>
          ) : (
            <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
              {wards.map((w) => (
                <button
                  key={w.ward}
                  onClick={() => setSelectedWard(selectedWard === w.ward ? null : w.ward)}
                  className={`w-full text-left px-4 py-3 rounded-lg border transition-all ${
                    selectedWard === w.ward
                      ? 'bg-indigo-50 border-indigo-400 ring-2 ring-indigo-200'
                      : 'bg-white border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <div className="font-medium text-sm text-gray-900">{w.ward}</div>
                  <div className="flex gap-3 mt-1 text-xs text-gray-500">
                    <span>{w.total} total</span>
                    <span className="text-green-600">{w.resolved} resolved</span>
                    <span className="text-amber-600">{w.pending} pending</span>
                  </div>
                </button>
              ))}
            </div>
          )}

          {/* Stats card for selected ward */}
          {selectedWardData && (
            <div className="bg-white border border-indigo-200 rounded-lg p-4 space-y-3">
              <h3 className="font-semibold text-indigo-800">{selectedWardData.ward}</h3>
              <div className="grid grid-cols-2 gap-2">
                <div className="bg-blue-50 rounded p-2 text-center">
                  <div className="text-xl font-bold text-blue-700">{selectedWardData.total}</div>
                  <div className="text-xs text-blue-600">Total</div>
                </div>
                <div className="bg-green-50 rounded p-2 text-center">
                  <div className="text-xl font-bold text-green-700">{selectedWardData.resolved}</div>
                  <div className="text-xs text-green-600">Resolved</div>
                </div>
                <div className="bg-amber-50 rounded p-2 text-center">
                  <div className="text-xl font-bold text-amber-700">{selectedWardData.pending}</div>
                  <div className="text-xs text-amber-600">Pending</div>
                </div>
                <div className="bg-red-50 rounded p-2 text-center">
                  <div className="text-xl font-bold text-red-700">{selectedWardData.high_priority}</div>
                  <div className="text-xs text-red-600">High Priority</div>
                </div>
              </div>
              <div className="text-xs text-gray-500">
                Resolution Rate:{' '}
                <span className="font-semibold">
                  {selectedWardData.total > 0
                    ? Math.round((selectedWardData.resolved / selectedWardData.total) * 100)
                    : 0}
                  %
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Map */}
        <div className="lg:col-span-3 h-[550px] rounded-lg overflow-hidden border border-gray-200 shadow-sm">
          <MapContainer center={defaultCenter} zoom={defaultZoom} className="h-full w-full" scrollWheelZoom>
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {selectedWardData && mapCenter[0] !== defaultCenter[0] && (
              <FlyTo center={mapCenter} zoom={14} />
            )}

            {/* Ward center markers */}
            {wards
              .filter((w) => w.lat && w.lng)
              .map((w) => (
                <Marker
                  key={`ward-${w.ward}`}
                  position={[w.lat!, w.lng!]}
                  icon={wardIcon(selectedWard === w.ward)}
                  eventHandlers={{ click: () => setSelectedWard(w.ward) }}
                >
                  <Popup>
                    <div className="text-sm">
                      <strong>{w.ward}</strong>
                      <br />
                      {w.total} complaints · {w.resolved} resolved
                    </div>
                  </Popup>
                </Marker>
              ))}

            {/* Complaint markers for selected ward */}
            {filteredComplaints.map((c) => (
              <Marker key={c.id} position={[c.latitude!, c.longitude!]} icon={complaintIcon(c.priority)}>
                <Popup>
                  <div className="text-sm max-w-[200px]">
                    <strong>{c.title}</strong>
                    <br />
                    <span className="capitalize">{c.category}</span> ·{' '}
                    <span
                      className={
                        c.priority === 'critical'
                          ? 'text-red-600'
                          : c.priority === 'high'
                          ? 'text-orange-600'
                          : 'text-gray-600'
                      }
                    >
                      {c.priority}
                    </span>
                    <br />
                    Status: <span className="capitalize">{c.status.replace('_', ' ')}</span>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>
      </div>
    </div>
  );
}
