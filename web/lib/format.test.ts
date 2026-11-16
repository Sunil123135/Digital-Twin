import { describe, expect, it } from "vitest";
import { formatDays, formatINR, formatPct } from "./format";

describe("formatINR", () => {
  it("shows crore above one crore", () => {
    expect(formatINR(1_864_000_000)).toBe("₹186.4 cr");
  });

  it("shows lakh between one lakh and one crore", () => {
    expect(formatINR(1_240_000)).toBe("₹12.4 L");
  });

  it("shows the full amount below one lakh", () => {
    expect(formatINR(84500)).toBe("₹84,500");
  });

  it("keeps a sign", () => {
    expect(formatINR(-42_600_000)).toBe("-₹4.3 cr");
  });
});

describe("formatPct and formatDays", () => {
  it("formats ratios and days", () => {
    expect(formatPct(0.986)).toBe("98.6%");
    expect(formatDays(12.2)).toBe("12 days");
  });
});
