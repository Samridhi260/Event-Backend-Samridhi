// v2 Cloud Functions syntax
const { onDocumentCreated } = require("firebase-functions/v2/firestore");

const { onRequest } = require("firebase-functions/v2/https");
const { onSchedule } = require("firebase-functions/v2/scheduler");

const { initializeApp } = require("firebase-admin/app");
const { getFirestore } = require("firebase-admin/firestore");

initializeApp();

/**
 * Trigger: runs automatically when a new doc is created in "events"
 * This uses v2 API (onDocumentCreated) and works in the emulator.
 */
exports.onEventCreate = onDocumentCreated("events/{eventId}", async (event) => {
  const snapshot = event.data;
  if (!snapshot) {
    console.log("No snapshot provided.");
    return;
  }

  const newEvent = snapshot.data();
  const eventId = event.params.eventId;
  console.log(`onEventCreate triggered for ${eventId}`, newEvent);

  const uid = newEvent.user_id;
  if (!uid) {
    console.log("No user_id on event; skipping analytics update");
    return;
  }

  const db = getFirestore();
  const analyticsRef = db.collection("analytics").doc(uid);

  await db.runTransaction(async (tx) => {
    const docSnap = await tx.get(analyticsRef);
    const current =
      docSnap.exists && docSnap.data().totalEvents
        ? docSnap.data().totalEvents
        : 0;
    tx.set(analyticsRef, { totalEvents: current + 1 }, { merge: true });
  });

  console.log(`Analytics updated for user ${uid}`);
});

// ===== Scheduled Notifications (bonus) =====

// Helper: generate notification docs for events created in the last 24h
async function generateUpcomingNotifications() {
  const db = getFirestore();
  const now = new Date();
  const since = new Date(now.getTime() - 24 * 60 * 60 * 1000); // last 24h

  // NOTE: Your events have "created_at" as an ISO string from the API.
  // We'll match events created in the last 24 hours.
  const snap = await db.collection("events")
    .where("created_at", ">=", since.toISOString())
    .get();

  let count = 0;
  for (const doc of snap.docs) {
    const data = doc.data() || {};
    const uid = data.user_id;
    if (!uid) continue;
    await db.collection("notifications").doc(uid)
      .collection("items").doc(doc.id)
      .set({
        type: "upcoming_event",
        title: data.title || "event",
        created_at: new Date().toISOString(),
        event_id: doc.id,
      }, { merge: true });
    count++;
  }
  console.log(`Notifications generated: ${count}`);
  return count;
}

// v2 Scheduled function — runs every 24 hours (UTC)
exports.nightlySummary = onSchedule("every 24 hours", async (event) => {
  console.log("nightlySummary started");
  await generateUpcomingNotifications();
  console.log("nightlySummary finished");
});

// v2 HTTPS function — run manually in emulator for instant testing
exports.runNotificationJobNow = onRequest(async (req, res) => {
  try {
    const count = await generateUpcomingNotifications();
    res.json({ ok: true, generated: count });
  } catch (e) {
    console.error(e);
    res.status(500).json({ ok: false, error: String(e) });
  }
});

