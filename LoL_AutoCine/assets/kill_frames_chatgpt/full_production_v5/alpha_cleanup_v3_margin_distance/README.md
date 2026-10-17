# Authorized margin cleanup — review only

This separate derivative removes only tiny isolated alpha=2 or alpha=3 components from empty margins. Original source images, raw generated PNGs and earlier alpha=1 derivatives remain unchanged. All RGB values and nonselected alpha values are identical.

Each selected 8-connected component has at most 64 pixels, fits within 8×8 pixels, and lies entirely more than 24 pixels from every alpha≥4 pixel. Artwork and its glow protection region are byte-identical.

Frozen raw snapshot: repair0100. Checked: 652. Modified PNGs: 189. Removed pixels: 4435. Remaining outer-edge warnings: 198. Final approved: 0.

Remaining edge warnings require generation and visual review; this permission does not authorize broad glow removal. These files have not yet replaced the live production candidates. Manifest: `checkpoints/margin_distance_cleanup_checkpoint_0634_repair0100.json`.
