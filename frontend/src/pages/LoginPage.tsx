import { Link } from "react-router-dom";
import { LoginForm } from "@/features/auth/LoginForm";

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-primary">FamilyOrganiser</h1>
          <p className="mt-2 text-gray-500">Zarządzaj finansami rodziny</p>
        </div>
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Zaloguj się</h2>
          <LoginForm />
          <p className="mt-6 text-center text-sm text-gray-500">
            Nie masz konta?{" "}
            <Link to="/register" className="text-primary font-medium hover:underline">
              Zarejestruj się
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
