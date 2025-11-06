import { NextResponse } from "next/server";
import { clearAuthCookies } from "@/lib/auth";

export const runtime = "edge";

export async function POST(request: Request) {
  await clearAuthCookies();
  const redirectUrl = new URL("/login", request.url);
  return NextResponse.redirect(redirectUrl, { status: 303 });
}

export async function GET(request: Request) {
  await clearAuthCookies();
  const redirectUrl = new URL("/login", request.url);
  return NextResponse.redirect(redirectUrl, { status: 303 });
}

