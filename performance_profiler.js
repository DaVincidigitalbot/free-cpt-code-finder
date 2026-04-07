(function () {
  const state = {
    enabled: true,
    marks: new Map(),
    stats: Object.create(null),
    events: [],
    maxEvents: 200
  };

  function now() {
    return (window.performance && performance.now) ? performance.now() : Date.now();
  }

  function ensure(name) {
    if (!state.stats[name]) {
      state.stats[name] = {
        name,
        total: 0,
        count: 0,
        avg: 0,
        max: 0,
        min: Infinity,
        blockingCount: 0,
        last: 0,
        lastMeta: null
      };
    }
    return state.stats[name];
  }

  function record(name, duration, meta = {}) {
    if (!state.enabled) return duration;
    const stat = ensure(name);
    stat.total += duration;
    stat.count += 1;
    stat.avg = stat.total / stat.count;
    stat.max = Math.max(stat.max, duration);
    stat.min = Math.min(stat.min, duration);
    stat.last = duration;
    stat.lastMeta = meta;
    if (meta.blocksUI) stat.blockingCount += 1;

    state.events.push({
      ts: new Date().toISOString(),
      name,
      duration,
      meta
    });
    if (state.events.length > state.maxEvents) state.events.shift();
    return duration;
  }

  const api = {
    enable() { state.enabled = true; },
    disable() { state.enabled = false; },
    start(name, meta = {}) {
      if (!state.enabled) return null;
      const token = Symbol(name);
      state.marks.set(token, { name, start: now(), meta });
      return token;
    },
    end(token, extraMeta = {}) {
      if (!state.enabled || !token || !state.marks.has(token)) return 0;
      const mark = state.marks.get(token);
      state.marks.delete(token);
      return record(mark.name, now() - mark.start, { ...mark.meta, ...extraMeta });
    },
    measure(name, fn, meta = {}) {
      const token = this.start(name, meta);
      try {
        const result = fn();
        if (result && typeof result.then === 'function') {
          return result.then((value) => {
            this.end(token);
            return value;
          }).catch((error) => {
            this.end(token, { error: error && error.message ? error.message : String(error) });
            throw error;
          });
        }
        this.end(token);
        return result;
      } catch (error) {
        this.end(token, { error: error && error.message ? error.message : String(error) });
        throw error;
      }
    },
    log(name, duration, meta = {}) {
      return record(name, duration, meta);
    },
    summary() {
      return Object.values(state.stats)
        .map((stat) => ({
          functionName: stat.name,
          totalMs: Number(stat.total.toFixed(2)),
          avgMs: Number(stat.avg.toFixed(2)),
          maxMs: Number(stat.max.toFixed(2)),
          minMs: Number((stat.min === Infinity ? 0 : stat.min).toFixed(2)),
          callCount: stat.count,
          blocksUI: stat.blockingCount > 0 ? 'sometimes' : 'no',
          blockingCallCount: stat.blockingCount,
          lastMs: Number(stat.last.toFixed(2)),
          lastMeta: stat.lastMeta
        }))
        .sort((a, b) => b.totalMs - a.totalMs);
    },
    top(limit = 10) {
      return this.summary().slice(0, limit);
    },
    recentEvents(limit = 25) {
      return state.events.slice(-limit);
    },
    reset() {
      state.marks.clear();
      state.stats = Object.create(null);
      state.events = [];
    },
    print(limit = 10) {
      const rows = this.top(limit);
      console.table(rows);
      return rows;
    },
    export() {
      return {
        generatedAt: new Date().toISOString(),
        summary: this.summary(),
        events: [...state.events]
      };
    }
  };

  window.PerfProfiler = api;
})();
