import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "../lib/supabase";

export default function Settings() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [staff, setStaff] = useState(null);
  const [hostel, setHostel] = useState(null);
  const [startTime, setStartTime] = useState("20:00");
  const [endTime, setEndTime] = useState("22:00");
  const [message, setMessage] = useState("");

  const loadSettings = useCallback(async () => {
    setLoading(true);

    const { data: authData } = await supabase.auth.getUser();
    if (!authData?.user) {
      navigate("/");
      return;
    }

    const { data: staffData, error: staffError } = await supabase
      .from("staff")
      .select("*, hostels(*)")
      .eq("auth_id", authData.user.id)
      .single();

    if (staffError || !staffData) {
      console.log("STAFF ERROR:", staffError);
      setLoading(false);
      return;
    }

    setStaff(staffData);
    setHostel(staffData.hostels);
    setStartTime(staffData.hostels.checkin_start_time?.slice(0, 5) || "20:00");
    setEndTime(staffData.hostels.checkin_end_time?.slice(0, 5) || "22:00");
    setLoading(false);
  }, [navigate]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadSettings();
  }, [loadSettings]);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage("");

    const { error } = await supabase
      .from("hostels")
      .update({
        checkin_start_time: startTime,
        checkin_end_time: endTime,
      })
      .eq("id", hostel.id);

    if (error) {
      setMessage("Failed to save. Please try again.");
    } else {
      setMessage("Settings saved successfully.");
    }

    setSaving(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <p className="text-slate-400">Loading...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="border-b border-slate-800 px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-bold">Settings</h1>
          <p className="text-slate-500 text-sm">{hostel?.name}</p>
        </div>
        <button
          onClick={() => navigate("/dashboard")}
          className="text-sm text-slate-400 hover:text-white border border-slate-700 rounded-lg px-4 py-2 transition"
        >
          Back to Dashboard
        </button>
      </div>

      <div className="p-6 max-w-md">
        <form
          onSubmit={handleSave}
          className="bg-slate-900 border border-slate-800 rounded-2xl p-6"
        >
          <h2 className="font-bold text-lg mb-1">Check-In Window</h2>
          <p className="text-slate-500 text-sm mb-6">
            Students can only check in during this time window each day.
          </p>

          <div className="space-y-4">
            <div>
              <label className="text-sm text-slate-400 block mb-2">
                Start Time
              </label>
              <input
                type="time"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                required
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="text-sm text-slate-400 block mb-2">
                End Time
              </label>
              <input
                type="time"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                required
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          {message && (
            <p
              className={`text-sm mt-4 ${
                message.includes("Failed") ? "text-red-400" : "text-green-400"
              }`}
            >
              {message}
            </p>
          )}

          <button
            type="submit"
            disabled={saving}
            className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-lg py-3 mt-6 transition disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save Settings"}
          </button>
        </form>
      </div>
    </div>
  );
}
