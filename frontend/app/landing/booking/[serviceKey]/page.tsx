"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { fetchDoctorsForService, type DoctorForService } from "@/lib/api/booking";
import { BookingModal } from "@/components/booking/BookingModal";

const SERVICE_LABELS: Record<string, string> = {
  intro_consultation: "Introductory Consultation",
  visa_consultation: "Visa Guidance",
  interview_preparation: "Interview Preparation",
  cv_sop_review: "CV & SoP Preparation",
  caapid_assistance: "ADEA CAAPID & PASS Guidance",
  license_guidance: "State License Guidance",
};

function formatPrice(amount: number, currency: string) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: currency.toUpperCase(),
    minimumFractionDigits: 0,
  }).format(amount / 100);
}

function DoctorAvatar({ name, photoUrl }: { name: string; photoUrl: string }) {
  const [failed, setFailed] = useState(false);
  const initials = name
    .split(" ")
    .map((w) => w[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  if (!photoUrl || failed) {
    return (
      <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-dent-badge-bg text-sm font-bold text-dent-deep ring-2 ring-dent-sky/20">
        {initials}
      </div>
    );
  }

  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={photoUrl}
      alt={name}
      onError={() => setFailed(true)}
      className="h-12 w-12 shrink-0 rounded-full object-cover ring-2 ring-dent-sky/20"
    />
  );
}

function DoctorCard({
  doctor,
  onSelect,
}: {
  doctor: DoctorForService;
  onSelect: (doctor: DoctorForService) => void;
}) {
  return (
    <article className="flex items-center gap-4 rounded-2xl border border-[#E2E8F0] bg-white px-5 py-4 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:shadow-[0_12px_32px_-8px_rgba(13,28,46,0.10)]">
      <DoctorAvatar name={doctor.name} photoUrl={doctor.photo_url} />

      <div className="flex min-w-0 flex-1 items-center gap-4">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="font-display text-base font-bold text-dent-ink">{doctor.name}</h3>
            <span className="shrink-0 rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] px-2.5 py-0.5 text-sm font-bold text-dent-ink">
              {formatPrice(doctor.effective_amount, doctor.currency)}
            </span>
          </div>
          {doctor.specializations.length > 0 && (
            <div className="mt-1 flex flex-wrap gap-1.5">
              {doctor.specializations.map((s) => (
                <span
                  key={s}
                  className="rounded-full border border-dent-sky/20 bg-dent-badge-bg px-2.5 py-0.5 text-[11px] font-semibold text-dent-deep"
                >
                  {s}
                </span>
              ))}
            </div>
          )}
          {doctor.bio && (
            <p className="mt-1 text-[12px] leading-relaxed text-[#64748B] line-clamp-1">
              {doctor.bio}
            </p>
          )}
        </div>

        <button
          type="button"
          onClick={() => onSelect(doctor)}
          className="shrink-0 inline-flex items-center gap-2 rounded-xl bg-dent-ink px-5 py-2.5 text-[13px] font-semibold text-white transition-colors hover:bg-dent-deep"
        >
          Select &amp; book
          <svg viewBox="0 0 16 16" fill="none" className="h-3.5 w-3.5" aria-hidden>
            <path
              d="M3.33 8h9.34M8.67 4l4 4-4 4"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>
    </article>
  );
}

export default function BookingDoctorSelectPage() {
  const params = useParams<{ serviceKey: string }>();
  const serviceKey = params.serviceKey;
  const serviceLabel = SERVICE_LABELS[serviceKey] ?? serviceKey.replace(/_/g, " ");

  const [doctors, setDoctors] = useState<DoctorForService[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeDoctor, setActiveDoctor] = useState<DoctorForService | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchDoctorsForService(serviceKey)
      .then((data) => { if (!cancelled) setDoctors(data); })
      .catch(() => { if (!cancelled) setError("Could not load doctors. Please try again."); });
    return () => { cancelled = true; };
  }, [serviceKey]);

  return (
    <>
      <div className="w-full pb-14">
        {/* Back */}
        <Link
          href="/landing/packages"
          className="mb-8 inline-flex items-center gap-1.5 text-[13px] font-medium text-[#64748B] transition-colors hover:text-dent-ink"
        >
          <svg viewBox="0 0 16 16" fill="none" className="h-3.5 w-3.5" aria-hidden>
            <path d="M12.67 8H3.33M7.33 4L3.33 8l4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Back to packages
        </Link>

        <header className="mb-8">
          <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#94A3B8]">
            Book a session
          </p>
          <h1 className="mt-1 font-display text-2xl font-bold tracking-tight text-dent-ink sm:text-3xl">
            {serviceLabel}
          </h1>
          <p className="mt-2 text-[14px] text-[#64748B]">
            Choose a doctor to view their available times.
          </p>
        </header>

        {error && (
          <div className="rounded-xl border border-red-100 bg-red-50 px-5 py-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {!error && doctors === null && (
          <div className="flex min-h-[30vh] items-center justify-center text-sm text-[#94A3B8]">
            Loading doctors…
          </div>
        )}

        {!error && doctors !== null && doctors.length === 0 && (
          <div className="rounded-xl border border-[#E2E8F0] bg-white px-6 py-10 text-center text-sm text-[#64748B]">
            No doctors are available for this service yet. Please check back soon.
          </div>
        )}

        {!error && doctors !== null && doctors.length > 0 && (
          <div className="grid gap-4">
            {doctors.map((d) => (
              <DoctorCard
                key={d.doctor_service_id}
                doctor={d}
                onSelect={setActiveDoctor}
              />
            ))}
          </div>
        )}
      </div>

      {/* Booking modal */}
      {activeDoctor && (
        <BookingModal
          doctor={activeDoctor}
          serviceKey={serviceKey}
          serviceLabel={serviceLabel}
          onClose={() => setActiveDoctor(null)}
        />
      )}
    </>
  );
}
