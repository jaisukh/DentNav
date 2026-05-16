import { API_ROUTES } from "./routes";

export type DoctorForService = {
  doctor_service_id: string;
  doctor_id: string;
  name: string;
  bio: string;
  photo_url: string;
  specializations: string[];
  effective_amount: number;
  currency: string;
};

export type SlotStatus = "available" | "reserved" | "booked";

export type Slot = {
  slot_time: string;
  status: SlotStatus;
};

export type ReserveResponse = {
  reservation_id: string;
  slot_time: string;
  expires_at: string;
};

export type CreateOrderResponse = {
  order_id: string;
  amount: number;
  currency: string;
  booking_id: string;
  expires_at: string;
};

export type VerifyPaymentResponse = {
  ok: boolean;
  booking_id: string;
  slot_time: string;
  doctor_name: string;
  calendly_invitee_uri: string | null;
};

export async function fetchDoctorsForService(serviceKey: string): Promise<DoctorForService[]> {
  const res = await fetch(API_ROUTES.serviceDoctors(serviceKey), {
    credentials: "include",
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`Failed to load doctors: ${res.status}`);
  return res.json() as Promise<DoctorForService[]>;
}

export async function fetchAvailability(
  doctorServiceId: string,
  dateFrom: string,
  dateTo: string,
): Promise<Slot[]> {
  const url = new URL(API_ROUTES.doctorAvailability(doctorServiceId));
  url.searchParams.set("date_from", dateFrom);
  url.searchParams.set("date_to", dateTo);
  const res = await fetch(url.toString(), {
    credentials: "include",
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`Failed to load availability: ${res.status}`);
  return res.json() as Promise<Slot[]>;
}

export async function reserveSlot(
  doctorServiceId: string,
  slotTime: string,
): Promise<ReserveResponse> {
  const res = await fetch(API_ROUTES.reserveSlot, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ doctor_service_id: doctorServiceId, slot_time: slotTime }),
  });
  if (res.status === 409) throw new Error("slot_taken");
  if (!res.ok) throw new Error(`Reserve failed: ${res.status}`);
  return res.json() as Promise<ReserveResponse>;
}

export async function releaseSlot(reservationId: string): Promise<void> {
  await fetch(API_ROUTES.releaseSlot, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ reservation_id: reservationId }),
  });
}

export async function createOrder(
  doctorServiceId: string,
  slotTime: string,
): Promise<CreateOrderResponse> {
  const res = await fetch(API_ROUTES.createOrder, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ doctor_service_id: doctorServiceId, slot_time: slotTime }),
  });
  if (res.status === 409) throw new Error("reservation_expired");
  if (!res.ok) throw new Error(`Create order failed: ${res.status}`);
  return res.json() as Promise<CreateOrderResponse>;
}

export async function cancelOrder(bookingId: string): Promise<void> {
  await fetch(API_ROUTES.cancelOrder, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ booking_id: bookingId }),
  });
}

export async function verifyPayment(
  razorpayOrderId: string,
  razorpayPaymentId: string,
  razorpaySignature: string,
): Promise<VerifyPaymentResponse> {
  const res = await fetch(API_ROUTES.verifyPayment, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({
      razorpay_order_id: razorpayOrderId,
      razorpay_payment_id: razorpayPaymentId,
      razorpay_signature: razorpaySignature,
    }),
  });
  if (res.status === 409) throw new Error("slot_expired");
  if (!res.ok) throw new Error(`Verify payment failed: ${res.status}`);
  return res.json() as Promise<VerifyPaymentResponse>;
}
