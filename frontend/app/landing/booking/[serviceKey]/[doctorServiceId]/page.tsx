"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { fetchAvailability, reserveSlot, type Slot, type SlotStatus } from "@/lib/api/booking";
import { API_ROUTES } from "@/lib/api/routes";

// ─── Date helpers ─────────────────────────────────────────────────────────────

function getMondayOf(d: Date): Date {
  const date = new Date(d);
  const day = date.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  date.setDate(date.getDate() + diff);
  date.setHours(0, 0, 0, 0);
  return date;
}

function addDays(d: Date, n: number): Date {
  const date = new Date(d);
  date.setDate(date.getDate() + n);
  return date;
}

function toDateParam(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function formatMonthRange(start: Date, end: Date): string {
  const s = start.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  const e = end.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  return `${s} – ${e}`;
}

function formatTime(isoString: string): string {
  return new Date(isoString).toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

function formatDayHeader(d: Date): { weekday: string; date: string } {
  return {
    weekday: d.toLocaleDateString("en-US", { weekday: "short" }),
    date: d.toLocaleDateString("en-US", { day: "numeric", month: "short" }),
  };
}

// ─── Slot button ──────────────────────────────────────────────────────────────

function SlotButton({
  slot,
  selected,
  onClick,
}: {
  slot: Slot;
  selected: boolean;
  onClick: () => void;
}) {
  const unavailable = slot.status === "reserved" || slot.status === "booked";

  if (unavailable) {
    return (
      <div className="flex items-center justify-center rounded-lg border border-[#E2E8F0] bg-[#F8FAFC] px-2 py-2 text-[12px] text-[#CBD5E1] line-through select-none">
        {formatTime(slot.slot_time)}
      </div>
    );
  }

  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-lg border px-2 py-2 text-[12px] font-medium transition-all ${
        selected
          ? "border-dent-deep bg-dent-ink text-white shadow-sm"
          : "border-[#E2E8F0] bg-white text-dent-ink hover:border-dent-sky/50 hover:bg-dent-badge-bg"
      }`}
    >
      {formatTime(slot.slot_time)}
    </button>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function SlotPickerPage() {
  const params = useParams<{ serviceKey: string; doctorServiceId: string }>();
  const searchParams = useSearchParams();
  const router = useRouter();

  const doctorName = searchParams.get("name") ?? "Doctor";
  const { serviceKey, doctorServiceId } = params;

  const [weekStart, setWeekStart] = useState<Date>(() => getMondayOf(new Date()));
  const [slots, setSlots] = useState<Slot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSlot, setSelectedSlot] = useState<string | null>(null);
  const [reserving, setReserving] = useState(false);
  const [reserveError, setReserveError] = useState<string | null>(null);

  const weekEnd = addDays(weekStart, 6);
  const today = getMondayOf(new Date());
  const isPastWeek = weekStart <= today;

  // ── Fetch slots for the current week ─────────────────────────────────────

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    setSelectedSlot(null);

    fetchAvailability(doctorServiceId, toDateParam(weekStart), toDateParam(weekEnd))
      .then((data) => {
        if (!cancelled) {
          setSlots(data);
          setLoading(false);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError("Could not load availability. Please try again.");
          setLoading(false);
        }
      });

    return () => { cancelled = true; };
  }, [doctorServiceId, weekStart]); // eslint-disable-line react-hooks/exhaustive-deps

  // ── WebSocket for real-time slot updates ──────────────────────────────────

  const wsRef = useRef<WebSocket | null>(null);

  const updateSlotStatus = useCallback((slotTime: string, status: SlotStatus) => {
    setSlots((prev) =>
      prev.map((s) => (s.slot_time === slotTime ? { ...s, status } : s))
    );
    // Deselect if the slot the user had chosen just got taken
    if (status !== "available") {
      setSelectedSlot((prev) => (prev === slotTime ? null : prev));
    }
  }, []);

  useEffect(() => {
    const ws = new WebSocket(API_ROUTES.slotWs(doctorServiceId));
    wsRef.current = ws;

    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data as string) as {
          type: string;
          slot_time: string;
          status: SlotStatus;
        };
        if (msg.type === "slot_update") {
          updateSlotStatus(msg.slot_time, msg.status);
        }
      } catch {
        // ignore malformed messages
      }
    };

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [doctorServiceId, updateSlotStatus]);

  // ── Reserve selected slot and navigate to checkout ────────────────────────

  async function handleContinue() {
    if (!selectedSlot) return;
    setReserving(true);
    setReserveError(null);

    try {
      await reserveSlot(doctorServiceId, selectedSlot);
      const query = new URLSearchParams({
        slot: selectedSlot,
        name: doctorName,
      });
      router.push(`/landing/booking/${serviceKey}/${doctorServiceId}/checkout?${query}`);
    } catch (err) {
      const msg = err instanceof Error && err.message === "slot_taken"
        ? "That slot was just taken. Please pick another."
        : "Could not reserve slot. Please try again.";
      setReserveError(msg);
      setReserving(false);
      setSelectedSlot(null);
    }
  }

  // ── Group slots by day ────────────────────────────────────────────────────

  const days = Array.from({ length: 7 }, (_, i) => addDays(weekStart, i));

  const slotsByDay = days.map((day) => {
    const dayStr = toDateParam(day);
    return {
      day,
      slots: slots.filter((s) => s.slot_time.startsWith(dayStr)),
    };
  });

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="w-full max-w-4xl pb-14">
      {/* Back */}
      <Link
        href={`/landing/booking/${serviceKey}`}
        className="mb-8 inline-flex items-center gap-1.5 text-[13px] font-medium text-[#64748B] transition-colors hover:text-dent-ink"
      >
        <svg viewBox="0 0 16 16" fill="none" className="h-3.5 w-3.5" aria-hidden>
          <path d="M12.67 8H3.33M7.33 4L3.33 8l4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        Back to doctors
      </Link>

      {/* Header */}
      <header className="mb-8 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#94A3B8]">
            Choose a time
          </p>
          <h1 className="mt-1 font-display text-2xl font-bold tracking-tight text-dent-ink">
            {doctorName}
          </h1>
        </div>

        {/* Week navigator */}
        <div className="flex items-center gap-2 rounded-xl border border-[#E2E8F0] bg-white px-3 py-2 shadow-sm">
          <button
            type="button"
            onClick={() => setWeekStart((w) => addDays(w, -7))}
            disabled={isPastWeek}
            className="flex h-7 w-7 items-center justify-center rounded-lg text-[#64748B] transition-colors hover:bg-slate-50 hover:text-dent-ink disabled:cursor-not-allowed disabled:opacity-30"
            aria-label="Previous week"
          >
            <svg viewBox="0 0 16 16" fill="none" className="h-4 w-4" aria-hidden>
              <path d="M10 4L6 8l4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
          <span className="min-w-[9rem] text-center text-[13px] font-semibold text-dent-ink">
            {formatMonthRange(weekStart, weekEnd)}
          </span>
          <button
            type="button"
            onClick={() => setWeekStart((w) => addDays(w, 7))}
            className="flex h-7 w-7 items-center justify-center rounded-lg text-[#64748B] transition-colors hover:bg-slate-50 hover:text-dent-ink"
            aria-label="Next week"
          >
            <svg viewBox="0 0 16 16" fill="none" className="h-4 w-4" aria-hidden>
              <path d="M6 4l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>
      </header>

      {/* Slot grid */}
      <div className="rounded-2xl border border-[#E2E8F0] bg-white shadow-sm">
        {loading && (
          <div className="flex min-h-[20rem] items-center justify-center text-sm text-[#94A3B8]">
            Loading availability…
          </div>
        )}

        {error && !loading && (
          <div className="flex min-h-[20rem] items-center justify-center px-6 text-center text-sm text-red-600">
            {error}
          </div>
        )}

        {!loading && !error && (
          <div className="grid grid-cols-7 divide-x divide-[#F1F5F9]">
            {slotsByDay.map(({ day, slots: daySlots }) => {
              const { weekday, date } = formatDayHeader(day);
              const isToday = toDateParam(day) === toDateParam(new Date());

              return (
                <div key={toDateParam(day)} className="flex flex-col">
                  {/* Day header */}
                  <div className={`border-b border-[#F1F5F9] px-1 py-3 text-center ${isToday ? "bg-dent-badge-bg" : ""}`}>
                    <p className={`text-[10px] font-bold uppercase tracking-wider ${isToday ? "text-dent-deep" : "text-[#94A3B8]"}`}>
                      {weekday}
                    </p>
                    <p className={`mt-0.5 text-[12px] font-semibold ${isToday ? "text-dent-deep" : "text-[#475569]"}`}>
                      {date}
                    </p>
                  </div>

                  {/* Slots */}
                  <div className="flex flex-col gap-1.5 p-1.5 sm:p-2">
                    {daySlots.length === 0 ? (
                      <p className="py-4 text-center text-[11px] text-[#CBD5E1]">—</p>
                    ) : (
                      daySlots.map((slot) => (
                        <SlotButton
                          key={slot.slot_time}
                          slot={slot}
                          selected={selectedSlot === slot.slot_time}
                          onClick={() => setSelectedSlot(slot.slot_time)}
                        />
                      ))
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer CTA */}
      <div className="mt-5 flex flex-col items-end gap-2">
        {reserveError && (
          <p className="text-[13px] text-red-600">{reserveError}</p>
        )}
        <button
          type="button"
          onClick={handleContinue}
          disabled={!selectedSlot || reserving}
          className="inline-flex items-center gap-2 rounded-xl bg-dent-ink px-6 py-3 text-[13px] font-semibold text-white transition-colors hover:bg-dent-deep disabled:cursor-not-allowed disabled:opacity-40"
        >
          {reserving ? "Reserving…" : "Continue to payment"}
          {!reserving && (
            <svg viewBox="0 0 16 16" fill="none" className="h-3.5 w-3.5" aria-hidden>
              <path d="M3.33 8h9.34M8.67 4l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          )}
        </button>
        {selectedSlot && !reserving && (
          <p className="text-[11px] text-[#94A3B8]">
            Selected: {new Date(selectedSlot).toLocaleString("en-US", { weekday: "short", month: "short", day: "numeric", hour: "numeric", minute: "2-digit", hour12: true })}
          </p>
        )}
      </div>
    </div>
  );
}
