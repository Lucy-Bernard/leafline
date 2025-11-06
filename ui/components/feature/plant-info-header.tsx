"use client";

import { Plant } from "@/lib/types/plant.types";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";

interface PlantInfoHeaderProps {
  plant: Plant;
  actionButton?: React.ReactNode;
}

export function PlantInfoHeader({ plant, actionButton }: PlantInfoHeaderProps) {
  return (
    <Card data-testid="plant-info-header">
      <div className="flex flex-col md:flex-row">
        {plant.image_url ? (
          <div className="w-full md:w-1/3 aspect-square md:aspect-auto">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={plant.image_url}
              alt={plant.name}
              className="object-cover w-full h-full rounded-t-lg md:rounded-l-lg md:rounded-tr-none"
            />
          </div>
        ) : (
          <div
            className="w-full md:w-1/3 aspect-square md:aspect-auto bg-muted flex items-center justify-center rounded-t-lg md:rounded-l-lg md:rounded-tr-none"
            data-testid="plant-placeholder"
          >
            <span className="text-8xl">🌿</span>
          </div>
        )}

        <div className="flex-1">
          <CardHeader>
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <CardTitle className="text-3xl mb-2">{plant.name}</CardTitle>
                <CardDescription>
                  Added {new Date(plant.created_at).toLocaleDateString()}
                </CardDescription>
              </div>
              <div className="flex items-center gap-2">
                {actionButton}
                <Badge variant="outline">Active</Badge>
              </div>
            </div>
          </CardHeader>

          <CardContent>
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2 text-sm text-muted-foreground">
                  WATERING SCHEDULE
                </h3>
                <p className="text-sm">{plant.care_schedule.watering_schedule}</p>
              </div>

              <Separator />

              <div className="flex flex-col h-[200px]">
                <h3 className="font-semibold text-sm text-muted-foreground mb-2">
                  CARE INSTRUCTIONS
                </h3>
                <ScrollArea className="flex-1 pr-4">
                  <p className="text-sm" data-testid="care-instructions">
                    {plant.care_schedule.care_instructions}
                  </p>
                </ScrollArea>
              </div>
            </div>
          </CardContent>
        </div>
      </div>
    </Card>
  );
}
