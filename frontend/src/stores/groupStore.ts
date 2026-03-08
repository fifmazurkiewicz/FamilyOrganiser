import { create } from "zustand";
import { persist } from "zustand/middleware";

interface FamilyGroup {
  id: string;
  name: string;
  member_count: number;
  pending_requests?: number;
}

interface GroupState {
  activeGroup: FamilyGroup | null;
  groups: FamilyGroup[];
  setActiveGroup: (group: FamilyGroup | null) => void;
  setGroups: (groups: FamilyGroup[]) => void;
}

export const useGroupStore = create<GroupState>()(
  persist(
    (set) => ({
      activeGroup: null,
      groups: [],
      setActiveGroup: (group) => set({ activeGroup: group }),
      setGroups: (groups) => set({ groups }),
    }),
    {
      name: "group-storage",
    }
  )
);
