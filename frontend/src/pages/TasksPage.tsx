import { TaskList } from "@/features/tasks/TaskList";

export default function TasksPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-foreground mb-6">Zadania</h1>
      <TaskList />
    </div>
  );
}