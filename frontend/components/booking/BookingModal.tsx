"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { fetchAvailability, reserveSlot, type Slot, type SlotStatus } from "@/lib/api/booking";
import { API_ROUTES } from "@/lib/api/routes";
import type { DoctorForService } from "@/lib/api/booking";

const MAX_DAYS_AHEAD = 60;

// ─── Helpers ──────────────────────────────────────────────────────────────────

function startOfToday(): Date {
  const d = new Date();
  d.setHours(0, 0, 0, 0);
  return d;
}

function addDays(d: Date, n: number): Date {
  const r = new Date(d);
  r.setDate(r.getDate() + n);
  return r;
}

function toDateStr(d: Date): string {
  return [
    d.getFullYear(),
    String(d.getMonth() + 1).padStart(2, "0"),
    String(d.getDate()).padStart(2, "0"),
  ].join("-");
}

function getDaysInMonth(year: number, month: number): number {
  return new Date(year, month + 1, 0).getDate();
}

function mondayFirstOffset(year: number, month: number): number {
  const day = new Date(year, month, 1).getDay(); // 0=Sun
  return day === 0 ? 6 : day - 1;
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

function formatPrice(amount: number, currency: string): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: currency.toUpperCase(),
    minimumFractionDigits: 0,
  }).format(amount / 100);
}

function getMonthOptions(): { label: string; year: number; month: number }[] {
  const base = new Date();
  return Array.from({ length: 3 }, (_, i) => {
    const d = new Date(base.getFullYear(), base.getMonth() + i, 1);
    return {
      label: d.toLocaleDateString("en-US", { month: "long", year: "numeric" }),
      year: d.getFullYear(),
      month: d.getMonth(),
    };
  });
}

const WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

// ─── Types ────────────────────────────────────────────────────────────────────

type ReservationInfo = {
  slot: string;
  reservationId: string;
  expiresAt: string;
};

type BookingModalProps = {
  doctor: DoctorForService;
  serviceKey: string;
  serviceLabel: string;
  onClose: () => void;
  onReserved: (info: ReservationInfo) => void;
};

// ─── Component ────────────────────────────────────────────────────────────────

