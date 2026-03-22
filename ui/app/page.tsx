import { AuthButton } from "@/components/auth-button";
import { ThemeSwitcher } from "@/components/theme-switcher";
import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center">
      <div className="flex-1 w-full flex flex-col gap-20 items-center">
        <nav className="w-full flex justify-center border-b border-b-foreground/10 h-20 border">
          <div className="w-full max-w-5xl flex justify-between items-center p-3 px-5 text-sm">
            <div className="flex gap-5 items-center font-semibold">
              <Link href={"/"}>
                <h1 className="font-poiret text-2xl">LeafLine</h1>
              </Link>
            </div>
            <AuthButton />
          </div>
        </nav>

        <div className="flex-1 flex flex-col gap-16 max-w-5xl p-5 w-full">
          {/* Hero */}
          <div className="flex flex-col gap-4">
            <h1 className="font-poiret text-5xl font-bold">
              Welcome to LeafLine
            </h1>
            <p className="text-lg text-muted-foreground max-w-xl">
              Your personal plant diagnostic companion. Upload a photo of any
              plant and LeafLine will identify it, build a care schedule, and
              walk you through a diagnosis if something looks wrong.
            </p>
          </div>

          {/* How it works */}
          <div className="flex flex-col gap-4">
            <h2 className="text-sm font-semibold uppercase tracking-widest text-muted-foreground">
              How it works
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="bg-card border border-border rounded-lg p-5 flex flex-col gap-2">
                <span className="text-2xl">
                  <i className="fa-solid fa-camera text-muted-foreground"></i>
                </span>
                <p className="font-semibold text-foreground">
                  1. Upload a photo
                </p>
                <p className="text-sm text-muted-foreground">
                  Take a clear, well-lit photo of your plant. Make sure the
                  whole plant or the affected area is in frame and in focus —
                  blurry or dark images may affect identification accuracy.
                </p>
              </div>

              <div className="bg-card border border-border rounded-lg p-5 flex flex-col gap-2">
                <span className="text-2xl">
                  <i className="fa-brands fa-pagelines text-primary"></i>
                </span>
                <p className="font-semibold text-foreground">
                  2. Get identified
                </p>
                <p className="text-sm text-muted-foreground">
                  LeafLine identifies your plant and generates a personalised
                  care schedule covering watering, light, humidity, and soil.
                </p>
              </div>

              <div className="bg-card border border-border rounded-lg p-5 flex flex-col gap-2">
                <span className="text-2xl">
                  <i className="fa-solid fa-book-medical text-destructive/70"></i>
                </span>
                <p className="font-semibold text-foreground">
                  3. Diagnose a problem
                </p>
                <p className="text-sm text-muted-foreground">
                  Something wrong? Start a diagnosis. An AI agent will ask
                  targeted questions and work through the evidence to find the
                  cause — no more Googling ten conflicting answers.
                </p>
              </div>
            </div>
          </div>

          {/* Photo tips */}
          <div className="flex items-start gap-3 bg-secondary/40 border border-secondary rounded-lg px-5 py-4 max-w-xl">
            <span className="text-lg mt-0.5">
              <i className="text-amber-400/90 fa-solid fa-lightbulb"></i>
            </span>
            <div className="flex flex-col gap-1">
              <p className="font-semibold text-secondary-foreground text-sm">
                Tips for a great photo
              </p>
              <ul className="text-sm text-secondary-foreground/80 list-disc list-inside space-y-0.5">
                <li>Good natural light, no harsh shadows</li>
                <li>Hold the camera steady — avoid blur</li>
                <li>Include leaves, stem, and soil if possible</li>
                <li>If showing damage, zoom in on the affected area</li>
                <li>
                  Do not have multiple plants in one picture, to avoid confusion
                </li>
              </ul>
            </div>
          </div>
        </div>

        <footer className="w-full flex items-center justify-center border-t mx-auto text-center text-xs gap-8 py-16">
          <ThemeSwitcher />
        </footer>
      </div>
    </main>
  );
}
