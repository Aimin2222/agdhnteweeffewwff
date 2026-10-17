# Authorized margin cleanup — review only

This separate derivative removes only tiny isolated alpha=2 or alpha=3 components from empty margins. Original source images, raw generated PNGs and earlier alpha=1 derivatives remain unchanged. All RGB values and nonselected alpha values are identical.

This earlier conservative pass protects the full alpha≥4 artwork bounding box expanded by 24 pixels. It is retained alongside the later distance-based pass.

Frozen raw snapshot: repair0100. Checked: 652. Modified PNGs: 5. Removed pixels: 41. Remaining outer-edge warnings: 198. Final approved: 0.

Remaining edge warnings require generation and visual review; this permission does not authorize broad glow removal. These files have not yet replaced the live production candidates. Manifest: `checkpoints/margin_dots_cleanup_checkpoint_0634_repair0100.json`.
