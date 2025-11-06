import { Card, CardContent, CardHeader } from "@/components/ui/card";

export function PlantsLoading() {
  return (
    <div
      className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
      data-testid="loading-skeleton"
    >
      {Array.from({ length: 6 }).map((_, i) => (
        <Card key={i} className="overflow-hidden">
          <div className="aspect-video w-full bg-muted animate-pulse" />
          <CardHeader>
            <div className="h-6 w-3/4 bg-muted animate-pulse rounded" />
            <div className="h-4 w-1/2 bg-muted animate-pulse rounded mt-2" />
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            <div className="h-4 w-full bg-muted animate-pulse rounded" />
            <div className="h-4 w-5/6 bg-muted animate-pulse rounded" />
            <div className="flex gap-2 mt-2">
              <div className="flex-1 h-10 bg-muted animate-pulse rounded" />
              <div className="h-10 w-10 bg-muted animate-pulse rounded" />
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
