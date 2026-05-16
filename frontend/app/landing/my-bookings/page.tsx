"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchMyBookings, type MyBooking } from "@/lib/api/booking";

// ─── Status pill ─────────────────────────────────────────────────────────────

const STATUS_CONFIG: Record<string, { label: string; classes: string }> = {
  confirmed:  { label: "Upcoming",   classes: "bg-emerald-50 text-emerald-700 ring-emerald-200" },
  completed:  { label: "Completed",  classes: "bg-slate-100 text-slate-600 ring-slate-200" },
  no_show:    { label: "No Show",    classes: "bg-gray-100 text-gray-500 ring-gray-200" },
};

function StatusPill({ status }: { status: string }) {
  const cfg = STATUS_CONFIG[status] ?? { label: status, classes: "bg-gray-100 text-gray-500 ring-gray-200" };
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-bold uppercase tracking-[0.12em] ring-1 ${cfg.classes}`}>
      {cfg.label}
    </span>
  );
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function formatSlot(iso: string) {
  const d = new Date(iso);
  return {
    date: d.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric" }),
    time: d.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit", hour12: true }),
  };
}

// ─── Booking card ────────────────────────────────────────────────────────────

function BookingCard({ booking }: { booking: MyBooking }) {
  const slot = booking.slot_time ? formatSlot(booking.slot_time) : null;
  const isUpcoming = booking.status === "confirmed";

  return (
    <div className={`rounded-2xl border bg-white p-5 shadow-sm transition-shadow hover:shadow-md ${isUpcoming ? "border-emerald-200" : "border-[#E2E8F0]"}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-[#94A3B8]">
            {booking.service_name}{booking.duration_minutes ? ` · ${booking.duration_minutes} min` : ""}
          </p>
          <p className="mt-1 font-display text-base font-bold text-dent-ink truncate">{booking.doctor_name}</p>
        </div>
        <StatusPill status={booking.status} />
      </div>

      {slot && (
        <div className="mt-3 flex items-center gap-2 text-[13px] text-[#475569]">
          <svg viewBox="0 0 16 16" fill="none" className="h-3.5 w-3.5 shrink-0 text-[#94A3B8]" aria-hidden>
            <rect x="1" y="2" width="14" height="13" rx="1.5" stroke="currentColor" strokeWidth="1.25" />
            <path d="M5 1v2M11 1v2M1 6h14" stroke="currentColor" strokeWidth="1.25" strokeLinecap="round" />
          </svg>
          <span>{slot.date}</span>
          <span className="font-semibold text-dent-ink">{slot.time}</span>
        </div>
      )}

      {booking.calendly_invitee_uri && isUpcoming && (
        <div className="mt-3 border-t border-[#F1F5F9] pt-3">
          <a
            href={booking.calendly_invitee_uri}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 text-[12px] font-semibold text-dent-sky hover:underline"
          >
            Reschedule or cancel
            <svg viewBox="0 0 12 12" fill="none" className="h-3 w-3" aria-hidden>
              <path d="M2 10L10 2M5 2h5v5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </a>
        </div>
      )}
    </div>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function MyBookingsPage() {
  const [bookings, setBookings] = useState<MyBooking[] | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetchMyBookings()
      .then(setBookings)
      .catch(() => setError(true));
  }, []);

  const visible = bookings ?? [];
  const upcoming = visible.filter((b) => b.status === "confirmed");
  const past = visible.filter((b) => b.status !== "confirmed");

  return (
    <div className="w-full max-w-2xl pb-10">
      <header className="mb-7">
        <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#94A3B8]">Overview</p>
        <h1 className="mt-1 font-display text-2xl font-bold tracking-tight text-dent-ink">My Bookings</h1>
      </header>

      {/* Loading */}
      {bookings === null && !error && (
        <div className="flex items-center gap-2 py-10 text-[13px] text-[#94A3B8]">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-[#E2E8F0] border-t-dent-sky" />
          Loading your bookings…
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="rounded-2xl border border-red-100 bg-red-50 px-5 py-4 text-[13px] text-red-700">
          Could not load bookings. Please refresh the page.
        </div>
      )}

      {/* Empty */}
      {bookings !== null && visible.length === 0 && (
        <div className="flex flex-col items-center gap-4 rounded-3xl border border-dashed border-[#E2E8F0] bg-white py-14 text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#F8F9FF] ring-1 ring-[#E2E8F0]">
            <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5 text-[#94A3B8]" aria-hidden>
              <rect x="3" y="4" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="1.75" />
              <path d="M16 2v4M8 2v4M3 10h18" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
            </svg>
          </div>
          <div>
            <p className="font-display text-base font-bold text-dent-ink">No bookings yet</p>
            <p className="mt-1 text-[13px] text-[#64748B]">Browse our services and book a session with a specialist.</p>
          </div>
          <Link
            href="/landing/packages"
            className="rounded-xl bg-dent-ink px-5 py-2.5 text-[13px] font-semibold text-white transition-colors hover:bg-dent-deep"
          >
            Browse services
          </Link>
        </div>
      )}

      {/* Upcoming */}
      {upcoming.length > 0 && (
        <section className="mb-6">
          <p className="mb-3 text-[11px] font-bold uppercase tracking-[0.16em] text-[#94A3B8]">Upcoming</p>
          <div className="flex flex-col gap-3">
            {upcoming.map((b) => <BookingCard key={b.id} booking={b} />)}
          </div>
        </section>
      )}

      {/* Past */}
      {past.length > 0 && (
        <section>
          <p className="mb-3 text-[11px] font-bold uppercase tracking-[0.16em] text-[#94A3B8]">Past</p>
          <div className="flex flex-col gap-3">
            {past.map((b) => <BookingCard key={b.id} booking={b} />)}
          </div>
        </section>
      )}
    </div>
  );
}
