// activityTracker.js
class ActivityTracker {
  constructor(timeoutMs = process.env.TIMEOUTMS ?? 10000) {
    this.timeoutMs = timeoutMs;
    this.lastSeen = new Map(); // id -> timestamp (ms)
  }

  update(ID_UUID) {
    this.lastSeen.set(ID_UUID, Date.now());
  }

  isActive(ID_UUID) {
    const last = this.lastSeen.get(ID_UUID);
    if (!last) return false;
    return Date.now() - last <= this.timeoutMs;
  }
}

export const tracker = new ActivityTracker();