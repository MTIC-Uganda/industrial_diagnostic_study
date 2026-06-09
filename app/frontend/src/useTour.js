// Standalone onboarding-tour hook. Wraps Driver.js and owns the first-visit
// auto-launch + replay behaviour. Kept separate from page logic so the tour is
// a self-contained feature (see tour.js for the editable step config).
//
// `onActiveChange(active)` is called with true when the tour starts and false
// when it ends, so the app can reveal demo-only affordances (e.g. the breadcrumb
// back/reset buttons) during the tour and hide them again afterwards.
import { useCallback, useEffect } from "react";
import { driver } from "driver.js";
import "driver.js/dist/driver.css";
import { TOUR_STEPS } from "./tour.js";

const SEEN_KEY = "mtic_tour_seen";
let autoLaunched = false; // guard against React StrictMode double-invoke

export function useTour(onActiveChange) {
  const startTour = useCallback(() => {
    onActiveChange?.(true);
    driver({
      showProgress: true,
      allowClose: true,
      smoothScroll: true,
      overlayOpacity: 0.6,
      nextBtnText: "Next →",
      prevBtnText: "← Back",
      doneBtnText: "Done",
      onDestroyed: () => onActiveChange?.(false), // fires on Done / close / Esc
      // The diagram is taller than the viewport, so earlier steps scroll the
      // content area DOWN to reveal it. The breadcrumb (with the back/reset
      // buttons) lives at the very top, so when we reach it scroll the area back
      // UP — otherwise those buttons stay hidden above the fold. Instant scroll so
      // Driver.js reads the element's final position when it places the popover.
      onHighlightStarted: (el) => {
        const sc = document.getElementById("tour-scroll");
        if (sc && el && (el.id === "tour-breadcrumb" || el.id === "tour-tip")) {
          sc.scrollTo({ top: 0 });
        }
      },
      steps: TOUR_STEPS,
    }).drive();
  }, [onActiveChange]);

  // Auto-launch once, on a user's first visit only (tracked in localStorage).
  useEffect(() => {
    if (autoLaunched || localStorage.getItem(SEEN_KEY) === "1") return;
    autoLaunched = true;
    localStorage.setItem(SEEN_KEY, "1");
    const id = setTimeout(startTour, 800); // let the app render first
    return () => clearTimeout(id);
  }, [startTour]);

  return { startTour };
}
