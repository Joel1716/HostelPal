import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "../lib/supabase";

function getToday() {
  return new Date().toISOString().split("T")[0];
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [staff, setStaff] = useState(null);
  const [hostel, setHostel] = useState(null);
  const [students, setStudents] = useState([]);
  const [rooms, setRooms] = useState({});
  const [selectedDate, setSelectedDate] = useState(getToday());

  // Load staff + students (once)
  const loadInitial = useCallback(async () => {
    setLoading(true);

    const { data: authData } = await supabase.auth.getUser();
    if (!authData?.user) {
      navigate("/");
      return;
    }

    const { data: staffData, error: staffError } = await supabase
      .from("staff")
      .select("*, hostels(id, name)")
      .eq("auth_id", authData.user.id)
      .single();

    if (staffError || !staffData) {
      console.log("STAFF ERROR:", staffError);
      setLoading(false);
      return;
    }

    setStaff(staffData);
    setHostel(staffData.hostels);

    const { data: studentsData, error: studentsError } = await supabase
      .from("students")
      .select("*")
      .eq("hostel_id", staffData.hostel_id)
      .order("room_number");

    if (studentsError) {
      console.log("STUDENTS ERROR:", studentsError);
      setLoading(false);
      return;
    }

    setStudents(studentsData || []);
    setLoading(false);

    return staffData.hostel_id;
  }, [navigate]);

  // Load attendance for selected date and merge with students
  const loadAttendance = useCallback(async (hostelId, date, studentList) => {
    if (!hostelId || !studentList.length) {
      setRooms({});
      return;
    }

    const { data: attendance } = await supabase
      .from("attendance_log")
      .select("matric_number")
      .eq("hostel_id", hostelId)
      .gte("timestamp", `${date}T00:00:00`)
      .lte("timestamp", `${date}T23:59:59`);

    const checkedInSet = new Set(
      (attendance || []).map((a) => a.matric_number),
    );

    const grouped = {};
    studentList.forEach((student) => {
      const room = student.room_number;
      if (!grouped[room]) grouped[room] = [];
      grouped[room].push({
        ...student,
        checkedIn: checkedInSet.has(student.matric_number),
      });
    });

    setRooms(grouped);
  }, []);

  // On mount — load staff + students, then attendance for today
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadInitial().then((hostelId) => {
      if (hostelId) {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        loadAttendance(hostelId, selectedDate, []);
      }
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Whenever students load OR date changes, refresh attendance grid
  useEffect(() => {
    if (staff && students.length > 0) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      loadAttendance(staff.hostel_id, selectedDate, students);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [staff, students, selectedDate]);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    navigate("/");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <p className="text-slate-400">Loading...</p>
      </div>
    );
  }

  const roomNumbers = Object.keys(rooms).sort();
  const isToday = selectedDate === getToday();

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <div className="border-b border-slate-800 px-6 py-4 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-lg font-bold">{hostel?.name}</h1>
          <p className="text-slate-500 text-sm">{staff?.name}</p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <label className="text-sm text-slate-400">Date:</label>
            <input
              type="date"
              value={selectedDate}
              max={getToday()}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          <button
            onClick={handleLogout}
            className="text-sm text-slate-400 hover:text-white border border-slate-700 rounded-lg px-4 py-2 transition"
          >
            Logout
          </button>
        </div>
      </div>

      {/* Status banner */}
      <div className="px-6 pt-4">
        <p className="text-sm text-slate-500">
          Showing attendance for{" "}
          <span className="text-slate-300 font-medium">
            {isToday ? "Today" : selectedDate}
          </span>
        </p>
      </div>

      {/* Rooms */}
      <div className="p-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {roomNumbers.length === 0 && (
          <p className="text-slate-500 col-span-full text-center mt-12">
            No students found for this hostel.
          </p>
        )}

        {roomNumbers.map((room) => {
          const studentsInRoom = rooms[room];
          const checkedInCount = studentsInRoom.filter(
            (s) => s.checkedIn,
          ).length;

          return (
            <div
              key={room}
              className="bg-slate-900 border border-slate-800 rounded-2xl p-5"
            >
              <div className="flex items-center justify-between mb-3">
                <h2 className="font-bold text-lg">Room {room}</h2>
                <span className="text-xs text-slate-500">
                  {checkedInCount}/{studentsInRoom.length} checked in
                </span>
              </div>

              <div className="space-y-2">
                {studentsInRoom.map((student) => (
                  <div
                    key={student.id}
                    className="flex items-center justify-between bg-slate-800/50 rounded-lg px-3 py-2"
                  >
                    <div>
                      <p className="text-sm font-medium">{student.name}</p>
                      <p className="text-xs text-slate-500">
                        {student.matric_number}
                      </p>
                    </div>
                    <span
                      className={`w-3 h-3 rounded-full ${
                        student.checkedIn ? "bg-green-500" : "bg-red-500"
                      }`}
                    />
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
