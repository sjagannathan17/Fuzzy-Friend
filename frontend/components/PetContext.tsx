"use client";

import React, { createContext, useContext, useState, ReactNode } from "react";

type PetContextType = {
  petName: string;
  setPetName: (name: string) => void;
};

const PetContext = createContext<PetContextType | undefined>(undefined);

export function PetProvider({ children }: { children: ReactNode }) {
  const [petName, setPetName] = useState<string>("your pet");
  return (
    <PetContext.Provider value={{ petName, setPetName }}>
      {children}
    </PetContext.Provider>
  );
}

export function usePet() {
  const context = useContext(PetContext);
  if (!context) {
    throw new Error("usePet must be used within a PetProvider");
  }
  return context;
}
