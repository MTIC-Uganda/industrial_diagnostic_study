// ─────────────────────────────────────────────────────────────────────────────
// Onboarding tour — single source of truth for the steps.
// Edit copy / order / targets HERE only; no component logic lives in this file.
// Each step: { element?: "#id", popover: { title, description, side?, align? } }
// A step with no `element` shows as a centered modal (used for intro/outro).
// ─────────────────────────────────────────────────────────────────────────────

export const TOUR_STEPS = [
  {
    popover: {
      title: "Welcome to MTIC Value Chains",
      description:
        "This tool breaks a finished product down into everything used to make it — its technology types, then the components, materials, labour and machinery beneath them. Take 30 seconds and we'll show you around.",
    },
  },
  {
    element: "#tour-valuechain",
    popover: {
      title: "Step 1 — Pick a value chain",
      description:
        "Start here. Choose which sector to explore — for example Iron & Steel, Textiles & Garments, or Cement.",
      side: "bottom",
      align: "start",
    },
  },
  {
    element: "#tour-product",
    popover: {
      title: "Step 2 — Pick a finished product",
      description:
        "Then choose the specific product you want to trace back to its raw materials.",
      side: "bottom",
      align: "start",
    },
  },
  {
    element: "#tour-diagram",
    popover: {
      title: "Step 3 — Read the diagram",
      description:
        "The finished product sits on the left; its inputs branch out to the right, going further upstream toward raw materials. Each block is a 'node' (a system, component, material, or cost). The width of each flow shows how big a share of cost it is.",
      side: "top",
      align: "center",
    },
  },
  {
    element: "#tour-node",
    popover: {
      title: "Step 4 — Click a block to dig deeper",
      description:
        "Each bar like this one is a block. Click it and two things happen: the chart re-centres on that block to show its own breakdown, and a details panel opens on the right with its function, HS codes, live ITC TradeMap trade data, and sources.",
      side: "right",
      align: "start",
    },
  },
  {
    element: "#tour-breadcrumb",
    popover: {
      title: "Step 5 — Find your way back",
      description:
        "This breadcrumb trail tracks where you are as you drill into blocks — here it's showing a sample step from the product into one of its inputs. Use ‹ back to step out one level, or ✕ reset to jump straight back to the original product.",
      side: "bottom",
      align: "start",
    },
  },
  {
    element: "#tour-layers",
    popover: {
      title: "Step 6 — Control the depth",
      description:
        "Use the Layers slider to choose how many steps upstream to show: 1 shows just the first breakdown; higher values go deeper toward raw materials.",
      side: "bottom",
      align: "start",
    },
  },
  {
    element: "#tour-minflow",
    popover: {
      title: "Step 7 — Declutter the view",
      description:
        "Raise the Min flow slider to hide the smaller flows, so you see only the most significant inputs.",
      side: "bottom",
      align: "start",
    },
  },
  {
    element: "#tour-legend",
    popover: {
      title: "Step 8 — The colour key",
      description:
        "The legend explains what each block colour means — finished product, technology type, component, material, energy, labour or machinery.",
      side: "top",
      align: "start",
    },
  },
  {
    element: "#tour-button",
    popover: {
      title: "That's it — explore!",
      description:
        "You can replay this walkthrough anytime using the Take a Tour button here. Enjoy exploring Uganda's value chains.",
      side: "bottom",
      align: "end",
    },
  },
];
