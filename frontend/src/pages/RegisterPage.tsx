import { Link } from "react-router-dom";
import { RegisterForm } from "@/features/auth/RegisterForm";

export default function RegisterPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-primary">FamilyOrganiser</h1>
          <p className="mt-2 text-gray-500">Zarządzaj finansami rodziny</p>
        </div>
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Utwórz konto</h2>
          <RegisterForm />
          <p className="mt-6 text-center text-sm text-gray-500">
            Masz już konto?{" "}
            <Link to="/login" className="text-primary font-medium hover:underline">
              Zaloguj się
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
