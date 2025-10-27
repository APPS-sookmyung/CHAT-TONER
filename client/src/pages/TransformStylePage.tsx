import { TransformStyleCard } from "@/components/Organisms/TransformStyleCard";

export default function TransformStylePage() {
  return (
    <div>
      <h1 className="font-bold text-black text-7xl">Transform Style Page</h1>
      <p className="mt-4 mb-12 text-5xl font-medium text-gray-700">
        Transform document style instantly
      </p>

      <TransformStyleCard />
    </div>
  );
}
