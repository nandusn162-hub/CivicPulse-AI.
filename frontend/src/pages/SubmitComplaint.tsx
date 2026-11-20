import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Upload,
  MapPin,
  AlertCircle,
  Image as ImageIcon,
  Send,
  X,
  Trash2,
} from 'lucide-react';
import { createComplaint, uploadEvidenceFile } from '../lib/api';

const CATEGORIES = [
  { id: 'pothole', label: 'Roads & Potholes', icon: '🛣️' },
  { id: 'garbage', label: 'Waste Management', icon: '🗑️' },
  { id: 'streetlight', label: 'Street Lighting', icon: '💡' },
  { id: 'water_leak', label: 'Water Supply', icon: '💧' },
  { id: 'drainage', label: 'Drainage & Sewage', icon: '🌊' },
  { id: 'road_damage', label: 'Road Damage', icon: '⚠️' },
  { id: 'encroachment', label: 'Encroachment', icon: '🚧' },
  { id: 'noise', label: 'Noise Pollution', icon: '📢' },
  { id: 'other', label: 'Other Issue', icon: '📋' },
];

export default function SubmitComplaintPage() {
  const [category, setCategory] = useState('garbage');
  const [description, setDescription] = useState('');
  const [locationAddress, setLocationAddress] = useState('');
  const [ward, setWard] = useState('Ward 84 - Whitefield');
  const [latitude, setLatitude] = useState(12.9698);
  const [longitude, setLongitude] = useState(77.7499);
  const [severity, setSeverity] = useState<'low' | 'medium' | 'high'>('medium');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [agreedTerms, setAgreedTerms] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const navigate = useNavigate();
  const MAX_DESC = 500;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.size > 5 * 1024 * 1024) {
        setError('File size must be under 5MB.');
        return;
      }
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setError(null);
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      if (file.size > 5 * 1024 * 1024) {
        setError('File size must be under 5MB.');
        return;
      }
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setError(null);
    }
  };

  const handleGetLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setLatitude(pos.coords.latitude);
          setLongitude(pos.coords.longitude);
          setLocationAddress(
            `GPS: ${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)}`
          );
        },
        () => {
          setError('Unable to fetch GPS. Using default coordinates.');
        }
      );
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (description.trim().length < 10) {
      setError('Please provide a detailed description (at least 10 characters).');
      return;
    }

    setLoading(true);

    try {
      const catLabel = CATEGORIES.find((c) => c.id === category)?.label || category;
      const complaint = await createComplaint({
        title: `${catLabel} issue at ${locationAddress || ward}`,
        description,
        category,
        location_address: locationAddress || `${ward}, Bangalore`,
        latitude,
        longitude,
        ward,
      });

      if (selectedFile) {
        try {
          await uploadEvidenceFile(selectedFile);
        } catch (uploadErr) {
          console.warn('Evidence upload notice:', uploadErr);
        }
      }

      navigate(`/complaints/${complaint.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to submit complaint. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Page Header */}
      <div className="flex items-center space-x-3 mb-6">
        <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
          <Send size={18} className="text-blue-600" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-gray-900">Submit a Civic Complaint</h1>
          <p className="text-sm text-gray-500">Report civic issues and help build a better city</p>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm flex items-start gap-2">
          <AlertCircle size={16} className="shrink-0 text-red-600 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
          {/* Row 1: Category + Location */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Issue Category */}
            <div>
              <label className="block text-sm font-semibold text-gray-800 mb-2">
                Issue Category <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 appearance-none cursor-pointer"
                >
                  {CATEGORIES.map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.icon} {cat.label}
                    </option>
                  ))}
                </select>
                <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
                  ▾
                </div>
              </div>
            </div>

            {/* Location */}
            <div>
              <label className="block text-sm font-semibold text-gray-800 mb-2">
                Location <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <MapPin size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  value={locationAddress}
                  onChange={(e) => setLocationAddress(e.target.value)}
                  placeholder="Koramangala, Bengaluru, Karnataka"
                  className="w-full pl-10 pr-20 py-3 border border-gray-300 rounded-lg text-sm font-medium text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <button
                  type="button"
                  onClick={handleGetLocation}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-xs font-semibold text-blue-600 hover:text-blue-700 px-2 py-1 rounded hover:bg-blue-50 transition-colors"
                >
                  📍 GPS
                </button>
              </div>
            </div>
          </div>

          {/* Row 2: Description + Map Preview */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Description */}
            <div>
              <label className="block text-sm font-semibold text-gray-800 mb-2">
                Description <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <textarea
                  value={description}
                  onChange={(e) => {
                    if (e.target.value.length <= MAX_DESC) setDescription(e.target.value);
                  }}
                  rows={5}
                  placeholder="Describe the issue in detail..."
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                />
                <div className="absolute bottom-2 right-3 text-xs text-gray-400">
                  {description.length}/{MAX_DESC}
                </div>
              </div>
            </div>

            {/* Map Preview */}
            <div>
              <div className="h-full min-h-[160px] rounded-lg overflow-hidden border border-gray-200 bg-gray-100 relative">
                <iframe
                  title="Location Preview"
                  src={`https://www.openstreetmap.org/export/embed.html?bbox=${longitude - 0.01}%2C${latitude - 0.005}%2C${longitude + 0.01}%2C${latitude + 0.005}&layer=mapnik&marker=${latitude}%2C${longitude}`}
                  className="w-full h-full min-h-[160px]"
                  style={{ border: 0 }}
                />
              </div>
            </div>
          </div>

          {/* Row 3: Upload Image + Severity */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Upload Image */}
            <div>
              <label className="block text-sm font-semibold text-gray-800 mb-2">
                Upload Image (Optional)
              </label>
              <div
                className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 hover:bg-blue-50/30 transition-all cursor-pointer relative"
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <ImageIcon size={28} className="mx-auto text-gray-400 mb-2" />
                <div className="text-sm text-gray-600">
                  <span className="font-semibold text-gray-800">Click to upload</span> or drag and
                  drop
                </div>
                <div className="text-xs text-gray-400 mt-1">Supports: JPG, PNG (Max 5MB)</div>
              </div>

              {/* Preview thumbnail */}
              {previewUrl && (
                <div className="mt-3 relative inline-block">
                  <img
                    src={previewUrl}
                    alt="Preview"
                    className="w-24 h-24 object-cover rounded-lg border border-gray-200 shadow-sm"
                  />
                  <button
                    type="button"
                    onClick={removeFile}
                    className="absolute -top-2 -right-2 w-5 h-5 bg-gray-800 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition-colors"
                  >
                    <X size={12} />
                  </button>
                </div>
              )}
            </div>

            {/* Severity Level */}
            <div>
              <label className="block text-sm font-semibold text-gray-800 mb-2">
                Severity Level
              </label>
              <div className="flex gap-3">
                {(['low', 'medium', 'high'] as const).map((level) => {
                  const colors = {
                    low: { bg: 'bg-green-50', border: 'border-green-400', text: 'text-green-700', dot: 'bg-green-500', activeBg: 'bg-green-100' },
                    medium: { bg: 'bg-yellow-50', border: 'border-yellow-400', text: 'text-yellow-700', dot: 'bg-yellow-500', activeBg: 'bg-yellow-100' },
                    high: { bg: 'bg-red-50', border: 'border-red-400', text: 'text-red-700', dot: 'bg-red-500', activeBg: 'bg-red-100' },
                  };
                  const c = colors[level];
                  const isActive = severity === level;
                  return (
                    <button
                      key={level}
                      type="button"
                      onClick={() => setSeverity(level)}
                      className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg border-2 font-semibold text-sm transition-all ${
                        isActive
                          ? `${c.activeBg} ${c.border} ${c.text} ring-1 ring-offset-1`
                          : 'bg-white border-gray-200 text-gray-500 hover:border-gray-300'
                      }`}
                    >
                      <span className={`w-2.5 h-2.5 rounded-full ${isActive ? c.dot : 'bg-gray-300'}`} />
                      <span className="capitalize">{level}</span>
                    </button>
                  );
                })}
              </div>

              {/* Ward selector */}
              <div className="mt-4">
                <label className="block text-sm font-semibold text-gray-800 mb-2">
                  Municipal Ward
                </label>
                <select
                  value={ward}
                  onChange={(e) => setWard(e.target.value)}
                  className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none cursor-pointer"
                >
                  <option value="Ward 84 - Whitefield">Ward 84 - Whitefield</option>
                  <option value="Ward 85 - Kadugodi">Ward 85 - Kadugodi</option>
                  <option value="Ward 82 - Garudacharpalya">Ward 82 - Garudacharpalya</option>
                  <option value="Ward 113 - Bellandur">Ward 113 - Bellandur</option>
                  <option value="Ward 150 - HSR Layout">Ward 150 - HSR Layout</option>
                  <option value="Whitefield Ward 1">Whitefield Ward 1</option>
                  <option value="Whitefield Ward 2">Whitefield Ward 2</option>
                </select>
              </div>

              {/* Terms */}
              <div className="mt-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={agreedTerms}
                    onChange={(e) => setAgreedTerms(e.target.checked)}
                    className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-600">
                    I agree to the{' '}
                    <span className="text-blue-600 font-medium hover:underline cursor-pointer">
                      terms and conditions
                    </span>
                  </span>
                </label>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || !agreedTerms || description.length < 10}
            className="w-full py-3.5 px-4 bg-[#1a2744] hover:bg-[#243557] text-white font-bold rounded-lg text-sm shadow-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Submitting...
              </span>
            ) : (
              <>
                <Send size={16} />
                <span>Submit Complaint</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
