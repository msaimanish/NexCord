export default function Home() {
  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100">
      <div className="flex min-h-screen">
        {/* Sidebar */}
        <aside className="hidden w-64 flex-col border-r border-zinc-800 bg-zinc-950 px-5 py-6 md:flex">
          <div className="mb-10">
            <div className="text-xl font-semibold tracking-tight">NexCord</div>
            <div className="mt-1 text-xs text-zinc-500">
              Event Operations Intelligence
            </div>
          </div>

          <nav className="space-y-2 text-sm">
            <a
              href="#"
              className="block rounded-lg bg-zinc-800 px-3 py-2.5 font-medium text-white"
            >
              Overview
            </a>

            <a
              href="#"
              className="block rounded-lg px-3 py-2.5 text-zinc-400 transition hover:bg-zinc-900 hover:text-white"
            >
              Incidents
            </a>

            <a
              href="#"
              className="block rounded-lg px-3 py-2.5 text-zinc-400 transition hover:bg-zinc-900 hover:text-white"
            >
              Plans
            </a>

            <a
              href="#"
              className="block rounded-lg px-3 py-2.5 text-zinc-400 transition hover:bg-zinc-900 hover:text-white"
            >
              Executions
            </a>
          </nav>

          <div className="mt-auto rounded-xl border border-zinc-800 bg-zinc-900/60 p-4">
            <div className="text-xs uppercase tracking-wider text-zinc-500">
              System
            </div>

            <div className="mt-3 flex items-center gap-2 text-sm">
              <span className="h-2 w-2 rounded-full bg-emerald-400" />
              All systems operational
            </div>
          </div>
        </aside>

        {/* Main content */}
        <section className="flex-1">
          {/* Header */}
          <header className="flex items-center justify-between border-b border-zinc-800 px-6 py-5 lg:px-10">
            <div>
              <div className="text-sm text-zinc-500">GITAM TechFest 2026</div>
              <h1 className="mt-1 text-2xl font-semibold tracking-tight">
                Operations Overview
              </h1>
            </div>

            <div className="flex items-center gap-2 rounded-full border border-zinc-800 bg-zinc-900 px-3 py-1.5 text-xs">
              <span className="h-2 w-2 rounded-full bg-emerald-400" />
              LIVE
            </div>
          </header>

          <div className="space-y-8 px-6 py-8 lg:px-10">
            {/* Summary cards */}
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <div className="rounded-2xl border border-zinc-800 bg-zinc-900/70 p-5">
                <div className="text-sm text-zinc-500">Active incidents</div>
                <div className="mt-3 text-3xl font-semibold">3</div>
                <div className="mt-2 text-xs text-zinc-500">
                  Requiring operator attention
                </div>
              </div>

              <div className="rounded-2xl border border-zinc-800 bg-zinc-900/70 p-5">
                <div className="text-sm text-zinc-500">Highest risk</div>
                <div className="mt-3 text-3xl font-semibold">HIGH</div>
                <div className="mt-2 text-xs text-zinc-500">
                  Current event risk level
                </div>
              </div>

              <div className="rounded-2xl border border-zinc-800 bg-zinc-900/70 p-5">
                <div className="text-sm text-zinc-500">System health</div>
                <div className="mt-3 text-3xl font-semibold">97%</div>
                <div className="mt-2 text-xs text-zinc-500">
                  Services responding normally
                </div>
              </div>
            </div>

            {/* Incident */}
            <section>
              <div className="mb-4">
                <div className="text-sm text-zinc-500">Attention required</div>
                <h2 className="mt-1 text-xl font-semibold">
                  Active Incident
                </h2>
              </div>

              <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-6">
                <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
                  <div>
                    <div className="flex items-center gap-3">
                      <h3 className="text-lg font-semibold">
                        Projector failure
                      </h3>

                      <span className="rounded-full border border-red-500/30 bg-red-500/10 px-2.5 py-1 text-xs font-medium text-red-300">
                        HIGH
                      </span>
                    </div>

                    <p className="mt-2 text-sm text-zinc-400">
                      Main Auditorium · Robotics Final
                    </p>

                    <div className="mt-4 flex flex-wrap gap-2">
                      <span className="rounded-lg bg-zinc-800 px-3 py-1.5 text-xs text-zinc-300">
                        Equipment
                      </span>

                      <span className="rounded-lg bg-zinc-800 px-3 py-1.5 text-xs text-zinc-300">
                        Schedule
                      </span>

                      <span className="rounded-lg bg-zinc-800 px-3 py-1.5 text-xs text-zinc-300">
                        Audience
                      </span>
                    </div>
                  </div>

                  <button className="rounded-xl bg-white px-5 py-3 text-sm font-medium text-black transition hover:bg-zinc-200">
                    Simulate Response
                  </button>
                </div>
              </div>
            </section>

            {/* Agent */}
            <section>
              <div className="mb-4">
                <div className="text-sm text-zinc-500">Human-in-the-loop</div>
                <h2 className="mt-1 text-xl font-semibold">NexCord Agent</h2>
              </div>

              <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-6">
                <div className="flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
                  <div>
                    <div className="text-sm text-zinc-500">Agent status</div>
                    <div className="mt-2 flex items-center gap-2 text-sm">
                      <span className="h-2 w-2 rounded-full bg-emerald-400" />
                      Ready
                    </div>

                    <p className="mt-4 max-w-2xl text-lg text-zinc-200">
                      Ask NexCord about incidents, risks, schedules, resources,
                      or response plans.
                    </p>
                  </div>

                  <button className="flex h-14 w-14 items-center justify-center rounded-full bg-white text-xl text-black transition hover:bg-zinc-200">
                    🎤
                  </button>
                </div>
              </div>
            </section>
          </div>
        </section>
      </div>
    </main>
  );
}