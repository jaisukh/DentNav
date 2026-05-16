"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { createOrder, releaseSlot, verifyPayment } from "@/lib/api/booking";

// ─── Helpers ──────────────────────────────────────────────────────────────────

function loadRazorpayScript(): Promise<void> {
  return new Promise((resolve, reject) => {
    if (document.getElementById("rzp-script")) { resolve(); return; }
    const script = document.createElement("script");
    script.id = "rzp-script";
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.onload = () => resolve();
    script.onerror = () => reject(new Error("Failed to load Razorpay"));
    document.body.appendChild(script);
  });
}

function formatPrice(amount: number, currency: string) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: currency.toUpperCase(),
    minimumFractionDigits: 0,
  }).format(amount / 100);
}

function formatSlotTime(iso: string) {
  const d = new Date(iso);
  return {
    date: d.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric" }),
    time: d.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit", hour12: true }),
  };
}

function getInitials(name: string) {
  return name.split(" ").map((n) => n[0]).join("").slice(0, 2).toUpperCase();
}

// ─── Countdown timer ──────────────────────────────────────────────────────────

function useCountdown(expiresAt: string | null) {
  const [secondsLeft, setSecondsLeft] = useState<number | null>(null);

  useEffect(() => {
    if (!expiresAt) return;
    const tick = () => {
      const diff = Math.max(0, Math.floor((new Date(expiresAt).getTime() - Date.now()) / 1000));
      setSecondsLeft(diff);
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [expiresAt]);

  return secondsLeft;
}

// ─── Page ─────────────────────────────────────────────────────────────────────

type Phase = "ready" | "creating" | "paying" | "verifying" | "success" | "expired" | "error";

export default function CheckoutPage() {
  const params = useParams<{ serviceKey: string; doctorServiceId: string }>();
  const searchParams = useSearchParams();
  const router = useRouter();

  const slotIso = searchParams.get("slot") ?? "";
  const doctorName = searchParams.get("name") ?? "Doctor";
  const reservationExpiresAt = searchParams.get("expires_at") ?? null;
  const reservationId = searchParams.get("reservation_id") ?? null;
  const previewAmount = Number(searchParams.get("amount") ?? "0");
  const previewCurrency = searchParams.get("currency") ?? "INR";
  const serviceName = searchParams.get("service") ?? "";
  const specialization = searchParams.get("specialization") ?? "";
  const photoUrl = searchParams.get("photo") ?? "";
  const { serviceKey, doctorServiceId } = params;

  const [phase, setPhase] = useState<Phase>("ready");
  const [order, setOrder] = useState<{ orderId: string; amount: number; currency: string; bookingId: string } | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const paying = useRef(false);
  const secondsLeft = useCountdown(reservationExpiresAt);

  const displayAmount = order ? order.amount : previewAmount;
  const displayCurrency = order ? order.currency : previewCurrency;

  useEffect(() => {
    if (secondsLeft === 0 && phase === "ready" && !order) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setPhase("expired");
    }
  }, [secondsLeft, phase, order]);

  async function handlePay() {
    if (paying.current || !slotIso) return;
    paying.current = true;

    let activeOrder = order;
    if (!activeOrder) {
      setPhase("creating");
      try {
        const res = await createOrder(doctorServiceId, slotIso);
        activeOrder = { orderId: res.order_id, amount: res.amount, currency: res.currency, bookingId: res.booking_id };
        setOrder(activeOrder);
      } catch (err: unknown) {
        paying.current = false;
        if (err instanceof Error && err.message === "reservation_expired") {
          setPhase("expired");
        } else {
          setErrorMsg("Could not create payment order. Please go back and try again.");
          setPhase("error");
        }
        return;
      }
    }

    if (!activeOrder) return;

    try {
      await loadRazorpayScript();
    } catch {
      paying.current = false;
      setErrorMsg("Could not load payment gateway. Please refresh and try again.");
      setPhase("error");
      return;
    }

    const key = process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID;
    if (!key) {
      paying.current = false;
      setErrorMsg("Payment gateway is not configured.");
      setPhase("error");
      return;
    }

    setPhase("paying");

    const rzp = new window.Razorpay({
      key,
      amount: activeOrder.amount,
      currency: activeOrder.currency.toUpperCase(),
      order_id: activeOrder.orderId,
      name: "DentNav",
      description: `Session with ${doctorName}`,
      handler: async (response) => {
        setPhase("verifying");
        try {
          await verifyPayment(
            response.razorpay_order_id,
            response.razorpay_payment_id,
            response.razorpay_signature,
          );
          setPhase("success");
          router.replace("/landing?booking_confirmed=1");
        } catch (err: unknown) {
          if (err instanceof Error && err.message === "slot_expired") {
            setPhase("expired");
          } else {
            setErrorMsg("Payment could not be verified. If you were charged, please contact support.");
            setPhase("error");
          }
        }
      },
      modal: {
        ondismiss: () => {
          paying.current = false;
          router.push(`/landing/booking/${serviceKey}`);
        },
      },
      theme: { color: "#0C1A2E" },
    });

    rzp.open();
  }

  const slot = slotIso ? formatSlotTime(slotIso) : null;

  return (
    <div className="w-full pb-14">

      {/* Back */}
      {phase !== "success" && (
        <button
          type="button"
          onClick={async () => {
            if (!order && reservationId) {
              await releaseSlot(reservationId).catch(() => {});
            }
            router.push(`/landing/booking/${serviceKey}`);
          }}
          className="mb-8 inline-flex items-center gap-1.5 text-[13px] font-medium text-[#64748B] transition-colors hover:text-dent-ink"
        >
          <svg viewBox="0 0 16 16" fill="none" className="h-3.5 w-3.5" aria-hidden>
            <path d="M12.67 8H3.33M7.33 4L3.33 8l4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Back to doctors
        </button>
      )}

      {/* ── Success ── */}
      {phase === "success" && (
        <div className="flex items-center justify-center gap-2 py-16 text-[13px] text-[#94A3B8]">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-[#E2E8F0] border-t-dent-sky" />
          Booking confirmed — redirecting…
        </div>
      )}

      {/* ── Expired ── */}
      {phase === "expired" && (
        <div className="flex flex-col items-center gap-5 py-8 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-amber-50 ring-1 ring-amber-100">
            <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6 text-amber-500" aria-hidden>
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.75" />
              <path d="M12 7v5l3 3" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
            </svg>
          </div>
          <div>
            <h1 className="font-display text-xl font-bold text-dent-ink">Slot expired</h1>
            <p className="mt-2 text-[14px] text-[#64748B]">
              The hold on your slot has lapsed. Please go back and choose a new time.
            </p>
          </div>
          <Link
            href={`/landing/booking/${serviceKey}`}
            className="w-full rounded-xl bg-dent-ink py-3 text-center text-[13px] font-semibold text-white transition-colors hover:bg-dent-deep"
          >
            Choose another slot
          </Link>
        </div>
      )}

      {/* ── Error ── */}
      {phase === "error" && (
        <div className="flex flex-col items-center gap-5 py-8 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-red-50 ring-1 ring-red-100">
            <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6 text-red-500" aria-hidden>
              <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </div>
          <div>
            <h1 className="font-display text-xl font-bold text-dent-ink">Something went wrong</h1>
            <p className="mt-2 text-[14px] text-[#64748B]">{errorMsg}</p>
          </div>
          <Link
            href={`/landing/booking/${serviceKey}`}
            className="w-full rounded-xl bg-dent-ink py-3 text-center text-[13px] font-semibold text-white transition-colors hover:bg-dent-deep"
          >
            Go back
          </Link>
        </div>
      )}

      {/* ── Ready / Creating / Paying / Verifying ── */}
      {(phase === "ready" || phase === "creating" || phase === "paying" || phase === "verifying") && (
        <>
          <header className="mb-6">
            <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#94A3B8]">
              Complete your booking
            </p>
            <h1 className="mt-1 font-display text-2xl font-bold tracking-tight text-dent-ink">
              Review &amp; pay
            </h1>
          </header>

          {/* ── Two equal columns, both bottom-aligned ── */}
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2 lg:items-end">

            {/* LEFT: doctor + appointment details + inclusions */}
            <div className="flex flex-col gap-4">

              {/* Doctor card */}
              <div className="flex items-center gap-4 rounded-2xl border border-[#E2E8F0] bg-white p-4 shadow-sm">
                {photoUrl ? (
                  <Image
                    src={photoUrl}
                    alt={doctorName}
                    width={52}
                    height={52}
                    className="rounded-full object-cover ring-2 ring-[#F1F5F9]"
                  />
                ) : (
                  <div className="flex h-[52px] w-[52px] shrink-0 items-center justify-center rounded-full bg-dent-ink text-[15px] font-bold text-white">
                    {getInitials(doctorName)}
                  </div>
                )}
                <div className="min-w-0">
                  <p className="truncate font-display text-[15px] font-bold text-dent-ink">{doctorName}</p>
                  {specialization && (
                    <p className="mt-0.5 text-[12px] text-[#64748B]">{specialization}</p>
                  )}
                  {serviceName && (
                    <span className="mt-1.5 inline-block rounded-full bg-sky-50 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-[0.1em] text-sky-600">
                      {serviceName}
                    </span>
                  )}
                </div>
              </div>

              {/* Appointment details */}
              <div className="rounded-2xl border border-[#E2E8F0] bg-white p-5 shadow-sm">
                <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-[#94A3B8]">Appointment details</p>
                <div className="mt-4 space-y-3.5">
                  {slot && (
                    <>
                      <div className="flex items-start gap-3">
                        <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-[#F8FAFF]">
                          <svg viewBox="0 0 16 16" fill="none" className="h-3.5 w-3.5 text-dent-sky" aria-hidden>
                            <rect x="1" y="2" width="14" height="13" rx="1.5" stroke="currentColor" strokeWidth="1.25" />
                            <path d="M5 1v2M11 1v2M1 6h14" stroke="currentColor" strokeWidth="1.25" strokeLinecap="round" />
                          </svg>
                        </div>
                        <div>
                          <p className="text-[11px] font-medium text-[#94A3B8]">Date</p>
                          <p className="text-[13px] font-semibold text-dent-ink">{slot.date}</p>
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-[#F8FAFF]">
                          <svg viewBox="0 0 16 16" fill="none" className="h-3.5 w-3.5 text-dent-sky" aria-hidden>
                            <circle cx="8" cy="8" r="6.5" stroke="currentColor" strokeWidth="1.25" />
                            <path d="M8 5v3.5l2 2" stroke="currentColor" strokeWidth="1.25" strokeLinecap="round" />
                          </svg>
                        </div>
                        <div>
                          <p className="text-[11px] font-medium text-[#94A3B8]">Time</p>
                          <p className="text-[13px] font-semibold text-dent-ink">{slot.time}</p>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* What's included */}
              <div className="rounded-2xl border border-[#E2E8F0] bg-white p-5 shadow-sm">
                <p className="mb-3 text-[10px] font-bold uppercase tracking-[0.16em] text-[#94A3B8]">What&apos;s included</p>
                <div className="space-y-3">
                  {[
                    { icon: "M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z", label: "Instant booking confirmation" },
                    { icon: "M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z", label: "Confirmation email to both parties" },
                    { icon: "M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z", label: "Calendar invite from your doctor" },
                  ].map(({ icon, label }) => (
                    <div key={label} className="flex items-center gap-2.5">
                      <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-50">
                        <svg viewBox="0 0 24 24" fill="none" className="h-3 w-3 text-emerald-500" aria-hidden>
                          <path d={icon} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                      </div>
                      <span className="text-[12px] font-medium text-[#475569]">{label}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* RIGHT: order summary only */}
            <div className="flex flex-col gap-4">
              <div className="rounded-2xl border border-[#E2E8F0] bg-white p-5 shadow-sm">
                <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-[#94A3B8]">Order summary</p>
                <div className="mt-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[13px] text-[#64748B]">Consultation</span>
                    <span className="text-[13px] font-semibold text-dent-ink">
                      {displayAmount ? formatPrice(displayAmount, displayCurrency) : "—"}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-[13px] text-[#64748B]">Platform fee</span>
                    <span className="text-[13px] font-medium text-emerald-600">Free</span>
                  </div>
                  <div className="h-px bg-[#F1F5F9]" />
                  <div className="flex items-center justify-between">
                    <span className="text-[14px] font-bold text-dent-ink">Total due</span>
                    <span className="font-display text-xl font-bold text-dent-ink">
                      {displayAmount ? formatPrice(displayAmount, displayCurrency) : "—"}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* ── Payment bar — centred below both columns ── */}
          <div className="mx-auto mt-5 flex w-full max-w-sm flex-col gap-3">

            {/* Countdown */}
            {phase === "ready" && !order && secondsLeft !== null && secondsLeft > 0 && (
              <div className="flex items-center justify-center gap-2 rounded-xl border border-amber-100 bg-amber-50 px-4 py-2.5">
                <svg viewBox="0 0 24 24" fill="none" className="h-4 w-4 shrink-0 text-amber-500" aria-hidden>
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.75" />
                  <path d="M12 7v5l3 3" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
                </svg>
                <p className="text-[12px] font-medium text-amber-700">
                  Slot held for{" "}
                  <span className="font-bold tabular-nums">
                    {String(Math.floor(secondsLeft / 60)).padStart(2, "0")}:
                    {String(secondsLeft % 60).padStart(2, "0")}
                  </span>
                  {" "}— complete payment before it expires
                </p>
              </div>
            )}

            {/* CTA */}
            {phase === "ready" && (
              <button
                type="button"
                onClick={handlePay}
                className="flex w-full items-center justify-center gap-2 rounded-xl bg-dent-ink py-3.5 text-[14px] font-semibold text-white transition-colors hover:bg-dent-deep"
              >
                <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4" aria-hidden>
                  <rect x="1" y="5" width="18" height="12" rx="2" stroke="currentColor" strokeWidth="1.5" />
                  <path d="M1 9h18" stroke="currentColor" strokeWidth="1.5" />
                </svg>
                Pay {displayAmount ? formatPrice(displayAmount, displayCurrency) : "now"}
              </button>
            )}
            {(phase === "creating" || phase === "paying" || phase === "verifying") && (
              <div className="flex items-center justify-center gap-2 rounded-xl border border-[#E2E8F0] bg-white py-3.5 text-[13px] text-[#94A3B8] shadow-sm">
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-[#E2E8F0] border-t-dent-sky" />
                {phase === "creating" && "Preparing payment…"}
                {phase === "paying" && "Opening payment…"}
                {phase === "verifying" && "Verifying payment…"}
              </div>
            )}

            {/* Trust */}
            <div className="flex items-center justify-center gap-1.5 text-[11px] text-[#94A3B8]">
              <svg viewBox="0 0 16 16" fill="none" className="h-3.5 w-3.5" aria-hidden>
                <path d="M8 1.5L2 4v4c0 3.31 2.57 6.41 6 7 3.43-.59 6-3.69 6-7V4L8 1.5z" stroke="currentColor" strokeWidth="1.25" strokeLinejoin="round" />
                <path d="M5.5 8l1.5 1.5 3-3" stroke="currentColor" strokeWidth="1.25" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              Secured by Razorpay · SSL encrypted · No extra charges
            </div>
          </div>
        </>
      )}
    </div>
  );
}
