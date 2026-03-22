"use client";

import { Plant } from "@/lib/types/plant.types";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { Trash2 } from "lucide-react";
import { useState } from "react";

interface PlantCardProps {
  plant: Plant;
  onDelete: (id: string) => Promise<void>;
}

export function PlantCard({ plant, onDelete }: PlantCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const handleDelete = async () => {
    if (!showConfirm) {
      setShowConfirm(true);
      return;
    }

    setIsDeleting(true);
    try {
      await onDelete(plant.id);
    } catch {
      setIsDeleting(false);
      setShowConfirm(false);
    }
  };

  return (
    <Card
      className="overflow-hidden hover:shadow-lg transition-shadow flex flex-col"
      data-testid="plant-card"
    >
      {plant.image_url && (
        <div className="w-full bg-muted h-64 overflow-hidden">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={plant.image_url}
            alt={plant.name}
            className="object-cover w-full h-full"
          />
        </div>
      )}
      {!plant.image_url && (
        <div
          className="w-full bg-muted h-64 flex items-center justify-center"
          data-testid="plant-placeholder"
        >
          <span className="text-4xl">🌿</span>
        </div>
      )}
      <CardHeader>
        <CardTitle>{plant.name}</CardTitle>
        <CardDescription>
          Added {new Date(plant.created_at).toLocaleDateString()}
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-3 mt-auto">
        <p className="text-sm text-muted-foreground line-clamp-2">
          {plant.care_schedule.watering_schedule}
        </p>
        <div className="flex gap-2">
          <Button asChild className="flex-1" data-testid="view-details-button">
            <Link href={`/plants/${plant.id}`}>View Details</Link>
          </Button>
          <Button
            variant={showConfirm ? "destructive" : "outline"}
            size="icon"
            onClick={handleDelete}
            disabled={isDeleting}
            data-testid="delete-button"
          >
            {isDeleting ? (
              <span className="animate-spin">⏳</span>
            ) : (
              <Trash2 className="h-4 w-4" />
            )}
          </Button>
        </div>
        {showConfirm && (
          <p className="text-xs text-destructive" data-testid="confirm-message">
            Click delete again to confirm
          </p>
        )}
      </CardContent>
    </Card>
  );
}
