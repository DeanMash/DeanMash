import { NextResponse } from "next/server";
import { registerBusiness } from "@/lib/store";
import type { VerticalId } from "@/lib/types";

export async function POST(request: Request) {
  const body = (await request.json()) as {
    name?: string;
    vertical?: VerticalId;
    city?: string;
    country?: string;
    ownerName?: string;
    ownerPhone?: string;
    whatsappNumber?: string;
    facebookHandle?: string;
    trialCode?: string;
    ecocashNumber?: string;
    payNow?: boolean;
  };

  if (!body.name || !body.ownerPhone || !body.facebookHandle || !body.vertical) {
    return NextResponse.json(
      {
        error:
          "name, vertical, ownerPhone, and facebookHandle are required",
      },
      { status: 400 },
    );
  }

  try {
    const result = registerBusiness({
      name: body.name,
      vertical: body.vertical,
      city: body.city || "Harare",
      country: body.country,
      ownerName: body.ownerName || "Owner",
      ownerPhone: body.ownerPhone,
      whatsappNumber: body.whatsappNumber,
      facebookHandle: body.facebookHandle,
      trialCode: body.trialCode,
      ecocashNumber: body.ecocashNumber,
      payNow: body.payNow,
    });

    return NextResponse.json(result);
  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Registration failed" },
      { status: 400 },
    );
  }
}
