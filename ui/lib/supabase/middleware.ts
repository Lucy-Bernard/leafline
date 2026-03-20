import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";

// This runs on every request (via middleware.ts) and does two things:
// 1. Refreshes the user's session token if it's about to expire
// 2. Redirects unauthenticated users away from protected routes
export async function updateSession(request: NextRequest) {
  // Start with a basic "continue" response — we'll attach cookies to this
  let supabaseResponse = NextResponse.next({ request });

  // Create a server-side Supabase client that reads/writes cookies on the request
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_OR_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          // Write updated cookies to both the request and response
          // so the session stays in sync across the full request lifecycle
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value),
          );
          supabaseResponse = NextResponse.next({ request });
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options),
          );
        },
      },
    },
  );

  // getClaims() must be called here to keep the session alive.
  // Do not put any code between createServerClient and getClaims() —
  // it can cause users to get randomly logged out.
  const { data } = await supabase.auth.getClaims();
  const user = data?.claims;

  // If there's no logged-in user and they're trying to access a protected route,
  // redirect them to the login page
  if (
    request.nextUrl.pathname !== "/" &&
    !user &&
    !request.nextUrl.pathname.startsWith("/login") &&
    !request.nextUrl.pathname.startsWith("/auth")
  ) {
    const url = request.nextUrl.clone();
    url.pathname = "/auth/login";
    return NextResponse.redirect(url);
  }

  // If a logged-in user tries to visit the login page, send them to dashboard
  if (user && request.nextUrl.pathname.startsWith("/auth/login")) {
    const url = request.nextUrl.clone();
    url.pathname = "/dashboard";
    return NextResponse.redirect(url);
  }

  // Always return supabaseResponse — it carries the refreshed session cookies.
  // If you create a new NextResponse here instead, you'll break session handling.
  return supabaseResponse;
}
