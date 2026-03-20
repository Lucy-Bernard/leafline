import { updateSession } from "@/lib/supabase/middleware";
import { type NextRequest, NextResponse } from "next/server";

export async function middleware(request: NextRequest) {
  // Optional basic auth layer — useful for staging environments where you want
  // to password-protect the whole site before Supabase auth even runs.
  // Set BASIC_AUTH_USER and BASIC_AUTH_PASSWORD in your env to enable this.
  if (process.env.BASIC_AUTH_USER && process.env.BASIC_AUTH_PASSWORD) {
    const basicAuth = request.headers.get("authorization");

    if (basicAuth) {
      const authValue = basicAuth.split(" ")[1];
      const [user, pwd] = atob(authValue).split(":");

      if (
        user === process.env.BASIC_AUTH_USER &&
        pwd === process.env.BASIC_AUTH_PASSWORD
      ) {
        // Basic auth passed — hand off to Supabase session handling
        return await updateSession(request);
      }
    }

    // No valid basic auth header — prompt the browser to show a login dialog
    return new NextResponse("Auth required", {
      status: 401,
      headers: {
        "WWW-Authenticate": 'Basic realm="Secure Area"',
      },
    });
  }

  // No basic auth configured — go straight to Supabase session handling
  return await updateSession(request);
}

export const config = {
  matcher: [
    // Run middleware on all routes except static assets and images
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