export function BookingModal({ doctor, serviceLabel, onClose, onReserved }: BookingModalProps) {
  const today = startOfToday();
  const maxDate = addDays(today, MAX_DAYS_AHEAD);
  const monthOptions = getMonthOptions();

  const [viewMonthIdx, setViewMonthIdx] = useState(0);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [slots, setSlots] = useState<Slot[]>([]);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState<string | null>(null);
  const [reserving, setReserving] = useState(false);
  const [reserveError, setReserveError] = useState<string | null>(null);
  const reservingRef = useRef(false);

  const { year, month } = monthOptions[viewMonthIdx];

  // ── Calendar grid ──────────────────────────────────────────────────────────

  const calendarDays: (number | null)[] = [];
  const offset = mondayFirstOffset(year, month);
  for (let i = 0; i < offset; i++) calendarDays.push(null);
  for (let d = 1; d <= getDaysInMonth(year, month); d++) calendarDays.push(d);
  const tail = (7 - (calendarDays.length % 7)) % 7;
  for (let i = 0; i < tail; i++) calendarDays.push(null);

  function isDaySelectable(day: number) {
    const d = new Date(year, month, day);
    d.setHours(0, 0, 0, 0);
    return d >= today && d <= maxDate;
  }

  function isDaySelected(day: number) {
    return (
      !!selectedDate &&
      selectedDate.getFullYear() === year &&
      selectedDate.getMonth() === month &&
      selectedDate.getDate() === day
    );
  }

  function isToday(day: number) {
    return (
      today.getFullYear() === year &&
      today.getMonth() === month &&
      today.getDate() === day
    );
  }

  // ── Fetch slots (shared logic) ─────────────────────────────────────────────

  const refreshSlots = useCallback(
    (date: Date, preserveSelected: boolean) => {
      const dateStr = toDateStr(date);
      fetchAvailability(doctor.doctor_service_id, dateStr, dateStr)
        .then((data) => {
          setSlots(data);
          if (!preserveSelected) {
            setSelectedSlot(null);
          } else {
            // Clear selected slot only if it's no longer available
            setSelectedSlot((prev) => {
              if (!prev) return null;
              const prevMs = new Date(prev).getTime();
              const stillAvailable = data.some(
                (s) =>
                  new Date(s.slot_time).getTime() === prevMs &&
                  s.status === "available"
              );
              return stillAvailable ? prev : null;
            });
          }
        })
        .catch(() => {});
    },
    [doctor.doctor_service_id, setSelectedSlot]
  );

  // ── Fetch slots when date changes ──────────────────────────────────────────

  useEffect(() => {
    if (!selectedDate) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoadingSlots(true);
    setSlots([]);
    setSelectedSlot(null);

    const dateStr = toDateStr(selectedDate);
    let cancelled = false;
    fetchAvailability(doctor.doctor_service_id, dateStr, dateStr)
      .then((data) => {
        if (!cancelled) {
          setSlots(data);
          setLoadingSlots(false);
        }
      })
      .catch(() => {
        if (!cancelled) setLoadingSlots(false);
      });

    return () => {
      cancelled = true;
    };
  }, [selectedDate, doctor.doctor_service_id]);

  // ── Periodic re-fetch + re-fetch on tab focus ──────────────────────────────
  // TTL expiries (soft-lock 5 min, pending-payment 15 min) are passive —
  // no WS broadcast fires when they expire. Polling keeps both browsers in sync.

  useEffect(() => {
    if (!selectedDate) return;

    const interval = setInterval(() => refreshSlots(selectedDate, true), 60_000);

    const handleFocus = () => refreshSlots(selectedDate, true);
    window.addEventListener("focus", handleFocus);

    return () => {
      clearInterval(interval);
      window.removeEventListener("focus", handleFocus);
    };
  }, [selectedDate, refreshSlots]);

  // ── WebSocket ──────────────────────────────────────────────────────────────

  const updateSlotStatus = useCallback((slotTime: string, status: SlotStatus) => {  // eslint-disable-line react-hooks/preserve-manual-memoization
    const tsMs = new Date(slotTime).getTime();
    setSlots((prev) =>
      prev.map((s) =>
        new Date(s.slot_time).getTime() === tsMs ? { ...s, status } : s
      )
    );
    if (status !== "available" && !reservingRef.current) {
      setSelectedSlot((prev) =>
        prev && new Date(prev).getTime() === tsMs ? null : prev
      );
    }
  }, []);

  useEffect(() => {
    const ws = new WebSocket(API_ROUTES.slotWs(doctor.doctor_service_id));
    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data as string) as {
          type: string;
          slot_time: string;
          status: SlotStatus;
        };
        if (msg.type === "slot_update") updateSlotStatus(msg.slot_time, msg.status);
      } catch {
        // ignore malformed frames
      }
    };
    return () => ws.close();
  }, [doctor.doctor_service_id, updateSlotStatus]);

  // ── Keyboard + scroll lock ─────────────────────────────────────────────────

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handler);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", handler);
      document.body.style.overflow = "";
    };
  }, [onClose]);

  // ── Reserve + navigate ─────────────────────────────────────────────────────

  async function handleContinue() {
    if (!selectedSlot) return;
    reservingRef.current = true;
    setReserving(true);
    setReserveError(null);
    try {
      const reservation = await reserveSlot(doctor.doctor_service_id, selectedSlot);
      onReserved({
        slot: selectedSlot,
        reservationId: reservation.reservation_id,
        expiresAt: reservation.expires_at,
      });
    } catch (err) {
      reservingRef.current = false;
      setReserveError(
        err instanceof Error && err.message === "slot_taken"
          ? "That slot was just taken. Please pick another."
          : "Could not reserve slot. Please try again."
      );
      setReserving(false);
      setSelectedSlot(null);
    }
  }

  // ── Render ─────────────────────────────────────────────────────────────────

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden
      />

      {/* Modal */}
      <div className="relative z-10 flex w-full max-w-2xl flex-col overflow-hidden rounded-2xl bg-white shadow-2xl sm:flex-row">
        {/* Close */}
        <button
          type="button"
          onClick={onClose}
          aria-label="Close"
          className="absolute right-3 top-3 z-20 flex h-7 w-7 items-center justify-center rounded-full bg-white/90 text-[#64748B] shadow-sm transition-colors hover:bg-slate-100 hover:text-dent-ink"
        >
          <svg viewBox="0 0 16 16" fill="none" className="h-3.5 w-3.5" aria-hidden>
            <path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </button>

        {/* ── Left: calendar + slots ──────────────────────────────────────── */}
        <div className="flex flex-col border-b border-[#F1F5F9] p-5 sm:w-[55%] sm:border-b-0 sm:border-r sm:p-6">

          {/* Month dropdown */}
          <select
            value={viewMonthIdx}
            onChange={(e) => {
              setViewMonthIdx(Number(e.target.value));
              setSelectedDate(null);
            }}
            className="mb-4 w-full rounded-lg border border-[#E2E8F0] bg-white px-3 py-2 text-[13px] font-semibold text-dent-ink focus:outline-none focus:ring-2 focus:ring-dent-sky/30"
          >
            {monthOptions.map((opt, i) => (
              <option key={i} value={i}>{opt.label}</option>
            ))}
          </select>

          {/* Calendar grid */}
          <div className="mb-4">
            <div className="mb-1.5 grid grid-cols-7">
              {WEEKDAYS.map((d) => (
                <div
                  key={d}
                  className="text-center text-[10px] font-bold uppercase tracking-wide text-[#94A3B8]"
                >
                  {d}
                </div>
              ))}
            </div>
            <div className="grid grid-cols-7 gap-y-0.5">
              {calendarDays.map((day, i) => {
                if (!day) return <div key={i} />;
                const selectable = isDaySelectable(day);
                const selected = isDaySelected(day);
                const todayFlag = isToday(day);

                return (
                  <button
                    key={i}
                    type="button"
                    disabled={!selectable}
                    onClick={() => {
                      const d = new Date(year, month, day);
                      d.setHours(0, 0, 0, 0);
                      setSelectedDate(d);
                    }}
                    className={`mx-auto flex h-8 w-8 items-center justify-center rounded-full text-[13px] font-medium transition-colors
                      ${
                        selected
                          ? "bg-dent-ink text-white"
                          : todayFlag && selectable
                          ? "ring-1 ring-dent-sky text-dent-deep hover:bg-dent-badge-bg"
                          : selectable
                          ? "text-[#475569] hover:bg-dent-badge-bg"
                          : "cursor-not-allowed text-[#CBD5E1]"
                      }`}
                  >
                    {day}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Divider */}
          <div className="mb-4 h-px bg-[#F1F5F9]" />

          {/* Slots */}
          <div className="min-h-24">
            {!selectedDate && (
              <p className="py-2 text-center text-[13px] text-[#94A3B8]">
                Select a date to see available times
              </p>
            )}
            {selectedDate && loadingSlots && (
              <p className="py-2 text-center text-[13px] text-[#94A3B8]">Loading…</p>
            )}
            {selectedDate && !loadingSlots && slots.length === 0 && (
              <p className="py-2 text-center text-[13px] text-[#94A3B8]">
                No availability on this day
              </p>
            )}
            {selectedDate && !loadingSlots && slots.length > 0 && (
              <>
                <p className="mb-2 text-[10px] font-bold uppercase tracking-[0.14em] text-[#94A3B8]">
                  Available times
                </p>
                <div className="grid grid-cols-3 gap-1.5">
                  {slots.map((slot) => {
                    const unavailable = slot.status !== "available";
                    const isSelected = selectedSlot === slot.slot_time;

                    if (unavailable) {
                      return (
                        <div
                          key={slot.slot_time}
                          className="flex items-center justify-center rounded-lg border border-[#F1F5F9] bg-[#F8FAFC] py-2 text-[12px] text-[#CBD5E1] line-through select-none"
                        >
                          {formatTime(slot.slot_time)}
                        </div>
                      );
                    }

                    return (
                      <button
                        key={slot.slot_time}
                        type="button"
                        onClick={() =>
                          setSelectedSlot(isSelected ? null : slot.slot_time)
                        }
                        className={`rounded-lg border py-2 text-[12px] font-medium transition-all
                          ${
                            isSelected
                              ? "border-dent-deep bg-dent-ink text-white"
                              : "border-[#E2E8F0] bg-white text-dent-ink hover:border-dent-sky/50 hover:bg-dent-badge-bg"
                          }`}
                      >
                        {formatTime(slot.slot_time)}
                      </button>
                    );
                  })}
                </div>
              </>
            )}
          </div>
        </div>

        {/* ── Right: summary + CTA ────────────────────────────────────────── */}
        <div className="flex flex-col justify-between p-5 sm:w-[45%] sm:p-6">
          <div>
            {/* Service + doctor */}
            <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-[#94A3B8]">
              {serviceLabel}
            </p>
            <h2 className="mt-1 font-display text-lg font-bold text-dent-ink">
              {doctor.name}
            </h2>
            {doctor.specializations.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {doctor.specializations.map((s) => (
                  <span
                    key={s}
                    className="rounded-full border border-dent-sky/20 bg-dent-badge-bg px-2 py-0.5 text-[11px] font-semibold text-dent-deep"
                  >
                    {s}
                  </span>
                ))}
              </div>
            )}

            <div className="my-4 h-px bg-[#F1F5F9]" />

            {/* Price */}
            <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-[#94A3B8]">
              Session fee
            </p>
            <p className="mt-1 font-display text-2xl font-bold text-dent-ink">
              {formatPrice(doctor.effective_amount, doctor.currency)}
            </p>

            <div className="my-4 h-px bg-[#F1F5F9]" />

            {/* Selected slot summary */}
            {selectedSlot && (
              <div className="rounded-xl border border-dent-sky/20 bg-dent-badge-bg px-4 py-3">
                <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-[#94A3B8]">
                  Your selected time
                </p>
                <p className="mt-1 text-[13px] font-semibold text-dent-ink">
                  {new Date(selectedSlot).toLocaleDateString("en-US", {
                    weekday: "long",
                    month: "short",
                    day: "numeric",
                  })}
                </p>
                <p className="text-[13px] font-medium text-dent-deep">
                  {formatTime(selectedSlot)}
                </p>
              </div>
            )}
          </div>

          {/* CTA */}
          <div className="mt-6">
            {reserveError && (
              <p className="mb-2 text-[12px] text-red-600">{reserveError}</p>
            )}
            <button
              type="button"
              onClick={handleContinue}
              disabled={!selectedSlot || reserving}
              className="w-full rounded-xl bg-dent-ink py-3 text-[13px] font-semibold text-white transition-colors hover:bg-dent-deep disabled:cursor-not-allowed disabled:opacity-40"
            >
              {reserving ? "Reserving…" : "Continue to payment →"}
            </button>
            <p className="mt-2 text-center text-[11px] text-[#94A3B8]">
              Slot held for 5 min — complete payment to confirm
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
