import { GameBoard } from "@/components/game";

export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50">
      <main className="flex flex-col items-center gap-8 py-8">
        <h1 className="text-2xl font-semibold text-zinc-900 font-mono">
          Tic-Tac-Toe
        </h1>
        <GameBoard />
      </main>
    </div>
  );
}
