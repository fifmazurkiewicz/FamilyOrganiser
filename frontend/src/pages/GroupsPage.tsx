import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import { useGroupStore } from "@/stores/groupStore";
import { Users, Plus, UserMinus, Link, Check } from "lucide-react";

export default function GroupsPage() {
  const [showCreate, setShowCreate] = useState(false);
  const [groupName, setGroupName] = useState("");
  const qc = useQueryClient();
  const { activeGroup, setActiveGroup } = useGroupStore();

  const { data: groups = [], isLoading } = useQuery({
    queryKey: ["groups"],
    queryFn: () => api.get("/groups/").then((r) => r.data),
  });

  const { data: members = [] } = useQuery({
    queryKey: ["members", activeGroup?.id],
    queryFn: () =>
      activeGroup ? api.get(`/groups/${activeGroup.id}/members`).then((r) => r.data) : [],
    enabled: !!activeGroup?.id,
  });

  const createMutation = useMutation({
    mutationFn: (name: string) => api.post("/groups/", { name }),
    onSuccess: (res) => {
      qc.invalidateQueries({ queryKey: ["groups"] });
      setShowCreate(false);
      setGroupName("");
    },
  });

  const [invLink, setInvLink] = useState<string | null>(null);
  const createInviteMutation = useMutation({
    mutationFn: (groupId: string) =>
      api.post(`/groups/${groupId}/invitations`, { single_use: false, expire_days: 7 }).then((r) => r.data),
    onSuccess: (data) => {
      const url = `${window.location.origin}/register?invite=${data.token}`;
      setInvLink(url);
    },
  });

  const removeMemberMutation = useMutation({
    mutationFn: ({ groupId, userId }: { groupId: string; userId: string }) =>
      api.delete(`/groups/${groupId}/members/${userId}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["members", activeGroup?.id] });
    },
  });

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Moje grupy rodzinne</h1>
          <p className="text-gray-500 text-sm">{groups.length} grup(y)</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90"
        >
          <Plus className="h-4 w-4" />
          Nowa grupa
        </button>
      </div>

      {showCreate && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <h2 className="font-semibold text-gray-900 mb-3">Utwórz grupę rodzinną</h2>
          <div className="flex gap-2">
            <input
              value={groupName}
              onChange={(e) => setGroupName(e.target.value)}
              placeholder="Np. Rodzina Kowalskich"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
            <button
              onClick={() => createMutation.mutate(groupName)}
              disabled={!groupName || createMutation.isPending}
              className="bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
            >
              Utwórz
            </button>
            <button
              onClick={() => setShowCreate(false)}
              className="px-4 py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-100"
            >
              Anuluj
            </button>
          </div>
        </div>
      )}

      {/* Group tiles */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {groups.map((group: any) => (
          <div
            key={group.id}
            className={`bg-white rounded-xl shadow-sm border-2 p-5 cursor-pointer transition-all ${
              activeGroup?.id === group.id ? "border-primary" : "border-gray-100 hover:border-gray-200"
            }`}
            onClick={() => setActiveGroup(group)}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="bg-primary/10 rounded-lg p-2">
                  <Users className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="font-semibold text-gray-900">{group.name}</p>
                  <p className="text-xs text-gray-400">{group.member_count} członków</p>
                </div>
              </div>
              {activeGroup?.id === group.id && (
                <span className="text-xs bg-primary text-white px-2 py-0.5 rounded-full">aktywna</span>
              )}
            </div>

            <div className="flex gap-2 mt-3">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  createInviteMutation.mutate(group.id);
                }}
                className="flex items-center gap-1 text-xs text-blue-600 border border-blue-200 px-2 py-1 rounded hover:bg-blue-50"
              >
                <Link className="h-3 w-3" />
                Zaproś
              </button>
            </div>
          </div>
        ))}
      </div>

      {invLink && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
          <p className="text-sm font-medium text-blue-900 mb-2">Link zaproszeniowy:</p>
          <div className="flex gap-2">
            <input
              readOnly
              value={invLink}
              className="flex-1 bg-white border border-blue-200 rounded px-3 py-1.5 text-sm"
            />
            <button
              onClick={() => { navigator.clipboard.writeText(invLink); }}
              className="flex items-center gap-1 bg-blue-600 text-white px-3 py-1.5 rounded text-sm hover:bg-blue-700"
            >
              <Check className="h-3 w-3" />
              Kopiuj
            </button>
          </div>
          <button onClick={() => setInvLink(null)} className="text-xs text-blue-500 mt-2">Zamknij</button>
        </div>
      )}

      {/* Active group members */}
      {activeGroup && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <h2 className="font-semibold text-gray-900 mb-4">
            Członkowie: {activeGroup.name}
          </h2>
          {members.length === 0 ? (
            <p className="text-gray-400 text-sm">Brak członków</p>
          ) : (
            <div className="space-y-2">
              {members.map((member: any) => (
                <div key={member.id} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="bg-gray-100 rounded-full h-8 w-8 flex items-center justify-center">
                      <span className="text-sm font-medium text-gray-600">
                        {member.full_name.charAt(0)}
                      </span>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{member.full_name}</p>
                      <p className="text-xs text-gray-400">{member.email}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${
                        member.role === "admin"
                          ? "bg-amber-100 text-amber-700"
                          : "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {member.role === "admin" ? "Admin" : "Członek"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
